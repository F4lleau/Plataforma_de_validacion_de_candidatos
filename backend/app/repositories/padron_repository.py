from sqlalchemy import select, func, update, text
from app.models import PartyMember, AffiliateImportBatch


class PadronRepository:
    def __init__(self, db):
        self.db = db

    def lock_import(self):
        if self.db.bind.dialect.name == "postgresql":
            self.db.execute(
                text("SELECT pg_advisory_xact_lock(hashtext('padron_import'))")
            )

    def activate(self, batch):
        self.db.execute(
            update(AffiliateImportBatch)
            .where(AffiliateImportBatch.is_current.is_(True))
            .values(is_current=False)
        )
        self.db.flush()
        batch.is_current = True
        self.db.flush()

    def query(self, search="", section="", circuit="", state="", page=1, page_size=25):
        base = (
            select(PartyMember)
            .join(AffiliateImportBatch)
            .where(AffiliateImportBatch.is_current.is_(True))
        )
        if search:
            base = base.where(
                (PartyMember.normalized_name.contains(search, autoescape=True))
                | PartyMember.dni.contains(search, autoescape=True)
            )
        for field, value in [
            (PartyMember.section, section),
            (PartyMember.circuit, circuit),
            (PartyMember.affiliation_status, state),
        ]:
            if value:
                base = base.where(func.upper(field) == value.upper())
        total = self.db.scalar(select(func.count()).select_from(base.subquery()))
        rows = list(
            self.db.scalars(
                base.order_by(PartyMember.last_name, PartyMember.id)
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
        )
        current = self.db.scalar(
            select(AffiliateImportBatch).where(
                AffiliateImportBatch.is_current.is_(True)
            )
        )
        sections = (
            self.db.scalar(
                select(func.count(func.distinct(PartyMember.section))).where(
                    PartyMember.source_batch_id == current.id
                )
            )
            if current
            else 0
        )
        return {
            "items": rows,
            "total": total,
            "page": page,
            "page_size": page_size,
            "current_batch": current,
            "sections": sections,
            "total_members": current.valid_rows if current else 0,
        }

    def batches(self):
        return list(
            self.db.scalars(
                select(AffiliateImportBatch)
                .order_by(AffiliateImportBatch.id.desc())
                .limit(100)
            ).all()
        )
