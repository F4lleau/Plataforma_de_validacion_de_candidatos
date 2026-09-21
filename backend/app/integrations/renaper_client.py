from dataclasses import dataclass


@dataclass(frozen=True)
class IdentityResult:
    status: str
    code: str
    message: str
    source: str = "not_configured"
    approvable: bool = False


class RenaperClient:
    """Provider boundary. No fabricated URL or matching algorithm without a contract."""

    def get_person_by_dni(self, dni: str) -> IdentityResult:
        return IdentityResult(
            "pendiente",
            "RENAPER_NOT_CONFIGURED",
            "RENAPER no disponible: falta configurar un proveedor autorizado.",
        )
