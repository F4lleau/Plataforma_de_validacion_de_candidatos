from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ListCandidate(Base):
    __tablename__ = "list_candidates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    list_id: Mapped[int] = mapped_column(ForeignKey("electoral_lists.id"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)

    role_definition_id: Mapped[int | None] = mapped_column(
        ForeignKey("list_role_definitions.id"),
        nullable=True,
        index=True,
    )

    cargo_label: Mapped[str] = mapped_column(String(150), nullable=False)
    cargo_group: Mapped[str] = mapped_column(String(100), nullable=False)

    position_number: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(30), nullable=False)

    is_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    validation_summary: Mapped[str | None] = mapped_column(Text, nullable=True)