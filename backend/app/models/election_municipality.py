from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ElectionMunicipality(Base):
    __tablename__ = "election_municipalities"
    __table_args__ = (UniqueConstraint("election_id", "municipality_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    election_id: Mapped[int] = mapped_column(ForeignKey("elections.id"), index=True)
    municipality_id: Mapped[int] = mapped_column(
        ForeignKey("municipalities.id"), index=True
    )
