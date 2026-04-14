from sqlalchemy.orm import Session

from app.models.person import Person
from app.models.candidate import Candidate
from app.repositories.candidate_repository import CandidateRepository
from app.schemas.candidate import CandidateCreate
from app.utils.enums import CandidateStatus


class CandidateService:
    def __init__(self, db: Session, candidate_repository: CandidateRepository):
        self.db = db
        self.candidate_repository = candidate_repository

    def list_candidates(self):
        return self.candidate_repository.list_all()

    def create_candidate(self, payload: CandidateCreate, created_by: int) -> Candidate:
        person = Person(
            dni=payload.person.dni,
            first_name=payload.person.first_name,
            last_name=payload.person.last_name,
            birth_date=payload.person.birth_date,
            gender=payload.person.gender,
            address=payload.person.address,
            municipality_id=payload.person.municipality_id,
        )
        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)

        candidate = Candidate(
            person_id=person.id,
            office_id=payload.office_id,
            election_id=payload.election_id,
            candidate_status=CandidateStatus.PENDIENTE_VALIDACION,
            created_by=created_by,
        )
        return self.candidate_repository.create(candidate)