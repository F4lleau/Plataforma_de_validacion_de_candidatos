class RenaperValidationService:
    def validate(self, dni: str, first_name: str, last_name: str) -> dict:
        return {
            "status": "ok",
            "message": "Validación RENAPER pendiente de implementación real",
            "details": {
                "dni": dni,
                "first_name": first_name,
                "last_name": last_name,
            },
        }