
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from rag_module.triage.symptom_models import (
    SymptomExtraction,
)


class SymptomValidationResult(BaseModel):
    """Результат проверки извлечённых симптомов."""

    model_config = ConfigDict(extra="forbid", strict=True)

    is_valid: bool
    requires_review: bool

    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    extraction: SymptomExtraction | None = None


def normalize_symptom_name(name: str) -> str:
    """
    Нормализует название симптома для сравнения.

    Не меняет исходное название в результате.
    """

    normalized = name.casefold().strip()
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized


def validate_symptom_extraction(
    data: Any,
) -> SymptomValidationResult:
    """
    Проверяет результат извлечения симптомов.

    Проверяет:
    - соответствие Pydantic-модели;
    - пустые названия симптомов;
    - дублирующиеся записи;
    - противоречащие друг другу статусы;
    - согласованность uncertainty и unclear.

    Не определяет медицинскую безопасность.
    """

    errors: list[str] = []
    warnings: list[str] = []

    # 1. Проверяем структуру данных.

    try:
        extraction = SymptomExtraction.model_validate(data)

    except ValidationError as error:
        return SymptomValidationResult(
            is_valid=False,
            requires_review=True,
            errors=[
                f"Некорректная структура результата: {error}"
            ],
        )

    # 2. Проверяем названия и повторяющиеся симптомы.

    seen: dict[tuple[str, str, str], str] = {}

    for symptom in extraction.symptoms:

        name = normalize_symptom_name(symptom.name)

        if not name:
            errors.append(
                "Обнаружен симптом с пустым названием."
            )
            continue

        key = (
            name,
            symptom.time,
            symptom.subject,
        )

        previous_status = seen.get(key)

        if previous_status is None:
            seen[key] = symptom.status
            continue

        # 3. Проверяем противоречия.

        if previous_status != symptom.status:
            errors.append(
                "Обнаружены противоречащие записи "
                f"для симптома '{symptom.name}': "
                f"статусы '{previous_status}' "
                f"и '{symptom.status}' "
                f"при одинаковом времени и субъекте."
            )

        else:
            warnings.append(
                "Обнаружена повторяющаяся запись "
                f"для симптома '{symptom.name}'."
            )

    # 4. Проверяем неопределённость.

    has_unclear_symptoms = any(
        symptom.status == "unclear"
        for symptom in extraction.symptoms
    )

    if has_unclear_symptoms and not extraction.uncertainty:
        errors.append(
            "Есть симптомы со статусом unclear, "
            "но uncertainty=False."
        )

    # 5. Формируем результат.

    is_valid = not errors

    requires_review = (
        not is_valid
        or bool(warnings)
        or extraction.uncertainty
    )

    return SymptomValidationResult(
        is_valid=is_valid,
        requires_review=requires_review,
        errors=errors,
        warnings=warnings,
        extraction=extraction,
    )
