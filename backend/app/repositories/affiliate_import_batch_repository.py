from sqlalchemy.orm import Session

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