"""Retired identity checks cannot affect current electoral workflows."""

from sqlalchemy import select
from tests.test_auth_rbac import db_session, client, users, headers
from tests.test_tasks_04_09 import scenario, candidate
from app.models import CandidateValidation, ElectionRule, AuditLog
from app.utils.enums import ValidationType, ValidationResult


def test_old_rules_remain_immutable_but_are_not_exposed_or_accepted(
    client, scenario, db_session
):
    s = scenario
    rule = db_session.get(ElectionRule, s["rule"]["id"])
    rule.rules = {**rule.rules, "requires_renaper": True}
    db_session.commit()
    url = f"/api/v1/elections/{s['election']['id']}/rules"
    h = headers(s["admin"])
    public = client.get(url, headers=h).json()
    assert all("requires_renaper" not in r["rules"] for r in public)
    detail = client.get(f"/api/v1/lists/{s['list']['id']}", headers=h).json()
    assert "requires_renaper" not in detail["rule"]["rules"]
    saved = client.post(
        url + f"/{s['office']['id']}", headers=h, json=s["rule"]["rules"]
    )
    assert saved.status_code == 201, saved.text
    assert saved.json()["id"] == rule.id
    assert "requires_renaper" not in saved.json()["rules"]
    invalid = client.post(
        url + f"/{s['office']['id']}",
        headers=h,
        json={**s["rule"]["rules"], "requires_renaper": True},
    )
    assert invalid.status_code == 422
    db_session.refresh(rule)
    assert rule.rules["requires_renaper"] is True


def test_retired_results_hidden_and_preserved_when_revalidating(
    client, scenario, db_session
):
    s = scenario
    url = f"/api/v1/lists/{s['list']['id']}"
    h = headers(s["apod"])
    response = client.post(url + "/candidates", headers=h, json=candidate())
    assert response.status_code == 201, response.text
    c = response.json()
    legacy = CandidateValidation(
        candidate_id=c["id"],
        candidate_revision=c["revision"],
        validation_type=ValidationType.RENAPER,
        status=ValidationResult.PENDIENTE,
        message="Historical identity check",
        response_json={"origin": "not_configured"},
    )
    db_session.add(legacy)
    db_session.commit()
    for _ in range(2):
        r = client.post(url + f"/candidates/{c['id']}/validate", headers=h)
        assert r.status_code == 200, r.text
        assert {v["type"] for v in r.json()["validations"]} == {
            "afiliacion",
            "requisitos_cargo",
        }
    detail = client.get(url, headers=h).json()["candidates"][0]
    assert all(
        v["type"] != "renaper" for v in detail["validations"] + detail["history"]
    )
    db_session.refresh(legacy)
    assert legacy.status == ValidationResult.PENDIENTE
    assert legacy.message == "Historical identity check"
    events = db_session.scalars(
        select(AuditLog).where(AuditLog.action == "candidate.validation_evaluated")
    )
    for event in events:
        assert "renaper" not in event.details_json["before"]
        assert "renaper" not in event.details_json["after"]


def test_retired_warning_does_not_add_candidate_to_review(client, scenario, db_session):
    s = scenario
    r = client.post(
        f"/api/v1/lists/{s['list']['id']}/candidates",
        headers=headers(s["apod"]),
        json=candidate(),
    )
    assert r.status_code == 201, r.text
    c = r.json()
    for v in db_session.scalars(select(CandidateValidation)):
        v.status = ValidationResult.OK
    db_session.add(
        CandidateValidation(
            candidate_id=c["id"],
            candidate_revision=c["revision"],
            validation_type=ValidationType.RENAPER,
            status=ValidationResult.WARNING,
            message="Retired warning",
        )
    )
    db_session.commit()
    response = client.get("/api/v1/admin/candidate-review", headers=headers(s["admin"]))
    assert response.status_code == 200, response.text
    assert response.json()["total"] == 0
