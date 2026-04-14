#postulación de una persona a una elección y a un cargo.

from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.utils.enums import CandidateStatus


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"), nullable=False, index=True)
    office_id: Mapped[int] = mapped_column(ForeignKey("offices.id"), nullable=False, index=True)
    election_id: Mapped[int] = mapped_column(ForeignKey("elections.id"), nullable=False, index=True)

    candidate_status: Mapped[CandidateStatus] = mapped_column(
        Enum(CandidateStatus),
        default=CandidateStatus.BORRADOR,
        nullable=False,
    )

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)