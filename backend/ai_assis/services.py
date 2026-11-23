"""Adapter layer between the AI session API and the RAG library.

The RAG library depends on external services (GigaChat, Qdrant) and loads
heavy ML models on import.  Nothing is imported at module import time here:
every integration is lazy and degrades to a conservative, safe fallback.
"""

import copy
import logging

logger = logging.getLogger(__name__)

# Statuses come from rag_module.triage.safety_models.DangerStatus.
DANGER_DANGEROUS = "dangerous"
DANGER_UNCERTAIN = "uncertain"
DANGER_NONE = "no_critical_signs_detected"

_DANGER_SEVERITY = {
    DANGER_NONE: 0,
    DANGER_UNCERTAIN: 1,
    DANGER_DANGEROUS: 2,
}

EMERGENCY_ACTION = (
    "Вызовите скорую помощь по номеру 103 или 112. "
    "Не ждите окончания опроса."
)

# The client paginates these questions itself, so the API generates a batch
# once and then simply re-sends the stored list with every response.
AI_QUESTION_MIN = 6
AI_QUESTION_MAX = 10


def ai_question_count() -> int:
    """Configurable batch size, clamped to the 6-10 range from the spec."""
    try:
        from django.conf import settings

        value = getattr(settings, "AI_QUESTION_COUNT", AI_QUESTION_MIN)
        value = int(value)
    except (Exception, TypeError, ValueError):
        value = AI_QUESTION_MIN
    return max(AI_QUESTION_MIN, min(AI_QUESTION_MAX, value))


AI_QUESTION_COUNT = ai_question_count()

FALLBACK_QUESTIONS = (
    "Как давно появились эти симптомы?",
    "Как выражены симптомы по шкале от 1 до 10?",
    "Что помогает облегчить состояние?",
    "Есть ли хронические заболевания или принимаемые лекарства?",
    "Были ли похожие эпизоды раньше?",
    "Есть ли аллергия на лекарства или продукты?",
    "Как меняется состояние в течение дня?",
    "Есть ли связь с приемом пищи или физической нагрузкой?",
    "Какие лекарства вы принимали в последнее время?",
    "Были ли результаты обследований или анализов?",
)


def choose_worst_safety(*results: dict) -> dict:
    """Pick the most severe safety verdict; used for per-answer re-checks."""
    valid = [item for item in results if isinstance(item, dict)]
    if not valid:
        return _fallback_safety("Нет результатов проверки безопасности.")
    return max(
        valid,
        key=lambda item: _DANGER_SEVERITY.get(item.get("danger_status"), 0),
    )


def _safety(
    danger_status: str,
    urgency: str,
    reason: str,
    recommended_action: str,
    matched_signs: list | tuple = (),
    should_stop: bool = False,
) -> dict:
    """Build the unified safety payload returned by every AI endpoint."""
    return {
        "danger_status": danger_status,
        "is_dangerous": danger_status == DANGER_DANGEROUS,
        "urgency": urgency,
        "reason": reason,
        "matched_signs": list(matched_signs),
        "recommended_action": recommended_action,
        "should_stop": bool(should_stop),
    }


def _fallback_safety(reason: str) -> dict:
    """Fail-safe result: stop the survey when the check could not run."""
    return _safety(
        danger_status=DANGER_UNCERTAIN,
        urgency="undetermined",
        reason=reason,
        recommended_action=(
            "Опрос приостановлен. Не удалось надёжно проверить сообщение; "
            "обратитесь к специалисту."
        ),
        should_stop=True,
    )


def _map_rule_result(rule_result) -> dict:
    status = rule_result.danger_status
    if status == DANGER_DANGEROUS:
        return _safety(
            danger_status=status,
            urgency="emergency",
            reason=rule_result.reason,
            recommended_action=EMERGENCY_ACTION,
            matched_signs=rule_result.matched_rules,
            should_stop=True,
        )
    if status == DANGER_UNCERTAIN:
        return _safety(
            danger_status=status,
            urgency="undetermined",
            reason=rule_result.reason,
            recommended_action=(
                "Опрос приостановлен. Ситуация требует уточнения "
                "или оценки специалистом."
            ),
            matched_signs=rule_result.matched_rules,
            should_stop=True,
        )
    return _safety(
        danger_status=DANGER_NONE,
        urgency="undetermined",
        reason=rule_result.reason,
        recommended_action=(
            "Продолжайте опрос. Отсутствие критических признаков "
            "не исключает заболевание."
        ),
        matched_signs=rule_result.matched_rules,
        should_stop=False,
    )


def check_message_safety(message: str, use_llm: bool = True) -> dict:
    """Check one patient message for critical signs.

    The rule filter is deterministic and needs no external services.  It runs
    first and short-circuits on dangerous/uncertain results.  When creds are
    configured, GigaChat is used only to catch signs the rules missed.
    """
    if not isinstance(message, str) or not message.strip():
        return _fallback_safety("Сообщение пациента пустое.")

    try:
        from rag_module.triage.safety_rules import check_message_with_rules

        rule_result = check_message_with_rules(message)
        mapped = _map_rule_result(rule_result)
        if mapped["should_stop"]:
            return mapped
    except Exception:
        logger.exception("Rule-based safety check failed")
        return _fallback_safety("Не удалось выполнить проверку правил.")

    if not use_llm:
        return mapped

    try:
        from rag_module.config import GIGACHAT_CREDENTIALS

        if not GIGACHAT_CREDENTIALS:
            return mapped
    except Exception:
        return mapped

    try:
        from rag_module.triage.message_safety_checker import (
            check_message_safety as rag_check,
        )

        llm_result = rag_check(message)
        data = llm_result.model_dump()
        return _safety(
            danger_status=data["danger_status"],
            urgency=data.get("urgency", "undetermined"),
            reason=data["reason"],
            recommended_action=data["recommended_action"],
            matched_signs=data.get("matched_signs", ()),
            should_stop=data.get("should_stop", False),
        )
    except Exception:
        logger.exception("LLM safety check failed, using rule-based result")
        return mapped


def build_answers(session) -> list[dict]:
    """Convert persisted questions to the rag_module ``{'question','answer'}`` history."""
    return [
        {"question": q.question_text, "answer": q.answer_text.strip()}
        for q in session.questions.order_by("order_number")
        if q.answer_text and q.answer_text.strip()
    ]


def get_session_safety(session, use_llm: bool = False) -> dict:
    """Aggregate safety across all answered messages; the worst status wins."""
    answers = build_answers(session)
    if not answers:
        return _safety(
            danger_status=DANGER_NONE,
            urgency="undetermined",
            reason="Ответов пациента пока нет.",
            recommended_action="Продолжайте опрос.",
            should_stop=False,
        )

    worst = None
    signs: list[str] = []
    for item in answers:
        result = check_message_safety(item["answer"], use_llm=use_llm)
        signs.extend(result["matched_signs"])
        if worst is None or (
            _DANGER_SEVERITY.get(result["danger_status"], 0)
            > _DANGER_SEVERITY.get(worst["danger_status"], 0)
        ):
            worst = result

    if worst is None:  # pragma: no cover - defensive
        return _fallback_safety("Не удалось оценить ответы пациента.")

    worst = copy.deepcopy(worst)
    worst["matched_signs"] = list(dict.fromkeys(signs))
    return worst


def generate_next_questions(session, count: int | None = None) -> list[str]:
    """Generate the whole batch of AI questions at once (6-10 by default).

    Safety has already been checked by the caller, so the low-level generator
    is used directly instead of running the full RAG triage six times.  Any
    failed or duplicate generation is replaced with a built-in question so the
    client always receives the full set.
    """
    count = ai_question_count() if count is None else count
    generated: list[str] = []
    answers = build_answers(session)

    try:
        from rag_module.config import GIGACHAT_CREDENTIALS
        from rag_module.generation.question_generator import (
            generate_next_question as rag_generate,
        )

        if not GIGACHAT_CREDENTIALS:
            raise RuntimeError("GIGACHAT_CREDENTIALS is not configured")

        for _ in range(count):
            try:
                result = rag_generate(answers)
                question = result.get("question") if isinstance(result, dict) else None
                if isinstance(question, str) and question.strip():
                    question = question.strip()
                    if question not in generated:
                        generated.append(question)
            except Exception:
                logger.warning("One RAG question could not be generated")
    except Exception:
        logger.warning("RAG question generation unavailable, using fallbacks")

    for question in FALLBACK_QUESTIONS:
        if len(generated) >= count:
            break
        if question not in generated:
            generated.append(question)

    return generated[:count]


def generate_next_question(session) -> str:
    """Backward-compatible single-question helper."""
    return generate_next_questions(session, count=1)[0]


URGENCY_MAP = {
    "emergency": "EMERGENCY",
    "urgent_24h": "URGENT",
    "urgent": "URGENT",
    "planned": "PLANNED",
    "self_care": "SELF_HELP",
    "self-help": "SELF_HELP",
}


def map_urgency(value: str | None) -> str:
    """Map rag_module urgency to RoutingResult.Urgency."""
    from routing.models import RoutingResult

    mapped = URGENCY_MAP.get((value or "").lower(), "PLANNED")
    valid = {choice for choice, _ in RoutingResult.Urgency.choices}
    return mapped if mapped in valid else RoutingResult.Urgency.PLANNED


def to_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("recommendation", "message", "text", "reason", "summary"):
            part = value.get(key)
            if isinstance(part, str) and part.strip():
                return part
    return str(value or "")


def generate_recommendation(session, safety: dict) -> dict:
    """Return a recommendation payload; never raise to the API layer."""
    if safety["should_stop"]:
        return {
            "source": "safety_check",
            "recommendation": safety["recommended_action"],
            "justification": safety["reason"],
            "urgency": safety["urgency"],
            "doctor": "",
            "place": "",
            "evidence": [],
        }

    try:
        from rag_module import process_patient_answers

        result = process_patient_answers(build_answers(session))
        if isinstance(result, dict) and result:
            return {
                "source": "rag",
                "recommendation": to_text(result.get("recommendation")),
                "justification": to_text(result.get("reason")),
                "urgency": result.get("urgency", "planned"),
                "doctor": result.get("doctor", ""),
                "place": result.get("place", ""),
                "evidence": result.get("evidence", []),
            }
    except Exception:
        logger.exception("RAG recommendation unavailable, using safe fallback")

    return {
        "source": "fallback",
        "recommendation": (
            "Автоматическая рекомендация недоступна. "
            "Обратитесь к врачу для клинической оценки состояния."
        ),
        "justification": (
            "Недостаточно подтверждающих данных или внешний сервис "
            "рекомендаций недоступен."
        ),
        "urgency": "planned",
        "doctor": "",
        "place": "",
        "evidence": [],
    }


def process_user_message(consultation, user_message_text: str, history: list = None) -> dict:
    """Backward-compatible service contract used by older callers."""
    safety = check_message_safety(user_message_text)
    return {
        "reply": safety["recommended_action"],
        "is_emergency": safety["is_dangerous"],
        "emergency_reason": safety["reason"] if safety["is_dangerous"] else None,
        "is_final": safety["should_stop"],
        "safety": safety,
    }
