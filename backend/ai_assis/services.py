"""Слой-адаптер между API AI-сессий и библиотекой RAG.

Библиотека RAG зависит от внешних сервисов (GigaChat, Qdrant) и загружает
тяжёлые ML-модели при импорте. Здесь ничего не импортируется при загрузке
модуля: каждая интеграция ленивая и при сбое переходит к консервативному
безопасному резервному варианту.
"""

import copy
import logging
from datetime import date

logger = logging.getLogger(__name__)

# Статусы берутся из rag_module.triage.safety_models.DangerStatus.
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

# Клиент сам пагинирует вопросы, поэтому API создаёт пачку один раз
# и затем просто пересылает сохранённый список в каждом ответе.
AI_QUESTION_MIN = 6
AI_QUESTION_MAX = 10


def ai_question_count() -> int:
    """Размер пачки настраивается, ограничение — 6–10 вопросов."""
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


def _age_years(birth_date, today=None):
    if not birth_date:
        return None
    today = today or date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def _years_word(age):
    if 10 <= age % 100 <= 20:
        return 'лет'
    if age % 10 == 1:
        return 'год'
    if 2 <= age % 10 <= 4:
        return 'года'
    return 'лет'


def _birth_date_variants(birth_date):
    short_year = str(birth_date.year)[2:]
    return dict.fromkeys((
        f'{birth_date.day:02d}.{birth_date.month:02d}.{birth_date.year}',
        f'{birth_date.day}.{birth_date.month}.{birth_date.year}',
        f'{birth_date.day:02d}/{birth_date.month:02d}/{birth_date.year}',
        f'{birth_date.day}/{birth_date.month}/{birth_date.year}',
        f'{birth_date.year}-{birth_date.month:02d}-{birth_date.day:02d}',
        f'{birth_date.year}-{birth_date.month}-{birth_date.day}',
        f'{birth_date.day:02d}.{birth_date.month:02d}.{short_year}',
        f'{birth_date.day}.{birth_date.month}.{short_year}',
    ))


def patient_identifiers(patient):
    values = {}
    if patient is None:
        return values

    for name in (patient.first_name, patient.last_name):
        if name and name.strip():
            values[name.strip()] = '[ИМЯ]'

    user = getattr(patient, 'user', None)
    if user is not None:
        for name in (user.first_name, user.last_name):
            if name and name.strip():
                values[name.strip()] = '[ИМЯ]'
        max_id = getattr(user, 'max_id', None)
        if max_id:
            values[max_id] = '[ID]'

    age = _age_years(patient.birth_date)
    if age is not None and age >= 0:
        replacement = f'пациенту {age} {_years_word(age)}'
        for variant in _birth_date_variants(patient.birth_date):
            values[variant] = replacement
    return values


def choose_worst_safety(*results: dict) -> dict:
    """Выбирает самую тяжёлую оценку безопасности при повторной проверке ответов."""
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
    force_stop: bool = False,
) -> dict:
    """Формирует единый payload безопасности для всех AI-эндпоинтов."""
    return {
        "danger_status": danger_status,
        "is_dangerous": danger_status == DANGER_DANGEROUS,
        "urgency": urgency,
        "reason": reason,
        "matched_signs": list(matched_signs),
        "recommended_action": recommended_action,
        # uncertain не завершает опрос; остановка — только dangerous и сбои проверки.
        "should_stop": bool(force_stop or (should_stop and danger_status == DANGER_DANGEROUS)),
    }


def _fallback_safety(reason: str) -> dict:
    """Резервный результат: остановить опрос, если проверку выполнить не удалось."""
    return _safety(
        danger_status=DANGER_UNCERTAIN,
        urgency="undetermined",
        reason=reason,
        recommended_action=(
            "Опрос приостановлен. Не удалось надёжно проверить сообщение; "
            "обратитесь к специалисту."
        ),
        force_stop=True,
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
                "Продолжайте опрос. Ситуация требует уточнения, "
                "но критических признаков не найдено."
            ),
            matched_signs=rule_result.matched_rules,
            should_stop=False,
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


def check_message_safety(message: str, use_llm: bool = True, patient=None) -> dict:
    """Проверяет одно сообщение пациента на критические признаки.

    Фильтр правил детерминирован и не требует внешних сервисов. Он выполняется
    первым и сразу завершается при dangerous. Если настроены ключи, GigaChat
    используется только для признаков, которые правила не нашли.
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
        logger.warning("Rule-based safety check failed")
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
        from rag_module.triage.deidentification import deidentify
        from rag_module.triage.message_safety_checker import (
            check_message_safety as rag_check,
        )

        llm_result = rag_check(deidentify(message, patient_identifiers(patient)))
        data = llm_result.model_dump()
        # uncertain от GigaChat больше не завершает сессию.
        return _safety(
            danger_status=data["danger_status"],
            urgency=data.get("urgency", "undetermined"),
            reason=data["reason"],
            recommended_action=data["recommended_action"],
            matched_signs=data.get("matched_signs", ()),
            should_stop=data.get("should_stop", False),
        )
    except Exception:
        logger.warning("LLM safety check failed, using rule-based result")
        return mapped


_ANAMNESIS_STATUS_LABELS = {
    "YES": "да",
    "NO": "нет",
    "UNKNOWN": "неизвестно",
    "NA": "не применимо",
    "never": "никогда",
    "former": "ранее",
    "current": "сейчас",
    "sometimes": "иногда",
    "regularly": "регулярно",
}


def _anamnesis_status(value, default="не указано") -> str:
    if not isinstance(value, str) or not value.strip():
        return default
    return _ANAMNESIS_STATUS_LABELS.get(value, value.strip())


def _anamnesis_relation_items(relation, ref_attr: str) -> list[str]:
    items = []
    for obj in relation.all():
        ref = getattr(obj, ref_attr, None)
        name = getattr(ref, "name", None) if ref is not None else None
        custom = (getattr(obj, "custom_name", "") or "").strip()
        label = str(name).strip() if name else custom
        if label:
            items.append(label)
    return items


def anamnesis_context(patient) -> str:
    """Собирает обезличенный фон из анамнеза, не попадая в safety-проверку."""
    if patient is None:
        return ""

    from anamnesis.models import Anamnesis
    from rag_module.triage.deidentification import deidentify

    try:
        anamnesis = (
            Anamnesis.objects.select_related("patient", "patient__user")
            .prefetch_related(
                "chronic_diseases__disease",
                "hereditary_diseases__disease",
                "medications__medication",
                "allergies__allergen",
            )
            .get(patient=patient)
        )
    except Anamnesis.DoesNotExist:
        return ""
    except Exception:
        logger.warning("Anamnesis context unavailable")
        return ""

    parts = []
    smoking = _anamnesis_status(anamnesis.smoking_status)
    alcohol = _anamnesis_status(anamnesis.alcohol_status)
    if smoking != "не указано":
        parts.append(f"курение: {smoking}")
    if alcohol != "не указано":
        parts.append(f"алкоголь: {alcohol}")

    pregnancy = _anamnesis_status(anamnesis.pregnancy, default="неизвестно")
    lactation = _anamnesis_status(anamnesis.lactation, default="неизвестно")
    if pregnancy in {"да", "нет"}:
        parts.append(f"беременность: {pregnancy}")
    if lactation in {"да", "нет"}:
        parts.append(f"лактация: {lactation}")

    for label, items in (
        ("хронические заболевания", _anamnesis_relation_items(anamnesis.chronic_diseases, "disease")),
        ("наследственные заболевания", _anamnesis_relation_items(anamnesis.hereditary_diseases, "disease")),
        ("лекарства", _anamnesis_relation_items(anamnesis.medications, "medication")),
        ("аллергии", _anamnesis_relation_items(anamnesis.allergies, "allergen")),
    ):
        if items:
            parts.append(f"{label}: {', '.join(items)}")

    notes = (anamnesis.recent_events_notes or "").strip()
    if notes:
        parts.append(f"недавние события: {notes}")

    if not parts:
        return ""

    text = "; ".join(parts)
    return deidentify(text, patient_identifiers(patient)).strip()


def build_answers(session, include_anamnesis: bool = False) -> list[dict]:
    """Преобразует сохранённые вопросы в историю rag_module: question/answer."""
    from rag_module.triage.deidentification import deidentify

    values = patient_identifiers(getattr(session, "patient", None))
    answers = []
    if include_anamnesis:
        context = anamnesis_context(getattr(session, "patient", None))
        if context:
            answers.append(
                {
                    "question": "Анамнез пациента (фон)",
                    "answer": context,
                }
            )

    answers.extend(
        {
            "question": deidentify(q.question_text or "", values),
            "answer": deidentify(q.answer_text.strip(), values),
        }
        for q in session.questions.order_by("order_number")
        if q.answer_text and q.answer_text.strip()
    )
    return answers


def get_session_safety(session, use_llm: bool = False) -> dict:
    """Собирает safety по всем ответам; побеждает самый тяжёлый статус."""
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
        result = check_message_safety(
            item["answer"], use_llm=use_llm, patient=getattr(session, "patient", None)
        )
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
    """Сразу генерирует всю пачку AI-вопросов (по умолчанию 6–10).

    Безопасность уже проверена вызывающим кодом, поэтому используется низкоуровневый
    генератор, а не полный RAG-триаж шесть раз. Любая неудачная или дублирующаяся
    генерация заменяется встроенным вопросом, чтобы клиент всегда получил полный набор.
    """
    count = ai_question_count() if count is None else count
    generated: list[str] = []
    answers = build_answers(session, include_anamnesis=True)

    try:
        from rag_module.config import GIGACHAT_CREDENTIALS
        from rag_module.generation.question_generator import (
            generate_next_question as rag_generate,
        )
        from rag_module.triage.deidentification import deidentify

        if not GIGACHAT_CREDENTIALS:
            raise RuntimeError("GIGACHAT_CREDENTIALS is not configured")

        for _ in range(count):
            try:
                result = rag_generate(answers)
                question = result.get("question") if isinstance(result, dict) else None
                if isinstance(question, str) and question.strip():
                    question = deidentify(question.strip(), patient_identifiers(session.patient))
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
    """Обратно совместимый хелпер для одного вопроса."""
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
    """Преобразует urgency из rag_module в RoutingResult.Urgency."""
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
    """Возвращает рекомендацию; никогда не выбрасывает исключение в API."""
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

        result = process_patient_answers(
            build_answers(session, include_anamnesis=True)
        )
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
        logger.warning("RAG recommendation unavailable, using safe fallback")

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
    """Обратно совместимый контракт сервиса для старых вызывающих."""
    safety = check_message_safety(user_message_text)
    return {
        "reply": safety["recommended_action"],
        "is_emergency": safety["is_dangerous"],
        "emergency_reason": safety["reason"] if safety["is_dangerous"] else None,
        "is_final": safety["should_stop"],
        "safety": safety,
    }
