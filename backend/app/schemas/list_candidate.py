from pydantic import BaseModel


class ListCandidateCreate(BaseModel):
    candidate_id: int
    role_definition_id: int | None = None
    cargo_label: str
    cargo_group: str
    position_number: int
    gender: str


class ListCandidateResponse(BaseModel):
    id: int
    list_id: int
    candidate_id: int
    role_definition_id: int | None
    cargo_label: str
    cargo_group: str
    position_number: int
    gender: str
    is_validated: bool
    validation_summary: str | None

    model_config = {"from_attributes": True}