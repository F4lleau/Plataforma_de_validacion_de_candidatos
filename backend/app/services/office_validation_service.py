class OfficeValidationService:
    def validate(self, office_id, birth_date):
        return {
            "status": "pendiente",
            "message": "Falta configurar requisitos y fecha de cómputo.",
        }

    def validate_rules(self, rules, birth_date, election):
        if not rules or rules.get("age_reference") == "unconfirmed":
            return {
                "status": "pendiente",
                "message": "Fecha de cómputo de edad pendiente de configuración.",
            }
        reference = (
            election.election_date
            if rules["age_reference"] == "election_date"
            else election.loading_closes
        )
        if reference is None:
            return {"status": "pendiente", "message": "Falta la fecha de referencia."}
        age = (
            reference.year
            - birth_date.year
            - ((reference.month, reference.day) < (birth_date.month, birth_date.day))
        )
        if age < rules["minimum_age"]:
            return {
                "status": "warning",
                "message": f"Edad {age}: el mínimo configurado es {rules['minimum_age']}. Requiere revisión.",
            }
        if not rules.get("other_requirements_confirmed") or rules.get(
            "template_is_test"
        ):
            return {
                "status": "pendiente",
                "message": f"Edad {age} cumple; otros requisitos o plantilla oficial pendientes.",
            }
        return {
            "status": "ok",
            "message": f"Edad {age} cumple los requisitos configurados.",
        }
