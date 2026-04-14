from sqlalchemy import Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.utils.enums import UserModuleType


class UserModule(Base):
    __tablename__ = "user_modules"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    election_id: Mapped[int] = mapped_column(ForeignKey("elections.id"), nullable=False, index=True)
    office_id: Mapped[int] = mapped_column(ForeignKey("offices.id"), nullable=False, index=True)
    municipality_id: Mapped[int | None] = mapped_column(ForeignKey("municipalities.id"), nullable=True, index=True)
    module_type: Mapped[UserModuleType] = mapped_column(Enum(UserModuleType), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)