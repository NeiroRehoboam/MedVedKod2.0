from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TriageStatus = Literal[
    "emergency",
    "urgent",
    "needs_assessment",
    "no_red_flags_detected",
]


class TriageResult(BaseModel):
    """Результат предварительной проверки опасных симптомов."""

    model_config = ConfigDict(extra="forbid", strict=True)

    status: TriageStatus

    should_stop: bool

    message: str = Field(min_length=1)

    matched_rules: list[str] = Field(default_factory=list)

    emergency_number: str | None = None