import json
from datetime import timedelta
from cryptography.fernet import Fernet
from fastapi import HTTPException
from jose import jwt
import pytest
from sqlalchemy import select, func
from app.core.config import settings
from app.core.passwords import hash_password, verify_password, validate_password
from app.core.security import decode_token
from app.models.auth_session import (
    AuthSession,
    PasswordReset,
    MailOutbox,
    AuthRateLimit,
)
from app.models.audit_log import AuditLog
from app.repositories.auth_repository import now, digest
from app.services.auth_service import AuthService
from app.services.mail_service import MailService
from tests.test_auth_rbac import db_session, client, users, headers


@pytest.fixture(autouse=True)
def mail_key(monkeypatch):
    monkeypatch.setattr(settings, "mail_outbox_key", Fernet.generate_key().decode())


def login(client, user, password="admin-password"):
    response = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": password}
    )
    assert response.status_code == 200
    return response


def bearer(response):
    return {"Authorization": "Bearer " + response.json()["access_token"]}


def reset_raw(db):
    row = db.scalar(
        select(MailOutbox)
        .where(MailOutbox.kind == "reset")
        .order_by(MailOutbox.created_at.desc())
    )
    payload = json.loads(
        Fernet(settings.mail_outbox_key.encode()).decrypt(row.payload.encode())
    )
    return payload["text"].split("#token=")[1].split()[0], row


def test_cookie_csrf_refresh_replay_and_immediate_revoke(client, users, db_session):
    admin, _ = users
    result = login(client, admin)
    assert "refresh_token" not in result.json()
    cookie = result.headers["set-cookie"]
    assert (
        "HttpOnly" in cookie
        and "SameSite=strict" in cookie
        and "Path=/api/v1/auth" in cookie
    )
    original = client.cookies.get("je_refresh")
    h = bearer(result)
    assert client.get("/api/v1/auth/me", headers=h).status_code == 200
    assert (
        client.post(
            "/api/v1/auth/refresh", headers={"Origin": "https://attacker.invalid"}
        ).status_code
        == 403
    )
    refreshed = client.post("/api/v1/auth/refresh")
    assert refreshed.status_code == 200 and client.cookies.get("je_refresh") != original
    assert client.get("/api/v1/auth/me", headers=h).status_code == 200
    with pytest.raises(HTTPException) as exc:
        AuthService(db_session).refresh(original, "test")
    assert exc.value.status_code == 401
    assert client.get("/api/v1/auth/me", headers=bearer(refreshed)).status_code == 401


@pytest.mark.parametrize(
    "claim,value",
    [
        ("iss", "other"),
        ("aud", "other"),
        ("type", "refresh"),
        ("iat", 4102444800),
        ("iat", "bad"),
        ("exp", 1),
        ("sid", []),
        ("jti", None),
        ("sub", "x"),
        ("nbf", 4102444800),
    ],
)
def test_claim_validation(client, users, claim, value):
    result = login(client, users[0])
    data = jwt.get_unverified_claims(result.json()["access_token"])
    data[claim] = value
    encoded = jwt.encode(
        data,
        settings.secret_key,
        algorithm="HS256",
        headers={"kid": settings.jwt_key_id},
    )
    assert (
        client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer " + encoded}
        ).status_code
        == 401
    )


def test_logout_idempotent_and_session_isolation(client, users):
    admin, apod = users
    first = login(client, admin)
    second = login(client, admin)
    other = headers(apod)
    own = client.get("/api/v1/auth/sessions", headers=bearer(second)).json()
    assert len(own) == 2
    assert (
        client.delete(
            "/api/v1/auth/sessions/" + own[0]["id"], headers=other
        ).status_code
        == 404
    )
    assert client.post("/api/v1/auth/logout").status_code == 200
    assert client.post("/api/v1/auth/logout").status_code == 200
    assert client.get("/api/v1/auth/me", headers=bearer(second)).status_code == 401
    assert client.get("/api/v1/auth/me", headers=bearer(first)).status_code == 200


def test_lock_expiry_no_extension_existing_sessions_and_unlock(
    client, users, db_session
):
    admin, apod = users
    result = login(client, admin)
    user_result = login(client, apod, "apoderado-password")
    for _ in range(settings.login_max_failures):
        assert (
            client.post(
                "/api/v1/auth/login",
                json={"email": apod.email.upper(), "password": "wrong"},
            ).status_code
            == 401
        )
    db_session.refresh(apod)
    until = apod.locked_until
    assert until and apod.failed_attempts == 5
    assert client.get("/api/v1/auth/me", headers=bearer(user_result)).status_code == 200
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": apod.email, "password": "apoderado-password"},
        ).status_code
        == 401
    )
    db_session.refresh(apod)
    assert apod.locked_until == until
    assert (
        client.post(
            f"/api/v1/admin/users/{apod.id}/unlock",
            headers=bearer(result),
            json={"reason": "Prueba local"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/auth/reauthenticate",
            headers=bearer(result),
            json={"password": "admin-password"},
        ).status_code
        == 200
    )
    apod.is_active = False
    db_session.commit()
    for _ in range(2):
        assert (
            client.post(
                f"/api/v1/admin/users/{apod.id}/unlock",
                headers=bearer(result),
                json={"reason": "Prueba local"},
            ).status_code
            == 200
        )
    db_session.refresh(apod)
    assert not apod.is_active and not apod.locked_until and apod.failed_attempts == 0
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.action == "auth.unlocked")
        )
        == 1
    )


def test_expired_lock_allows_login(client, users, db_session):
    admin, _ = users
    admin.failed_attempts = 5
    admin.locked_until = now() - timedelta(seconds=1)
    db_session.commit()
    login(client, admin)
    assert admin.failed_attempts == 0 and admin.locked_until is None


def test_reset_single_use_revokes_all_preserves_other_accounts(
    client, users, db_session
):
    admin, apod = users
    current = login(client, admin)
    old_refresh = client.cookies.get("je_refresh")
    other = headers(apod)
    response = client.post("/api/v1/auth/password/forgot", json={"email": admin.email})
    missing = client.post(
        "/api/v1/auth/password/forgot", json={"email": "unknown@example.com"}
    )
    assert (
        response.status_code == missing.status_code == 200
        and response.json() == missing.json()
    )
    raw, row = reset_raw(db_session)
    assert raw not in row.payload
    assert db_session.get(PasswordReset, digest(raw))
    assert client.get("/api/v1/auth/me", headers=bearer(current)).status_code == 200
    # GET/mail scanner cannot consume the link.
    assert client.get("/api/v1/auth/password/reset").status_code == 405
    password = "Una contraseña nueva 🦋 muy larga"
    admin.locked_until = now() + timedelta(minutes=15)
    db_session.commit()
    assert (
        client.post(
            "/api/v1/auth/password/reset", json={"token": raw, "new_password": password}
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/v1/auth/password/reset", json={"token": raw, "new_password": password}
        ).status_code
        == 400
    )
    assert client.get("/api/v1/auth/me", headers=bearer(current)).status_code == 401
    assert client.get("/api/v1/auth/me", headers=other).status_code == 200
    assert not admin.locked_until
    with pytest.raises(HTTPException):
        AuthService(db_session).refresh(old_refresh, "test")
    login(client, admin, password)
    assert not any(
        raw in str(a.details_json) or password in str(a.details_json)
        for a in db_session.scalars(select(AuditLog))
    )


def test_multiple_reset_requests_coexist_and_cooldown(client, users, db_session):
    admin, _ = users
    service = AuthService(db_session)
    service.forgot(admin.email, "test")
    raw, _ = reset_raw(db_session)
    service.forgot(admin.email, "test")
    assert db_session.scalar(select(func.count()).select_from(PasswordReset)) == 1
    admin.last_recovery_at = now() - timedelta(minutes=2)
    db_session.commit()
    service.forgot(admin.email, "test")
    assert db_session.scalar(select(func.count()).select_from(PasswordReset)) == 2
    assert not db_session.get(PasswordReset, digest(raw)).consumed_at
    service.reset_password(raw, "Frase bastante larga para probar", "test")
    assert all(r.consumed_at for r in db_session.scalars(select(PasswordReset)))


@pytest.mark.parametrize("condition", ["expired", "disabled", "changed", "wrong"])
def test_invalid_reset(client, users, db_session, condition):
    admin, _ = users
    AuthService(db_session).forgot(admin.email, "test")
    raw, _ = reset_raw(db_session)
    reset = db_session.get(PasswordReset, digest(raw))
    if condition == "expired":
        reset.expires_at = now() - timedelta(seconds=1)
    if condition == "disabled":
        admin.is_active = False
    if condition == "changed":
        admin.credential_version += 1
    if condition == "wrong":
        raw = "x" * 43
    db_session.commit()
    response = client.post(
        "/api/v1/auth/password/reset",
        json={"token": raw, "new_password": "Una frase nueva bastante larga"},
    )
    assert response.status_code == 400


def test_password_change_logout_all_reauth(client, users):
    admin, _ = users
    result = login(client, admin)
    assert (
        client.post("/api/v1/auth/logout-all", headers=bearer(result)).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/auth/password/change",
            headers=bearer(result),
            json={"password": "bad", "new_password": "Una nueva frase privada"},
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/v1/auth/password/change",
            headers=bearer(result),
            json={
                "password": "admin-password",
                "new_password": "Una nueva frase privada",
            },
        ).status_code
        == 200
    )
    assert client.get("/api/v1/auth/me", headers=bearer(result)).status_code == 401
    fresh = login(client, admin, "Una nueva frase privada")
    assert (
        client.post(
            "/api/v1/auth/reauthenticate",
            headers=bearer(fresh),
            json={"password": "Una nueva frase privada"},
        ).status_code
        == 200
    )
    assert (
        client.post("/api/v1/auth/logout-all", headers=bearer(fresh)).status_code == 200
    )
    assert client.get("/api/v1/auth/me", headers=bearer(fresh)).status_code == 401


def test_bcrypt_rehash_and_unicode(client, users, db_session):
    admin, _ = users
    import bcrypt

    admin.password_hash = bcrypt.hashpw(b"legacy-password", bcrypt.gensalt()).decode()
    db_session.commit()
    login(client, admin, "legacy-password")
    assert admin.password_hash.startswith("$argon2id$")
    password = "á😀 espacio " * 10
    validate_password(password)
    assert verify_password(password, hash_password(password))
    for bad in ("short", "a" * 40, "password123456789", "x" * 129):
        with pytest.raises(HTTPException):
            validate_password(bad)


def test_quota_unknown_identifiers_csrf_and_sanitized_inputs(client, monkeypatch):
    assert (
        client.post(
            "/api/v1/auth/login",
            headers={"X-CSRF-Token": ""},
            json={"email": "unknown@example.com", "password": "secret"},
        ).status_code
        == 403
    )
    monkeypatch.setattr(settings, "auth_ip_limit", 2)
    statuses = [
        client.post(
            "/api/v1/auth/login",
            json={"email": "unknown@example.com", "password": "wrong"},
        ).status_code
        for _ in range(3)
    ]
    assert statuses == [401, 401, 429]
    secret = "SECRET-DO-NOT-REFLECT" * 100
    result = client.post(
        "/api/v1/auth/login", json={"email": "test@example.com", "password": secret}
    )
    assert result.status_code == 422 and secret not in result.text


def test_mail_retry_purge_cancel_and_no_secret_logs(users, db_session, monkeypatch):
    admin, _ = users
    AuthService(db_session).forgot(admin.email, "test")
    raw, row = reset_raw(db_session)
    messages = []
    monkeypatch.setattr(
        MailService,
        "send",
        lambda *args: (_ for _ in ()).throw(TimeoutError("secret server response")),
    )
    assert MailService(db_session).process_one()
    db_session.refresh(row)
    assert (
        row.state == "pending"
        and row.attempts == 1
        and row.last_error == "delivery_failed"
    )
    row.available_at = now() - timedelta(seconds=1)
    db_session.commit()
    monkeypatch.setattr(
        MailService, "send", lambda self, identity, data: messages.append(data)
    )
    assert MailService(db_session).process_one()
    assert row.state == "sent" and row.payload is None
    assert raw in messages[0]["text"] and "<a href=" in messages[0]["html"]
    assert "admin-password" not in str(messages)
    assert not MailService(db_session).process_one()


def test_mail_recovery_after_worker_crash_and_expired_token(
    users, db_session, monkeypatch
):
    admin, _ = users
    AuthService(db_session).forgot(admin.email, "test")
    raw, row = reset_raw(db_session)
    row.state = "processing"
    row.available_at = now() - timedelta(seconds=1)
    db_session.get(PasswordReset, digest(raw)).consumed_at = now()
    db_session.commit()
    monkeypatch.setattr(
        MailService, "send", lambda *args: pytest.fail("Revoked link must not be sent")
    )
    assert MailService(db_session).process_one()
    assert row.state == "failed" and row.payload is None


def test_session_inactivity_absolute_expiry_and_key_rotation(
    client, users, db_session, monkeypatch
):
    admin, _ = users
    result = login(client, admin)
    token = result.json()["access_token"]
    claims = decode_token(token)
    session = db_session.get(AuthSession, claims["sid"])
    session.last_used_at = now() - timedelta(hours=settings.session_idle_hours + 1)
    db_session.commit()
    assert client.get("/api/v1/auth/me", headers=bearer(result)).status_code == 401
    session.last_used_at = now()
    session.expires_at = now() - timedelta(seconds=1)
    db_session.commit()
    assert client.get("/api/v1/auth/me", headers=bearer(result)).status_code == 401
    old_key, old_id = settings.secret_key, settings.jwt_key_id
    monkeypatch.setattr(settings, "jwt_previous_keys", {old_id: old_key})
    monkeypatch.setattr(settings, "jwt_key_id", "next")
    monkeypatch.setattr(
        settings, "secret_key", "replacement-test-key-0123456789abcdefgh"
    )
    assert decode_token(token)
    monkeypatch.setattr(settings, "jwt_previous_keys", {})
    assert decode_token(token) is None


def test_admin_unlock_other_admin_and_apoderado_forbidden(client, users, db_session):
    admin, apod = users
    admin.failed_attempts = 5
    admin.locked_until = now() + timedelta(minutes=15)
    db_session.commit()
    assert (
        client.get("/api/v1/admin/users/locks", headers=headers(apod)).status_code
        == 403
    )
    assert (
        client.post(
            f"/api/v1/admin/users/{admin.id}/unlock",
            headers=headers(apod),
            json={"reason": "Prueba"},
        ).status_code
        == 403
    )
    from app.models.user import User
    from app.utils.enums import UserRole

    operator = User(
        username="other-admin",
        email="other-admin@example.com",
        full_name="Other Admin",
        password_hash=hash_password("Another admin phrase"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(operator)
    db_session.commit()
    result = login(client, operator, "Another admin phrase")
    client.post(
        "/api/v1/auth/reauthenticate",
        headers=bearer(result),
        json={"password": "Another admin phrase"},
    )
    assert (
        client.post(
            f"/api/v1/admin/users/{admin.id}/unlock",
            headers=bearer(result),
            json={"reason": "Verificación de identidad"},
        ).status_code
        == 200
    )
    assert not admin.locked_until and admin.role == UserRole.ADMIN


def test_mail_permanent_failure_and_configuration(users, db_session, monkeypatch):
    import smtplib
    from app.core.config import Settings

    admin, _ = users
    AuthService(db_session).forgot(admin.email, "test")
    _, row = reset_raw(db_session)
    monkeypatch.setattr(
        MailService,
        "send",
        lambda *args: (_ for _ in ()).throw(
            smtplib.SMTPAuthenticationError(535, b"private smtp error")
        ),
    )
    MailService(db_session).process_one()
    assert (
        row.state == "failed"
        and row.payload is None
        and row.last_error == "smtp_permanent"
    )
    data = settings.model_dump()
    for changes in (
        {"secret_key": "x" * 32},
        {"algorithm": "none"},
        {"cors_origins": ["*"]},
        {"smtp_host": "remote.example.com", "smtp_tls": "none"},
        {"app_env": "production", "cookie_secure": False},
    ):
        with pytest.raises(ValueError):
            Settings(**{**data, **changes})


def test_smtp_tls_failure_does_not_fallback(users, db_session, monkeypatch):
    import smtplib
    import ssl

    calls = []

    class Transport:
        def __init__(self, *a, **k):
            calls.append("connect")

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def starttls(self, **k):
            assert k["context"].verify_mode == ssl.CERT_REQUIRED
            calls.append("tls")
            raise ssl.SSLCertVerificationError("invalid certificate")

        def send_message(self, *a):
            calls.append("send")

    monkeypatch.setattr(settings, "smtp_tls", "starttls")
    monkeypatch.setattr(smtplib, "SMTP", Transport)
    with pytest.raises(ssl.SSLCertVerificationError):
        MailService(db_session).send(
            "test",
            {
                "to": "test@example.com",
                "subject": "Prueba",
                "text": "Texto",
                "html": "<p>Texto</p>",
            },
        )
    assert calls == ["connect", "tls"]


def test_crash_after_smtp_acceptance_retries_same_message(
    users, db_session, monkeypatch
):
    admin, _ = users
    AuthService(db_session).forgot(admin.email, "test")
    _, row = reset_raw(db_session)
    sent = []
    monkeypatch.setattr(
        MailService, "send", lambda self, identity, data: sent.append(identity)
    )
    commit = db_session.commit
    commits = 0

    def crash_commit():
        nonlocal commits
        commits += 1
        if commits == 2:
            raise RuntimeError("simulated crash after SMTP acceptance")
        commit()

    monkeypatch.setattr(db_session, "commit", crash_commit)
    with pytest.raises(RuntimeError):
        MailService(db_session).process_one()
    db_session.rollback()
    monkeypatch.setattr(db_session, "commit", commit)
    db_session.refresh(row)
    assert row.state == "processing" and row.payload is not None
    row.available_at = now() - timedelta(seconds=1)
    db_session.commit()
    MailService(db_session).process_one()
    assert sent == [
        row.id,
        row.id,
    ]  # SMTP can duplicate; no new link/event is generated.
    assert row.state == "sent" and row.payload is None
    assert db_session.scalar(select(func.count()).select_from(PasswordReset)) == 1
