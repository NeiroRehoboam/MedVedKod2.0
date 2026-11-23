
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SymptomStatus = Literal[
    "present",
    "absent",
    "unclear",
]

SymptomTime = Literal[
    "current",
    "past",
    "future",
    "unknown",
]

SymptomSubject = Literal[
    "user",
    "other",
    "unknown",
]

SymptomSeverity = Literal[
    "mild",
    "moderate",
    "severe",
    "unknown",
]

SymptomFrequency = Literal[
    "constant",
    "intermittent",
    "unknown",
]


class ExtractedSymptom(BaseModel):
    """Информация об одном упомянутом симптоме."""

    model_config = ConfigDict(extra="forbid", strict=True)

    name: str = Field(min_length=1)

    status: SymptomStatus
    time: SymptomTime
    subject: SymptomSubject

    severity: SymptomSeverity = "unknown"
    onset: str | None = None
    frequency: SymptomFrequency = "unknown"
    details: list[str] = Field(default_factory=list)


class SymptomExtraction(BaseModel):
    """Результат извлечения симптомов из ответов пользователя."""

    model_config = ConfigDict(extra="forbid", strict=True)

    symptoms: list[ExtractedSymptom] = Field(default_factory=list)
    uncertainty: bool


SYMPTOM_EXTRACTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "symptoms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "present",
                            "absent",
                            "unclear",
                        ],
                    },
                    "time": {
                        "type": "string",
                        "enum": [
                            "current",
                            "past",
                            "future",
                            "unknown",
                        ],
                    },
                    "subject": {
                        "type": "string",
                        "enum": [
                            "user",
                            "other",
                            "unknown",
                        ],
                    },
                    "severity": {
                        "type": "string",
                        "enum": [
                            "mild",
                            "moderate",
                            "severe",
                            "unknown",
                        ],
                    },
                    "onset": {
                        "type": ["string", "null"],
                    },
                    "frequency": {
                        "type": "string",
                        "enum": [
                            "constant",
                            "intermittent",
                            "unknown",
                        ],
                    },
                    "details": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                    },
                },
                "required": [
                    "name",
                    "status",
                    "time",
                    "subject",
                    "severity",
                    "onset",
                    "frequency",
                    "details",
                ],
                "additionalProperties": False,
            },
        },
        "uncertainty": {
            "type": "boolean"
        },
    },
    "required": [
        "symptoms",
        "uncertainty",
    ],
    "additionalProperties": False,
}
