from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch
import pytest
from fastapi.routing import APIRoute
from sqlalchemy import select, func
from app.main import app
from app.models import AuditLog
from app.models.auth_session import AuthSession
from app.core.security import get_current_user
from app.repositories.auth_repository import AuthRepository, now
from app.repositories.legal_repository import LegalDocumentRepository
from app.services.legal_service import LegalService
from app.schemas.legal import TermsAcceptanceInput
from tests.auth_helpers import accept_terms_request, session_token
from tests.test_auth_rbac import (
    db_session as db_session,
    client as client,
    users as users,
)


@pytest.fixture(params=[0, 1], ids=["admin", "apoderado"])
def pending(users, db_session, request):
    user = users[request.param]
    user.terms_accepted_at = user.terms_version = user.terms_snapshot = None
    db_session.commit()
    return user


def header(user):
    return {"Authorization": "Bearer " + session_token(user)}


def body():
    doc = LegalDocumentRepository().documents()["terms"]
    return {"accepted": True, "version": doc["version"], "sha256": doc["sha256"]}


def test_pending_cannot_bypass_but_me_refresh_logout_work(client, pending):
    password = (
        "admin-password" if pending.role.value == "admin" else "apoderado-password"
    )
    login = client.post(
        "/api/v1/auth/login", json={"email": pending.email, "password": password}
    )
    assert (
        login.status_code == 200 and login.json()["user"]["terms_accepted_at"] is None
    )
    h = {"Authorization": "Bearer " + login.json()["access_token"]}
    for method, path in [
        ("GET", "/auth/modules"),
        ("GET", "/lists/page"),
        ("GET", "/padron"),
        ("GET", "/admin/invitations"),
        ("GET", "/auth/sessions"),
        ("POST", "/auth/reauthenticate"),
        ("POST", "/lists/"),
        ("POST", "/padron/import"),
    ]:
        r = client.request(method, "/api/v1" + path, headers=h, json={})
        assert r.status_code == 403, (path, r.text)
        assert r.json()["detail"]["code"] == "TERMS_ACCEPTANCE_REQUIRED"
    assert client.get("/api/v1/auth/me", headers=h).status_code == 200
    renewed = client.post("/api/v1/auth/refresh")
    assert (
        renewed.status_code == 200 and not renewed.json()["user"]["terms_accepted_at"]
    )
    assert client.post("/api/v1/auth/logout").status_code == 200
    assert (
        client.post("/api/v1/auth/terms/accept", json=body(), headers=h).status_code
        == 401
    )


def test_accept_once_and_keep_snapshot_across_login_cleanup_and_content_change(
    client, pending, db_session
):
    h = header(pending)
    original = accept_terms_request(client, h).json()
    assert original["terms_accepted_at"] and "terms_snapshot" not in original
    stored = deepcopy(pending.terms_snapshot)
    assert client.get("/api/v1/auth/modules", headers=h).status_code == 200
    documents = LegalDocumentRepository().documents()
    documents["terms"]["version"] = "future-version"
    documents["terms"]["sha256"] = "a" * 64
    with patch.object(LegalDocumentRepository, "documents", return_value=documents):
        repeated = client.post("/api/v1/auth/terms/accept", json=body(), headers=h)
        assert repeated.json()["terms_accepted_at"] == original["terms_accepted_at"]
        assert repeated.json()["terms_version"] == original["terms_version"]
    assert pending.terms_snapshot == stored
    audit = db_session.scalar(
        select(AuditLog).where(AuditLog.action == "legal.terms_accepted")
    )
    audit.created_at = now() - timedelta(days=365)
    db_session.commit()
    AuthRepository(db_session).cleanup()
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.action == "legal.terms_accepted")
        )
        == 1
    )
    password = (
        "admin-password" if pending.role.value == "admin" else "apoderado-password"
    )
    again = client.post(
        "/api/v1/auth/login", json={"email": pending.email, "password": password}
    )
    assert again.json()["user"]["terms_accepted_at"] == original["terms_accepted_at"]


def test_reading_never_accepts_and_version_race_fails(client, pending):
    h = header(pending)
    for _ in range(2):
        r = client.get("/api/v1/legal/documents")
        assert r.status_code == 200 and r.headers["cache-control"] == "no-store"
        assert "provisorio" in r.json()["privacy"]["notice"]
    assert pending.terms_accepted_at is None
    r = client.post(
        "/api/v1/auth/terms/accept", json={**body(), "sha256": "0" * 64}, headers=h
    )
    assert (
        r.status_code == 409 and r.json()["detail"]["code"] == "TERMS_DOCUMENT_CHANGED"
    )
    assert pending.terms_accepted_at is None


@pytest.mark.parametrize(
    "extra",
    [
        {"accepted": False},
        {"accepted": "true"},
        {"user_id": 99},
        {"terms_accepted_at": "2020-01-01"},
        {"terms_snapshot": {}},
    ],
)
def test_explicit_input_and_no_mass_assignment(client, pending, extra):
    r = client.post(
        "/api/v1/auth/terms/accept", json={**body(), **extra}, headers=header(pending)
    )
    assert r.status_code == 422
    assert pending.terms_accepted_at is None


def test_csrf_authentication_revocation_and_atomicity(client, pending, db_session):
    assert client.post("/api/v1/auth/terms/accept", json=body()).status_code == 401
    h = header(pending)
    assert (
        client.post(
            "/api/v1/auth/terms/accept",
            json=body(),
            headers={**h, "Origin": "https://invalid.example"},
        ).status_code
        == 403
    )
    with patch(
        "app.services.legal_service.AuditService.record",
        side_effect=RuntimeError("audit failed"),
    ):
        with pytest.raises(RuntimeError):
            client.post("/api/v1/auth/terms/accept", json=body(), headers=h)
    db_session.refresh(pending)
    assert pending.terms_accepted_at is None
    session = db_session.scalar(
        select(AuthSession).where(AuthSession.user_id == pending.id)
    )
    session.revoked_at = now()
    db_session.commit()
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        LegalService(db_session).accept(
            pending.id, session.id, TermsAcceptanceInput(**body())
        )
    assert exc.value.status_code == 401
    pending.is_active = False
    db_session.commit()
    assert (
        client.post("/api/v1/auth/terms/accept", json=body(), headers=h).status_code
        == 401
    )


def test_all_api_routes_have_gate_or_explicit_public_minimal_exception():
    # Regression inventory: newly exposed protected endpoints must use the central gate.
    exceptions = {
        "/api/v1/auth/csrf",
        "/api/v1/auth/health",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v1/auth/logout",
        "/api/v1/auth/me",
        "/api/v1/auth/support",
        "/api/v1/auth/password/forgot",
        "/api/v1/auth/password/reset",
        "/api/v1/auth/invitations/inspect",
        "/api/v1/auth/invitations/accept",
        "/api/v1/auth/terms/accept",
        "/api/v1/legal/documents",
    }

    def has_gate(dependency):
        return dependency.call is get_current_user or any(
            has_gate(d) for d in dependency.dependencies
        )

    for route in app.routes:
        if isinstance(route, APIRoute) and route.path.startswith("/api/v1/"):
            assert route.path in exceptions or has_gate(route.dependant), route.path


def test_password_changes_reset_unlock_and_logout_preserve_acceptance(
    client, users, db_session
):
    from app.services.auth_service import AuthService
    from app.models.auth_session import PasswordReset
    from app.repositories.auth_repository import digest

    user = users[0]
    original = (
        user.terms_accepted_at,
        user.terms_version,
        deepcopy(user.terms_snapshot),
    )
    service = AuthService(db_session)
    service.change_password(
        user, "admin-password", "Una nueva clave para probar términos", "test"
    )
    raw = "synthetic-reset-token-22-test-only"
    db_session.add(
        PasswordReset(
            digest=digest(raw),
            user_id=user.id,
            credential_version=user.credential_version,
            expires_at=now() + timedelta(minutes=5),
        )
    )
    db_session.commit()
    service.reset_password(raw, "Otra clave para restablecer términos", "test")
    user.failed_attempts = 5
    user.locked_until = now() + timedelta(minutes=15)
    db_session.commit()
    service.unlock(user, user.id, "Verificación sintética de persistencia")
    _, refresh = service.login(
        user.email, "Otra clave para restablecer términos", "test"
    )
    service.logout(refresh)
    assert (user.terms_accepted_at, user.terms_version, user.terms_snapshot) == original
