
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


DangerStatus = Literal[
    "dangerous",
    "no_critical_signs_detected",
    "uncertain",
]

UrgencyStatus = Literal[
    "emergency",
    "urgent_24h",
    "planned",
    "self_care",
    "undetermined",
]


DANGER_STATUS_LABELS = {
    "dangerous": "Опасно",
    "no_critical_signs_detected": "Критические признаки не выявлены",
    "uncertain": "Требуется уточнение",
}

URGENCY_LABELS = {
    "emergency": "Экстренно",
    "urgent_24h": "Срочно, в течение 24 часов",
    "planned": "Планово",
    "self_care": "Самопомощь",
    "undetermined": "Не определена",
}


class SafetyCheckResult(BaseModel):
    """Результат проверки сообщения пациента на опасность."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    danger_status: DangerStatus
    urgency: UrgencyStatus

    reason: str = Field(min_length=1)

    matched_signs: list[str] = Field(
        default_factory=list
    )

    recommended_action: str = Field(min_length=1)

    should_stop: bool

    @computed_field
    @property
    def status_ru(self) -> str:
        """Русская подпись статуса опасности."""
        return DANGER_STATUS_LABELS[self.danger_status]

    @computed_field
    @property
    def urgency_ru(self) -> str:
        """Русская подпись срочности."""
        return URGENCY_LABELS[self.urgency]

class SafetyCheckLLMResponse(BaseModel):
    """Структурированный ответ GigaChat после проверки сообщения."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    danger_status: DangerStatus

    reason: str = Field(min_length=1)

    matched_signs: list[str] = Field(
        default_factory=list
    )

    recommended_action: str = Field(min_length=1)


SAFETY_CHECK_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "danger_status": {
            "type": "string",
            "enum": [
                "dangerous",
                "no_critical_signs_detected",
                "uncertain",
            ],
        },
        "reason": {
            "type": "string",
        },
        "matched_signs": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "recommended_action": {
            "type": "string",
        },
    },
    "required": [
        "danger_status",
        "reason",
        "matched_signs",
        "recommended_action",
    ],
    "additionalProperties": False,
}