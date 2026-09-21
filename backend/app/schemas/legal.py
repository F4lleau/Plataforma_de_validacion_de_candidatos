from datetime import date
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator


class LegalDocument(BaseModel):
    id: str
    title: str
    version: str
    published_on: date
    notice: str
    paragraphs: list[str]
    sha256: str


class LegalDocuments(BaseModel):
    terms: LegalDocument
    privacy: LegalDocument


class TermsAcceptanceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    accepted: StrictBool
    version: str = Field(min_length=1, max_length=64)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")

    @field_validator("accepted")
    @classmethod
    def explicit_acceptance(cls, value):
        if not value:
            raise ValueError("Confirmá la aceptación de los términos para continuar.")
        return value
