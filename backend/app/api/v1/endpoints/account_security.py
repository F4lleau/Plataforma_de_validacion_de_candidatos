from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from app.core.cookies import csrf
from app.core.security import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UnlockInput
from app.services.auth_service import AuthService
from app.repositories.auth_repository import now

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("/users/locks")
def locks(
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    locked_only: bool = True,
    db: Session = Depends(get_db),
):
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "failed_attempts": u.failed_attempts,
            "locked_until": u.locked_until,
            "locked": bool(u.locked_until and u.locked_until > now()),
        }
        for u in AuthService(db).repo.locks(offset, limit, locked_only)
    ]


@router.get("/users/unlock-requests")
def unlock_requests(
    status: str = Query("pending", pattern="^(pending|resolved|all)$"),
    db: Session = Depends(get_db),
):
    return AuthService(db).unlock_requests(status)


@router.post("/users/{identity}/unlock", dependencies=[Depends(csrf)])
def unlock(
    identity: int,
    payload: UnlockInput,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(require_admin),
):
    service = AuthService(db)
    service.recent(request.state.session_id)
    service.unlock(actor, identity, payload.reason.strip())
    return {
        "message": "Bloqueo temporal retirado. El estado de activación se conserva."
    }


@router.post("/users/{identity}/password-recovery", dependencies=[Depends(csrf)])
def recovery(
    identity: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(require_admin),
):
    service = AuthService(db)
    service.recent(request.state.session_id)
    user = service.repo.user(identity)
    if not user:
        from fastapi import HTTPException

        raise HTTPException(404, "Cuenta no encontrada.")
    email = user.email
    db.rollback()
    return service.forgot(email, request.client.host, actor.id)
