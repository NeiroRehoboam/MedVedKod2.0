
from pydantic import BaseModel, ConfigDict, Field


class AnswerEvidence(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    source: int = Field(ge=1)
    quote: str = Field(min_length=1)


class AnswerClaim(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    text: str = Field(min_length=1)
    evidence: list[AnswerEvidence] = Field(min_length=1)


class AnswerPayload(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    claims: list[AnswerClaim]
    insufficient_information: str


ANSWER_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string"
                    },
                    "evidence": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source": {
                                    "type": "integer",
                                    "minimum": 1
                                },
                                "quote": {
                                    "type": "string"
                                }
                            },
                            "required": ["source", "quote"],
                            "additionalProperties": False
                        },
                        "minItems": 1
                    }
                },
                "required": ["text", "evidence"],
                "additionalProperties": False
            }
        },
        "insufficient_information": {
            "type": "string"
        }
    },
    "required": ["claims", "insufficient_information"],
    "additionalProperties": False
}
