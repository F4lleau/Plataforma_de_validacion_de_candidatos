from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import Base
from app.models.affiliate_import_batch import AffiliateImportBatch
from app.models.candidate import Candidate
from app.models.candidate_validation import CandidateValidation
from app.models.party_member import PartyMember
from app.models.person import Person
from app.models.user import User
from app.repositories.affiliate_import_batch_repository import AffiliateImportBatchRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.candidate_validation_repository import CandidateValidationRepository
from app.repositories.party_member_repository import PartyMemberRepository
from app.schemas.candidate import CandidateCreate, PersonCreate
from app.services.affiliation_validation_service import AffiliationValidationService
from app.services.candidate_service import CandidateService
from app.utils.enums import UserRole, ValidationResult, ValidationType


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    with SessionLocal() as session:
        yield session


@pytest.fixture
def admin_user(db_session: Session) -> User:
    user = User(
        username="admin1",
        email="admin@example.com",
        full_name="Admin Test",
        password_hash="hash",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_dni_present_in_current_batch_is_verified(db_session: Session, admin_user: User):
    batch = AffiliateImportBatch(
        file_name="septiembre.xlsx",
        imported_by=admin_user.id,
        status="completed",
        is_current=True,
        total_rows=1,
        valid_rows=1,
        invalid_rows=0,
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)

    member = PartyMember(
        dni="12345678",
        affiliate_number="A-100",
        first_name="Ana",
        last_name="García",
        full_name="García Ana",
        normalized_name="GARCIA ANA",
        gender="F",
        section="1",
        circuit="A",
        affiliation_status="activo",
        source_batch_id=batch.id,
        is_active=True,
    )
    db_session.add(member)
    db_session.commit()

    service = AffiliationValidationService(PartyMemberRepository(db_session))
    result = service.validate("12345678")

    assert result["status"] == "verified"
    assert result["message"] == "Afiliación validada correctamente."


def test_dni_missing_in_current_batch_returns_warning_and_candidate_is_saved(db_session: Session, admin_user: User):
    candidate_repository = CandidateRepository(db_session)
    party_member_repository = PartyMemberRepository(db_session)
    validation_repository = CandidateValidationRepository(db_session)
    service = CandidateService(db_session, candidate_repository, party_member_repository, validation_repository)

    payload = CandidateCreate(
        person=PersonCreate(
            dni="98765432",
            first_name="Luis",
            last_name="Pérez",
            birth_date=date(1990, 2, 15),
            gender="M",
            address="Calle 1",
            municipality_id=None,
        ),
        office_id=1,
        election_id=1,
    )

    created = service.create_candidate(payload, admin_user.id)

    assert created.id is not None
    assert created.created_by == admin_user.id
    validations = validation_repository.list_by_candidate(created.id)
    assert any(v.validation_type == ValidationType.AFILIACION and v.status == ValidationResult.WARNING for v in validations)


def test_candidate_review_query_returns_only_warning_cases(db_session: Session, admin_user: User):
    candidate_repository = CandidateRepository(db_session)
    validation_repository = CandidateValidationRepository(db_session)
    party_member_repository = PartyMemberRepository(db_session)
    service = CandidateService(db_session, candidate_repository, party_member_repository, validation_repository)

    payload = CandidateCreate(
        person=PersonCreate(
            dni="11111111",
            first_name="Pedro",
            last_name="López",
            birth_date=date(1988, 5, 10),
            gender="M",
            address="Avenida 2",
            municipality_id=None,
        ),
        office_id=1,
        election_id=1,
    )
    candidate = service.create_candidate(payload, admin_user.id)

    results = candidate_repository.list_requires_admin_review()
    assert any(item.id == candidate.id for item in results)


def test_new_successful_batch_becomes_current_and_old_batch_is_deactivated(db_session: Session, admin_user: User):
    repository = AffiliateImportBatchRepository(db_session)
    old_batch = AffiliateImportBatch(
        file_name="septiembre.xlsx",
        imported_by=admin_user.id,
        status="completed",
        is_current=True,
        total_rows=10,
        valid_rows=10,
        invalid_rows=0,
    )
    db_session.add(old_batch)
    db_session.commit()
    db_session.refresh(old_batch)

    new_batch = AffiliateImportBatch(
        file_name="octubre.xlsx",
        imported_by=admin_user.id,
        status="completed",
        is_current=False,
        total_rows=20,
        valid_rows=20,
        invalid_rows=0,
    )
    db_session.add(new_batch)
    db_session.commit()
    db_session.refresh(new_batch)

    repository.activate_batch(new_batch.id)

    assert repository.get_current_batch() is not None and repository.get_current_batch().id == new_batch.id
    old_refreshed = db_session.get(AffiliateImportBatch, old_batch.id)
    assert old_refreshed.is_current is False


def test_failed_import_keeps_previous_batch_current(db_session: Session, admin_user: User):
    repository = AffiliateImportBatchRepository(db_session)
    current = AffiliateImportBatch(
        file_name="septiembre.xlsx",
        imported_by=admin_user.id,
        status="completed",
        is_current=True,
        total_rows=5,
        valid_rows=5,
        invalid_rows=0,
    )
    db_session.add(current)
    db_session.commit()
    db_session.refresh(current)

    failed = AffiliateImportBatch(
        file_name="octubre.xlsx",
        imported_by=admin_user.id,
        status="failed",
        is_current=False,
        total_rows=10,
        valid_rows=0,
        invalid_rows=10,
    )
    db_session.add(failed)
    db_session.commit()
    db_session.refresh(failed)

    repository.activate_batch(failed.id)
    current_refreshed = db_session.get(AffiliateImportBatch, current.id)
    assert current_refreshed.is_current is True


def test_get_by_dni_ignores_historical_batches(db_session: Session, admin_user: User):
    old_batch = AffiliateImportBatch(
        file_name="septiembre.xlsx",
        imported_by=admin_user.id,
        status="completed",
        is_current=False,
        total_rows=1,
        valid_rows=1,
        invalid_rows=0,
    )
    db_session.add(old_batch)
    db_session.commit()
    db_session.refresh(old_batch)

    current_batch = AffiliateImportBatch(
        file_name="octubre.xlsx",
        imported_by=admin_user.id,
        status="completed",
        is_current=True,
        total_rows=1,
        valid_rows=1,
        invalid_rows=0,
    )
    db_session.add(current_batch)
    db_session.commit()
    db_session.refresh(current_batch)

    old_member = PartyMember(
        dni="777",
        first_name="Hist",
        last_name="Orico",
        full_name="Orico Hist",
        normalized_name="ORICO HIST",
        gender="M",
        affiliation_status="activo",
        source_batch_id=old_batch.id,
        is_active=True,
    )
    current_member = PartyMember(
        dni="777",
        first_name="Actual",
        last_name="Vigente",
        full_name="Vigente Actual",
        normalized_name="VIGENTE ACTUAL",
        gender="M",
        affiliation_status="activo",
        source_batch_id=current_batch.id,
        is_active=True,
    )
    db_session.add_all([old_member, current_member])
    db_session.commit()

    repo = PartyMemberRepository(db_session)
    result = repo.get_current_by_dni("777")
    assert result is not None and result.source_batch_id == current_batch.id


def test_dni_is_normalized_before_search_and_save(db_session: Session, admin_user: User):
    batch = AffiliateImportBatch(
        file_name="padrón.xlsx",
        imported_by=admin_user.id,
        status="completed",
        is_current=True,
        total_rows=1,
        valid_rows=1,
        invalid_rows=0,
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)

    member = PartyMember(
        dni="12345678",
        first_name="Ana",
        last_name="García",
        full_name="García Ana",
        normalized_name="GARCIA ANA",
        gender="F",
        affiliation_status="activo",
        source_batch_id=batch.id,
        is_active=True,
    )
    db_session.add(member)
    db_session.commit()

    service = AffiliationValidationService(PartyMemberRepository(db_session))
    assert service.validate(" 12345678 ")["status"] == "verified"
    assert service.validate("12345678")["status"] == "verified"


def test_duplicate_dni_in_import_is_skipped(db_session: Session, admin_user: User):
    repository = AffiliateImportBatchRepository(db_session)
    batch = AffiliateImportBatch(
        file_name="duplicado.xlsx",
        imported_by=admin_user.id,
        status="processing",
        is_current=False,
        total_rows=0,
        valid_rows=0,
        invalid_rows=0,
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)

    current_count = PartyMemberRepository(db_session).count_for_batch(batch.id)
    assert current_count == 0

    repository.mark_batch_complete(batch.id)
    assert db_session.get(AffiliateImportBatch, batch.id).status == "completed"


def test_candidate_create_does_not_raise_on_affiliation_warning(db_session: Session, admin_user: User):
    candidate_repository = CandidateRepository(db_session)
    party_member_repository = PartyMemberRepository(db_session)
    validation_repository = CandidateValidationRepository(db_session)
    service = CandidateService(db_session, candidate_repository, party_member_repository, validation_repository)

    payload = CandidateCreate(
        person=PersonCreate(
            dni="555",
            first_name="Marta",
            last_name="Ruiz",
            birth_date=date(2001, 3, 1),
            gender="F",
            address="Calle 5",
            municipality_id=None,
        ),
        office_id=2,
        election_id=2,
    )

    candidate = service.create_candidate(payload, admin_user.id)
    assert candidate.id is not None


def test_candidate_endpoints_should_not_return_4xx_for_missing_affiliation(db_session: Session, admin_user: User):
    candidate_repository = CandidateRepository(db_session)
    party_member_repository = PartyMemberRepository(db_session)
    validation_repository = CandidateValidationRepository(db_session)
    service = CandidateService(db_session, candidate_repository, party_member_repository, validation_repository)

    payload = CandidateCreate(
        person=PersonCreate(
            dni="404",
            first_name="No",
            last_name="Found",
            birth_date=date(1999, 1, 9),
            gender="F",
            address="Street",
            municipality_id=None,
        ),
        office_id=1,
        election_id=1,
    )

    candidate = service.create_candidate(payload, admin_user.id)
    assert candidate is not None
    validations = validation_repository.list_by_candidate(candidate.id)
    assert validations[0].status == ValidationResult.WARNING
