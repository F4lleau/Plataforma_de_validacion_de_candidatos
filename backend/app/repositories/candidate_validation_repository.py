from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate_validation import CandidateValidation
from app.utils.enums import ValidationResult


class CandidateValidationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, validation: CandidateValidation) -> CandidateValidation:
        self.db.add(validation)
        self.db.commit()
        self.db.refresh(validation)
        return validation

    def list_by_candidate(self, candidate_id: int) -> list[CandidateValidation]:
        stmt = (
            select(CandidateValidation)
            .where(CandidateValidation.candidate_id == candidate_id)
            .order_by(CandidateValidation.validated_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def has_warning_for_candidate(self, candidate_id: int) -> bool:
        stmt = select(CandidateValidation).where(
            CandidateValidation.candidate_id == candidate_id,
            CandidateValidation.status == ValidationResult.WARNING,
        )
        return self.db.scalar(stmt) is not None