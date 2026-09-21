from datetime import datetime, timezone
from app.models import ElectoralList, Election, ElectionRule, ListValidation
from app.repositories.reporting_repository import ReportingRepository
from app.repositories.padron_repository import PadronRepository
from app.services.electoral_workflow_service import ElectoralWorkflowService
from app.services.composition_service import CompositionService
from app.services.access_service import AccessService
from app.services.transaction import atomic_mutation
from app.utils.enums import ListStatus, ValidationType, ValidationResult


class SubmissionService(ElectoralWorkflowService):
    def snapshot(self, row, result, user):
        snapshot = self.repo.add(
            ListValidation(
                list_id=row.id,
                validation_type=ValidationType.COMPOSICION_LISTA,
                status=ValidationResult(result["status"]),
                message=result["message"][:255],
                response_json=result,
            )
        )
        self.audit.record(
            user.id,
            "list.composition_evaluated",
            "electoral_lists",
            row.id,
            {
                "evaluation_id": snapshot.id,
                "rule_version_id": row.rule_version_id,
                "can_submit": result["can_submit"],
                "issues": [i["code"] for i in result["issues"]],
            },
        )
        return snapshot

    @atomic_mutation
    def evaluate(self, list_id, user):
        row = self.get_list(list_id, user, True)
        result = CompositionService(self.db).evaluate(row)
        snapshot = self.snapshot(row, result, user)
        row.status = (
            ListStatus.BORRADOR
            if result["can_submit"]
            else ListStatus.INCOMPLETA
            if any(
                i["code"] in ("COUNT", "MISSING", "NO_TEMPLATE")
                for i in result["issues"]
            )
            else ListStatus.RECHAZADA_COMPOSICION
        )
        self.commit()
        return {
            "state": row.status,
            "evaluation_id": snapshot.id,
            "composition": result,
        }

    @staticmethod
    def approval_blockers(rule, rows, output):
        blockers = []
        if not rule or rule.rules.get("template_is_test", True):
            blockers.append("Plantilla institucional pendiente.")
        if rule and not rule.rules.get("other_requirements_confirmed", False):
            blockers.append("Otros requisitos no confirmados.")
        required = [ValidationType.REQUISITOS_CARGO]
        if not rule or rule.rules.get("requires_affiliation", True):
            required.append(ValidationType.AFILIACION)
        if not rule or rule.rules.get("requires_renaper", True):
            required.append(ValidationType.RENAPER)
        for member, candidate, person in rows:
            validations = output[candidate.id]
            for kind in required:
                val = next((v for v in validations if v.validation_type == kind), None)
                evidence = (val.response_json or {}) if val else {}
                if (
                    not val
                    or val.status != ValidationResult.OK
                    or val.candidate_revision != candidate.revision
                ):
                    blockers.append(
                        f"Posición {member.position_number}: {kind.value} pendiente u observada."
                    )
                elif kind == ValidationType.RENAPER and (
                    evidence.get("origin") != "authorized_provider"
                    or evidence.get("approvable") is not True
                ):
                    blockers.append(
                        f"Posición {member.position_number}: identidad sin verificación real."
                    )
        return blockers

    @atomic_mutation
    def submit(self, list_id, user):
        row = self.require(ElectoralList, list_id, True)
        AccessService(self.db).require_list(user, list_id)
        if row.status in (ListStatus.ENVIADA_ADMIN, ListStatus.APROBADA_SISTEMA):
            evaluations = ReportingRepository(self.db).list_evaluations(row.id, 1)
            previous = evaluations[0].response_json if evaluations else {}
            return {
                "submitted": True,
                "already_submitted": True,
                "state": row.status,
                "submitted_at": row.submitted_at,
                "approval_blockers": previous.get("approval_blockers", []),
            }
        self.require(Election, row.election_id, True)
        row = self.get_list(list_id, user, True)
        # Same lock used by imports ensures every candidate sees the same register batch.
        PadronRepository(self.db).lock_import()
        result = CompositionService(self.db).evaluate(row)
        snapshot = self.snapshot(row, result, user)
        if not result["can_submit"]:
            row.status = (
                ListStatus.INCOMPLETA
                if any(
                    i["code"] in ("COUNT", "MISSING", "NO_TEMPLATE")
                    for i in result["issues"]
                )
                else ListStatus.RECHAZADA_COMPOSICION
            )
            self.commit()
            return {
                "submitted": False,
                "already_submitted": False,
                "state": row.status,
                "composition": result,
                "approval_blockers": [],
            }
        entries = ReportingRepository(self.db).members(row.id)
        row.status = ListStatus.EN_VALIDACION
        output = {}
        for member, candidate, person in entries:
            self.validate_candidate(candidate, person, row, actor_id=user.id)
            output[candidate.id] = self.repo.validations(candidate)
        rule = self.repo.get(ElectionRule, row.rule_version_id)
        blockers = self.approval_blockers(rule, entries, output)
        row.status = ListStatus.ENVIADA_ADMIN
        row.submitted_at = datetime.now(timezone.utc).replace(tzinfo=None)
        event = self.audit.record(
            user.id,
            "list.submitted",
            "electoral_lists",
            row.id,
            {
                "evaluation_id": snapshot.id,
                "rule_version_id": rule.id,
                "candidate_revisions": {str(c.id): c.revision for m, c, p in entries},
                "approval_blockers": blockers,
            },
        )
        if not blockers and result["status"] == "ok":
            row.status = ListStatus.APROBADA_SISTEMA
            self.audit.record(
                None,
                "list.automatically_approved",
                "electoral_lists",
                row.id,
                {
                    "submission_event_id": event.id,
                    "evaluation_id": snapshot.id,
                    "triggered_by": user.id,
                },
            )
        snapshot.response_json = {
            **result,
            "approval_evaluated": True,
            "approval_blockers": blockers,
            "resulting_state": row.status.value,
            "candidate_validations": {
                str(cid): [
                    {
                        "id": v.id,
                        "revision": v.candidate_revision,
                        "type": v.validation_type.value,
                        "status": v.status.value,
                        "evidence": v.response_json,
                    }
                    for v in vals
                ]
                for cid, vals in output.items()
            },
        }
        self.commit()
        return {
            "submitted": True,
            "already_submitted": False,
            "state": row.status,
            "submitted_at": row.submitted_at,
            "composition": result,
            "approval_blockers": blockers,
        }
