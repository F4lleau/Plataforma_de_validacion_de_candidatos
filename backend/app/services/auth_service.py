from datetime import timedelta
from uuid import uuid4
import secrets
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.core.auth_timing import comparable_response
from app.core.passwords import (
    hash_password,
    verify_password,
    needs_rehash,
    validate_password,
)
from app.core.security import create_access_token, valid_session
from app.models.auth_session import AuthSession, RefreshCredential, PasswordReset
from app.models.unlock_request import UnlockRequest
from app.models.user import User
from app.repositories.auth_repository import AuthRepository, digest, now
from app.services.audit_service import AuditService

DUMMY_HASH = hash_password(secrets.token_urlsafe(32))
GENERIC = {
    "message": "Si la cuenta permite recuperar el acceso, recibirás un correo con las instrucciones."
}


class AuthService:
    def __init__(self, db):
        self.db = db
        self.repo = AuthRepository(db)
        self.audit = AuditService(db)

    def throttle(self, scope, ip, identifier="", identifier_limit=None):
        ip_ok = self.repo.quota(scope + ":ip", ip, settings.auth_ip_limit)
        if not ip_ok:
            raise HTTPException(429, "Demasiadas solicitudes. Intentá más tarde.")
        identity_ok = (
            self.repo.quota(
                scope + ":identifier",
                identifier,
                identifier_limit or settings.auth_identifier_limit,
            )
            if identifier
            else True
        )
        if not ip_ok or not identity_ok:
            raise HTTPException(429, "Demasiadas solicitudes. Intentá más tarde.")

    def issue(self, user, session):
        raw = secrets.token_urlsafe(32)
        self.repo.add(RefreshCredential(digest=digest(raw), session_id=session.id))
        return {
            "access_token": create_access_token(str(user.id), {"sid": session.id}),
            "token_type": "bearer",
            "user": user,
        }, raw

    @comparable_response
    def login(self, email, password, ip):
        self.throttle("login", ip, email.lower().strip())
        user = self.repo.email_user(email)
        valid = verify_password(password, user.password_hash if user else DUMMY_HASH)
        timestamp = now()
        if (
            not user
            or not user.is_active
            or (user.locked_until and user.locked_until > timestamp)
        ):
            self.db.rollback()
            raise HTTPException(401, "Credenciales inválidas.")
        if not valid:
            if (
                not user.failure_window_at
                or user.failure_window_at
                <= timestamp - timedelta(minutes=settings.login_window_minutes)
                or user.locked_until
            ):
                user.failed_attempts, user.failure_window_at, user.locked_until = (
                    0,
                    timestamp,
                    None,
                )
            user.failed_attempts += 1
            if user.failed_attempts >= settings.login_max_failures:
                user.locked_until = timestamp + timedelta(
                    minutes=settings.login_lock_minutes
                )
                self.audit.record(
                    user.id,
                    "auth.locked",
                    "users",
                    user.id,
                    {"attempts": user.failed_attempts},
                )
            elif user.failed_attempts == 1:
                self.audit.record(user.id, "auth.login_failed", "users", user.id)
            self.db.commit()
            raise HTTPException(401, "Credenciales inválidas.")
        user.failed_attempts, user.failure_window_at, user.locked_until = 0, None, None
        if needs_rehash(user.password_hash):
            user.password_hash = hash_password(password)
        session = self.repo.add(
            AuthSession(
                id=str(uuid4()),
                user_id=user.id,
                created_at=timestamp,
                last_used_at=timestamp,
                expires_at=timestamp
                + timedelta(days=settings.refresh_token_expire_days),
            )
        )
        result = self.issue(user, session)
        self.audit.record(user.id, "auth.login", "users", user.id, {"sid": session.id})
        self.db.commit()
        return result

    def refresh(self, raw, ip):
        self.throttle("refresh", ip)
        credential = self.repo.refresh(raw)
        if not credential:
            raise HTTPException(401, "Sesión inválida o vencida.")
        session_snapshot = self.repo.session(credential.session_id)
        user = self.repo.user(
            session_snapshot.user_id
        )  # user -> session lock order everywhere
        session = self.repo.session(credential.session_id, True)
        self.db.refresh(credential)
        if credential.used_at:
            session.revoked_at = now()
            self.audit.record(
                user.id, "auth.refresh_replay", "users", user.id, {"sid": session.id}
            )
            self.db.commit()
            raise HTTPException(401, "Sesión inválida o vencida.")
        if not user.is_active or not valid_session(session):
            raise HTTPException(401, "Sesión inválida o vencida.")
        credential.used_at, session.last_used_at = now(), now()
        result = self.issue(user, session)
        self.audit.record(
            user.id, "auth.refreshed", "users", user.id, {"sid": session.id}
        )
        self.db.commit()
        return result

    def logout(self, raw):
        credential = self.repo.refresh(raw)
        if credential:
            session = self.repo.session(credential.session_id, True)
            if not session.revoked_at:
                session.revoked_at = now()
                self.audit.record(
                    session.user_id,
                    "auth.logout",
                    "users",
                    session.user_id,
                    {"sid": session.id},
                )
                self.db.commit()

    def reauthenticate(self, user, sid, password, ip):
        self.throttle("reauth", ip, str(user.id), 5)
        user = self.repo.user(user.id)
        if not verify_password(password, user.password_hash):
            raise HTTPException(400, "No se pudo verificar la contraseña actual.")
        session = self.repo.session(sid, True)
        if not valid_session(session):
            raise HTTPException(401, "Sesión inválida.")
        session.reauthenticated_at = now()
        self.audit.record(user.id, "auth.reauthenticated", "users", user.id)
        self.db.commit()

    def recent(self, sid):
        session = self.repo.session(sid)
        if (
            not valid_session(session)
            or not session.reauthenticated_at
            or session.reauthenticated_at
            < now() - timedelta(minutes=settings.reauth_minutes)
        ):
            raise HTTPException(403, "Confirmá tu contraseña para continuar.")

    def revoke(self, user, sid=None):
        self.repo.user(user.id)
        if sid:
            session = self.repo.session(sid, True)
            if not session or session.user_id != user.id:
                raise HTTPException(404, "Sesión no encontrada.")
            session.revoked_at = now()
        else:
            self.repo.revoke_all(user.id)
        self.audit.record(
            user.id, "auth.sessions_revoked", "users", user.id, {"sid": sid}
        )
        self.db.commit()

    @comparable_response
    def forgot(self, email, ip, actor_id=None):
        self.throttle("forgot", ip, email.lower().strip(), 5)
        verify_password(secrets.token_urlsafe(32), DUMMY_HASH)
        user = self.repo.email_user(email)
        if (
            user
            and user.is_active
            and (
                not user.last_recovery_at
                or user.last_recovery_at
                < now() - timedelta(seconds=settings.mail_cooldown_seconds)
            )
        ):
            from app.services.mail_service import MailService

            raw = secrets.token_urlsafe(32)
            reset = self.repo.add(
                PasswordReset(
                    digest=digest(raw),
                    user_id=user.id,
                    credential_version=user.credential_version,
                    expires_at=now() + timedelta(minutes=settings.reset_expire_minutes),
                )
            )
            MailService(self.db).enqueue(user, "reset", raw=raw, reset=reset)
            user.last_recovery_at = now()
            self.audit.record(
                actor_id,
                "auth.recovery_requested",
                "users",
                user.id,
                {"source": "admin" if actor_id else "public"},
            )
            self.db.commit()
        else:
            self.db.rollback()
        return GENERIC

    @comparable_response
    def request_unlock(self, email, ip, note=None):
        self.throttle("unlock-request", ip, email.lower().strip(), 5)
        verify_password(secrets.token_urlsafe(32), DUMMY_HASH)
        user = self.repo.email_user(email)
        if user and user.is_active:
            existing = self.db.scalar(
                select(UnlockRequest).where(
                    UnlockRequest.user_id == user.id,
                    UnlockRequest.status == "pending",
                )
            )
            if existing:
                existing.note = note or existing.note
                request = existing
            else:
                request = UnlockRequest(
                    user_id=user.id,
                    email=user.email,
                    status="pending",
                    note=note,
                    requested_at=now(),
                )
                self.db.add(request)
                self.db.flush()
            from app.services.mail_service import MailService

            try:
                MailService(self.db).enqueue_unlock_request(request, user)
            except IntegrityError:
                self.db.rollback()
                return {
                    "message": "Si la cuenta existe, enviaremos la solicitud al administrador."
                }
            self.audit.record(
                user.id,
                "auth.unlock_requested",
                "users",
                user.id,
                {"request_id": request.id},
            )
            self.db.commit()
        else:
            self.db.rollback()
        return {"message": "Si la cuenta existe, enviaremos la solicitud al administrador."}

    def unlock_requests(self, status="pending"):
        stmt = (
            select(UnlockRequest)
            .order_by(UnlockRequest.requested_at.desc())
            .limit(100)
        )
        if status != "all":
            stmt = stmt.where(UnlockRequest.status == status)
        requests = list(self.db.scalars(stmt).all())
        user_ids = {row.user_id for row in requests}
        users = (
            {
                user.id: user
                for user in self.db.scalars(
                    select(User).where(User.id.in_(user_ids))
                ).all()
            }
            if user_ids
            else {}
        )
        return [
            {
                "id": row.id,
                "user_id": row.user_id,
                "email": row.email,
                "status": row.status,
                "note": row.note,
                "requested_at": row.requested_at,
                "resolved_at": row.resolved_at,
                "user_full_name": users[row.user_id].full_name
                if row.user_id in users
                else "",
                "failed_attempts": users[row.user_id].failed_attempts
                if row.user_id in users
                else 0,
                "locked_until": users[row.user_id].locked_until
                if row.user_id in users
                else None,
                "locked": bool(
                    row.user_id in users
                    and users[row.user_id].locked_until
                    and users[row.user_id].locked_until > now()
                ),
            }
            for row in requests
        ]

    def set_password(self, user, password, action):
        validate_password(password)
        if verify_password(password, user.password_hash):
            raise HTTPException(
                422, "La nueva contraseña debe ser distinta de la actual."
            )
        user.password_hash = hash_password(password)
        user.credential_version += 1
        user.failed_attempts, user.locked_until, user.failure_window_at = 0, None, None
        self.repo.revoke_all(user.id)
        from app.services.mail_service import MailService

        MailService(self.db).enqueue(user, "password_changed")
        self.audit.record(user.id, action, "users", user.id)
        self.db.commit()

    def reset_password(self, raw, password, ip):
        self.throttle("reset", ip)
        reset = self.repo.reset(raw)
        if not reset:
            raise HTTPException(
                400, "El enlace no es válido, venció o ya fue utilizado."
            )
        user = self.repo.user(reset.user_id)
        self.db.refresh(reset)
        if (
            not user.is_active
            or reset.consumed_at
            or reset.expires_at <= now()
            or reset.credential_version != user.credential_version
        ):
            raise HTTPException(
                400, "El enlace no es válido, venció o ya fue utilizado."
            )
        self.set_password(user, password, "auth.password_reset")

    def change_password(self, user, password, new_password, ip):
        self.throttle("change", ip, str(user.id), 5)
        user = self.repo.user(user.id)
        if not verify_password(password, user.password_hash):
            raise HTTPException(400, "No se pudo verificar la contraseña actual.")
        self.set_password(user, new_password, "auth.password_changed")

    def unlock(self, actor, identity, reason):
        user = self.repo.user(identity)
        if not user:
            raise HTTPException(404, "Cuenta no encontrada.")
        changed = False
        if user.failed_attempts or user.locked_until:
            before = {
                "attempts": user.failed_attempts,
                "locked_until": str(user.locked_until),
            }
            user.failed_attempts, user.failure_window_at, user.locked_until = (
                0,
                None,
                None,
            )
            from app.services.mail_service import MailService

            MailService(self.db).enqueue(user, "unlocked", cooldown=True)
            self.audit.record(
                actor.id,
                "auth.unlocked",
                "users",
                user.id,
                {"before": before, "reason": reason},
            )
            changed = True
        for request in self.db.scalars(
            select(UnlockRequest).where(
                UnlockRequest.user_id == user.id,
                UnlockRequest.status == "pending",
            )
        ):
            request.status = "resolved"
            request.resolved_at = now()
            request.resolved_by = actor.id
            changed = True
        if changed:
            self.db.commit()
