
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RecommendationEvidence(BaseModel):
    """Подтверждение рекомендации фрагментом документа."""

    model_config = ConfigDict(extra="forbid", strict=True)

    source: int = Field(ge=1)
    quote: str = Field(min_length=1)


class RecommendationPayload(BaseModel):
    """Структурированный ответ GigaChat."""

    model_config = ConfigDict(extra="forbid", strict=True)

    doctor: str
    urgency: Literal[
        "emergency",
        "urgent_24h",
        "planned",
        "self_care"
    ]
    place: str
    recommendation: str
    reason: str
    evidence: list[RecommendationEvidence]


# JSON Schema для структурированного вывода GigaChat.
RECOMMENDATION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "doctor": {
            "type": "string"
        },
        "urgency": {
            "type": "string",
            "enum": [
                "emergency",
                "urgent_24h",
                "planned",
                "self_care"
            ]
        },
        "place": {
            "type": "string"
        },
        "recommendation": {
            "type": "string"
        },
        "reason": {
            "type": "string"
        },
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "integer"
                    },
                    "quote": {
                        "type": "string"
                    }
                },
                "required": [
                    "source",
                    "quote"
                ],
                "additionalProperties": False
            }
        }
    },
    "required": [
        "doctor",
        "urgency",
        "place",
        "recommendation",
        "reason",
        "evidence"
    ],
    "additionalProperties": False
}
