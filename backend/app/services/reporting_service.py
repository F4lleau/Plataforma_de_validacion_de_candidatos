from app.services.audit_service import safe_details
from fastapi import HTTPException
from app.models import Election, Office, Municipality, User, AuditLog
from app.services.management_service import ManagementService
from app.repositories.reporting_repository import ReportingRepository
from app.utils.enums import UserRole


class ReportingService(ManagementService):
    def __init__(self, db):
        super().__init__(db)
        self.reporting = ReportingRepository(db)

    def check_filters(self, user, filters):
        for field, model in [
            ("election_id", Election),
            ("office_id", Office),
            ("municipality_id", Municipality),
            ("apoderado_id", User),
        ]:
            value = getattr(filters, field)
            if value:
                self.require(model, value)
        if (
            user.role != UserRole.ADMIN
            and filters.apoderado_id
            and filters.apoderado_id != user.id
        ):
            raise HTTPException(403, "No puede consultar métricas de otro apoderado.")

    def page(self, user, filters, page, page_size):
        self.check_filters(user, filters)
        items, total = self.reporting.list_page(user, filters, page, page_size)
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def summary(self, user, filters):
        self.check_filters(user, filters)
        return {
            **self.reporting.summary(user, filters),
            "filters": filters.model_dump(mode="json"),
        }

    def dashboard(self, user, filters):
        result = self.summary(user, filters)
        result["recent_lists"] = self.reporting.list_page(user, filters, 1, 6)[0]
        result["modules"] = (
            self.reporting.modules(user.id) if user.role == UserRole.APODERADO else []
        )
        if filters.election_id:
            result["modules"] = [
                m for m in result["modules"] if m["election_id"] == filters.election_id
            ]
        return result

    def review(self, page, page_size):
        items, total = self.reporting.review_page(page, page_size)
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def audit_page(self, filters, page, page_size):
        if (
            filters.date_from
            and filters.date_to
            and filters.date_from > filters.date_to
        ):
            raise HTTPException(422, "Rango de fechas inválido.")
        items, total = self.reporting.audit_page(filters, page, page_size)
        for item in items:
            item["details"] = safe_details(item["details"])
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def audit_detail(self, identity):
        event = self.require(AuditLog, identity)
        return {
            "id": event.id,
            "actor_id": event.user_id,
            "action": event.action,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "details": safe_details(event.details_json),
            "created_at": event.created_at,
        }
