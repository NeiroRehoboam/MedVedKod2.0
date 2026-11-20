from pydantic import BaseModel, ConfigDict, Field


class NextQuestion(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    question: str = Field(min_length=1)


NEXT_QUESTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {
            "type": "string"
        }
    },
    "required": ["question"],
    "additionalProperties": False
}