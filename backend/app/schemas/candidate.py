from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.utils.enums import CandidateStatus


class PersonCreate(BaseModel):
    dni: str
    first_name: str
    last_name: str
    birth_date: date
    gender: str
    address: str | None = None
    municipality_id: int | None = None


class CandidateCreate(BaseModel):
    person: PersonCreate
    office_id: int
    election_id: int


class CandidateResponse(BaseModel):
    id: int
    person_id: int
    office_id: int
    election_id: int
    candidate_status: CandidateStatus
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AffiliationValidationResponse(BaseModel):
    status: Literal["verified", "warning"]
    code: str | None = None
    message: str
    requires_admin_review: bool
    details: dict[str, Any] = Field(default_factory=dict)


class CandidateCreateResponse(BaseModel):
    candidate: CandidateResponse
    affiliation: AffiliationValidationResponse