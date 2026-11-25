import json
import logging
from pathlib import Path

from gigachat import GigaChat
from gigachat.models import (
    ChatCompletionRequest,
    ChatMessage,
    ChatContentPart,
    ChatModelOptions,
    ChatResponseFormat,
)
from pydantic import ValidationError

from rag_module.config import (
    GIGACHAT_CREDENTIALS,
    GIGACHAT_SCOPE,
    GIGACHAT_MODEL,
)
from rag_module.triage.safety_models import (
    SafetyCheckLLMResponse,
    SafetyCheckResult,
    SAFETY_CHECK_JSON_SCHEMA,
)

from rag_module.triage.safety_rules import check_message_with_rules

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CERT_PATH = PROJECT_ROOT / "certs" / "russian_trusted_root_ca_pem.crt"


SAFETY_CHECK_PROMPT = """
Ты — модуль первичной проверки медицинской безопасности сообщений пациента.

Твоя задача — обнаруживать конкретные признаки непосредственной
медицинской опасности, а не оценивать любое недомогание как экстренную ситуацию.

ВАЖНО:
Необходимо отличать обычные жалобы пациента от экстренных симптомов.
Само по себе наличие боли, дискомфорта или другого недомогания
НЕ означает опасную ситуацию.

Проверяй следующие экстренные признаки:

1. Боль или сдавление в груди, особенно сильные, давящие
   или сопровождающиеся другими тревожными симптомами.
2. Одышка в покое или выраженное затруднение дыхания.
3. Потеря сознания.
4. Судороги.
5. Сильное или неостанавливающееся кровотечение.
6. Признаки инсульта по FAST:
   - внезапная асимметрия лица;
   - внезапная слабость или онемение руки;
   - внезапное нарушение речи.
7. Признаки анафилаксии:
   - затруднение дыхания после возможного аллергена;
   - отёк языка или горла;
   - другие признаки тяжёлой аллергической реакции.
8. Острая сильная боль в животе.
9. Температура выше 39.5 °C у ребёнка.
10. Травма головы с потерей сознания.

ОТДЕЛЬНЫЕ ПРАВИЛА ДЛЯ ГОЛОВНОЙ БОЛИ:

- Обычная головная боль сама по себе НЕ является экстренным признаком.
- Несильная или умеренная головная боль не является основанием
  для dangerous или uncertain.
- Периодическая головная боль не является экстренным признаком.
- Боль во лбу, висках, затылке или другой области головы
  сама по себе не является экстренным признаком.
- Начало головной боли сегодня или несколько часов назад
  само по себе не означает экстренную ситуацию.
- Не направляй пациента за экстренной помощью только потому,
  что он сообщил о головной боли.
- Головная боль становится основанием для dangerous,
  если одновременно присутствуют конкретные экстренные признаки,
  например внезапная чрезвычайно сильная боль с нарушением сознания,
  судорогами или признаками инсульта.
- Если пациент сообщает только о головной боли без перечисленных
  экстренных признаков, выбирай no_critical_signs_detected.

ПРАВИЛА АНАЛИЗА:

- Анализируй только информацию, действительно присутствующую
  в сообщении пациента.
- Не придумывай симптомы, обстоятельства, возраст и историю болезни.
- Не предполагай наличие опасных симптомов, о которых пациент
  ничего не сообщал.
- Отсутствие упоминания симптома НЕ означает, что он точно отсутствует,
  но и НЕ является основанием для uncertain.
- Если экстренные признаки в сообщении не описаны,
  выбирай no_critical_signs_detected.
- Не выбирай uncertain только из-за недостатка информации
  о симптомах, которые пациент не упоминал.
- Учитывай отрицания: «боли в груди нет» означает отсутствие
  упомянутой боли в груди, а не её наличие.
- Отличай текущие симптомы от перенесённых и уже прошедших.
- Не считай гипотетические примеры описанием состояния пациента.
- Если пациент прямо сообщает о потенциально опасном симптоме,
  но невозможно понять, присутствует ли он сейчас,
  выбирай uncertain.
- Если опасный симптом возникал в прошлом и уже прошёл,
  не объявляй его автоматически текущей экстренной ситуацией.
  Если обстоятельства требуют уточнения, выбирай uncertain.
- Если обнаружен хотя бы один актуальный экстренный признак,
  выбирай dangerous.
- Не ставь диагноз.
- Не назначай лекарства и дозировки.

ПРАВИЛА ВЫБОРА СТАТУСА:

dangerous:
Обнаружен конкретный актуальный экстренный признак.
Необходимо немедленно прекратить обычный опрос.

no_critical_signs_detected:
В сообщении не обнаружены конкретные экстренные признаки.
Этот статус НЕ означает, что пациент здоров.
Его следует использовать и при обычных жалобах,
включая головную боль, слабость или умеренный дискомфорт,
если экстренные признаки не описаны.

uncertain:
Пациент действительно упоминает потенциально опасный симптом,
но его актуальность или смысл невозможно однозначно определить.
Не используй этот статус просто из-за отсутствия подробностей.

ПРИМЕРЫ:

Сообщение: «У меня иногда болит голова».
Статус: no_critical_signs_detected.

Сообщение: «Сегодня утром заболел лоб, боль несильная».
Статус: no_critical_signs_detected.

Сообщение: «У меня болит голова, других симптомов не замечаю».
Статус: no_critical_signs_detected.

Сообщение: «Внезапно возникла самая сильная головная боль в жизни,
появились судороги».
Статус: dangerous.

Сообщение: «Сейчас сильная давящая боль в груди».
Статус: dangerous.

Сообщение: «Вчера была сильная боль в груди, сейчас прошла».
Статус: uncertain, если требуется уточнение обстоятельств.

Сообщение: «У меня нет боли в груди и затруднения дыхания».
Статус: no_critical_signs_detected.

ФОРМАТ ОТВЕТА:

Строго соблюдай переданную JSON-схему.
Не добавляй текст вне JSON.

Поле reason должно содержать краткое объяснение на русском языке.
Поле matched_signs должно содержать только реально обнаруженные признаки.
Не добавляй в matched_signs симптомы, которые пациент не упоминал.
Поле recommended_action должно содержать понятную рекомендацию на русском языке.

Если обнаружен экстренный признак, обязательно укажи:
«Вызовите скорую помощь по номеру 103 или 112.
Не ждите окончания опроса».

Если экстренные признаки не обнаружены, не утверждай,
что пациент здоров или находится вне опасности.

"""


def _create_uncertain_result() -> SafetyCheckResult:
    """Безопасный результат, если проверку не удалось выполнить."""

    return SafetyCheckResult(
        danger_status="uncertain",
        urgency="undetermined",
        reason="Не удалось надёжно выполнить проверку сообщения.",
        matched_signs=[],
        recommended_action=(
            "Опрос приостановлен. Требуется повторная проверка "
            "или оценка специалистом."
        ),
        should_stop=True,
    )


def check_message_safety(message: str) -> SafetyCheckResult:
    """
    Проверяет одно сообщение пациента на экстренные признаки.

    При ошибке проверки возвращает uncertain и останавливает опрос.
    """

    if not isinstance(message, str) or not message.strip():
        raise ValueError("Сообщение пациента не должно быть пустым.")

    try:
        # Независимая проверка до обращения к GigaChat.
        rules_result = check_message_with_rules(message)

        # Экстренный признак от правил имеет высший приоритет.
        if rules_result.danger_status == "dangerous":
            logger.warning(
                "Независимые правила обнаружили опасный признак: %s",
                rules_result.matched_rules,
            )

            return SafetyCheckResult(
                danger_status="dangerous",
                urgency="emergency",
                reason=rules_result.reason,
                matched_signs=list(rules_result.matched_rules),
                recommended_action=(
                    "Немедленно вызовите скорую помощь по номеру "
                    "103 или 112. Не продолжайте обычный опрос."
                ),
                should_stop=True,
            )

        prompt = (
            f"{SAFETY_CHECK_PROMPT}\n\n"
            f"Сообщение пациента:\n{message.strip()}"
        )

        request = ChatCompletionRequest(
            model=GIGACHAT_MODEL,
            messages=[
                ChatMessage(
                    role="user",
                    content=[
                        ChatContentPart(text=prompt)
                    ],
                )
            ],
            model_options=ChatModelOptions(
                temperature=0.1,
                max_tokens=700,
                response_format=ChatResponseFormat(
                    type="json_schema",
                    schema_=SAFETY_CHECK_JSON_SCHEMA,
                    strict=True,
                ),
            ),
        )

        with GigaChat(
            credentials=GIGACHAT_CREDENTIALS,
            scope=GIGACHAT_SCOPE,
            model=GIGACHAT_MODEL,
            ca_bundle_file=str(CERT_PATH),
        ) as client:
            response = client.chat.create(request)

        raw_response = response.messages[0].content[0].text
        try:
            response_data = json.loads(raw_response)
            llm_result = SafetyCheckLLMResponse.model_validate(
                response_data
            )
        except (ValueError, TypeError):
            raise RuntimeError(
                "Некорректный ответ GigaChat при проверке безопасности."
            ) from None

        # Проверяем согласованность статуса и найденных признаков.
        if (
            llm_result.danger_status == "dangerous"
            and not llm_result.matched_signs
        ):
            logger.warning(
                "GigaChat вернул dangerous без matched_signs."
            )
            return _create_uncertain_result()

        if (
            llm_result.danger_status == "no_critical_signs_detected"
            and llm_result.matched_signs
        ):
            logger.warning(
                "GigaChat вернул no_critical_signs_detected "
                "при наличии matched_signs."
            )
            return _create_uncertain_result()

        # Независимые правила не позволяют отменить uncertain.
        if (
            rules_result.danger_status == "uncertain"
            and llm_result.danger_status
            == "no_critical_signs_detected"
        ):
            return SafetyCheckResult(
                danger_status="uncertain",
                urgency="undetermined",
                reason=(
                    rules_result.reason + " " + llm_result.reason
                ),
                matched_signs=list(rules_result.matched_rules),
                recommended_action=(
                    "Необходимо уточнить обстоятельства и время "
                    "появления симптомов. Обычный опрос приостановлен."
                ),
                should_stop=True,
            )

        # Решение об остановке принимает Python, а не GigaChat.
        should_stop = (
            llm_result.danger_status
            in ("dangerous", "uncertain")
        )

        urgency = (
            "emergency"
            if llm_result.danger_status == "dangerous"
            else "undetermined"
        )

        return SafetyCheckResult(
            danger_status=llm_result.danger_status,
            urgency=urgency,
            reason=llm_result.reason,
            matched_signs=llm_result.matched_signs,
            recommended_action=llm_result.recommended_action,
            should_stop=should_stop,
        )

    except Exception:
        logger.warning("Ошибка при проверке безопасности сообщения.")
        return _create_uncertain_result()
