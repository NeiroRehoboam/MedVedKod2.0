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

Твоя задача — определить, содержит ли сообщение признаки, требующие
немедленного прекращения обычного опроса и экстренной помощи.

Проверяй следующие признаки из технического задания:

1. Боль или сдавление в груди.
2. Одышка в покое, выраженное затруднение дыхания.
3. Потеря сознания.
4. Судороги.
5. Кровотечение.
6. Признаки инсульта по FAST:
   - асимметрия лица;
   - слабость или онемение руки;
   - нарушение речи.
7. Признаки анафилаксии:
   - затруднение дыхания после возможного аллергена;
   - отёк языка или горла;
   - другие признаки тяжёлой аллергической реакции.
8. Острая сильная боль в животе.
9. Температура выше 39.5 °C у ребёнка.
10. Травма головы с потерей сознания.

Правила:

- Анализируй только информацию, которая действительно присутствует
  в сообщении.
- Не придумывай симптомы, обстоятельства, возраст и медицинскую историю.
- Учитывай отрицания: «боли в груди нет» не означает наличие боли.
- Отличай текущие симптомы от перенесённых и уже прошедших.
- Если опасный симптом возникал недавно, но уже прошёл,
  не объявляй его текущим экстренным признаком автоматически.
- Если в прошлом сообщении описан потенциально серьёзный симптом,
  который требует дополнительной оценки (например, боль в груди),
  выбирай uncertain, чтобы передать ситуацию на уточнение.
- Не теряй информацию о прошедших симптомах.
- Не считай гипотетические примеры описанием состояния пациента.
- Фразы «у меня болит грудь», «сильная боль в груди»,
  «давит в груди» и «сдавление в груди» являются сообщениями
  о симптоме, если пациент не отрицает его наличие
  и не описывает его как гипотетический или прошедший.
- Не классифицируй конкретное описание симптома как отсутствие
  медицинской информации.
- Сильная давящая боль в груди в настоящий момент означает dangerous.
- Если невозможно уверенно определить наличие или отсутствие опасного
  признака, выбирай uncertain.
- Если обнаружен хотя бы один актуальный экстренный признак,
  выбирай dangerous.
- Если в сообщении не обнаружено перечисленных экстренных признаков,
  выбирай no_critical_signs_detected.
- Не ставь диагноз.
- Не назначай лекарства и дозировки.

Статусы:

dangerous — обнаружен экстренный признак.
no_critical_signs_detected — перечисленные экстренные признаки
не обнаружены в данном сообщении.
uncertain — информации недостаточно или её смысл неоднозначен.

Поле reason должно содержать краткое объяснение на русском языке.
Поле matched_signs должно содержать найденные признаки.
Поле recommended_action должно содержать понятную рекомендацию
на русском языке.

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
        response_data = json.loads(raw_response)

        llm_result = SafetyCheckLLMResponse.model_validate(
            response_data
        )

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
        logger.exception(
            "Ошибка при проверке безопасности сообщения."
        )
        return _create_uncertain_result()