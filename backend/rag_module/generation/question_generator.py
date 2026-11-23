
import json
from pathlib import Path

from gigachat import GigaChat
from gigachat.models import (
    ChatCompletionRequest,
    ChatMessage,
    ChatContentPart,
    ChatModelOptions,
    ChatResponseFormat,
)

from rag_module.config import (
    GIGACHAT_CREDENTIALS,
    GIGACHAT_SCOPE,
    GIGACHAT_MODEL,
)
from rag_module.generation.question_models import (
    NextQuestion,
    NEXT_QUESTION_JSON_SCHEMA,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CERT_PATH = PROJECT_ROOT / "certs" / "russian_trusted_root_ca_pem.crt"


def generate_next_question(
    answers: list[dict],
) -> dict:
    """
    Генерирует следующий вопрос опроса на основе
    предыдущих ответов пользователя.

    Не использует RAG и Qdrant.
    Возвращает словарь с полем question.
    """

    if not GIGACHAT_CREDENTIALS:
        raise RuntimeError(
            "Не указан GIGACHAT_CREDENTIALS в файле .env"
        )

    if not isinstance(answers, list) or not answers:
        raise ValueError(
            "Необходимо передать хотя бы один предыдущий ответ."
        )

    answers_text = []

    for index, item in enumerate(answers, start=1):
        if not isinstance(item, dict):
            continue

        question = item.get("question")
        answer = item.get("answer")

        if not isinstance(question, str) or not question.strip():
            continue

        if not isinstance(answer, str) or not answer.strip():
            continue

        answers_text.append(
            f"Вопрос {index}: {question.strip()}\n"
            f"Ответ пользователя: {answer.strip()}"
        )

    if not answers_text:
        raise ValueError(
            "Не найдено корректных вопросов и ответов."
        )

    context = "\n\n".join(answers_text)

    prompt = f"""
Ты — помощник, который проводит предварительный опрос
пользователя о его самочувствии.

Твоя задача — задать ОДИН следующий уточняющий вопрос,
который логически продолжает текущую жалобу пользователя.

ГЛАВНОЕ ПРАВИЛО:
Не меняй тему основной жалобы пользователя.
Все новые вопросы должны относиться к той проблеме,
с которой пользователь изначально обратился.

ПРАВИЛА:

1. Сначала определи основную жалобу по первому ответу пользователя.
2. Учитывай все предыдущие вопросы и ответы.
3. Задавай вопрос, который уточняет именно основную жалобу.
4. Не переключайся на другие симптомы, если пользователь
   сам о них не сообщил и они не связаны с текущей жалобой.
5. Не задавай повторно вопросы, на которые уже получен ответ.
6. Считай информацию уже известной, если пользователь
   прямо или однозначно сообщил её в предыдущих ответах.
7. Если пользователь уже назвал область боли
   (например, поясница, колено, голова), не спрашивай,
   где именно находится боль.
8. Не перефразируй ранее заданный вопрос, чтобы получить
   уже известную информацию.
9. Перед выбором вопроса проверь, какие сведения уже известны:
   локализация, продолжительность, интенсивность,
   характер боли и сопутствующие симптомы.
10. Не ставь диагнозы.
11. Не назначай лечение и лекарства.
12. Не делай медицинских выводов.
13. Не добавляй приветствия и пояснения.
14. Верни только JSON в соответствии с заданной схемой.

ПРОВЕРКА ПЕРЕД ОТВЕТОМ:

- Относится ли вопрос к первоначальной жалобе?
- Не задавался ли этот вопрос ранее?
- Поможет ли ответ уточнить текущую проблему?

Если вопрос не соответствует хотя бы одному условию,
выбери другой.

ПРЕДЫДУЩИЕ ВОПРОСЫ И ОТВЕТЫ:

{context}
"""

    request = ChatCompletionRequest(
        model=GIGACHAT_MODEL,
        messages=[
            ChatMessage(
                role="user",
                content=[
                    ChatContentPart(text=prompt)
                ]
            )
        ],
        model_options=ChatModelOptions(
            response_format=ChatResponseFormat(
                type="json_schema",
                schema_=NEXT_QUESTION_JSON_SCHEMA,
                strict=True,
            )
        )
    )

    with GigaChat(
        credentials=GIGACHAT_CREDENTIALS,
        scope=GIGACHAT_SCOPE,
        model=GIGACHAT_MODEL,
        ca_bundle_file=str(CERT_PATH)
    ) as client:

        response = client.chat.create(request)

    if not response.messages:
        raise RuntimeError(
            "GigaChat не вернул сообщение."
        )

    content = response.messages[0].content

    if not content or not content[0].text:
        raise RuntimeError(
            "GigaChat вернул пустой ответ."
        )

    try:
        data = json.loads(content[0].text.strip())
        payload = NextQuestion.model_validate(data)

    except (json.JSONDecodeError, ValueError) as error:
        raise RuntimeError(
            "Не удалось проверить JSON сгенерированного вопроса."
        ) from error

    return payload.model_dump()
