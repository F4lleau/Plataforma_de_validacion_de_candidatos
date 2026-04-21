from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class PartyMember(Base):
    __tablename__ = "party_members"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    dni: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    affiliate_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    gender: Mapped[str | None] = mapped_column(String(30), nullable=True)
    section: Mapped[str | None] = mapped_column(String(100), nullable=True)
    circuit: Mapped[str | None] = mapped_column(String(100), nullable=True)

    affiliation_status: Mapped[str] = mapped_column(String(50), default="activo", nullable=False)
    affiliation_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    source_batch_id: Mapped[int] = mapped_column(
        ForeignKey("affiliate_import_batches.id"),
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)