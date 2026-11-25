
from rag_module.triage.models import TriageResult
from rag_module.triage.safety_models import SafetyCheckResult


def convert_safety_result(
    result: SafetyCheckResult,
) -> TriageResult:
    """
    Преобразует результат проверки безопасности
    в формат, совместимый с существующим Triage API.

    Важно:
    no_critical_signs_detected не означает,
    что клиническая оценка завершена.
    """

    if not isinstance(result, SafetyCheckResult):
        raise TypeError(
            "Ожидается объект SafetyCheckResult."
        )

    if result.danger_status == "dangerous":
        return TriageResult(
            status="emergency",
            should_stop=True,
            message=(
                f"Причина остановки опроса: {result.reason}\n\n"
                f"Обнаруженные признаки: {', '.join(result.matched_signs)}\n\n"
                f"{result.recommended_action}"
            ),
            matched_rules=list(result.matched_signs),
            emergency_number="103 или 112",
        )

    if result.danger_status == "uncertain":
        return TriageResult(
            status="needs_assessment",
            should_stop=True,
            message=result.recommended_action,
            matched_rules=list(result.matched_signs),
        )

    return TriageResult(
        status="needs_assessment",
        should_stop=False,
        message=(
            "В данном сообщении критические признаки "
            "не обнаружены. Это не подтверждает отсутствие "
            "риска и не заменяет клиническую оценку."
        ),
        matched_rules=list(result.matched_signs),
    )
