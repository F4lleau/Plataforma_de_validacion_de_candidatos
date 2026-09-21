from app.models import Election, AffiliateImportBatch
from app.services.electoral_workflow_service import ElectoralWorkflowService
from app.services.composition_service import CompositionService
from app.repositories.reporting_repository import ReportingRepository


class InspectionService(ElectoralWorkflowService):
    def detail(self, list_id, user):
        row = self.get_list(list_id, user)
        reporting = ReportingRepository(self.db)
        entries = reporting.members(list_id)
        history = reporting.validation_history([c.id for m, c, p in entries])
        grouped = {}
        for v in history:
            grouped.setdefault(v.candidate_id, []).append(v)
        election = self.require(Election, row.election_id)
        batches = self.repo.all(AffiliateImportBatch, is_current=True)
        batch_id = batches[0].id if batches else None
        candidates = []
        for member, candidate, person in entries:
            data = self.candidate_output(
                candidate,
                member,
                row,
                person=person,
                validations=[
                    v
                    for v in grouped.get(candidate.id, [])
                    if v.candidate_revision == candidate.revision
                ],
                election=election,
                batch_id=batch_id,
                context_loaded=True,
            )
            data["history"] = [
                {
                    "id": v.id,
                    "type": v.validation_type,
                    "status": v.status,
                    "message": v.message,
                    "revision": v.candidate_revision,
                    "validated_at": v.validated_at,
                    "current_revision": v.candidate_revision == candidate.revision,
                }
                for v in grouped.get(candidate.id, [])
            ]
            candidates.append(data)
        result = reporting.decorate([row])[0]
        result["assigned_user_ids"] = [a["id"] for a in result["apoderados"]]
        from app.models import ElectionRule

        result["rule"] = (
            self.repo.get(ElectionRule, row.rule_version_id)
            if row.rule_version_id
            else None
        )
        result["candidates"] = candidates
        result["composition"] = CompositionService(self.db).evaluate(row)
        result["evaluations"] = reporting.list_evaluations(list_id)
        return result
