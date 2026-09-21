from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session, aliased

from app.models.candidate import Candidate
from app.models.candidate_validation import CandidateValidation
from app.models.person import Person
from app.repositories.user_module_repository import UserModuleRepository
from app.utils.enums import ValidationResult


class CandidateRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Candidate]:
        stmt = select(Candidate).order_by(Candidate.id.desc())
        return list(self.db.scalars(stmt).all())

    def list_for_user(self, user_id: int) -> list[Candidate]:
        from app.models import ListCandidate, ElectoralList, ListAssignment

        stmt = (
            select(Candidate)
            .join(ListCandidate, ListCandidate.candidate_id == Candidate.id)
            .join(ElectoralList, ElectoralList.id == ListCandidate.list_id)
            .join(ListAssignment, ListAssignment.list_id == ElectoralList.id)
            .where(
                ListAssignment.user_id == user_id,
                UserModuleRepository.access_condition(
                    user_id,
                    ElectoralList.election_id,
                    ElectoralList.office_id,
                    ElectoralList.municipality_id,
                ),
            )
            .distinct()
            .order_by(Candidate.id.desc())
        )
        return list(self.db.scalars(stmt).all())

    def create(self, candidate: Candidate) -> Candidate:
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate

    def list_requires_admin_review(self) -> list[Candidate]:
        versioned = aliased(CandidateValidation)
        has_current_history = (
            select(versioned.id)
            .where(
                versioned.candidate_id == Candidate.id,
                versioned.candidate_revision.is_not(None),
            )
            .correlate(Candidate)
            .exists()
        )
        stmt = (
            select(Candidate)
            .join(CandidateValidation, CandidateValidation.candidate_id == Candidate.id)
            .where(
                CandidateValidation.status == ValidationResult.WARNING,
                or_(
                    CandidateValidation.candidate_revision == Candidate.revision,
                    and_(
                        CandidateValidation.candidate_revision.is_(None),
                        ~has_current_history,
                    ),
                ),
            )
            .distinct()
            .order_by(Candidate.id.desc())
        )
        return list(self.db.scalars(stmt).all())
