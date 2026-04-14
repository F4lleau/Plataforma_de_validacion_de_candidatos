class AffiliationValidationService:
    def validate(self, dni: str) -> dict:
        return {
            "status": "ok",
            "message": "Validación de afiliación pendiente de implementación real",
            "details": {"dni": dni},
        }