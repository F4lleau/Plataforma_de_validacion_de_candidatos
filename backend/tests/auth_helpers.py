from uuid import uuid4
from datetime import timedelta
from sqlalchemy.orm import object_session
from app.models.auth_session import AuthSession
from app.repositories.auth_repository import now
from app.core.security import create_access_token


def session_token(user, extra=None):
    db = object_session(user)
    session = AuthSession(
        id=str(uuid4()),
        user_id=user.id,
        created_at=now(),
        last_used_at=now(),
        expires_at=now() + timedelta(days=1),
    )
    db.add(session)
    db.commit()
    return create_access_token(str(user.id), {"sid": session.id, **(extra or {})})


def invitation_raw(db, invitation_id):
    import json
    from sqlalchemy import select
    from cryptography.fernet import Fernet
    from app.core.config import settings
    from app.models.auth_session import MailOutbox

    mail = db.scalar(
        select(MailOutbox)
        .where(MailOutbox.invitation_id == invitation_id)
        .order_by(MailOutbox.created_at.desc())
    )
    data = json.loads(
        Fernet(settings.mail_outbox_key.encode()).decrypt(mail.payload.encode())
    )
    return data["text"].split("#token=")[1].split()[0]


def invite_account(client, db, actor, body):
    from app.models.user import User
    from sqlalchemy import select

    h = {"Authorization": "Bearer " + session_token(actor)}
    assert (
        client.post(
            "/api/v1/auth/reauthenticate",
            json={"password": "admin-password"},
            headers=h,
        ).status_code
        == 200
    )
    result = client.post(
        "/api/v1/admin/invitations",
        json={"email": body["email"], "modules": body["modules"]},
        headers=h,
    )
    assert result.status_code == 201, result.text
    raw = invitation_raw(db, result.json()["id"])
    accepted = client.post(
        "/api/v1/auth/invitations/accept",
        json={
            "token": raw,
            **{k: body[k] for k in ("full_name", "username", "password")},
        },
    )
    assert accepted.status_code == 200, accepted.text
    user = db.scalar(select(User).where(User.email == body["email"]))
    accept_terms_request(client, {"Authorization": "Bearer " + session_token(user)})
    return user


def accepted_terms_fixture(user):
    """Existing authorized-domain fixtures; new users remain pending by default."""
    from app.repositories.legal_repository import LegalDocumentRepository
    document = LegalDocumentRepository().documents()["terms"]
    user.terms_accepted_at = now()
    user.terms_version = document["version"]
    user.terms_snapshot = document


def accept_terms_request(client, headers):
    document = client.get("/api/v1/legal/documents").json()["terms"]
    response = client.post("/api/v1/auth/terms/accept", headers=headers, json={
        "accepted": True, "version": document["version"], "sha256": document["sha256"],
    })
    assert response.status_code == 200, response.text
    return response
