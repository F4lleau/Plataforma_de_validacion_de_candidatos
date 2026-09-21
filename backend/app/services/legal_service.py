from fastapi import HTTPException
from app.core.security import valid_session
from app.repositories.auth_repository import AuthRepository, now
from app.repositories.legal_repository import LegalDocumentRepository
from app.services.audit_service import AuditService


class LegalService:
    def __init__(self, db):
        self.db = db
        self.repo = AuthRepository(db)

    @staticmethod
    def documents():
        return LegalDocumentRepository().documents()

    def accept(self, user_id, sid, payload):
        # Same lock order as authentication: user -> session. Recheck revocation
        # after locking, including requests already authenticated at the boundary.
        user = self.repo.user(user_id)
        session = self.repo.session(sid, True)
        if (
            not user
            or not user.is_active
            or not valid_session(session)
            or session.user_id != user_id
        ):
            raise HTTPException(401, "Sesión inválida o vencida.")
        if user.terms_accepted_at:
            return (
                user  # Idempotent even if content has changed since first acceptance.
            )
        document = LegalDocumentRepository().documents()["terms"]
        if (
            payload.version != document["version"]
            or payload.sha256 != document["sha256"]
        ):
            raise HTTPException(
                409,
                {
                    "code": "TERMS_DOCUMENT_CHANGED",
                    "message": "Los términos se actualizaron. Revisalos y confirmá nuevamente.",
                },
            )
        try:
            user.terms_accepted_at = now()
            user.terms_version = document["version"]
            user.terms_snapshot = document
            AuditService(self.db).record(
                user.id,
                "legal.terms_accepted",
                "users",
                user.id,
                {
                    "version": document["version"],
                    "sha256": document["sha256"],
                    "accepted_at": user.terms_accepted_at.isoformat() + "Z",
                },
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return user
