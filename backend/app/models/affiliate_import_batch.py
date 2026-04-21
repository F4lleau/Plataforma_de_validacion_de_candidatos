from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AffiliateImportBatch(Base):
    __tablename__ = "affiliate_import_batches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    imported_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="processing", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    imported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)