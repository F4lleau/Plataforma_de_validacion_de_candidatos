from pydantic import BaseModel


class OfficeCreate(BaseModel):
    code: str
    name: str
    scope_type: str
    municipality_based: bool = False
    required_positions: int
    requires_parity: bool = False
    requires_alternation: bool = False
    active: bool = True


class OfficeResponse(BaseModel):
    id: int
    code: str
    name: str
    scope_type: str
    municipality_based: bool
    required_positions: int
    requires_parity: bool
    requires_alternation: bool
    active: bool

    model_config = {"from_attributes": True}