import json
import smtplib
import ssl
from email.message import EmailMessage
from html import escape
from datetime import timedelta
from uuid import uuid4
from cryptography.fernet import Fernet
from app.core.config import settings
from app.models.auth_session import MailOutbox
from app.repositories.auth_repository import now
from app.repositories.mail_repository import MailRepository
from app.services.audit_service import AuditService


class MailService:
    def __init__(self, db):
        self.db = db
        self.repo = MailRepository(db)

    def enqueue_invitation(self, invitation, raw):
        from types import SimpleNamespace

        recipient = SimpleNamespace(id=None, full_name="", email=invitation.email)
        self.enqueue(recipient, "invitation", raw=raw, invitation=invitation)

    def enqueue_unlock_request(self, request, user):
        support_email = settings.support_contact or "juspjchaco@gmail.com"
        text = (
            "Solicitud de desbloqueo de usuario.\n\n"
            f"Usuario: {user.full_name}\n"
            f"Correo: {user.email}\n"
            f"Rol: {user.role.value}\n"
            f"Intentos fallidos: {user.failed_attempts}\n"
            f"Bloqueado hasta: {user.locked_until or 'sin bloqueo vigente'}\n"
            f"Mensaje: {request.note or 'Sin mensaje adicional'}\n\n"
            "Revisá el panel administrador para desbloquear la cuenta si corresponde."
        )
        data = {
            "to": support_email,
            "subject": "Solicitud de desbloqueo de usuario",
            "text": text,
            "html": "<html lang=\"es\"><body><h1>Solicitud de desbloqueo</h1><p>"
            + escape(text).replace("\n", "<br>")
            + "</p></body></html>",
        }
        payload = (
            Fernet(settings.mail_outbox_key.encode())
            .encrypt(json.dumps(data).encode())
            .decode()
        )
        identity = str(uuid4())
        self.db.add(
            MailOutbox(
                id=identity,
                event_key=f"unlock_request:{request.id}",
                user_id=user.id,
                kind="unlock_request",
                payload=payload,
                state="pending",
                attempts=0,
                available_at=now(),
                expires_at=now() + timedelta(days=1),
                created_at=now(),
            )
        )
        self.db.flush()

    def enqueue(
        self, user, kind, raw=None, reset=None, cooldown=False, invitation=None
    ):
        if cooldown and self.repo.recent(user.id, kind, settings.mail_cooldown_seconds):
            return
        titles = {
            "reset": "Recuperá tu contraseña",
            "password_changed": "Tu contraseña fue actualizada",
            "unlocked": "Tu cuenta fue desbloqueada",
            "invitation": "Invitación a Junta Electoral",
        }
        text = f"Hola {user.full_name}.\n\n{titles[kind]}.\n"
        link = None
        if raw:
            route = "restablecer-clave" if kind == "reset" else "invitacion"
            link = f"{settings.frontend_url.rstrip('/')}/{route}#token={raw}"
            text += f"Abrí {link}\nEl enlace vence en {settings.reset_expire_minutes if kind == 'reset' else settings.invitation_expire_hours * 60} minutos y se usa una sola vez.\n"
        text += f"\nSi no reconocés esta acción, contactá a la Junta Electoral. {settings.support_contact}\nPartido Justicialista · Distrito Chaco"
        data = {
            "to": user.email,
            "subject": titles[kind],
            "text": text,
            "html": '<html lang="es"><body><h1>Junta Electoral</h1><p>'
            + escape(text).replace("\n", "<br>")
            + (
                f'<br><a href="{escape(link, quote=True)}">Continuar de forma segura</a>'
                if link
                else ""
            )
            + "</p></body></html>",
        }
        # Mandatory even in development: never persist a reset link in plaintext.
        payload = (
            Fernet(settings.mail_outbox_key.encode())
            .encrypt(json.dumps(data).encode())
            .decode()
        )
        identity = str(uuid4())
        self.db.add(
            MailOutbox(
                id=identity,
                event_key=f"{kind}:{reset.digest if reset else identity}",
                user_id=user.id,
                invitation_id=invitation.id if invitation else None,
                invitation_digest=invitation.digest if invitation else None,
                kind=kind,
                payload=payload,
                reset_digest=reset.digest if reset else None,
                state="pending",
                attempts=0,
                available_at=now(),
                expires_at=invitation.expires_at
                if invitation
                else reset.expires_at
                if reset
                else now() + timedelta(days=1),
                created_at=now(),
            )
        )
        self.db.flush()

    def send(self, identity, data):
        message = EmailMessage()
        message["From"], message["To"], message["Subject"] = (
            settings.smtp_from,
            data["to"],
            data["subject"],
        )
        message["Message-ID"] = f"<{identity}@junta-electoral.local>"
        message.set_content(data["text"])
        message.add_alternative(data["html"], subtype="html")
        context = ssl.create_default_context()
        transport = smtplib.SMTP_SSL if settings.smtp_tls == "ssl" else smtplib.SMTP
        kwargs = {"timeout": settings.smtp_timeout}
        if settings.smtp_tls == "ssl":
            kwargs["context"] = context
        with transport(settings.smtp_host, settings.smtp_port, **kwargs) as smtp:
            if settings.smtp_tls == "starttls":
                smtp.starttls(context=context)
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)

    def process_one(self):
        row = self.repo.claim()
        if not row:
            self.db.rollback()
            return False
        if not self.repo.valid(row) or row.attempts >= settings.mail_max_attempts:
            row.state, row.payload, row.last_error = (
                "failed",
                None,
                "expired_or_exhausted",
            )
            self.db.commit()
            return True
        identity, lease = row.id, str(uuid4())
        row.lease_id, row.state = lease, "processing"
        row.attempts += 1
        row.available_at = now() + timedelta(seconds=settings.mail_lease_seconds)
        self.db.commit()
        # Lock until SMTP completes: a second consumer cannot reclaim a live delivery.
        row = self.repo.locked(identity)
        if row.lease_id != lease or not self.repo.valid(row):
            self.db.rollback()
            return True
        try:
            data = json.loads(
                Fernet(settings.mail_outbox_key.encode()).decrypt(row.payload.encode())
            )
            self.send(identity, data)
        except Exception as exc:
            permanent = (
                isinstance(exc, smtplib.SMTPResponseException)
                and 500 <= exc.smtp_code < 600
            )
            terminal = permanent or row.attempts >= settings.mail_max_attempts
            row.state = "failed" if terminal else "pending"
            row.last_error = "smtp_permanent" if permanent else "delivery_failed"
            row.available_at = now() + timedelta(
                seconds=min(3600, 30 * 2**row.attempts)
            )
            if terminal:
                row.payload = None
            AuditService(self.db).record(
                None,
                "mail.failed",
                "invitations" if row.invitation_id else "users",
                row.invitation_id or row.user_id,
                {"outbox_id": identity, "attempts": row.attempts, "terminal": terminal},
            )
        else:
            row.state, row.payload, row.last_error = "sent", None, None
            AuditService(self.db).record(
                None,
                "mail.smtp_accepted",
                "invitations" if row.invitation_id else "users",
                row.invitation_id or row.user_id,
                {"outbox_id": identity},
            )
        self.db.commit()
        return True
