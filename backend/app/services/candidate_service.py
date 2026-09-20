from sqlalchemy.orm import Session

from app.models.candidate_validation import CandidateValidation
from app.models.person import Person
from app.models.candidate import Candidate
from app.repositories.candidate_validation_repository import CandidateValidationRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.party_member_repository import PartyMemberRepository
from app.schemas.candidate import CandidateCreate
from app.services.affiliation_validation_service import AffiliationValidationService
from app.utils.enums import CandidateStatus, ValidationResult, ValidationType


class CandidateService:
    def __init__(
        self,
        db: Session,
        candidate_repository: CandidateRepository,
        party_member_repository: PartyMemberRepository | None = None,
        validation_repository: CandidateValidationRepository | None = None,
    ):
        self.db = db
        self.candidate_repository = candidate_repository
        self.party_member_repository = party_member_repository
        self.validation_repository = validation_repository or CandidateValidationRepository(db)
        self.affiliation_validation_service = (
            AffiliationValidationService(self.party_member_repository)
            if self.party_member_repository is not None
            else None
        )

    def list_candidates(self):
        return self.candidate_repository.list_all()

    def create_candidate(self, payload: CandidateCreate, created_by: int) -> Candidate:
        candidate, _ = self._create_candidate(payload, created_by)
        return candidate

    def create_candidate_with_validation(
        self,
        payload: CandidateCreate,
        created_by: int,
    ) -> tuple[Candidate, dict]:
        return self._create_candidate(payload, created_by)

    def _create_candidate(
        self,
        payload: CandidateCreate,
        created_by: int,
    ) -> tuple[Candidate, dict]:
        dni = payload.person.dni.strip() if payload.person.dni else ""

        if self.affiliation_validation_service is not None:
            validation_result = self.affiliation_validation_service.validate(dni)
        else:
            validation_result = {
                "status": "warning",
                "code": "AFFILIATION_NOT_FOUND",
                "message": "El candidato no figura en el padrón de afiliados vigente.",
                "requires_admin_review": True,
                "details": {"dni": dni},
            }

        person = Person(
            dni=dni,
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
        created_candidate = self.candidate_repository.create(candidate)

        validation_status = ValidationResult.OK if validation_result.get("status") == "verified" else ValidationResult.WARNING
        validation_message = validation_result.get("message") or "Validación de afiliación registrada."

        validation = CandidateValidation(
            candidate_id=created_candidate.id,
            validation_type=ValidationType.AFILIACION,
            status=validation_status,
            message=validation_message,
            response_json=validation_result,
        )
        self.validation_repository.create(validation)

        return created_candidate, validation_result