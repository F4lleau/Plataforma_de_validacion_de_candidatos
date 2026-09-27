from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class PadronCircuit(Base):
    __tablename__ = "padron_circuits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    section: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    section_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    source_batch_id: Mapped[int] = mapped_column(
        ForeignKey("affiliate_import_batches.id"),
        nullable=False,
        index=True,
    )
