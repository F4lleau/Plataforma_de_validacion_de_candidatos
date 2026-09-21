from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Any
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.passwords import (
    hash_password as hash_password,
    verify_password as verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.repositories.auth_repository import AuthRepository, now
from app.utils.enums import UserRole

bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(subject: str, extra_data: dict[str, Any] | None = None) -> str:
    issued = datetime.now(timezone.utc)
    payload = dict(extra_data or {})
    payload.update(
        sub=subject,
        iss=settings.jwt_issuer,
        aud=settings.jwt_audience,
        iat=int(issued.timestamp()),
        exp=int(
            (
                issued + timedelta(minutes=settings.access_token_expire_minutes)
            ).timestamp()
        ),
        jti=str(uuid4()),
        type="access",
    )
    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm="HS256",
        headers={"kid": settings.jwt_key_id, "typ": "JWT"},
    )


def decode_token(token: str) -> dict | None:
    try:
        header = jwt.get_unverified_header(token)
        if header.get("alg") != "HS256" or header.get("typ") != "JWT":
            return None
        keys = {**settings.jwt_previous_keys, settings.jwt_key_id: settings.secret_key}
        key = keys.get(header.get("kid"))
        if not key:
            return None
        payload = jwt.decode(
            token,
            key,
            algorithms=["HS256"],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
            options={
                "require_exp": True,
                "require_iat": True,
                "require_sub": True,
                "require_aud": True,
                "require_iss": True,
                "leeway": 5,
            },
        )
        if any(
            not isinstance(payload.get(k), str) or not payload[k]
            for k in ("sub", "sid", "jti")
        ):
            return None
        if "nbf" in payload and type(payload["nbf"]) is not int:
            return None
        if payload.get("aud") != settings.jwt_audience:
            return None
        if (
            any(type(payload.get(k)) is not int for k in ("iat", "exp"))
            or payload["iat"] > datetime.now(timezone.utc).timestamp() + 5
            or payload["exp"] <= payload["iat"]
            or payload.get("type") != "access"
        ):
            return None
        return payload
    except (JWTError, ValueError, TypeError, OverflowError):
        return None


def valid_session(session):
    return (
        session
        and not session.revoked_at
        and session.expires_at > now()
        and session.last_used_at > now() - timedelta(hours=settings.session_idle_hours)
    )


def get_authenticated_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials) if credentials else None
    try:
        uid = int(payload["sub"]) if payload else 0
        if not 0 < uid <= 2147483647:
            raise ValueError()
    except (ValueError, TypeError):
        raise HTTPException(401, "Autenticación requerida.")
    repo = AuthRepository(db)
    session = repo.session(payload["sid"])
    user = db.get(User, uid)
    if (
        not valid_session(session)
        or session.user_id != uid
        or not user
        or not user.is_active
    ):
        raise HTTPException(401, "Sesión inválida o vencida.")
    request.state.session_id = session.id
    return user


def get_current_user(user: User = Depends(get_authenticated_user)) -> User:
    """Default dependency for every protected operation, including role checks."""
    if not user.terms_accepted_at:
        raise HTTPException(
            403,
            {
                "code": "TERMS_ACCEPTANCE_REQUIRED",
                "message": "Aceptá los términos y condiciones antes de ingresar.",
            },
        )
    return user


def require_roles(*allowed_roles: UserRole):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(403, "No tiene permisos para esta operación.")
        return current_user

    return dependency


require_admin = require_roles(UserRole.ADMIN)
