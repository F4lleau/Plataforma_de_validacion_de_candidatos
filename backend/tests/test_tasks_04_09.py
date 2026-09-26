from datetime import date, timedelta
from tests.auth_helpers import invite_account
from io import BytesIO
import pandas as pd
import pytest
from sqlalchemy import select, func
from tests.test_auth_rbac import db_session, client, users, headers
from app.models import (
    User,
    Person,
    Candidate,
    CandidateValidation,
    ListCandidate,
    AuditLog,
    ElectionRule,
    AffiliateImportBatch,
    PartyMember,
)
from app.services.affiliate_import_service import AffiliateImportService


@pytest.fixture
def scenario(client, users):
    admin, apod = users
    h = headers(admin)
    today = date.today()

    def post(path, body):
        r = client.post("/api/v1" + path, json=body, headers=h)
        assert r.status_code == 201, r.text
        return r.json()

    election_body = {
        "name": "Proceso sintético",
        "election_type": "interna",
        "election_date": str(today + timedelta(days=100)),
        "loading_opens": str(today - timedelta(days=1)),
        "loading_closes": str(today + timedelta(days=50)),
        "active": True,
    }
    election = post("/elections/", election_body)
    office = post(
        "/offices/",
        {
            "code": "diputados_prueba",
            "name": "Diputados de prueba",
            "scope_type": "provincial",
            "required_positions": 24,
            "requires_alternation": False,
        },
    )
    local = post(
        "/offices/",
        {
            "code": "consejos_prueba",
            "name": "Consejos de prueba",
            "scope_type": "municipal",
            "municipality_based": True,
            "required_positions": 22,
            "requires_alternation": True,
        },
    )
    municipality = post("/municipalities/", {"name": "Distrito sintético"})

    def rules(n, alt):
        return {
            "minimum_age": 21 if alt else 25,
            "age_reference": "election_date",
            "required_positions": n,
            "requires_alternation": alt,
            "template_is_test": True,
            "positions": [
                {"position": i + 1, "name": f"Prueba {i + 1}", "group": "prueba"}
                for i in range(n)
            ],
        }

    rule = post(f"/elections/{election['id']}/rules/{office['id']}", rules(24, False))
    post(f"/elections/{election['id']}/rules/{local['id']}", rules(22, True))
    user_body = {
        "username": apod.username,
        "email": apod.email,
        "full_name": apod.full_name,
        "is_active": True,
        "modules": [
            {
                "election_id": election["id"],
                "office_id": office["id"],
                "municipality_id": None,
            },
            {
                "election_id": election["id"],
                "office_id": local["id"],
                "municipality_id": municipality["id"],
            },
        ],
    }
    r = client.put(f"/api/v1/users/{apod.id}", json=user_body, headers=h)
    assert r.status_code == 200, r.text
    list_body = {
        "election_id": election["id"],
        "office_id": office["id"],
        "municipality_id": None,
        "list_name": "Lista sintética",
        "list_number": "S-01",
    }
    r = client.post("/api/v1/lists/", json=list_body, headers=headers(apod))
    assert r.status_code == 201, r.text
    return dict(
        admin=admin,
        apod=apod,
        election=election,
        election_body=election_body,
        office=office,
        local=local,
        municipality=municipality,
        rule=rule,
        list=r.json(),
        list_body=list_body,
        user_body=user_body,
    )


def candidate(**changes):
    return {
        "dni": "98000001",
        "first_name": "Persona",
        "last_name": "Sintética",
        "birth_date": "1990-01-01",
        "gender": "F",
        "position": 1,
        "action": "validate",
        **changes,
    }


def test_config_version_and_catalog_scope(client, scenario, db_session):
    s = scenario
    h = headers(s["admin"])
    a = headers(s["apod"])
    assert (
        client.get("/api/v1/elections/", headers=a).json()[0]["id"]
        == s["election"]["id"]
    )
    assert (
        client.post(
            "/api/v1/elections/", json=s["election_body"], headers=a
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/elections/",
            json={**s["election_body"], "loading_closes": "2000-01-01"},
            headers=h,
        ).status_code
        == 422
    )
    r = client.post(
        f"/api/v1/elections/{s['election']['id']}/rules/{s['office']['id']}",
        json={**s["rule"]["rules"], "minimum_age": 26},
        headers=h,
    )
    assert r.status_code == 201 and r.json()["version"] == 2
    detail = client.get(f"/api/v1/lists/{s['list']['id']}", headers=a).json()
    assert (
        detail["rule"]["version"] == 1
        and detail["rule"]["rules"]["requires_alternation"] is False
    )
    assert db_session.scalar(select(func.count()).select_from(AuditLog)) >= 7


@pytest.mark.parametrize(
    "change",
    [
        {"required_positions": 23},
        {"minimum_age": -1},
        {"positions": [{"position": 1, "name": "Prueba", "group": "prueba"}]},
    ],
)
def test_invalid_rules_not_persisted(client, scenario, db_session, change):
    s = scenario
    n = db_session.scalar(select(func.count()).select_from(ElectionRule))
    r = client.post(
        f"/api/v1/elections/{s['election']['id']}/rules/{s['office']['id']}",
        json={**s["rule"]["rules"], **change},
        headers=headers(s["admin"]),
    )
    assert (
        r.status_code == 422
        and db_session.scalar(select(func.count()).select_from(ElectionRule)) == n
    )


def test_account_hash_reset_and_immediate_revoke(client, scenario, db_session):
    s = scenario
    h = headers(s["admin"])
    old = headers(s["apod"])
    body = {**s["user_body"], "password": "new-password-test-only"}
    r = client.put(f"/api/v1/users/{s['apod'].id}", json=body, headers=h)
    assert r.status_code == 422  # Legacy admin password override is closed (Task 19).
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": s["apod"].email, "password": "apoderado-password"},
        ).status_code
        == 200
    )
    client.put(
        f"/api/v1/users/{s['apod'].id}",
        json={**s["user_body"], "modules": []},
        headers=h,
    )
    assert (
        client.get(f"/api/v1/lists/{s['list']['id']}", headers=old).status_code == 403
    )
    client.put(
        f"/api/v1/users/{s['apod'].id}",
        json={**s["user_body"], "is_active": False},
        headers=h,
    )
    assert client.get("/api/v1/auth/me", headers=old).status_code == 401
    assert not any(
        "new-password-test-only" in str(a.details_json)
        for a in db_session.scalars(select(AuditLog))
    )


def test_duplicate_user_and_modules_are_atomic(client, scenario, db_session):
    s = scenario
    h = headers(s["admin"])
    before = db_session.scalar(select(func.count()).select_from(User))
    body = {**s["user_body"], "password": "test-password-123", "username": "other"}
    assert client.post("/api/v1/users/", json=body, headers=h).status_code == 410
    assert db_session.scalar(select(func.count()).select_from(User)) == before
    body["email"] = "other@example.com"
    body["modules"] = [body["modules"][0], body["modules"][0]]
    assert (
        client.put(
            f"/api/v1/users/{s['apod'].id}",
            json={**body, "email": s["apod"].email, "password": None},
            headers=h,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/users/", json={**body, "role": "admin"}, headers=headers(s["apod"])
        ).status_code
        == 403
    )
    assert db_session.scalar(select(func.count()).select_from(User)) == before


def test_ownership_requires_assignment_and_module(client, scenario):
    s = scenario
    h = headers(s["admin"])
    a = headers(s["apod"])
    p = f"/api/v1/lists/{s['list']['id']}"
    assert (
        client.put(p + "/assignments", json={"user_ids": []}, headers=a).status_code
        == 403
    )
    assert (
        client.put(p + "/assignments", json={"user_ids": []}, headers=h).status_code
        == 200
    )
    assert client.get(p, headers=a).status_code == 403
    assert (
        client.post(p + "/candidates", json=candidate(), headers=a).status_code == 403
    )
    assert client.get("/api/v1/lists/", headers=a).json() == []
    assert (
        client.put(
            p + "/assignments", json={"user_ids": [s["apod"].id]}, headers=h
        ).status_code
        == 200
    )
    assert client.get(p, headers=a).status_code == 200
    assert (
        client.post("/api/v1/lists/", json=s["list_body"], headers=a).status_code == 409
    )


def test_draft_edit_validate_preserves_warning_and_versions(
    client, scenario, db_session
):
    s = scenario
    a = headers(s["apod"])
    p = f"/api/v1/lists/{s['list']['id']}/candidates"
    r = client.post(p, json=candidate(action="draft"), headers=a)
    assert r.status_code == 201, r.text
    c = r.json()
    assert c["candidate_status"] == "borrador"
    assert {v["type"]: v["status"] for v in c["validations"]} == {
        "afiliacion": "warning",
        "requisitos_cargo": "pendiente",
    }
    r = client.put(p + f"/{c['id']}", json=candidate(first_name="Corregida"), headers=a)
    assert r.status_code == 200, r.text
    assert r.json()["revision"] == 2
    for model in (Person, Candidate, ListCandidate):
        assert db_session.scalar(select(func.count()).select_from(model)) == 1
    before = db_session.scalar(select(func.count()).select_from(CandidateValidation))
    for _ in range(2):
        assert client.post(p + f"/{c['id']}/validate", headers=a).status_code == 200
    assert (
        db_session.scalar(select(func.count()).select_from(CandidateValidation))
        == before
    )
    assert client.get("/api/v1/candidates", headers=a).json()[0]["id"] == c["id"]


def test_duplicate_positions_future_birth_and_unknown_candidate(
    client, scenario, db_session
):
    s = scenario
    a = headers(s["apod"])
    p = f"/api/v1/lists/{s['list']['id']}/candidates"
    assert client.post(p, json=candidate(), headers=a).status_code == 201
    for payload, status in [
        (candidate(dni="98000002"), 409),
        (candidate(position=2), 409),
        (candidate(dni="98000002", position=25), 422),
        (candidate(dni="98000002", position=2, birth_date="2999-01-01"), 422),
    ]:
        assert client.post(p, json=payload, headers=a).status_code == status
    assert (
        client.put(p + "/9999", json=candidate(position=2), headers=a).status_code
        == 404
    )
    assert db_session.scalar(select(func.count()).select_from(Person)) == 1


def test_municipal_district_is_not_person_address(client, scenario):
    s = scenario
    a = headers(s["apod"])
    r = client.post(
        "/api/v1/lists/",
        headers=a,
        json={
            **s["list_body"],
            "office_id": s["local"]["id"],
            "municipality_id": s["municipality"]["id"],
        },
    )
    assert r.status_code == 201
    r = client.post(
        f"/api/v1/lists/{r.json()['id']}/candidates",
        headers=a,
        json=candidate(municipality_id=None),
    )
    assert r.status_code == 201, r.text
    assert r.json()["person"]["municipality_id"] is None


def test_closed_window_denies_writes(client, scenario):
    s = scenario
    a = headers(s["apod"])
    h = headers(s["admin"])
    r = client.put(
        f"/api/v1/elections/{s['election']['id']}",
        json={
            **s["election_body"],
            "loading_opens": "2000-01-01",
            "loading_closes": "2000-02-01",
        },
        headers=h,
    )
    assert r.status_code == 200
    assert (
        client.post(
            f"/api/v1/lists/{s['list']['id']}/candidates", json=candidate(), headers=a
        ).status_code
        == 409
    )


def xlsx(rows):
    f = BytesIO()
    pd.DataFrame(rows).to_excel(f, index=False)
    f.seek(0)
    return f


def official(**changes):
    return {
        "Sección": "SINTETICA",
        "Cod. Sección": "01",
        "Circuito": "A",
        "Cod. Circuito": "A1",
        "Apellido": "Prueba",
        "Nombre": "Persona",
        "Género": "F",
        "Tipo documento": "DNI",
        "Matrícula": 98000001.0,
        "Fecha nacimiento": "01/01/1990",
        "Clase": 1990,
        "Estado actual elector": "HABILITADO",
        "Estado afiliación": "ACTIVO",
        "Fecha afiliación": "01/01/2020",
        "Analfabeto": "NO",
        "Profesión": "PRUEBA",
        "Fecha domicilio": "01/01/2021",
        "Domicilio": "Domicilio ficticio",
        **changes,
    }


def test_official_fields_filters_and_batch_invalidation(client, scenario):
    s = scenario
    a = headers(s["apod"])
    h = headers(s["admin"])
    p = f"/api/v1/lists/{s['list']['id']}/candidates"
    c = client.post(p, json=candidate(), headers=a).json()
    r = client.post(
        "/api/v1/padron/import",
        files={"file": ("synthetic.xlsx", xlsx([official()]))},
        headers=h,
    )
    assert r.status_code == 200 and r.json()["status"] == "completed", r.text
    rows = client.get(
        "/api/v1/padron?search=persona&section=SINTETICA", headers=h
    ).json()
    assert (
        rows["total"] == 1
        and rows["sections"] == 1
        and rows["items"][0]["dni"] == "98000001"
    )
    assert (
        rows["items"][0]["birth_date"] == "1990-01-01"
        and rows["items"][0]["section_code"] == "01"
    )
    assert client.get("/api/v1/padron", headers=a).status_code == 403
    assert client.get("/api/v1/padron").status_code == 401
    detail = client.get(f"/api/v1/lists/{s['list']['id']}", headers=a).json()
    assert (
        next(
            v
            for v in detail["candidates"][0]["validations"]
            if v["type"] == "afiliacion"
        )["status"]
        == "pendiente"
    )
    refreshed = client.post(p + f"/{c['id']}/validate", headers=a).json()
    assert (
        next(v for v in refreshed["validations"] if v["type"] == "afiliacion")["status"]
        == "ok"
    )


@pytest.mark.parametrize(
    "rows",
    [
        [],
        [official(), official()],
        [official(**{"Fecha nacimiento": "no-fecha"})],
        [official(Nombre=None)],
        [official(Matrícula=123.5)],
    ],
)
def test_invalid_import_preserves_current(scenario, db_session, rows):
    service = AffiliateImportService(db_session)
    actor = scenario["admin"].id
    good = service.import_excel(xlsx([official()]), "good.xlsx", actor)
    assert good.is_current
    bad = service.import_excel(xlsx(rows), "bad.xlsx", actor)
    assert bad.status == "failed"
    assert db_session.get(AffiliateImportBatch, good.id).is_current
    assert db_session.scalar(select(func.count()).select_from(PartyMember)) == 1


def test_inactive_register_row_is_warning(scenario, db_session):
    from app.repositories.party_member_repository import PartyMemberRepository
    from app.services.affiliation_validation_service import AffiliationValidationService

    AffiliateImportService(db_session).import_excel(
        xlsx([official(**{"Estado afiliación": "INACTIVO"})]),
        "inactive.xlsx",
        scenario["admin"].id,
    )
    assert (
        AffiliationValidationService(PartyMemberRepository(db_session)).validate(
            "98000001"
        )["status"]
        == "warning"
    )


@pytest.mark.parametrize(
    "minimum,birth,reference,expected",
    [
        (25, date(2000, 6, 2), date(2025, 6, 1), "warning"),
        (25, date(2000, 6, 2), date(2025, 6, 2), "ok"),
        (25, date(2000, 6, 2), date(2025, 6, 3), "ok"),
        (21, date(2004, 2, 29), date(2025, 2, 28), "warning"),
        (21, date(2004, 2, 29), date(2025, 3, 1), "ok"),
        (21, date(2004, 6, 2), date(2025, 6, 1), "warning"),
        (21, date(2004, 6, 2), date(2025, 6, 2), "ok"),
    ],
)
def test_age_boundary(minimum, birth, reference, expected):
    from types import SimpleNamespace
    from app.services.office_validation_service import OfficeValidationService

    rule = {
        "minimum_age": minimum,
        "age_reference": "election_date",
        "template_is_test": False,
        "other_requirements_confirmed": True,
    }
    assert (
        OfficeValidationService().validate_rules(
            rule, birth, SimpleNamespace(election_date=reference)
        )["status"]
        == expected
    )


def test_intermediate_failure_rolls_back_all_candidate_writes(
    client, scenario, db_session, monkeypatch
):
    from app.services.electoral_workflow_service import ElectoralWorkflowService

    def failure(*args, **kwargs):
        raise RuntimeError("Injected failure")

    monkeypatch.setattr(ElectoralWorkflowService, "validate_candidate", failure)
    s = scenario
    with pytest.raises(RuntimeError):
        client.post(
            f"/api/v1/lists/{s['list']['id']}/candidates",
            json=candidate(),
            headers=headers(s["apod"]),
        )
    for model in (Person, Candidate, ListCandidate):
        assert db_session.scalar(select(func.count()).select_from(model)) == 0


def test_list_pagination_and_forbidden_payload_fields(client, scenario):
    s = scenario
    a = headers(s["apod"])
    r = client.get("/api/v1/lists/page?page=1&page_size=1&search=S-01", headers=a)
    assert (
        r.status_code == 200 and r.json()["total"] == 1 and len(r.json()["items"]) == 1
    )
    assert (
        client.get("/api/v1/lists/page?page=2&page_size=1", headers=a).json()["items"]
        == []
    )
    assert (
        client.post(
            "/api/v1/lists/",
            json={**s["list_body"], "status": "aprobada_sistema"},
            headers=a,
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"/api/v1/lists/{s['list']['id']}/candidates",
            json=candidate(created_by=s["admin"].id),
            headers=a,
        ).status_code
        == 422
    )


def test_second_apoderado_same_scope_cannot_open_foreign_list(
    client, scenario, db_session
):
    s = scenario
    h = headers(s["admin"])
    body = {
        **s["user_body"],
        "username": "second-apod",
        "email": "second-apod@example.com",
        "full_name": "Segundo sintético",
        "password": "test-password-only",
    }
    created_user = invite_account(client, db_session, s["admin"], body)
    token = client.post(
        "/api/v1/auth/login",
        json={"email": body["email"], "password": body["password"]},
    ).json()["access_token"]
    a = {"Authorization": "Bearer " + token}
    p = f"/api/v1/lists/{s['list']['id']}"
    assert client.get("/api/v1/lists/page", headers=a).json()["total"] == 0
    assert client.get(p, headers=a).status_code == 403
    assert (
        client.post(p + "/candidates", json=candidate(), headers=a).status_code == 403
    )
    assert (
        client.put(
            p + "/assignments",
            json={"user_ids": [s["apod"].id, created_user.id]},
            headers=h,
        ).status_code
        == 200
    )
    assert client.get(p, headers=a).status_code == 200


def test_updated_affiliation_removes_historical_warning_from_review(
    client, scenario, db_session
):
    s = scenario
    a = headers(s["apod"])
    p = f"/api/v1/lists/{s['list']['id']}/candidates"
    c = client.post(p, json=candidate(), headers=a).json()
    AffiliateImportService(db_session).import_excel(
        xlsx([official()]), "updated.xlsx", s["admin"].id
    )
    assert client.put(p + f"/{c['id']}", json=candidate(), headers=a).status_code == 200
    reviewed = client.get(
        "/api/v1/candidates/review", headers=headers(s["admin"])
    ).json()
    assert c["id"] not in [v["id"] for v in reviewed]


def test_composition_uses_pinned_rule_not_user_supplied_type(client, scenario):
    s = scenario
    result = client.get(
        f"/api/v1/validations/list/{s['list']['id']}?office_type=consejo_local",
        headers=headers(s["apod"]),
    ).json()
    assert result["details"]["requires_alternation"] is False
    assert result["details"]["required_positions"] == 24
    assert result["details"]["approval_evaluated"] is False


@pytest.mark.parametrize("module_indexes", [[0], [1], [0, 1]])
def test_provincial_local_and_combined_account_modules(
    client, scenario, module_indexes, db_session
):
    s = scenario
    body = {
        **s["user_body"],
        "username": "scope-test",
        "email": "scope-test@example.com",
        "full_name": "Cuenta sintética",
        "password": "scope-test-password",
        "modules": [s["user_body"]["modules"][i] for i in module_indexes],
    }
    invite_account(client, db_session, s["admin"], body)
    token = client.post(
        "/api/v1/auth/login",
        json={"email": body["email"], "password": body["password"]},
    ).json()["access_token"]
    scope = client.get(
        "/api/v1/offices/", headers={"Authorization": "Bearer " + token}
    ).json()
    assert {o["id"] for o in scope} == {m["office_id"] for m in body["modules"]}
