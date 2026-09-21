from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.core.cookies import csrf
from app.core.security import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.invitation import InvitationInput, InvitationToken, InvitationAccept
from app.services.auth_service import AuthService
from app.services.invitation_service import InvitationService

admin_router = APIRouter(dependencies=[Depends(require_admin)])
public_router = APIRouter(dependencies=[Depends(csrf)])


@admin_router.get("")
def listing(
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = InvitationService(db)
    return [service.output(row) for row in service.repo.listing(offset, limit)]


@admin_router.post("", status_code=201, dependencies=[Depends(csrf)])
def create(
    payload: InvitationInput,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(require_admin),
):
    AuthService(db).recent(request.state.session_id)
    return InvitationService(db).create(payload, actor.id)


@admin_router.post("/{identity}/resend", dependencies=[Depends(csrf)])
def resend(
    identity: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(require_admin),
):
    AuthService(db).recent(request.state.session_id)
    return InvitationService(db).change(identity, actor.id, "resend")


@admin_router.post("/{identity}/cancel", dependencies=[Depends(csrf)])
def cancel(
    identity: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(require_admin),
):
    AuthService(db).recent(request.state.session_id)
    return InvitationService(db).change(identity, actor.id, "cancel")


@public_router.post("/inspect")
def inspect(payload: InvitationToken, request: Request, db: Session = Depends(get_db)):
    AuthService(db).throttle("invitation-inspect", request.client.host)
    return InvitationService(db).inspect(payload.token)


@public_router.post("/accept")
def accept(payload: InvitationAccept, request: Request, db: Session = Depends(get_db)):
    AuthService(db).throttle(
        "invitation-accept", request.client.host, payload.token, 10
    )
    return InvitationService(db).accept(payload)
