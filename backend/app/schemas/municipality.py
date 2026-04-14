from pydantic import BaseModel


class MunicipalityCreate(BaseModel):
    name: str
    active: bool = True


class MunicipalityResponse(BaseModel):
    id: int
    name: str
    active: bool

    model_config = {"from_attributes": True}