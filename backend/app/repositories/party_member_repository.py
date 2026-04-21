from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.party_member import PartyMember


class PartyMemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_create(self, members: list[PartyMember]) -> None:
        self.db.add_all(members)
        self.db.commit()

    def get_by_dni(self, dni: str) -> PartyMember | None:
        stmt = select(PartyMember).where(
            PartyMember.dni == dni,
            PartyMember.is_active.is_(True),
        )
        return self.db.scalar(stmt)

    def delete_by_batch(self, batch_id: int) -> None:
        stmt = delete(PartyMember).where(PartyMember.source_batch_id == batch_id)
        self.db.execute(stmt)
        self.db.commit()