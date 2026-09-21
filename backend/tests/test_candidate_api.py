from tests.auth_helpers import session_token
from datetime import date

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import create_access_token
from app.db.session import Base, get_db
from app.main import app
from app.models.affiliate_import_batch import AffiliateImportBatch
from app.models.election import Election
from app.models.office import Office
from app.models.party_member import PartyMember
from app.models.user import User
from app.services.affiliate_import_service import AffiliateImportService
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
def admin_user(db_session: Session) -> User:
    user = User(
        username="admin-api",
        email="admin-api@example.com",
        full_name="Admin API",
        password_hash="unused",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add_all(
        [
            user,
            Election(
                name="Elección 2027",
                election_type="general",
                election_date=date(2027, 9, 1),
                active=True,
            ),
            Office(
                code="DIP-01",
                name="Diputado provincial",
                scope_type="provincial",
                municipality_based=False,
                required_positions=1,
                requires_parity=False,
                requires_alternation=False,
                active=True,
            ),
        ]
    )
    db_session.commit()
    db_session.refresh(user)
    return user


def auth_headers(user: User) -> dict[str, str]:
    token = session_token(user)
    return {"Authorization": f"Bearer {token}"}


def candidate_payload(dni: str) -> dict:
    return {
        "person": {
            "dni": dni,
            "first_name": "Ana",
            "last_name": "Pérez",
            "birth_date": "1990-02-15",
            "gender": "F",
        },
        "office_id": 1,
        "election_id": 1,
    }


def add_current_member(db_session: Session, dni: str) -> None:
    batch = AffiliateImportBatch(
        file_name="padron.xlsx",
        imported_by=1,
        status="completed",
        is_current=True,
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    db_session.add(
        PartyMember(
            dni=dni,
            first_name="Ana",
            last_name="Pérez",
            full_name="Pérez Ana",
            normalized_name="PEREZ ANA",
            affiliation_status="activo",
            source_batch_id=batch.id,
            is_active=True,
        )
    )
    db_session.commit()


def test_post_candidates_with_affiliation_returns_verified(
    client, db_session, admin_user
):
    add_current_member(db_session, "12345678")

    response = client.post(
        "/api/v1/candidates",
        json=candidate_payload("12345678"),
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 201
    assert response.json()["affiliation"]["status"] == "verified"
    assert response.json()["candidate"]["id"] is not None


def test_post_candidates_without_affiliation_returns_warning_and_review(
    client, db_session, admin_user
):
    response = client.post(
        "/api/v1/candidates",
        json=candidate_payload("87654321"),
        headers=auth_headers(admin_user),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["affiliation"]["status"] == "warning"
    assert body["affiliation"]["requires_admin_review"] is True

    review_response = client.get(
        "/api/v1/candidates/review",
        headers=auth_headers(admin_user),
    )
    assert review_response.status_code == 200
    assert any(item["id"] == body["candidate"]["id"] for item in review_response.json())


def test_successful_import_activates_batch_and_failed_import_preserves_current(
    db_session: Session,
    admin_user: User,
    tmp_path,
    monkeypatch,
):
    old_batch = AffiliateImportBatch(
        file_name="old.xlsx",
        imported_by=admin_user.id,
        status="completed",
        is_current=True,
    )
    db_session.add(old_batch)
    db_session.commit()

    monkeypatch.setattr(
        pd,
        "read_excel",
        lambda *args, **kwargs: pd.DataFrame(
            {"dni": ["12345678"], "nombre": ["Ana"], "apellido": ["Pérez"]}
        ),
    )
    service = AffiliateImportService(db_session)
    successful = service.import_excel(
        str(tmp_path / "ok.xlsx"), "ok.xlsx", admin_user.id
    )

    assert successful.status == "completed"
    assert successful.is_current is True
    assert db_session.get(AffiliateImportBatch, old_batch.id).is_current is False

    monkeypatch.setattr(
        pd, "read_excel", lambda *args, **kwargs: pd.DataFrame({"incorrecta": ["x"]})
    )
    failed = service.import_excel(
        str(tmp_path / "failed.xlsx"), "failed.xlsx", admin_user.id
    )

    assert failed.status == "failed"
    assert db_session.get(AffiliateImportBatch, successful.id).is_current is True
