import json
from datetime import timedelta
from unittest.mock import patch
import pytest
from sqlalchemy import select, func
from app.models import User, UserModule, ListAssignment, Office, AuditLog
from app.models.invitation import Invitation
from app.models.auth_session import MailOutbox, AuthSession
from app.core.config import settings
from app.core.passwords import verify_password
from app.repositories.auth_repository import now
from app.services.invitation_service import InvitationService
from app.services.mail_service import MailService
from tests.test_auth_rbac import (
    db_session as db_session,
    client as client,
    users as users,
    headers,
)
from tests.test_tasks_04_09 import scenario as scenario
from tests.auth_helpers import invitation_raw


@pytest.fixture
def admin_headers(client, users):
    h = headers(users[0])
    assert (
        client.post(
            "/api/v1/auth/reauthenticate",
            json={"password": "admin-password"},
            headers=h,
        ).status_code
        == 200
    )
    return h


def invite(client, db, h, modules=None, email="invited@example.com"):
    r = client.post(
        "/api/v1/admin/invitations",
        json={"email": email, "modules": modules or []},
        headers=h,
    )
    assert r.status_code == 201, r.text
    assert "token" not in r.text and "digest" not in r.text
    return r.json(), invitation_raw(db, r.json()["id"])


def profile(token, **extra):
    return {
        "token": token,
        "username": "new.apoderado",
        "full_name": "Persona de Prueba",
        "password": "Una contraseña inicial privada",
        **extra,
    }


def test_invitation_scanner_accept_login_scope_and_no_assignment(
    client, db_session, scenario, admin_headers
):
    row, raw = invite(
        client, db_session, admin_headers, scenario["user_body"]["modules"]
    )
    assert db_session.scalar(select(func.count()).select_from(User)) == 2
    assert client.get("/api/v1/auth/invitations/accept").status_code == 405
    for _ in range(2):
        inspection = client.post(
            "/api/v1/auth/invitations/inspect", json={"token": raw}
        )
        assert inspection.status_code == 200
        assert set(inspection.json()) == {"email", "role", "expires_at"}
    assert db_session.get(Invitation, row["id"]).state == "pending"
    assert (
        client.post("/api/v1/auth/invitations/accept", json=profile(raw)).status_code
        == 200
    )
    assert (
        client.post("/api/v1/auth/invitations/accept", json=profile(raw)).status_code
        == 400
    )
    user = db_session.scalar(select(User).where(User.email == row["email"]))
    assert user.email_verified_at and user.role.value == "apoderado" and user.is_active
    assert verify_password(profile(raw)["password"], user.password_hash)
    assert (
        len(
            list(
                db_session.scalars(
                    select(UserModule).where(UserModule.user_id == user.id)
                )
            )
        )
        == 2
    )
    assert not db_session.scalar(
        select(ListAssignment).where(ListAssignment.user_id == user.id)
    )
    assert not db_session.scalar(
        select(AuthSession).where(AuthSession.user_id == user.id)
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": row["email"], "password": profile(raw)["password"]},
    )
    h = {"Authorization": "Bearer " + response.json()["access_token"]}
    assert client.get("/api/v1/auth/me", headers=h).json()["email_verified_at"]
    assert client.get("/api/v1/lists/page", headers=h).json()["total"] == 0
    assert (
        client.get(f"/api/v1/lists/{scenario['list']['id']}", headers=h).status_code
        == 403
    )
    assert client.get("/api/v1/admin/invitations", headers=h).status_code == 403
    assert db_session.get(User, scenario["admin"].id).email_verified_at is None
    assert not any(
        raw in json.dumps(a.details_json) for a in db_session.scalars(select(AuditLog))
    )


def test_resend_cancel_expiry_and_mail_invalidation(client, db_session, admin_headers):
    row, raw = invite(client, db_session, admin_headers)
    path = f"/api/v1/admin/invitations/{row['id']}"
    assert client.post(path + "/resend", headers=admin_headers).status_code == 429
    stored = db_session.get(Invitation, row["id"])
    stored.sent_at -= timedelta(minutes=2)
    db_session.commit()
    assert (
        client.post(path + "/resend", headers=admin_headers).json()["generation"] == 2
    )
    new = invitation_raw(db_session, row["id"])
    assert new != raw
    assert (
        client.post("/api/v1/auth/invitations/inspect", json={"token": raw}).status_code
        == 400
    )
    oldmail = db_session.scalar(select(MailOutbox).order_by(MailOutbox.created_at))
    assert oldmail.state == "cancelled" and oldmail.payload is None
    assert client.post(path + "/cancel", headers=admin_headers).status_code == 200
    assert (
        client.post("/api/v1/auth/invitations/accept", json=profile(new)).status_code
        == 400
    )
    assert not MailService(db_session).process_one()
    stored.sent_at -= timedelta(minutes=2)
    db_session.commit()
    _, raw = invite(client, db_session, admin_headers)
    stored.expires_at = now() - timedelta(seconds=1)
    db_session.commit()
    assert (
        client.post("/api/v1/auth/invitations/accept", json=profile(raw)).status_code
        == 400
    )
    assert (
        client.get("/api/v1/admin/invitations", headers=admin_headers).json()[0][
            "state"
        ]
        == "expired"
    )


@pytest.mark.parametrize("change", ["inactive", "role", "office", "rules"])
def test_revalidate_authority_and_catalogs(
    client, db_session, scenario, admin_headers, change
):
    row, raw = invite(
        client, db_session, admin_headers, scenario["user_body"]["modules"]
    )
    if change == "inactive":
        scenario["admin"].is_active = False
    elif change == "role":
        scenario["admin"].role = scenario["apod"].role
    elif change == "office":
        db_session.get(Office, scenario["office"]["id"]).active = False
    else:
        from app.models import ElectionRule

        db_session.get(ElectionRule, scenario["rule"]["id"]).enabled = False
    db_session.commit()
    assert client.post(
        "/api/v1/auth/invitations/accept", json=profile(raw)
    ).status_code in (400, 409)
    assert db_session.scalar(select(func.count()).select_from(User)) == 2
    assert db_session.get(Invitation, row["id"]).state == "pending"


@pytest.mark.parametrize(
    "extra",
    [
        {"email": "other@example.com"},
        {"role": "admin"},
        {"modules": []},
        {"is_active": True},
    ],
)
def test_accept_rejects_mass_assignment(client, db_session, admin_headers, extra):
    _, raw = invite(client, db_session, admin_headers)
    assert (
        client.post(
            "/api/v1/auth/invitations/accept", json=profile(raw, **extra)
        ).status_code
        == 422
    )
    assert db_session.scalar(select(func.count()).select_from(User)) == 2


def test_admin_only_csrf_recent_auth_quota_and_duplicates(
    client, db_session, users, admin_headers, monkeypatch
):
    body = {"email": "invited@example.com", "modules": []}
    assert client.post("/api/v1/admin/invitations", json=body).status_code == 401
    assert (
        client.post(
            "/api/v1/admin/invitations", json=body, headers=headers(users[1])
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/admin/invitations", json=body, headers=headers(users[0])
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/admin/invitations",
            json=body,
            headers={**admin_headers, "Origin": "https://evil.invalid"},
        ).status_code
        == 403
    )
    for email in [users[0].email.upper(), users[1].email]:
        assert (
            client.post(
                "/api/v1/admin/invitations",
                json={**body, "email": email},
                headers=admin_headers,
            ).status_code
            == 409
        )
    row, raw = invite(client, db_session, admin_headers)
    assert (
        client.post(
            "/api/v1/admin/invitations", json=body, headers=admin_headers
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/api/v1/admin/invitations",
            json={**body, "role": "admin"},
            headers=admin_headers,
        ).status_code
        == 422
    )
    for action in ("resend", "cancel"):
        assert (
            client.post(
                f"/api/v1/admin/invitations/{row['id']}/{action}",
                headers=headers(users[1]),
            ).status_code
            == 403
        )
    monkeypatch.setattr(settings, "invitation_hourly_limit", 1)
    assert (
        client.post(
            "/api/v1/admin/invitations",
            json={**body, "email": "another@example.com"},
            headers=admin_headers,
        ).status_code
        == 429
    )


def test_wrong_purpose_tokens_and_rollback(client, db_session, admin_headers, users):
    row, raw = invite(client, db_session, admin_headers)
    assert (
        client.post(
            "/api/v1/auth/password/reset",
            json={"token": raw, "new_password": profile(raw)["password"]},
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/v1/auth/invitations/accept", json=profile("x" * 43)
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/v1/auth/invitations/accept",
            json=profile(raw, username=users[0].username),
        ).status_code
        == 409
    )
    assert db_session.get(Invitation, row["id"]).state == "pending"
    with patch(
        "app.services.invitation_service.AuditService.record",
        side_effect=RuntimeError("transaction interrupted"),
    ):
        from app.schemas.invitation import InvitationAccept

        with pytest.raises(RuntimeError):
            InvitationService(db_session).accept(InvitationAccept(**profile(raw)))
        db_session.rollback()
    assert db_session.scalar(select(func.count()).select_from(User)) == 2
    assert db_session.get(Invitation, row["id"]).state == "pending"
    assert (
        client.post("/api/v1/auth/invitations/accept", json=profile(raw)).status_code
        == 200
    )


def test_mail_retry_and_no_delivery_after_inviter_disabled(
    client, db_session, admin_headers, users, monkeypatch
):
    row, raw = invite(client, db_session, admin_headers)
    mail = db_session.scalar(select(MailOutbox))
    assert raw not in mail.payload

    def fail(*args):
        raise OSError("SMTP unavailable")

    monkeypatch.setattr(MailService, "send", fail)
    assert MailService(db_session).process_one()
    assert mail.state == "pending" and mail.attempts == 1
    assert db_session.scalar(select(func.count()).select_from(User)) == 2
    users[0].is_active = False
    mail.available_at = now()
    db_session.commit()
    sent = []
    monkeypatch.setattr(MailService, "send", lambda *args: sent.append(True))
    assert MailService(db_session).process_one()
    assert mail.state == "failed" and mail.payload is None and not sent


def test_manual_create_and_email_change_are_closed(client, users, admin_headers):
    user = users[1]
    body = {
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "modules": [],
    }
    assert (
        client.post(
            "/api/v1/users/",
            json={**body, "password": "Una contraseña manual larga"},
            headers=admin_headers,
        ).status_code
        == 410
    )
    assert (
        client.put(
            f"/api/v1/users/{user.id}",
            json={**body, "email": "changed@example.com"},
            headers=admin_headers,
        ).status_code
        == 422
    )


def test_create_rolls_back_if_mail_cannot_be_enqueued(db_session, users):
    from app.schemas.invitation import InvitationInput

    with patch(
        "app.services.invitation_service.MailService.enqueue_invitation",
        side_effect=RuntimeError("outbox unavailable"),
    ):
        with pytest.raises(RuntimeError):
            InvitationService(db_session).create(
                InvitationInput(email="rollback@example.com"), users[0].id
            )
        db_session.rollback()
    assert not db_session.scalar(select(Invitation))
    assert not db_session.scalar(select(MailOutbox))


def test_disabled_existing_account_cannot_be_reinvited(
    client, db_session, users, admin_headers
):
    users[1].is_active = False
    db_session.commit()
    assert (
        client.post(
            "/api/v1/admin/invitations",
            json={"email": users[1].email},
            headers=admin_headers,
        ).status_code
        == 409
    )
    assert not db_session.get(User, users[1].id).is_active


def test_retention_purges_expired_invitation_with_mail(
    db_session, client, admin_headers
):
    from app.repositories.auth_repository import AuthRepository

    row, _ = invite(client, db_session, admin_headers)
    old = now() - timedelta(days=settings.security_retention_days + 2)
    db_session.get(Invitation, row["id"]).expires_at = old
    mail = db_session.scalar(select(MailOutbox))
    mail.created_at = mail.expires_at = old
    db_session.commit()
    AuthRepository(db_session).cleanup()
    assert not db_session.scalar(select(Invitation))
    assert not db_session.scalar(select(MailOutbox))
