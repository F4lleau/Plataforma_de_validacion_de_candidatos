from pydantic import BaseModel


class ListRoleDefinitionResponse(BaseModel):
    id: int
    office_type: str
    code: str
    name: str
    group_name: str
    position_order: int
    required: bool
    gender_rule: str | None
    is_titular: bool
    is_suplente: bool

    model_config = {"from_attributes": True}