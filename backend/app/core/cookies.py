import secrets
from fastapi import Request, Response, HTTPException
from app.core.config import settings

COOKIE_PATH = settings.api_v1_prefix + "/auth"


def csrf(request: Request):
    origin = request.headers.get("origin")
    cookie = request.cookies.get("je_csrf", "")
    header = request.headers.get("x-csrf-token", "")
    if (
        origin not in settings.cors_origins
        or not cookie
        or not secrets.compare_digest(cookie, header)
    ):
        raise HTTPException(403, "Solicitud de seguridad inválida. Recargá la página.")


def set_refresh(response: Response, raw: str):
    response.set_cookie(
        "je_refresh",
        raw,
        max_age=settings.refresh_token_expire_days * 86400,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        path=COOKIE_PATH,
    )


def clear_refresh(response: Response):
    response.delete_cookie(
        "je_refresh",
        path=COOKIE_PATH,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
    )
