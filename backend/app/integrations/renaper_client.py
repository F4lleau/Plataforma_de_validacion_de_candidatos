class RenaperClient:
    def get_person_by_dni(self, dni: str) -> dict:
        return {
            "success": False,
            "message": "Cliente RENAPER no implementado todavía",
            "data": {"dni": dni},
        }