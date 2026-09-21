"""Opt-in integration tests in disposable PostgreSQL databases, migrated with Alembic."""

import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import timedelta
import pytest
from sqlalchemy import create_engine, text, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from alembic.config import Config
from alembic import command
from fastapi import HTTPException
from cryptography.fernet import Fernet
from app.core.config import settings
from app.core.passwords import hash_password
from app.models.user import User
from app.models.auth_session import PasswordReset, MailOutbox, AuthSession
from app.repositories.auth_repository import now, digest
from app.services.auth_service import AuthService
from app.services.mail_service import MailService
from app.utils.enums import UserRole

pytestmark = pytest.mark.skipif(
    os.environ.get("SECURITY_POSTGRES_TESTS") != "1",
    reason="Opt-in disposable PostgreSQL tests",
)


@pytest.fixture
def pg(monkeypatch):
    base = make_url(settings.database_url)
    if base.host not in ("localhost", "127.0.0.1"):
        pytest.fail("Integration tests require local PostgreSQL")
    name = "security_test_" + uuid.uuid4().hex
    operator = create_engine(
        base.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    with operator.connect() as c:
        c.execute(text(f'CREATE DATABASE "{name}"'))
    url = base.set(database=name)
    monkeypatch.setattr(
        settings, "database_url", url.render_as_string(hide_password=False)
    )
    monkeypatch.setattr(settings, "mail_outbox_key", Fernet.generate_key().decode())
    engine = create_engine(url)
    try:
        command.upgrade(Config("alembic.ini"), "head")
        yield engine
    finally:
        engine.dispose()
        with operator.connect() as c:
            c.execute(text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        operator.dispose()


def account(engine):
    with Session(engine) as db:
        user = User(
            username="concurrent",
            email="concurrent@example.com",
            full_name="Test",
            role=UserRole.ADMIN,
            password_hash=hash_password("Una frase inicial privada"),
            is_active=True,
        )
        db.add(user)
        db.commit()
        return user.id


def pair(work):
    barrier = Barrier(2)

    def run(_):
        barrier.wait()
        return work()

    with ThreadPoolExecutor(max_workers=2) as executor:
        return list(executor.map(run, range(2)))


def test_refresh_replay_serializes_and_revokes_family(pg):
    uid = account(pg)
    with Session(pg) as db:
        _, raw = AuthService(db).login(
            "concurrent@example.com", "Una frase inicial privada", "local"
        )

    def refresh():
        with Session(pg) as db:
            try:
                AuthService(db).refresh(raw, "local")
                return 200
            except HTTPException as e:
                return e.status_code

    assert sorted(pair(refresh)) == [200, 401]
    with Session(pg) as db:
        assert db.scalar(
            select(AuthSession).where(AuthSession.user_id == uid)
        ).revoked_at


def test_reset_exactly_one_consumption_under_concurrency(pg):
    uid = account(pg)
    raw = uuid.uuid4().hex + uuid.uuid4().hex
    with Session(pg) as db:
        db.add(
            PasswordReset(
                digest=digest(raw),
                user_id=uid,
                credential_version=0,
                expires_at=now() + timedelta(minutes=10),
            )
        )
        db.commit()

    def reset():
        with Session(pg) as db:
            try:
                AuthService(db).reset_password(
                    raw, "Una contraseña nueva bien larga", "local"
                )
                return 200
            except HTTPException as e:
                return e.status_code

    assert sorted(pair(reset)) == [200, 400]
    with Session(pg) as db:
        assert db.get(User, uid).credential_version == 1
        assert len(list(db.scalars(select(MailOutbox)))) == 1


def test_failures_atomic_and_double_worker(pg, monkeypatch):
    uid = account(pg)

    def attempt():
        with Session(pg) as db:
            try:
                AuthService(db).login("concurrent@example.com", "wrong", "local")
            except HTTPException as e:
                return e.status_code

    assert pair(attempt) == [401, 401]
    with Session(pg) as db:
        assert db.get(User, uid).failed_attempts == 2
        db.get(User, uid).failed_attempts = 4
        db.commit()
    assert pair(attempt) == [401, 401]
    with Session(pg) as db:
        assert db.get(User, uid).failed_attempts == 5
        assert db.get(User, uid).locked_until > now()
        AuthService(db).forgot("concurrent@example.com", "local")
    sent = []
    monkeypatch.setattr(
        MailService, "send", lambda self, identity, data: sent.append(identity)
    )

    def worker():
        with Session(pg) as db:
            return MailService(db).process_one()

    pair(worker)
    assert len(sent) == 1


def test_upgrade_existing_user_and_downgrade(pg):
    cfg = Config("alembic.ini")
    uid = account(pg)
    command.downgrade(cfg, "e271bb89a403")
    with pg.connect() as c:
        assert (
            c.execute(
                text("SELECT username FROM users WHERE id=:id"), {"id": uid}
            ).scalar_one()
            == "concurrent"
        )
    command.upgrade(cfg, "head")
    command.check(cfg)
    with Session(pg) as db:
        user = db.get(User, uid)
        assert user.failed_attempts == user.credential_version == 0 and user.is_active


def make_invitation(engine, uid):
    from app.services.invitation_service import InvitationService
    from app.schemas.invitation import InvitationInput
    from tests.auth_helpers import invitation_raw

    with Session(engine) as db:
        row = InvitationService(db).create(
            InvitationInput(email="invite@example.com"), uid
        )
        return row["id"], invitation_raw(db, row["id"])


def test_invitation_concurrent_acceptance_one_user(pg):
    from app.services.invitation_service import InvitationService
    from app.schemas.invitation import InvitationAccept
    from app.models.invitation import Invitation

    uid = account(pg)
    identity, raw = make_invitation(pg, uid)

    def accept():
        with Session(pg) as db:
            try:
                InvitationService(db).accept(
                    InvitationAccept(
                        token=raw,
                        username="invited",
                        full_name="Prueba",
                        password="Una frase nueva para la invitación",
                    )
                )
                return 200
            except HTTPException as e:
                return e.status_code

    assert sorted(pair(accept)) == [200, 400]
    with Session(pg) as db:
        assert len(list(db.scalars(select(User)))) == 2
        assert db.get(Invitation, identity).state == "accepted"


@pytest.mark.parametrize("action", ["resend", "cancel"])
def test_invitation_accept_vs_management_serializes(pg, action):
    from app.services.invitation_service import InvitationService
    from app.schemas.invitation import InvitationAccept
    from app.models.invitation import Invitation

    uid = account(pg)
    identity, raw = make_invitation(pg, uid)
    with Session(pg) as db:
        db.get(Invitation, identity).sent_at -= timedelta(minutes=2)
        db.commit()
    barrier = Barrier(2)

    def work(which):
        barrier.wait()
        with Session(pg) as db:
            try:
                service = InvitationService(db)
                if which == "accept":
                    service.accept(
                        InvitationAccept(
                            token=raw,
                            username="invited",
                            full_name="Prueba",
                            password="Una frase nueva para la invitación",
                        )
                    )
                else:
                    service.change(identity, uid, action)
                return which, 200
            except HTTPException as e:
                return which, e.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        result = dict(executor.map(work, ["accept", "manage"]))
    assert result in ({"accept": 200, "manage": 409}, {"accept": 400, "manage": 200})
    with Session(pg) as db:
        row = db.get(Invitation, identity)
        assert (row.state == "accepted") == (len(list(db.scalars(select(User)))) == 2)


def test_invitation_duplicate_email_across_two_admins(pg):
    from app.services.invitation_service import InvitationService
    from app.schemas.invitation import InvitationInput

    uid = account(pg)
    with Session(pg) as db:
        second = User(
            username="admin2",
            email="admin2@example.com",
            full_name="Second",
            role=UserRole.ADMIN,
            password_hash=hash_password("Una frase segunda privada"),
        )
        db.add(second)
        db.commit()
        second_id = second.id
    barrier = Barrier(2)

    def issue(actor):
        barrier.wait()
        with Session(pg) as db:
            try:
                InvitationService(db).create(
                    InvitationInput(email="same@example.com"), actor
                )
                return 201
            except HTTPException as e:
                return e.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(issue, [uid, second_id])) == [201, 409]
    with Session(pg) as db:
        assert len(list(db.scalars(select(MailOutbox)))) == 1


def test_email_conflict_preflight_and_preservation(pg):
    from app.models import Election, Office, UserModule, ElectoralList, ListAssignment
    from app.utils.enums import UserModuleType
    from datetime import date

    cfg = Config("alembic.ini")
    uid = account(pg)
    with Session(pg) as db:
        election = Election(
            name="Test", election_type="test", election_date=date(2030, 1, 1)
        )
        office = Office(
            code="test", name="Test", scope_type="provincial", required_positions=2
        )
        db.add_all([election, office])
        db.flush()
        module = UserModule(
            user_id=uid,
            election_id=election.id,
            office_id=office.id,
            module_type=UserModuleType.DIPUTADOS_PROVINCIALES,
        )
        row = ElectoralList(
            election_id=election.id,
            office_id=office.id,
            created_by=uid,
            list_name="Existing",
        )
        db.add_all([module, row])
        db.flush()
        assignment = ListAssignment(user_id=uid, list_id=row.id)
        db.add(assignment)
        db.commit()
        module_id, assignment_id = module.id, assignment.id
    command.downgrade(cfg, "6cb192ebc9fe")
    with pg.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users(username,email,full_name,password_hash,role,is_active,created_at,updated_at) SELECT 'collision', upper(email),full_name,password_hash,role,is_active,created_at,updated_at FROM users WHERE id=:id"
            ),
            {"id": uid},
        )
    with pytest.raises(RuntimeError, match="collisions"):
        command.upgrade(cfg, "head")
    with pg.begin() as connection:
        assert connection.execute(text("SELECT count(*) FROM users")).scalar_one() == 2
        assert (
            connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
            == "6cb192ebc9fe"
        )
        connection.execute(text("DELETE FROM users WHERE username='collision'"))
    command.upgrade(cfg, "head")
    command.check(cfg)
    with Session(pg) as db:
        assert db.get(User, uid).email_verified_at is None
        assert db.get(UserModule, module_id).enabled
        assert db.get(ListAssignment, assignment_id).user_id == uid


def test_backup_restore_after_invitation_downgrade(pg):
    """Exercise Docker pg_dump/pg_restore only against the fixture-owned test database."""
    import subprocess
    from app.models.invitation import Invitation

    base = make_url(settings.database_url)
    assert base.database.startswith("security_test_")
    uid = account(pg)
    identity, _ = make_invitation(pg, uid)
    docker = ["docker", "compose", "-f", "../local-deps.yml", "exec", "-T", "postgres"]
    backup = subprocess.run(
        docker + ["pg_dump", "-U", base.username, "-Fc", base.database],
        capture_output=True,
        check=True,
    ).stdout
    command.downgrade(Config("alembic.ini"), "6cb192ebc9fe")
    subprocess.run(
        docker
        + [
            "pg_restore",
            "-U",
            base.username,
            "--clean",
            "--if-exists",
            "--exit-on-error",
            "-d",
            base.database,
        ],
        input=backup,
        capture_output=True,
        check=True,
    )
    with Session(pg) as db:
        assert db.get(Invitation, identity).state == "pending"
        assert db.get(User, uid).is_active
    command.check(Config("alembic.ini"))
