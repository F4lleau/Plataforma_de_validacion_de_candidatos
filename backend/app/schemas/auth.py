from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from app.schemas.user import UserResponse


class AuthInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LoginRequest(AuthInput):
    email: EmailStr
    password: str = Field(max_length=1024)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordInput(AuthInput):
    password: str = Field(max_length=1024)


class ForgotInput(AuthInput):
    email: EmailStr


class UnlockRequestInput(AuthInput):
    email: EmailStr
    note: str | None = Field(default=None, max_length=300)

    @field_validator("note", mode="before")
    @classmethod
    def strip_note(cls, value):
        return value.strip() if isinstance(value, str) else value


class ResetInput(AuthInput):
    token: str = Field(min_length=20, max_length=128)
    new_password: str = Field(min_length=15, max_length=128)


class ChangeInput(PasswordInput):
    new_password: str = Field(min_length=15, max_length=128)


class UnlockInput(AuthInput):
    reason: str = Field(min_length=5, max_length=300)

    @field_validator("reason", mode="before")
    @classmethod
    def strip_reason(cls, value):
        return value.strip() if isinstance(value, str) else value
