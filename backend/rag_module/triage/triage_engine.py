
from rag_module.triage.models import TriageResult
from rag_module.triage.symptom_validator import (
    SymptomValidationResult,
)


def evaluate_symptoms(
    validation: SymptomValidationResult,
) -> TriageResult:
    """
    Проверяет качество извлечения симптомов.

    Не является полноценной клинической оценкой.
    Отсутствие обнаруженных опасных признаков
    не означает отсутствие медицинского риска.
    """

    if not validation.is_valid:
        return TriageResult(
            status="needs_assessment",
            should_stop=True,
            message=(
                "Не удалось надёжно проверить извлечённые "
                "симптомы. Требуется дополнительная оценка."
            ),
        )

    if validation.requires_review:
        return TriageResult(
            status="needs_assessment",
            should_stop=True,
            message=(
                "В извлечённых симптомах обнаружена "
                "неопределённость. Требуется дополнительная оценка."
            ),
        )

    return TriageResult(
        status="needs_assessment",
        should_stop=False,
        message=(
            "Извлечение симптомов прошло техническую проверку. "
            "Полноценная клиническая оценка не выполнена. "
            "Результат не подтверждает отсутствие медицинского риска."
        ),
    )
