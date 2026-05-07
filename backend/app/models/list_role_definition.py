from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ListRoleDefinition(Base):
    __tablename__ = "list_role_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    office_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    group_name: Mapped[str] = mapped_column(String(100), nullable=False)
    position_order: Mapped[int] = mapped_column(Integer, nullable=False)

    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    gender_rule: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_titular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_suplente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)