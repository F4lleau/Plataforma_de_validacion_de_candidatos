from collections import Counter

from app.repositories.list_repository import ListRepository
from app.repositories.list_role_definition_repository import ListRoleDefinitionRepository


class ListValidationService:
    def __init__(
        self,
        list_repository: ListRepository,
        role_repository: ListRoleDefinitionRepository,
    ):
        self.list_repository = list_repository
        self.role_repository = role_repository

    def validate(self, list_id: int, office_type: str) -> dict:
        roles = self.role_repository.list_by_office_type(office_type)
        list_candidates = self.list_repository.list_candidates(list_id)

        if not roles:
            return {
                "status": "error",
                "message": "No existe plantilla configurada para este tipo de lista.",
                "details": {"office_type": office_type},
            }

        required_roles = [r for r in roles if r.required]

        if len(list_candidates) < len(required_roles):
            return {
                "status": "error",
                "message": "La lista está incompleta.",
                "details": {
                    "required_positions": len(required_roles),
                    "current_positions": len(list_candidates),
                },
            }

        # Duplicados por DNI/candidate_id
        candidate_ids = [item.candidate_id for item in list_candidates]
        duplicates = [cid for cid, qty in Counter(candidate_ids).items() if qty > 1]
        if duplicates:
            return {
                "status": "error",
                "message": "Hay candidatos repetidos en la lista.",
                "details": {"duplicate_candidate_ids": duplicates},
            }

        # Posiciones duplicadas
        positions = [item.position_number for item in list_candidates]
        duplicated_positions = [pos for pos, qty in Counter(positions).items() if qty > 1]
        if duplicated_positions:
            return {
                "status": "error",
                "message": "Hay posiciones duplicadas en la lista.",
                "details": {"duplicated_positions": duplicated_positions},
            }

        # Cargos requeridos faltantes
        role_ids_in_list = {item.role_definition_id for item in list_candidates if item.role_definition_id}
        missing_roles = [r.name for r in required_roles if r.id not in role_ids_in_list]
        if missing_roles:
            return {
                "status": "error",
                "message": "Faltan cargos obligatorios en la lista.",
                "details": {"missing_roles": missing_roles},
            }

        # Paridad 50/50
        genders = [item.gender.strip().upper() for item in list_candidates]
        male_count = sum(1 for g in genders if g in ("M", "MASCULINO", "VARON", "VARÓN"))
        female_count = sum(1 for g in genders if g in ("F", "FEMENINO", "MUJER"))

        if male_count != female_count:
            return {
                "status": "error",
                "message": "No se cumple la paridad de género 50/50.",
                "details": {
                    "male_count": male_count,
                    "female_count": female_count,
                },
            }

        # Alternancia simple
        normalized = []
        for g in genders:
            if g in ("M", "MASCULINO", "VARON", "VARÓN"):
                normalized.append("M")
            elif g in ("F", "FEMENINO", "MUJER"):
                normalized.append("F")
            else:
                normalized.append("X")

        for i in range(1, len(normalized)):
            if normalized[i] == normalized[i - 1]:
                return {
                    "status": "error",
                    "message": "No se cumple la alternancia de género.",
                    "details": {"position_error": i + 1},
                }

        return {
            "status": "ok",
            "message": "La lista cumple estructura, paridad y alternancia.",
            "details": {
                "required_positions": len(required_roles),
                "current_positions": len(list_candidates),
                "male_count": male_count,
                "female_count": female_count,
            },
        }