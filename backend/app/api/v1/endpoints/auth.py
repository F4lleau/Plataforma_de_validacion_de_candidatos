import secrets
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.cookies import csrf, set_refresh, clear_refresh
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    PasswordInput,
    ForgotInput,
    ResetInput,
    ChangeInput,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


def ip(request):
    return request.client.host if request.client else "unknown"


@router.get("/csrf")
def csrf_token(request: Request, response: Response):
    token = request.cookies.get("je_csrf") or secrets.token_urlsafe(32)
    response.set_cookie(
        "je_csrf",
        token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        path=settings.api_v1_prefix,
    )
    return {"csrf_token": token}


@router.get("/health")
def auth_health():
    return {"module": "auth", "status": "ok"}


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(csrf)])
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    result, raw = AuthService(db).login(payload.email, payload.password, ip(request))
    set_refresh(response, raw)
    return result


@router.post("/refresh", response_model=TokenResponse, dependencies=[Depends(csrf)])
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    result, raw = AuthService(db).refresh(
        request.cookies.get("je_refresh", ""), ip(request)
    )
    set_refresh(response, raw)
    return result


@router.post("/logout", dependencies=[Depends(csrf)])
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    AuthService(db).logout(request.cookies.get("je_refresh", ""))
    clear_refresh(response)
    return {"message": "Sesión cerrada."}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/support")
def support():
    return {"contact": settings.support_contact, "mode": "email_recovery"}


@router.get("/modules")
def modules(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    from app.services.management_service import ManagementService

    return [m for m in ManagementService(db).repo.modules(current_user.id) if m.enabled]


@router.get("/sessions")
def sessions(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return [
        {
            "id": s.id,
            "created_at": s.created_at,
            "last_used_at": s.last_used_at,
            "expires_at": s.expires_at,
            "current": s.id == request.state.session_id,
        }
        for s in AuthService(db).repo.sessions(user.id)
    ]


@router.post("/reauthenticate", dependencies=[Depends(csrf)])
def reauthenticate(
    payload: PasswordInput,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    AuthService(db).reauthenticate(
        user, request.state.session_id, payload.password, ip(request)
    )
    return {"message": "Identidad confirmada."}


@router.post("/logout-all", dependencies=[Depends(csrf)])
def logout_all(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = AuthService(db)
    service.recent(request.state.session_id)
    service.revoke(user)
    clear_refresh(response)
    return {"message": "Todas las sesiones fueron cerradas."}


@router.delete("/sessions/{sid}", dependencies=[Depends(csrf)])
def revoke(
    sid: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    AuthService(db).revoke(user, sid)
    if sid == request.state.session_id:
        clear_refresh(response)
    return {"message": "Sesión cerrada."}


@router.post("/password/forgot", dependencies=[Depends(csrf)])
def forgot(payload: ForgotInput, request: Request, db: Session = Depends(get_db)):
    return AuthService(db).forgot(payload.email, ip(request))


@router.post("/password/reset", dependencies=[Depends(csrf)])
def reset(
    payload: ResetInput,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    AuthService(db).reset_password(payload.token, payload.new_password, ip(request))
    clear_refresh(response)
    return {"message": "Contraseña actualizada. Iniciá sesión nuevamente."}


@router.post("/password/change", dependencies=[Depends(csrf)])
def change(
    payload: ChangeInput,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    AuthService(db).change_password(
        user, payload.password, payload.new_password, ip(request)
    )
    clear_refresh(response)
    return {"message": "Contraseña actualizada. Iniciá sesión nuevamente."}
