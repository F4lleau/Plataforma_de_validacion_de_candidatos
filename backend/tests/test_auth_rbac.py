from tests.auth_helpers import session_token
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
from app.models.user_module import UserModule
from app.models.municipality import Municipality
from app.models.electoral_list import ElectoralList
from app.models.affiliate_import_batch import AffiliateImportBatch
from app.models.person import Person
from app.utils.enums import UserRole, UserModuleType
from sqlalchemy import select, func


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )
    with session_factory() as session:
        yield session


@pytest.fixture
def client(db_session: Session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        csrf = test_client.get("/api/v1/auth/csrf").json()["csrf_token"]
        test_client.headers.update(
            {"Origin": "http://localhost:5173", "X-CSRF-Token": csrf}
        )
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
    return {"Authorization": f"Bearer {session_token(user)}"}


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
    response = client.post(
        "/api/v1/auth/login", json=login_payload(admin.email, "admin-password")
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["user"]["role"] == "admin"


@pytest.mark.parametrize("password", ["wrong-password"])
def test_login_invalid_credentials_returns_401(client, users, password):
    admin, _ = users
    response = client.post(
        "/api/v1/auth/login", json=login_payload(admin.email, password)
    )
    assert response.status_code == 401


def test_login_unknown_user_returns_401(client):
    response = client.post(
        "/api/v1/auth/login", json=login_payload("unknown@example.com", "password")
    )
    assert response.status_code == 401


def test_auth_me_requires_token_and_returns_user(client, users):
    admin, _ = users
    assert client.get("/api/v1/auth/me").status_code == 401
    response = client.get("/api/v1/auth/me", headers=headers(admin))
    assert response.status_code == 200
    assert response.json()["id"] == admin.id


def test_invalid_and_expired_tokens_return_401(client):
    assert (
        client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer invalid"}
        ).status_code
        == 401
    )
    expired = jwt.encode(
        {
            "sub": "1",
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    assert (
        client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired}"}
        ).status_code
        == 401
    )


def test_padron_is_admin_only(client, db_session, users):
    admin, apoderado = users
    empty_file = BytesIO()
    pd.DataFrame({"dni": ["123"], "nombre": ["Ana"], "apellido": ["Pérez"]}).to_excel(
        empty_file, index=False
    )
    content = empty_file.getvalue()

    assert (
        client.post(
            "/api/v1/padron/import", files={"file": ("padron.xlsx", content)}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/padron/import",
            files={"file": ("padron.xlsx", content)},
            headers=headers(apoderado),
        ).status_code
        == 403
    )
    response = client.post(
        "/api/v1/padron/import",
        files={"file": ("padron.xlsx", content)},
        headers=headers(admin),
    )
    assert response.status_code == 200
    assert (
        db_session.get(AffiliateImportBatch, response.json()["batch_id"]).imported_by
        == admin.id
    )


def test_review_is_admin_only(client, users):
    admin, apoderado = users
    assert client.get("/api/v1/candidates/review").status_code == 401
    assert (
        client.get("/api/v1/candidates/review", headers=headers(apoderado)).status_code
        == 403
    )
    assert (
        client.get("/api/v1/candidates/review", headers=headers(admin)).status_code
        == 200
    )


def test_legacy_candidate_creation_is_admin_only(client, db_session, users):
    admin, apoderado = users
    response = client.post(
        "/api/v1/candidates", json=candidate_payload(), headers=headers(apoderado)
    )
    assert response.status_code == 403
    assert db_session.scalar(select(func.count()).select_from(Person)) == 0


def test_inactive_user_cannot_login_or_restore_session(client, db_session, users):
    admin, _ = users
    token_headers = headers(admin)
    admin.is_active = False
    db_session.commit()
    response = client.post(
        "/api/v1/auth/login", json=login_payload(admin.email, "admin-password")
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas."
    assert client.get("/api/v1/auth/me", headers=token_headers).status_code == 401


@pytest.mark.parametrize(
    "claims",
    [
        {"sub": "1", "type": "access"},
        {"sub": "invalid", "type": "access", "exp": 4102444800},
        {"sub": "999999999999999999999999", "type": "access", "exp": 4102444800},
        {"sub": "1", "type": "refresh", "exp": 4102444800},
        {"type": "access", "exp": 4102444800},
        {"sub": "1", "type": "access", "exp": None},
    ],
)
def test_invalid_claims_return_401(client, claims):
    token = jwt.encode(claims, settings.secret_key, algorithm=settings.algorithm)
    assert (
        client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        ).status_code
        == 401
    )


def test_token_signature_and_missing_user_are_rejected(client, users):
    admin, _ = users
    token = jwt.encode(
        {"sub": str(admin.id), "type": "access", "exp": 4102444800},
        "wrong-test-signing-key",
        algorithm=settings.algorithm,
    )
    assert (
        client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        ).status_code
        == 401
    )
    missing = create_access_token("99999")
    assert (
        client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {missing}"}
        ).status_code
        == 401
    )


def test_database_role_overrides_token_role(client, db_session, users):
    admin, apoderado = users
    forged_role = session_token(apoderado, {"role": "admin"})
    assert (
        client.get(
            "/api/v1/candidates/review",
            headers={"Authorization": f"Bearer {forged_role}"},
        ).status_code
        == 403
    )
    previous_headers = headers(admin)
    admin.role = UserRole.APODERADO
    db_session.commit()
    assert (
        client.get("/api/v1/candidates/review", headers=previous_headers).status_code
        == 403
    )


@pytest.mark.parametrize("path", ["/users/"])
def test_administrative_routes_are_admin_only(client, users, path):
    admin, apoderado = users
    assert client.get("/api/v1" + path).status_code == 401
    assert client.get("/api/v1" + path, headers=headers(apoderado)).status_code == 403
    assert client.get("/api/v1" + path, headers=headers(admin)).status_code == 200


@pytest.fixture
def assigned_scope(db_session, users):
    _, apoderado = users
    election = Election(
        name="Elección asignada",
        election_type="interna",
        election_date=date(2027, 1, 1),
        active=True,
    )
    office = Office(
        code="LOCAL",
        name="Consejo",
        scope_type="municipal",
        municipality_based=True,
        required_positions=2,
        requires_parity=True,
        requires_alternation=True,
        active=True,
    )
    municipalities = [Municipality(name="Asignada"), Municipality(name="Ajena")]
    db_session.add_all([election, office, *municipalities])
    db_session.flush()
    module = UserModule(
        user_id=apoderado.id,
        election_id=election.id,
        office_id=office.id,
        municipality_id=municipalities[0].id,
        module_type=UserModuleType.CONSEJOS_LOCALES,
        enabled=True,
    )
    lists = [
        ElectoralList(
            election_id=election.id,
            office_id=office.id,
            municipality_id=municipality.id,
            list_name=municipality.name,
            created_by=apoderado.id,
        )
        for municipality in municipalities
    ]
    db_session.add_all([module, *lists])
    db_session.flush()
    from app.models import ListAssignment

    db_session.add(ListAssignment(list_id=lists[0].id, user_id=apoderado.id))
    db_session.commit()
    return election, office, municipalities, module, lists


def test_list_read_and_validation_respect_assignments(
    client, db_session, users, assigned_scope
):
    admin, apoderado = users
    _, _, _, module, lists = assigned_scope
    assert client.get("/api/v1/lists/").status_code == 401
    assert client.get("/api/v1/list-templates/consejo_local").status_code == 401
    assert len(client.get("/api/v1/lists/", headers=headers(admin)).json()) == 2
    response = client.get("/api/v1/lists/", headers=headers(apoderado))
    assert [item["id"] for item in response.json()] == [lists[0].id]
    path = f"/api/v1/validations/list/{lists[0].id}?office_type=consejo_local"
    assert client.get(path).status_code == 401
    assert client.get(path, headers=headers(apoderado)).status_code == 200
    foreign = f"/api/v1/validations/list/{lists[1].id}?office_type=consejo_local"
    assert client.get(foreign, headers=headers(apoderado)).status_code == 403
    assert client.get(foreign, headers=headers(admin)).status_code == 200
    assert (
        client.get(
            "/api/v1/validations/list/999?office_type=consejo_local",
            headers=headers(admin),
        ).status_code
        == 404
    )
    module.enabled = False
    db_session.commit()
    assert client.get("/api/v1/lists/", headers=headers(apoderado)).json() == []
    assert client.get(path, headers=headers(apoderado)).status_code == 403


def test_unassigned_legacy_candidates_are_not_exposed(
    client, db_session, users, assigned_scope
):
    admin, apoderado = users
    election, office, municipalities, _, _ = assigned_scope
    payload = candidate_payload()
    payload.update(election_id=election.id, office_id=office.id)
    payload["person"]["municipality_id"] = municipalities[0].id
    assert (
        client.post(
            "/api/v1/candidates", json=payload, headers=headers(admin)
        ).status_code
        == 201
    )
    assert client.get("/api/v1/candidates", headers=headers(apoderado)).json() == []
    assert len(client.get("/api/v1/candidates", headers=headers(admin)).json()) == 1


@pytest.mark.parametrize(
    "change", ["disabled", "wrong_election", "wrong_office", "other_user"]
)
def test_assignment_must_match_user_election_office_and_enabled(
    client, db_session, users, assigned_scope, change
):
    admin, apoderado = users
    election, office, municipalities, module, _ = assigned_scope
    if change == "disabled":
        module.enabled = False
    elif change == "wrong_election":
        other = Election(
            name="Otra", election_type="interna", election_date=date(2028, 1, 1)
        )
        db_session.add(other)
        db_session.flush()
        module.election_id = other.id
    elif change == "wrong_office":
        other = Office(
            code="OTHER",
            name="Otro",
            scope_type="municipal",
            municipality_based=True,
            required_positions=2,
        )
        db_session.add(other)
        db_session.flush()
        module.office_id = other.id
    else:
        module.user_id = admin.id
    db_session.commit()
    payload = candidate_payload()
    payload.update(election_id=election.id, office_id=office.id)
    payload["person"]["municipality_id"] = municipalities[0].id
    assert (
        client.post(
            "/api/v1/candidates", json=payload, headers=headers(apoderado)
        ).status_code
        == 403
    )
    assert client.get("/api/v1/lists/", headers=headers(apoderado)).json() == []
    assert db_session.scalar(select(func.count()).select_from(Person)) == 0
