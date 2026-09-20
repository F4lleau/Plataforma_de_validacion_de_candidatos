from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.affiliate_import_batch import AffiliateImportBatch
from app.models.party_member import PartyMember


class PartyMemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_create(self, members: list[PartyMember]) -> None:
        self.db.add_all(members)
        self.db.commit()

    def normalize_dni(self, dni: str) -> str:
        if dni is None:
            return ""
        return "".join(ch for ch in str(dni).strip() if ch.isdigit())

    def get_by_dni(self, dni: str) -> PartyMember | None:
        normalized = self.normalize_dni(dni)
        if not normalized:
            return None

        stmt = (
            select(PartyMember)
            .join(AffiliateImportBatch, PartyMember.source_batch_id == AffiliateImportBatch.id)
            .where(
                PartyMember.dni == normalized,
                PartyMember.is_active.is_(True),
                AffiliateImportBatch.is_current.is_(True),
                AffiliateImportBatch.status == "completed",
            )
            .order_by(PartyMember.created_at.desc())
        )
        return self.db.scalar(stmt)

    def get_current_by_dni(self, dni: str) -> PartyMember | None:
        return self.get_by_dni(dni)

    def delete_by_batch(self, batch_id: int) -> None:
        stmt = delete(PartyMember).where(PartyMember.source_batch_id == batch_id)
        self.db.execute(stmt)
        self.db.commit()

    def count_for_batch(self, batch_id: int) -> int:
        stmt = select(PartyMember).where(PartyMember.source_batch_id == batch_id)
        return self.db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()