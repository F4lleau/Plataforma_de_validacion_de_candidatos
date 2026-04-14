from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate import Candidate


class CandidateRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Candidate]:
        stmt = select(Candidate).order_by(Candidate.id.desc())
        return list(self.db.scalars(stmt).all())

    def create(self, candidate: Candidate) -> Candidate:
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate