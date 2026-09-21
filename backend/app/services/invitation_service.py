import secrets
from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.core.passwords import hash_password, validate_password
from app.models import User, UserModule, Election, Office, Municipality
from app.models.invitation import Invitation
from app.repositories.auth_repository import AuthRepository, now, digest
from app.repositories.invitation_repository import InvitationRepository
from app.repositories.management_repository import ManagementRepository
from app.schemas.management import ModuleInput
from app.services.audit_service import AuditService
from app.services.mail_service import MailService
from app.utils.enums import UserRole, UserModuleType


class InvitationService:
    def __init__(self, db):
        self.db = db
        self.repo = InvitationRepository(db)
        self.auth = AuthRepository(db)
        self.management = ManagementRepository(db)

    def quota(self, actor_id):
        if not self.auth.quota(
            "invite-admin", str(actor_id), settings.invitation_hourly_limit, 3600
        ):
            raise HTTPException(
                429, "Límite de invitaciones alcanzado. Intentá más tarde."
            )

    def actor(self, identity):
        actor = self.auth.user(identity)
        if not actor or not actor.is_active or actor.role != UserRole.ADMIN:
            raise HTTPException(
                400,
                "La autorización de esta invitación ya no está vigente. Pedí una nueva.",
            )
        return actor

    def modules(self, values):
        # Lock each catalog in a global order, even across different election/module sets.
        elections = {
            key: self.management.get(Election, key, True)
            for key in sorted({m.election_id for m in values})
        }
        offices = {
            key: self.management.get(Office, key, True)
            for key in sorted({m.office_id for m in values})
        }
        municipalities = {
            key: self.management.get(Municipality, key, True)
            for key in sorted({m.municipality_id for m in values if m.municipality_id})
        }
        seen = set()
        for m in sorted(
            values, key=lambda m: (m.election_id, m.office_id, m.municipality_id or 0)
        ):
            key = (m.election_id, m.office_id, m.municipality_id)
            if key in seen or not m.enabled:
                raise HTTPException(
                    422, "Los módulos deben estar habilitados y no repetidos."
                )
            seen.add(key)
            election = elections[m.election_id]
            office = offices[m.office_id]
            municipality = municipalities.get(m.municipality_id)
            if (
                not election
                or not election.active
                or not office
                or not office.active
                or (m.municipality_id and (not municipality or not municipality.active))
            ):
                raise HTTPException(
                    409,
                    "Los catálogos del módulo ya no están activos. Cancelá y creá una nueva invitación.",
                )
            if office.municipality_based != (m.municipality_id is not None):
                raise HTTPException(
                    422, "El municipio no corresponde al alcance del cargo."
                )
            rule = self.management.rule(m.election_id, m.office_id)
            if not rule or not rule.enabled:
                raise HTTPException(409, "Las reglas del módulo no están habilitadas.")
        return [m.model_dump() for m in values]

    def output(self, row):
        return {
            "id": row.id,
            "email": row.email,
            "role": row.role,
            "modules": row.modules,
            "state": "expired"
            if row.state == "pending" and row.expires_at <= now()
            else row.state,
            "expires_at": row.expires_at,
            "generation": row.generation,
            "mail_state": self.repo.mail_state(row),
        }

    def commit(self):
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                409,
                "El correo o nombre de usuario ya está registrado. Revisá las cuentas e invitaciones existentes.",
            ) from exc

    def issue(self, row, actor, action):
        raw = secrets.token_urlsafe(32)
        row.digest, row.sent_at = digest(raw), now()
        row.expires_at = now() + timedelta(hours=settings.invitation_expire_hours)
        row.state, row.invited_by = "pending", actor.id
        try:
            self.db.add(row)
            self.db.flush()
            MailService(self.db).enqueue_invitation(row, raw)
            AuditService(self.db).record(
                actor.id,
                action,
                "invitations",
                row.id,
                {"generation": row.generation, "module_count": len(row.modules)},
            )
            self.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                409, "Ya existe una cuenta o invitación para ese correo."
            ) from exc
        return self.output(row)

    def create(self, payload, actor_id):
        self.quota(actor_id)
        actor = self.actor(actor_id)
        if self.repo.email_exists(payload.email):
            raise HTTPException(
                409,
                "Ya existe una cuenta. Usá gestión de cuentas o recuperación de contraseña.",
            )
        row = self.repo.by_email(payload.email)
        if row and row.state == "pending" and row.expires_at > now():
            raise HTTPException(
                409, "Ya existe una invitación pendiente. Usá reenviar o cancelar."
            )
        modules = self.modules(payload.modules)
        if row:
            if row.state == "accepted":
                raise HTTPException(409, "La invitación ya fue aceptada.")
            self.cooldown(row)
            self.repo.cancel_mail(row.id)
            row.modules, row.generation = modules, row.generation + 1
        else:
            row = Invitation(
                email=payload.email,
                modules=modules,
                role="apoderado",
                generation=1,
                created_at=now(),
            )
        return self.issue(row, actor, "auth.invitation_created")

    def cooldown(self, row):
        if row.sent_at > now() - timedelta(seconds=settings.mail_cooldown_seconds):
            raise HTTPException(429, "Esperá antes de reenviar la invitación.")

    def change(self, identity, actor_id, action):
        self.quota(actor_id)
        actor = self.actor(actor_id)
        row = self.repo.get(identity)
        if not row:
            raise HTTPException(404, "Invitación no encontrada.")
        if row.state != "pending":
            raise HTTPException(409, "Esta invitación ya fue aceptada o cancelada.")
        if action == "resend":
            self.cooldown(row)
            if self.repo.email_exists(row.email):
                raise HTTPException(409, "Ya existe una cuenta para este correo.")
            self.modules([ModuleInput(**m) for m in row.modules])
            self.repo.cancel_mail(row.id)
            row.generation += 1
            return self.issue(row, actor, "auth.invitation_resent")
        row.state = "cancelled"
        self.repo.cancel_mail(row.id)
        AuditService(self.db).record(
            actor.id, "auth.invitation_cancelled", "invitations", row.id
        )
        self.commit()
        return self.output(row)

    def valid(self, raw):
        # All changes lock actor then invitation; re-read digest after acquiring locks.
        initial = self.repo.by_digest(digest(raw))
        if not initial:
            raise HTTPException(
                400,
                "El enlace no es válido o ya no está disponible. Pedí una nueva invitación.",
            )
        inviter_id, identity = initial.invited_by, initial.id
        self.actor(inviter_id)
        row = self.repo.get(identity)
        if (
            not row
            or row.invited_by != inviter_id
            or row.digest != digest(raw)
            or row.state != "pending"
            or row.expires_at <= now()
            or row.role != "apoderado"
        ):
            raise HTTPException(
                400,
                "El enlace no es válido o ya no está disponible. Pedí una nueva invitación.",
            )
        return row

    def inspect(self, raw):
        row = self.valid(raw)
        return {"email": row.email, "role": "apoderado", "expires_at": row.expires_at}

    def accept(self, payload):
        validate_password(payload.password)
        encoded = hash_password(payload.password)
        row = self.valid(payload.token)
        if self.repo.email_exists(row.email):
            raise HTTPException(
                409,
                "Ya existe una cuenta para este correo. Solicitá recuperación de acceso.",
            )
        modules = self.modules([ModuleInput(**m) for m in row.modules])
        user = User(
            email=row.email,
            username=payload.username,
            full_name=payload.full_name,
            password_hash=encoded,
            role=UserRole.APODERADO,
            is_active=True,
            email_verified_at=now(),
        )
        try:
            self.db.add(user)
            self.db.flush()
            for m in modules:
                self.db.add(
                    UserModule(
                        user_id=user.id,
                        module_type=UserModuleType.CONSEJOS_LOCALES
                        if m["municipality_id"]
                        else UserModuleType.DIPUTADOS_PROVINCIALES,
                        **m,
                    )
                )
            row.state, row.accepted_at, row.user_id = "accepted", now(), user.id
            self.repo.cancel_mail(row.id)
            AuditService(self.db).record(
                user.id,
                "auth.invitation_accepted",
                "invitations",
                row.id,
                {"generation": row.generation},
            )
            self.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                409, "El nombre de usuario o correo ya está registrado."
            ) from exc
        return {
            "message": "Cuenta creada. Ya podés iniciar sesión con tu correo y contraseña."
        }
