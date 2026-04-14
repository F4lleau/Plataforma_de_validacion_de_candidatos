class OfficeValidationService:
    def validate(self, office_id: int, birth_date) -> dict:
        return {
            "status": "ok",
            "message": "Validación de requisitos del cargo pendiente de implementación real",
            "details": {
                "office_id": office_id,
                "birth_date": str(birth_date),
            },
        }