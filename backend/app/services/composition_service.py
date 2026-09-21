from collections import Counter
from app.models import ElectionRule
from app.repositories.management_repository import ManagementRepository
from app.repositories.reporting_repository import ReportingRepository


class CompositionService:
    def __init__(self, db):
        self.repo = ManagementRepository(db)
        self.reporting = ReportingRepository(db)

    def evaluate(self, row):
        rule = (
            self.repo.get(ElectionRule, row.rule_version_id)
            if row.rule_version_id
            else None
        )
        entries = self.reporting.members(row.id)
        issues = []
        if not rule or not rule.rules.get("positions"):
            return {
                "status": "pendiente",
                "message": "Falta una plantilla vinculada.",
                "can_submit": False,
                "issues": [
                    {
                        "code": "NO_TEMPLATE",
                        "message": "Configure una plantilla antes de enviar.",
                        "positions": [],
                    }
                ],
                "details": {
                    "current_positions": len(entries),
                    "required_positions": None,
                    "approval_evaluated": False,
                },
            }
        rules = rule.rules
        template = {p["position"]: p for p in rules["positions"]}
        count = rules["required_positions"]

        def issue(code, message, positions=None):
            issues.append(
                {"code": code, "message": message, "positions": positions or []}
            )

        actual = [m.position_number for m, c, p in entries]
        if len(entries) != count:
            issue(
                "COUNT",
                f"Se requieren exactamente {count} posiciones; hay {len(entries)}.",
            )
        missing = sorted(set(template) - set(actual))
        extra = sorted(set(actual) - set(template))
        if missing:
            issue("MISSING", "Faltan posiciones obligatorias.", missing)
        if extra:
            issue("EXTRA", "Hay posiciones fuera de la plantilla.", extra)
        duplicates = [pos for pos, qty in Counter(actual).items() if qty > 1]
        if duplicates:
            issue("DUPLICATE_POSITION", "Hay posiciones repetidas.", duplicates)
        repeated = {
            dni for dni, qty in Counter(p.dni for m, c, p in entries).items() if qty > 1
        }
        if repeated:
            issue(
                "DUPLICATE_DNI",
                "Una persona ocupa más de una posición.",
                [m.position_number for m, c, p in entries if p.dni in repeated],
            )
        for m, c, p in entries:
            expected = template.get(m.position_number)
            if expected and (
                m.cargo_group != expected["group"] or m.cargo_label != expected["name"]
            ):
                issue(
                    "POSITION_ROLE",
                    "El cargo/grupo no corresponde a la plantilla.",
                    [m.position_number],
                )
            if c.election_id != row.election_id or c.office_id != row.office_id:
                issue(
                    "CONTEXT",
                    "La candidatura corresponde a otra elección/cargo.",
                    [m.position_number],
                )
            if m.gender.upper() != p.gender.upper():
                issue(
                    "GENDER_MISMATCH",
                    "La posición no refleja el género vigente de la persona.",
                    [m.position_number],
                )
        genders = [p.gender.upper() for m, c, p in entries]
        unknown = [
            m.position_number
            for m, c, p in entries
            if p.gender.upper() not in ("F", "M")
        ]
        if unknown and (rules["requires_parity"] or rules["requires_alternation"]):
            issue(
                "GENDER_POLICY",
                "Falta definir cómo evaluar estas categorías de género; el registro se conserva.",
                unknown,
            )
        if (
            rules["requires_parity"]
            and not unknown
            and genders.count("M") != genders.count("F")
        ):
            issue("PARITY", "No se cumple la paridad global 50/50 configurada.")
        if rules["requires_alternation"] and not unknown:
            broken = [
                entries[i][0].position_number
                for i in range(1, len(genders))
                if genders[i] == genders[i - 1]
            ]
            if broken:
                issue(
                    "ALTERNATION",
                    "No se cumple la alternancia global configurada.",
                    broken,
                )
        expected_groups = Counter(p["group"] for p in template.values())
        actual_groups = Counter(m.cargo_group for m, c, p in entries)
        if expected_groups != actual_groups:
            issue("GROUPS", "La distribución por grupos no coincide con la plantilla.")
        test = rules.get("template_is_test", True)
        return {
            "status": "warning" if issues else "pendiente" if test else "ok",
            "message": f"{len(issues)} incumplimientos de composición."
            if issues
            else "Composición de prueba completa; puede enviar para revisión."
            if test
            else "Composición completa.",
            "can_submit": not issues,
            "issues": issues,
            "details": {
                "rule_version_id": rule.id,
                "required_positions": count,
                "current_positions": len(entries),
                "female": genders.count("F"),
                "male": genders.count("M"),
                "other": len(unknown),
                "requires_parity": rules["requires_parity"],
                "requires_alternation": rules["requires_alternation"],
                "groups_expected": dict(expected_groups),
                "groups_actual": dict(actual_groups),
                "template_is_test": test,
                "approval_evaluated": False,
                "gender_policy_pending": bool(unknown),
            },
        }
