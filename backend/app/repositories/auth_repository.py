from datetime import datetime, timedelta, timezone
import hashlib
import hmac
from sqlalchemy import select, update, delete, func, or_
from app.core.config import settings
from app.models.user import User
from app.db.functions import normalized_trim
from app.models.audit_log import AuditLog
from app.models.auth_session import (
    AuthSession,
    RefreshCredential,
    PasswordReset,
    AuthRateLimit,
    MailOutbox,
)


def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


class AuthRepository:
    def __init__(self, db):
        self.db = db

    def add(self, value):
        self.db.add(value)
        self.db.flush()
        return value

    def user(self, identity):
        return self.db.scalar(
            select(User)
            .where(User.id == identity)
            .with_for_update()
            .execution_options(populate_existing=True)
        )

    def email_user(self, email):
        rows = list(
            self.db.scalars(
                select(User)
                .where(func.lower(normalized_trim(User.email)) == email.strip().lower())
                .order_by(User.id)
                .limit(2)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
        )
        return (
            rows[0] if len(rows) == 1 else None
        )  # Fail closed on legacy normalized-email collisions.

    def session(self, sid, lock=False):
        stmt = (
            select(AuthSession)
            .where(AuthSession.id == sid)
            .execution_options(populate_existing=True)
        )
        return self.db.scalar(stmt.with_for_update() if lock else stmt)

    def refresh(self, raw):
        return self.db.get(RefreshCredential, digest(raw))

    def reset(self, raw):
        return self.db.get(PasswordReset, digest(raw))

    def sessions(self, uid):
        return list(
            self.db.scalars(
                select(AuthSession)
                .where(
                    AuthSession.user_id == uid,
                    AuthSession.revoked_at.is_(None),
                    AuthSession.expires_at > now(),
                    AuthSession.last_used_at
                    > now() - timedelta(hours=settings.session_idle_hours),
                )
                .order_by(AuthSession.created_at.desc())
            )
        )

    def revoke_all(self, uid):
        self.db.execute(
            update(AuthSession)
            .where(AuthSession.user_id == uid, AuthSession.revoked_at.is_(None))
            .values(revoked_at=now())
        )
        self.db.execute(
            update(PasswordReset)
            .where(PasswordReset.user_id == uid, PasswordReset.consumed_at.is_(None))
            .values(consumed_at=now())
        )

    def locks(self, offset, limit, locked_only):
        stmt = select(User)
        if locked_only:
            stmt = stmt.where(User.locked_until > now())
        return list(self.db.scalars(stmt.order_by(User.id).offset(offset).limit(limit)))

    def quota(self, scope, identity, maximum, seconds=900):
        """DB upsert + row lock serializes counters across workers (including unknown users)."""
        key = hmac.new(
            settings.secret_key.encode(), f"{scope}:{identity}".encode(), hashlib.sha256
        ).hexdigest()
        dialect = self.db.bind.dialect.name
        if dialect == "postgresql":
            from sqlalchemy.dialects.postgresql import insert
        else:
            from sqlalchemy.dialects.sqlite import insert
        self.db.execute(
            insert(AuthRateLimit)
            .values(key=key, count=0, window_at=now())
            .on_conflict_do_nothing(index_elements=["key"])
        )
        row = self.db.scalar(
            select(AuthRateLimit)
            .where(AuthRateLimit.key == key)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if row.window_at <= now() - timedelta(seconds=seconds):
            row.count, row.window_at = 0, now()
        row.count += 1
        allowed = row.count <= maximum
        self.db.commit()  # Quotas survive a later rejected domain transaction.
        return allowed

    def cleanup(self):
        cutoff = now() - timedelta(days=settings.security_retention_days)
        self.db.execute(
            delete(RefreshCredential).where(
                RefreshCredential.session_id.in_(
                    select(AuthSession.id).where(AuthSession.expires_at < cutoff)
                )
            )
        )
        self.db.execute(delete(AuthSession).where(AuthSession.expires_at < cutoff))
        self.db.execute(delete(PasswordReset).where(PasswordReset.expires_at < cutoff))
        self.db.execute(
            delete(AuthRateLimit).where(
                AuthRateLimit.window_at < now() - timedelta(days=1)
            )
        )
        self.db.execute(
            update(MailOutbox)
            .where(
                MailOutbox.expires_at < now(),
                MailOutbox.state.in_(["pending", "processing"]),
            )
            .values(payload=None, state="failed", last_error="expired")
        )
        self.db.execute(delete(MailOutbox).where(MailOutbox.created_at < cutoff))
        from app.models.invitation import Invitation

        self.db.execute(delete(Invitation).where(Invitation.expires_at < cutoff))
        self.db.execute(
            delete(AuditLog).where(
                AuditLog.created_at < cutoff,
                or_(AuditLog.action.like("auth.%"), AuditLog.action.like("mail.%")),
            )
        )
        self.db.commit()
