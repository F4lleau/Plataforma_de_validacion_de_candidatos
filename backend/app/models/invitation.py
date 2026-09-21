from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class Invitation(Base):
    __tablename__ = "invitations"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    invited_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(20), default="apoderado")
    modules: Mapped[list] = mapped_column(JSON)
    digest: Mapped[str] = mapped_column(String(64), unique=True)
    generation: Mapped[int] = mapped_column(default=1)
    state: Mapped[str] = mapped_column(String(20), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    sent_at: Mapped[datetime] = mapped_column(DateTime)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
