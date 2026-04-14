from datetime import datetime
from pydantic import BaseModel

from app.utils.enums import ValidationType, ValidationResult


class ValidationResponse(BaseModel):
    id: int
    validation_type: ValidationType
    status: ValidationResult
    message: str
    response_json: dict | None
    validated_at: datetime

    model_config = {"from_attributes": True}