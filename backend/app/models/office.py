from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Office(Base):
    __tablename__ = "offices"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    scope_type: Mapped[str] = mapped_column(String(50), nullable=False)
    municipality_based: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    required_positions: Mapped[int] = mapped_column(Integer, nullable=False)
    requires_parity: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_alternation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)