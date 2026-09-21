from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/health")
def auth_health():
    return {"module": "auth", "status": "ok"}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    result = AuthService(UserRepository(db)).login(payload.email, payload.password)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/support")
def support():
    from app.core.config import settings

    return {"contact": settings.support_contact, "mode": "admin_assisted"}


@router.get("/modules")
def modules(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    from app.services.management_service import ManagementService

    return [m for m in ManagementService(db).repo.modules(current_user.id) if m.enabled]
