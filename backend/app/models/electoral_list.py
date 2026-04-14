from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.utils.enums import ListStatus


class ElectoralList(Base):
    __tablename__ = "electoral_lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    election_id: Mapped[int] = mapped_column(ForeignKey("elections.id"), nullable=False, index=True)
    office_id: Mapped[int] = mapped_column(ForeignKey("offices.id"), nullable=False, index=True)
    municipality_id: Mapped[int | None] = mapped_column(ForeignKey("municipalities.id"), nullable=True, index=True)

    list_name: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[ListStatus] = mapped_column(
        Enum(ListStatus),
        default=ListStatus.BORRADOR,
        nullable=False,
    )

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)