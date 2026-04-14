from datetime import date

from sqlalchemy import String, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Election(Base):
    __tablename__ = "elections"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    election_type: Mapped[str] = mapped_column(String(100), nullable=False)
    election_date: Mapped[date] = mapped_column(Date, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)