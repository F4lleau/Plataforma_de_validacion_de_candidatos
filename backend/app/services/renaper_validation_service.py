from dataclasses import asdict
from app.integrations.renaper_client import RenaperClient


class RenaperValidationService:
    def __init__(self, client=None):
        self.client = client or RenaperClient()

    def validate(self, dni, first_name, last_name):
        try:
            result = asdict(self.client.get_person_by_dni(dni))
        except (TimeoutError, ConnectionError):
            return {
                "status": "pendiente",
                "code": "RENAPER_UNAVAILABLE",
                "message": "RENAPER no respondió. Datos conservados; reintente más tarde.",
                "approvable": False,
            }
        if result.get("source") != "authorized_provider":
            result["status"] = "pendiente"
            result["approvable"] = False
        return result
