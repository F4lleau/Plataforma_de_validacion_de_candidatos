from datetime import date, datetime, timedelta, timezone
from io import BytesIO

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.security import hash_password, create_access_token
from app.db.session import Base, get_db
from app.main import app
from app.models.candidate import Candidate
from app.models.election import Election
from app.models.office import Office
from app.models.user import User
from app.utils.enums import UserRole


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    with session_factory() as session:
        yield session


@pytest.fixture
def client(db_session: Session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def users(db_session: Session):
    admin = User(
        username="admin-task03",
        email="admin-task03@example.com",
        full_name="Admin Task 03",
        password_hash=hash_password("admin-password"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    apoderado = User(
        username="apoderado-task03",
        email="apoderado-task03@example.com",
        full_name="Apoderado Task 03",
        password_hash=hash_password("apoderado-password"),
        role=UserRole.APODERADO,
        is_active=True,
    )
    db_session.add_all([admin, apoderado])
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(apoderado)
    return admin, apoderado


def headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(str(user.id), {'role': user.role.value})}"}


def login_payload(email: str, password: str) -> dict[str, str]:
    return {"email": email, "password": password}


def candidate_payload() -> dict:
    return {
        "person": {
            "dni": "22222222",
            "first_name": "María",
            "last_name": "Gómez",
            "birth_date": "1990-01-01",
            "gender": "F",
        },
        "office_id": 1,
        "election_id": 1,
    }


def test_login_success_returns_token_and_user(client, users):
    admin, _ = users
    response = client.post("/api/v1/auth/login", json=login_payload(admin.email, "admin-password"))

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["user"]["role"] == "admin"


@pytest.mark.parametrize("password", ["wrong-password"])
def test_login_invalid_credentials_returns_401(client, users, password):
    admin, _ = users
    response = client.post("/api/v1/auth/login", json=login_payload(admin.email, password))
    assert response.status_code == 401


def test_login_unknown_user_returns_401(client):
    response = client.post("/api/v1/auth/login", json=login_payload("unknown@example.com", "password"))
    assert response.status_code == 401


def test_auth_me_requires_token_and_returns_user(client, users):
    admin, _ = users
    assert client.get("/api/v1/auth/me").status_code == 401
    response = client.get("/api/v1/auth/me", headers=headers(admin))
    assert response.status_code == 200
    assert response.json()["id"] == admin.id


def test_invalid_and_expired_tokens_return_401(client):
    assert client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"}).status_code == 401
    expired = jwt.encode(
        {"sub": "1", "type": "access", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401


def test_padron_is_admin_only(client, users):
    admin, apoderado = users
    empty_file = BytesIO()
    pd.DataFrame({"dni": ["123"], "nombre": ["Ana"], "apellido": ["Pérez"]}).to_excel(empty_file, index=False)
    content = empty_file.getvalue()

    assert client.post("/api/v1/padron/import", files={"file": ("padron.xlsx", content)}).status_code == 401
    assert client.post("/api/v1/padron/import", files={"file": ("padron.xlsx", content)}, headers=headers(apoderado)).status_code == 403
    assert client.post("/api/v1/padron/import", files={"file": ("padron.xlsx", content)}, headers=headers(admin)).status_code == 200


def test_review_is_admin_only(client, users):
    admin, apoderado = users
    assert client.get("/api/v1/candidates/review").status_code == 401
    assert client.get("/api/v1/candidates/review", headers=headers(apoderado)).status_code == 403
    assert client.get("/api/v1/candidates/review", headers=headers(admin)).status_code == 200


def test_candidate_creation_uses_current_user_id(client, db_session, users):
    admin, apoderado = users
    db_session.add_all([
        Election(name="Elección", election_type="general", election_date=date(2027, 9, 1), active=True),
        Office(code="DIP-03", name="Diputado", scope_type="provincial", municipality_based=False, required_positions=1, requires_parity=False, requires_alternation=False, active=True),
    ])
    db_session.commit()

    response = client.post("/api/v1/candidates", json=candidate_payload(), headers=headers(apoderado))
    assert response.status_code == 201
    candidate = db_session.get(Candidate, response.json()["candidate"]["id"])
    assert candidate is not None
    assert candidate.created_by == apoderado.id
    assert candidate.created_by != admin.id
