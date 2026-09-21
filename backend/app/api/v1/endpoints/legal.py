from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.core.cookies import csrf
from app.core.security import get_authenticated_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.legal import LegalDocuments, TermsAcceptanceInput
from app.schemas.user import UserResponse
from app.services.legal_service import LegalService

router = APIRouter()


@router.get("/legal/documents", response_model=LegalDocuments)
def documents(response: Response):
    response.headers["Cache-Control"] = "no-store"
    return LegalService.documents()


@router.post(
    "/auth/terms/accept", response_model=UserResponse, dependencies=[Depends(csrf)]
)
def accept_terms(
    payload: TermsAcceptanceInput,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_authenticated_user),
):
    response.headers["Cache-Control"] = "no-store"
    return LegalService(db).accept(user.id, request.state.session_id, payload)
