from datetime import datetime
from pydantic import BaseModel

from app.utils.enums import ListStatus


class ElectoralListCreate(BaseModel):
    election_id: int
    office_id: int
    municipality_id: int | None = None
    list_name: str


class ElectoralListResponse(BaseModel):
    id: int
    election_id: int
    office_id: int
    municipality_id: int | None
    list_name: str
    status: ListStatus
    created_by: int
    submitted_at: datetime | None

    model_config = {"from_attributes": True}