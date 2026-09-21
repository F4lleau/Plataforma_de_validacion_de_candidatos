import re


# Defense in depth: producers still select minimal, non-sensitive fields explicitly.
def safe_details(value):
    if isinstance(value, dict):
        return {
            k: safe_details(v)
            for k, v in value.items()
            if not any(
                term in k.lower()
                for term in (
                    "password",
                    "secret",
                    "token",
                    "authorization",
                    "credential",
                    "database_url",
                    "raw_payload",
                    "identity_payload",
                )
            )
        }
    if isinstance(value, list):
        return [safe_details(v) for v in value]
    if isinstance(value, str):
        value = re.sub(
            r"(?i)\b[a-z][a-z0-9+.-]*://[^\s/@]+:[^\s/@]+@[^\s]+",
            "[URL protegida]",
            value,
        )
        return re.sub(r"(?i)Bearer\s+\S+", "[token protegido]", value)
    return value


from app.models import AuditLog
from app.repositories.management_repository import ManagementRepository


class AuditService:
    def __init__(self, db):
        self.repository = ManagementRepository(db)

    def record(self, actor, action, entity, identity, details=None):
        # Callers supply an allowlist of non-sensitive fields, never passwords/payloads.
        return self.repository.add(
            AuditLog(
                user_id=actor,
                action=action,
                entity_type=entity,
                entity_id=identity,
                details_json=safe_details(details),
            )
        )
