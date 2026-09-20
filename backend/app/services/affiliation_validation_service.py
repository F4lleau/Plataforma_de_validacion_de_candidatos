from app.repositories.party_member_repository import PartyMemberRepository


class AffiliationValidationService:
    def __init__(self, party_member_repository: PartyMemberRepository):
        self.party_member_repository = party_member_repository

    def validate(self, dni: str) -> dict:
        normalized_dni = self.party_member_repository.normalize_dni(dni)
        member = self.party_member_repository.get_by_dni(normalized_dni)

        if not member:
            return {
                "status": "warning",
                "code": "AFFILIATION_NOT_FOUND",
                "message": "El candidato no figura en el padrón de afiliados vigente.",
                "requires_admin_review": True,
                "details": {"dni": normalized_dni},
            }

        return {
            "status": "verified",
            "message": "Afiliación validada correctamente.",
            "requires_admin_review": False,
            "details": {
                "dni": member.dni,
                "full_name": member.full_name,
                "affiliate_number": member.affiliate_number,
            },
        }