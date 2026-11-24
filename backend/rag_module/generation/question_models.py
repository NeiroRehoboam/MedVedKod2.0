from pydantic import BaseModel, ConfigDict, Field


class NextQuestion(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    question: str = Field(min_length=5)
    options: list[str] = Field(
        default_factory=list,
        max_length=5,
    )


NEXT_QUESTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {
            "type": "string",
            "minLength": 5,
        },
        "options": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "maxItems": 5,
        },
    },
    "required": [
        "question",
        "options",
    ],
    "additionalProperties": False,
}
