from datetime import date

from sqlalchemy import String, Boolean, Date, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Election(Base):
    __tablename__ = "elections"
    __table_args__ = (CheckConstraint("(loading_opens IS NULL AND loading_closes IS NULL) OR (loading_opens IS NOT NULL AND loading_closes IS NOT NULL AND loading_opens <= loading_closes AND loading_closes <= election_date)", name="ck_election_loading_dates"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    election_type: Mapped[str] = mapped_column(String(100), nullable=False)
    election_date: Mapped[date] = mapped_column(Date, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    loading_opens: Mapped[date | None] = mapped_column(Date, nullable=True)
    loading_closes: Mapped[date | None] = mapped_column(Date, nullable=True)
