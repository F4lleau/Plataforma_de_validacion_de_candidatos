from datetime import date, datetime
from pydantic import BaseModel, Field
from app.utils.enums import ListStatus


class ListFilters(BaseModel):
    election_id: int | None = Field(None, gt=0)
    office_id: int | None = Field(None, gt=0)
    municipality_id: int | None = Field(None, gt=0)
    apoderado_id: int | None = Field(None, gt=0)
    status: ListStatus | None = None
    search: str = Field("", max_length=255)


class AuditFilters(BaseModel):
    actor_id: int | None = Field(None, gt=0)
    action: str = Field("", max_length=100)
    entity_type: str = Field("", max_length=100)
    entity_id: int | None = Field(None, gt=0)
    list_id: int | None = Field(None, gt=0)
    date_from: date | None = None
    date_to: date | None = None


class AuditEvent(BaseModel):
    id: int
    actor_id: int | None
    actor_name: str | None = None
    action: str
    entity_type: str
    entity_id: int | None
    details: dict | None
    created_at: datetime


class AuditPage(BaseModel):
    items: list[AuditEvent]
    total: int
    page: int
    page_size: int
