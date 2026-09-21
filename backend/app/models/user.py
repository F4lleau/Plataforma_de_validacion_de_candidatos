# usuarios del sistema.
from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Enum,
    Index,
    func,
    JSON,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.db.functions import normalized_trim
from app.utils.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    failed_attempts: Mapped[int] = mapped_column(default=0, server_default="0")
    failure_window_at: Mapped[datetime | None] = mapped_column(DateTime)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    credential_version: Mapped[int] = mapped_column(default=0, server_default="0")
    last_recovery_at: Mapped[datetime | None] = mapped_column(DateTime)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    terms_accepted_at: Mapped[datetime | None] = mapped_column(DateTime)
    terms_version: Mapped[str | None] = mapped_column(String(64))
    terms_snapshot: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
    __table_args__ = (
        CheckConstraint(
            "(terms_accepted_at IS NULL AND terms_version IS NULL AND terms_snapshot IS NULL) OR "
            "(terms_accepted_at IS NOT NULL AND terms_version IS NOT NULL AND terms_snapshot IS NOT NULL)",
            name="ck_users_terms_complete",
        ),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


Index("uq_users_normalized_email", func.lower(normalized_trim(User.email)), unique=True)
