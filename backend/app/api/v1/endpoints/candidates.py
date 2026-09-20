from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles, require_admin
from app.db.session import get_db
from app.models.user import User
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.candidate_validation_repository import CandidateValidationRepository
from app.repositories.party_member_repository import PartyMemberRepository
from app.schemas.candidate import CandidateCreate, CandidateCreateResponse, CandidateResponse
from app.services.candidate_service import CandidateService
from app.utils.enums import UserRole

router = APIRouter()


def build_candidate_service(db: Session) -> CandidateService:
    return CandidateService(
        db=db,
        candidate_repository=CandidateRepository(db),
        party_member_repository=PartyMemberRepository(db),
        validation_repository=CandidateValidationRepository(db),
    )


@router.post("", response_model=CandidateCreateResponse, status_code=201)
def create_candidate(
    payload: CandidateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.APODERADO)),
):
    service = build_candidate_service(db)
    candidate, affiliation = service.create_candidate_with_validation(payload, current_user.id)
    return {"candidate": candidate, "affiliation": affiliation}


@router.get("/review", response_model=list[CandidateResponse])
def list_candidates_for_admin_review(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return CandidateRepository(db).list_requires_admin_review()


@router.get("", response_model=list[CandidateResponse])
def list_candidates(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return CandidateRepository(db).list_all()