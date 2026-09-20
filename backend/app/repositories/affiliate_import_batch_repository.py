from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.affiliate_import_batch import AffiliateImportBatch


class AffiliateImportBatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, batch: AffiliateImportBatch) -> AffiliateImportBatch:
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def update(self, batch: AffiliateImportBatch) -> AffiliateImportBatch:
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def get_current_batch(self) -> AffiliateImportBatch | None:
        stmt = select(AffiliateImportBatch).where(AffiliateImportBatch.is_current.is_(True)).order_by(AffiliateImportBatch.id.desc())
        return self.db.scalar(stmt)

    def activate_batch(self, batch_id: int) -> AffiliateImportBatch | None:
        batch = self.db.get(AffiliateImportBatch, batch_id)
        if batch is None:
            return None

        if batch.status != "completed":
            return self.get_current_batch()

        current = self.get_current_batch()
        if current is not None and current.id != batch.id:
            current.is_current = False

        batch.is_current = True
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def mark_batch_complete(self, batch_id: int) -> AffiliateImportBatch | None:
        batch = self.db.get(AffiliateImportBatch, batch_id)
        if batch is None:
            return None

        batch.status = "completed"
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch