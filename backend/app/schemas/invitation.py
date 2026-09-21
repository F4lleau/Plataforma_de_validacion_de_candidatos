from pydantic import Field, EmailStr, field_validator
from app.schemas.auth import AuthInput
from app.schemas.management import ModuleInput


class InvitationInput(AuthInput):
    email: EmailStr
    modules: list[ModuleInput] = Field(default_factory=list, max_length=100)

    @field_validator("email", mode="before")
    @classmethod
    def normalize(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class InvitationToken(AuthInput):
    token: str = Field(min_length=20, max_length=128)


class InvitationAccept(InvitationToken):
    full_name: str = Field(min_length=1, max_length=255)
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=15, max_length=128)

    @field_validator("username", "full_name", mode="before")
    @classmethod
    def strip_profile(cls, value):
        return value.strip() if isinstance(value, str) else value
