
from rag_module.triage.models import TriageResult
from rag_module.triage.rules import find_matching_rules


def check_answers(
    answers: list[dict],
    emergency_number: str | None = None,
) -> TriageResult:
    """
    Выполняет предварительную проверку ответов пользователя.

    Это прототип поиска опасных признаков, а не медицинская диагностика.

    Отсутствие совпадений не исключает опасное состояние.
    До внедрения клинически проверенного опроса система
    не разрешает выдачу обычных медицинских рекомендаций.
    """

    if not isinstance(answers, list) or not answers:
        return TriageResult(
            status="needs_assessment",
            should_stop=False,
            message=(
                "Недостаточно информации для оценки состояния. "
                "Необходимо уточнить симптомы."
            ),
        )

    all_matched_rules = []

    for item in answers:
        if not isinstance(item, dict):
            continue

        answer = item.get("answer", "")

        if not isinstance(answer, str):
            continue

        matched = find_matching_rules(answer)

        for rule in matched:
            if rule not in all_matched_rules:
                all_matched_rules.append(rule)

    if all_matched_rules:
        return TriageResult(
            status="emergency",
            should_stop=True,
            message=(
                "В ответах обнаружены признаки, которые могут "
                "указывать на опасное состояние. Необходимо "
                "немедленно обратиться за экстренной медицинской "
                "помощью. Не продолжайте обычный опрос и не "
                "полагайтесь на рекомендации ИИ."
            ),
            matched_rules=all_matched_rules,
            emergency_number=emergency_number,
        )

    return TriageResult(
        status="needs_assessment",
        should_stop=False,
        message=(
            "Настроенные правила не обнаружили совпадений, "
            "но проверка опасных состояний ещё не завершена. "
            "Обычная медицинская рекомендация пока недоступна. "
            "Необходимо продолжить проверку или обратиться "
            "за медицинской оценкой."
        ),
    )
