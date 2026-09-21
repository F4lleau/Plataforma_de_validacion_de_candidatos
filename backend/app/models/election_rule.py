from datetime import datetime
from sqlalchemy import ForeignKey, JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class ElectionRule(Base):
    __tablename__ = "election_rules"
    __table_args__ = (UniqueConstraint("election_id", "office_id", "version"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    election_id: Mapped[int] = mapped_column(ForeignKey("elections.id"), index=True)
    office_id: Mapped[int] = mapped_column(ForeignKey("offices.id"), index=True)
    version: Mapped[int] = mapped_column(nullable=False)
    enabled: Mapped[bool] = mapped_column(default=True)
    rules: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
