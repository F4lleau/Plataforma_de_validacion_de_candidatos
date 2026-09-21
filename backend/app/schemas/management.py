from datetime import date, datetime
from typing import Literal
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    EmailStr,
    field_validator,
    model_validator,
)


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ElectionInput(Input):
    name: str = Field(min_length=1, max_length=255)
    election_type: str = Field(min_length=1, max_length=100)
    election_date: date
    active: bool = True
    loading_opens: date | None = None
    loading_closes: date | None = None

    @model_validator(mode="after")
    def dates(self):
        if bool(self.loading_opens) != bool(self.loading_closes):
            raise ValueError("Indique apertura y cierre juntos.")
        if (
            self.loading_opens
            and not self.loading_opens <= self.loading_closes <= self.election_date
        ):
            raise ValueError("Se requiere apertura <= cierre <= elección.")
        return self


class OfficeInput(Input):
    code: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    name: str = Field(min_length=1, max_length=150)
    scope_type: str = Field(min_length=1, max_length=50)
    municipality_based: bool = False
    required_positions: int = Field(ge=1, le=200)
    requires_parity: bool = True
    requires_alternation: bool = False
    active: bool = True


class MunicipalityInput(Input):
    name: str = Field(min_length=1, max_length=150)
    active: bool = True


class Position(Input):
    name: str = Field(min_length=1, max_length=150)
    group: str = Field(min_length=1, max_length=100)
    position: int = Field(ge=1, le=200)


class RulesInput(Input):
    enabled: bool = True
    minimum_age: int = Field(ge=18, le=100)
    age_reference: Literal["election_date", "loading_closes", "unconfirmed"] = (
        "unconfirmed"
    )
    required_positions: int = Field(ge=1, le=200)
    requires_parity: bool = True
    requires_alternation: bool = False
    requires_affiliation: bool = True
    requires_renaper: bool = True
    other_requirements_confirmed: bool = False
    template_is_test: bool = True
    positions: list[Position] = Field(default_factory=list, max_length=200)

    @model_validator(mode="after")
    def positions_match(self):
        if self.requires_parity and self.required_positions % 2:
            raise ValueError("La paridad 50/50 requiere cantidad par.")
        if self.positions and sorted(p.position for p in self.positions) != list(
            range(1, self.required_positions + 1)
        ):
            raise ValueError(
                "La plantilla debe cubrir todas las posiciones sin duplicados."
            )
        return self


class ModuleInput(Input):
    election_id: int = Field(gt=0)
    office_id: int = Field(gt=0)
    municipality_id: int | None = Field(default=None, gt=0)
    enabled: bool = True


class ApoderadoInput(Input):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str | None = Field(default=None, min_length=15, max_length=128)
    is_active: bool = True
    modules: list[ModuleInput] = Field(default_factory=list, max_length=100)

    @field_validator("username", "email")
    @classmethod
    def normalize(cls, value):
        return value.strip().lower()


class ListInput(Input):
    election_id: int = Field(gt=0)
    office_id: int = Field(gt=0)
    municipality_id: int | None = Field(default=None, gt=0)
    list_name: str = Field(min_length=1, max_length=255)
    list_number: str = Field(min_length=1, max_length=40)


class ListEdit(Input):
    list_name: str = Field(min_length=1, max_length=255)
    list_number: str = Field(min_length=1, max_length=40)


class AssignmentsInput(Input):
    user_ids: list[int] = Field(max_length=100)


class CandidateInput(Input):
    dni: str = Field(pattern=r"^\d{7,9}$")
    first_name: str = Field(min_length=1, max_length=150)
    last_name: str = Field(min_length=1, max_length=150)
    birth_date: date
    gender: Literal["F", "M", "X"]
    address: str | None = Field(default=None, max_length=255)
    municipality_id: int | None = Field(default=None, gt=0)
    position: int = Field(ge=1, le=200)
    action: Literal["draft", "validate"] = "draft"

    @field_validator("birth_date")
    @classmethod
    def past(cls, value):
        if value > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura.")
        return value


class ElectionOutput(ElectionInput):
    model_config = ConfigDict(from_attributes=True)
    id: int


class OfficeOutput(OfficeInput):
    model_config = ConfigDict(from_attributes=True)
    id: int


class MunicipalityOutput(MunicipalityInput):
    model_config = ConfigDict(from_attributes=True)
    id: int


class RuleOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    election_id: int
    office_id: int
    version: int
    enabled: bool
    rules: RulesInput


class ModuleOutput(ModuleInput):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ApoderadoOutput(BaseModel):
    email_verified_at: datetime | None = None
    id: int
    username: str
    email: str
    full_name: str
    role: Literal["apoderado"]
    is_active: bool
    modules: list[ModuleOutput]
