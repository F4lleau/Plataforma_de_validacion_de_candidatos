from datetime import datetime
from pydantic import BaseModel


class AffiliateImportResponse(BaseModel):
    batch_id: int
    file_name: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    status: str
    imported_at: datetime


class PartyMemberResponse(BaseModel):
    id: int
    dni: str
    affiliate_number: str | None
    first_name: str
    last_name: str
    full_name: str
    normalized_name: str
    gender: str | None
    section: str | None
    circuit: str | None
    affiliation_status: str
    is_active: bool

    model_config = {"from_attributes": True}