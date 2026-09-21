from app.repositories.padron_repository import PadronRepository
from app.services.affiliate_import_service import AffiliateImportService


class PadronService:
    def __init__(self, db):
        self.repo = PadronRepository(db)

    def query(self, search, section, circuit, state, page, page_size):
        return self.repo.query(
            AffiliateImportService.normalize_text(search),
            AffiliateImportService.normalize_text(section),
            AffiliateImportService.normalize_text(circuit),
            AffiliateImportService.normalize_text(state),
            page,
            page_size,
        )

    def batches(self):
        return self.repo.batches()
