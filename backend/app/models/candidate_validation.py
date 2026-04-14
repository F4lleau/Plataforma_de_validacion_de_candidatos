from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.utils.enums import ValidationType, ValidationResult


class CandidateValidation(Base):
    __tablename__ = "candidate_validations"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    validation_type: Mapped[ValidationType] = mapped_column(Enum(ValidationType), nullable=False)
    status: Mapped[ValidationResult] = mapped_column(Enum(ValidationResult), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    response_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    validated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)