"""UTC naive timestamps, consistent with the existing database."""

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    last_used_at: Mapped[datetime] = mapped_column(DateTime)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    reauthenticated_at: Mapped[datetime | None] = mapped_column(DateTime)


class RefreshCredential(Base):
    __tablename__ = "refresh_credentials"
    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("auth_sessions.id", ondelete="CASCADE"), index=True
    )
    used_at: Mapped[datetime | None] = mapped_column(DateTime)


class PasswordReset(Base):
    __tablename__ = "password_resets"
    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    credential_version: Mapped[int] = mapped_column()
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime)


class AuthRateLimit(Base):
    __tablename__ = "auth_rate_limits"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    count: Mapped[int] = mapped_column(default=0)
    window_at: Mapped[datetime] = mapped_column(DateTime, index=True)


class MailOutbox(Base):
    __tablename__ = "mail_outbox"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_key: Mapped[str] = mapped_column(String(150), unique=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    invitation_id: Mapped[int | None] = mapped_column(
        ForeignKey("invitations.id"), index=True
    )
    invitation_digest: Mapped[str | None] = mapped_column(String(64))
    kind: Mapped[str] = mapped_column(String(40))
    payload: Mapped[str | None] = mapped_column(Text)
    reset_digest: Mapped[str | None] = mapped_column(String(64))
    state: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    attempts: Mapped[int] = mapped_column(default=0)
    available_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    lease_id: Mapped[str | None] = mapped_column(String(36))
    last_error: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime)
