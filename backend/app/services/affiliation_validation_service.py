from app.repositories.party_member_repository import PartyMemberRepository


class AffiliationValidationService:
    def __init__(self, party_member_repository: PartyMemberRepository):
        self.party_member_repository = party_member_repository

    def validate(self, dni: str) -> dict:
        member = self.party_member_repository.get_by_dni(dni)

        if not member:
            return {
                "status": "error",
                "message": "El candidato no figura en el padrón de afiliados vigente.",
                "details": {"dni": dni},
            }

        return {
            "status": "ok",
            "message": "Afiliación validada correctamente.",
            "details": {
                "dni": member.dni,
                "full_name": member.full_name,
                "affiliate_number": member.affiliate_number,
            },
        }