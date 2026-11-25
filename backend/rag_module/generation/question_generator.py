import json
import re
from difflib import SequenceMatcher
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

MAX_GENERATION_ATTEMPTS = 3

# Служебные слова не должны влиять на сравнение вопросов.
STOP_WORDS = {
    "а", "без", "бы", "был", "была", "были", "быть",
    "в", "вам", "вас", "вы", "где", "да", "для", "до",
    "его", "ее", "если", "есть", "ещё", "же", "за",
    "и", "из", "или", "именно", "как", "какая", "какие",
    "какой", "когда", "кто", "ли", "мне", "может",
    "на", "над", "не", "него", "нее", "нет", "ни",
    "но", "о", "об", "он", "она", "они", "оно",
    "от", "по", "под", "при", "про", "с", "со",
    "так", "также", "то", "только", "у", "уже",
    "что", "это", "этот", "эта", "эти", "я",
}


def _normalize_question(question: str) -> str:
    """Приводит вопрос к виду, удобному для сравнения."""

    question = question.lower().replace("ё", "е")
    question = re.sub(r"[^а-яa-z0-9\s]", " ", question)
    question = re.sub(r"\s+", " ", question).strip()

    return question


def _question_tokens(question: str) -> set[str]:
    """Возвращает значимые слова вопроса."""

    normalized = _normalize_question(question)

    return {
        word
        for word in normalized.split()
        if len(word) > 2 and word not in STOP_WORDS
    }

# Аспекты, которые система собирает во время опроса.
ASPECT_PATTERNS = {
    "location": (
        r"в какой части",
        r"где именно болит",
        r"где именно ощущается",
        r"локализ",
        r"област[ьи] (головы|живота|груди|спины|тела)",
        r"\bлоб\b",
        r"затыл",
        r"висок",
        r"справа",
        r"слева",
    ),
    "onset": (
        r"когда нач",
        r"когда впервые появ",
        r"как давно",
        r"с какого времени",
        r"начал[ао]сь",
        r"возникл[ао]",
        r"внезапно",
        r"постепенно",
    ),
    "duration": (
        r"как долго",
        r"сколько времени",
        r"продолжительност",
        r"сколько дл",
        r"\d+\s*(час|дн|недел|месяц)",
    ),
    "intensity": (
        r"интенсивност",
        r"насколько сильн",
        r"слабая",
        r"умеренная",
        r"сильная",
        r"от 0 до 10",
        r"оцените боль",
    ),
    "quality": (
        r"характер",
        r"какая боль",
        r"пульсир",
        r"давящ",
        r"ноющ",
        r"жгуч",
        r"острая",
        r"тупая",
    ),
    "frequency": (
        r"как часто",
        r"периодическ",
        r"постоянно",
        r"приступами",
        r"повторяет",
        r"частот",
    ),
    "associated_symptoms": (
        r"сопутств",
        r"вместе с",
        r"тошнот",
        r"рвот",
        r"головокруж",
        r"температур",
        r"слабост",
        r"онемени",
        r"нарушени[ея] зрения",
    ),
    "triggers_and_relief": (
        r"усиливает",
        r"облегчает",
        r"что провоцирует",
        r"при наклоне",
        r"при движении",
        r"при физической нагрузке",
        r"после отдыха",
    ),
    "daily_activity": (
        r"повседнев",
        r"обычной деятельност",
        r"мешает работать",
        r"мешает спать",
        r"влияет на активност",
    ),
    "medical_history": (
        r"хроническ",
        r"заболевани",
        r"принимаете лекарств",
        r"какие лекарств",
        r"медикамент",
    ),
}


def _detect_aspects(text: str) -> set[str]:
    """Определяет медицинские аспекты, упомянутые в тексте."""

    normalized = _normalize_question(text)
    detected = set()

    for aspect, patterns in ASPECT_PATTERNS.items():
        if any(
            re.search(pattern, normalized)
            for pattern in patterns
        ):
            detected.add(aspect)

    return detected


def _extract_covered_aspects(answers: list[dict]) -> set[str]:
    """Определяет аспекты, которые действительно выяснены."""

    covered = set()

    unknown_patterns = (
        r"^не знаю",
        r"^не помню",
        r"^не могу сказать",
        r"^затрудняюсь",
        r"^не уверен",
        r"^не уверена",
        r"^не могу определить",
        r"^сложно ответить",
        r"^не понял",
        r"^не поняла",
    )

    for item in answers:
        if not isinstance(item, dict):
            continue

        question = item.get("question", "")
        answer = item.get("answer", "")

        if not isinstance(question, str):
            continue

        if not isinstance(answer, str) or not answer.strip():
            continue

        normalized_answer = _normalize_question(answer)

        # Не считаем аспект выясненным,
        # если пользователь не смог ответить.
        if any(
            re.search(pattern, normalized_answer)
            for pattern in unknown_patterns
        ):
            continue

        # Аспект вопроса считается выясненным,
        # только если пользователь дал содержательный ответ.
        covered.update(_detect_aspects(question))

        # Также учитываем сведения, которые пользователь
        # самостоятельно сообщил в ответе.
        covered.update(_detect_aspects(answer))

    return covered

def _is_duplicate_question(
    new_question: str,
    previous_questions: list[str],
) -> bool:
    """
    Проверяет, не повторяет ли новый вопрос предыдущие.

    Используются текстовое сходство и пересечение значимых слов.
    Это дополнительная защита, а не полноценное семантическое
    сравнение смысла.
    """

    new_normalized = _normalize_question(new_question)
    new_tokens = _question_tokens(new_question)

    for previous_question in previous_questions:
        previous_normalized = _normalize_question(
            previous_question
        )

        if not previous_normalized:
            continue

        # Практически одинаковые формулировки.
        similarity = SequenceMatcher(
            None,
            new_normalized,
            previous_normalized,
        ).ratio()

        if similarity >= 0.78:
            return True

        previous_tokens = _question_tokens(previous_question)

        if not new_tokens or not previous_tokens:
            continue

        # Сравниваем пересечение значимых слов.
        intersection = new_tokens & previous_tokens
        union = new_tokens | previous_tokens

        jaccard_similarity = len(intersection) / len(union)

        if jaccard_similarity >= 0.72:
            return True

    return False


def _extract_answers(answers: list[dict]) -> tuple[str, list[str]]:
    """Проверяет и форматирует историю вопросов и ответов."""

    answers_text = []
    previous_questions = []

    for index, item in enumerate(answers, start=1):
        if not isinstance(item, dict):
            continue

        question = item.get("question")
        answer = item.get("answer")

        if not isinstance(question, str) or not question.strip():
            continue

        if not isinstance(answer, str) or not answer.strip():
            continue

        question = question.strip()
        answer = answer.strip()

        previous_questions.append(question)

        answers_text.append(
            f"Вопрос {index}: {question}\n"
            f"Ответ пользователя: {answer}"
        )

    if not answers_text:
        raise ValueError(
            "Не найдено корректных вопросов и ответов."
        )

    return "\n\n".join(answers_text), previous_questions


def _build_prompt(
    context: str,
    previous_questions: list[str],
    rejected_question: str | None = None,
    covered_aspects: set[str] | None = None,
) -> str:
    """Формирует инструкции для генерации следующего вопроса."""

    previous_questions_text = "\n".join(
        f"- {question}" for question in previous_questions
    )
    covered_aspects_text = (
        ", ".join(sorted(covered_aspects))
        if covered_aspects
        else "Пока не определены"
    )
    retry_instruction = ""

    if rejected_question:
        retry_instruction = f"""

ПРЕДЫДУЩИЙ ВАРИАНТ ОТКЛОНЁН:

{rejected_question}

Он повторяет ранее заданный вопрос.
Не перефразируй его. Выбери ДРУГОЙ аспект основной жалобы.
"""

    return f"""
Ты — помощник, который проводит предварительный опрос
пользователя о его самочувствии.

Твоя задача — задать ОДИН новый уточняющий вопрос
и предложить варианты ответа, если они уместны.

ОСНОВНАЯ ЗАДАЧА:

Помоги последовательно собрать недостающую информацию
о первоначальной жалобе пользователя.

ПРАВИЛА УТОЧНЕНИЯ НЕОДНОЗНАЧНЫХ ОТВЕТОВ:

1. Если предыдущий ответ допускает несколько трактовок,
   сначала уточни именно неоднозначную информацию.
2. Если пользователь описывает периодическую боль,
   не считай это автоматически экстренным признаком.
3. Различай наличие симптома сейчас и его наличие в прошлом.
4. Не спрашивай обо всех опасных симптомах повторно,
   если они уже были проверены и пользователь их отрицал.
5. Если текущий характер симптома неясен,
   задай один конкретный вопрос для уточнения.
6. Не делай вывод об отсутствии опасности только
   на основании того, что пользователь не упомянул симптом.

ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА:

1. Определи основную жалобу по истории ответов.
2. Учитывай ВСЕ предыдущие вопросы и ответы.
3. Не меняй тему первоначальной жалобы.
4. Не спрашивай повторно то, что пользователь уже сообщил.
5. Не задавай вопрос, который отличается от предыдущего
   только формулировкой.
6. Не спрашивай о локализации, если она уже известна.
7. Не спрашивай о продолжительности, если она уже известна.
8. Не спрашивай об интенсивности, если она уже известна.
9. Не спрашивай о характере симптома, если он уже известен.
10. Не повторяй уже выясненные сопутствующие симптомы.
11. Если пользователь сообщил несколько симптомов,
    учитывай их связь с первоначальной жалобой.
12. Выбирай сведения, которые ещё НЕ выяснены.
13. Каждый новый вопрос должен раскрывать новый аспект
    проблемы пользователя.
14. Не задавай несколько вопросов в одном сообщении.
15. Не ставь диагнозы.
16. Не назначай лечение и лекарства.
17. Не добавляй приветствия и пояснения.

ВОЗМОЖНЫЕ АСПЕКТЫ ДЛЯ УТОЧНЕНИЯ:

- когда началась проблема;
- как менялось состояние со временем;
- интенсивность симптома;
- характер и особенности симптома;
- обстоятельства появления или усиления;
- сопутствующие симптомы;
- что облегчает или усиливает состояние;
- влияние на повседневную активность;
- наличие хронических заболеваний и принимаемых лекарств.

Это не фиксированный список вопросов.
Не используй его как шаблон. Выбирай только то,
что действительно ещё неизвестно и относится к жалобе.

ПРАВИЛА ДЛЯ ВАРИАНТОВ ОТВЕТА:

1. Верни от 3 до 5 вариантов, если они действительно помогают.
2. Варианты должны подходить именно к сформулированному вопросу.
3. Не предлагай варианты, которые заранее предполагают диагноз.
4. Не используй варианты, которые искажают смысл вопроса.
5. Если вопрос предполагает свободный подробный ответ,
   верни пустой массив options.
6. Не помещай сам вопрос в варианты ответа.

УЖЕ ВЫЯСНЕННЫЕ МЕДИЦИНСКИЕ АСПЕКТЫ:

{covered_aspects_text}

Не задавай вопросы об этих аспектах повторно,
даже если можно сформулировать их другими словами.
Выбирай только действительно новую информацию.

ПРЕДЫДУЩИЕ ВОПРОСЫ:

{previous_questions_text}

ПРЕДЫДУЩИЕ ОТВЕТЫ:

{context}

{retry_instruction}

ПРОВЕРЬ ПЕРЕД ОТВЕТОМ:

- Вопрос относится к первоначальной жалобе?
- Информация ещё не известна?
- Вопрос не повторяет предыдущие даже другими словами?
- Он уточняет новый аспект проблемы?
- Варианты ответа подходят к этому вопросу?

Верни только JSON строго по заданной схеме:

{{
    "question": "Один новый уточняющий вопрос",
    "options": [
        "Вариант ответа 1",
        "Вариант ответа 2",
        "Вариант ответа 3"
    ]
}}
"""


def generate_next_question(
    answers: list[dict],
) -> dict:
    """
    Генерирует один следующий вопрос на основе истории ответов.

    Не использует RAG и Qdrant.

    Возвращает:
    {
        "question": "...",
        "options": ["...", "..."]
    }

    Публичная сигнатура функции сохранена.
    """

    if not GIGACHAT_CREDENTIALS:
        raise RuntimeError(
            "Не указан GIGACHAT_CREDENTIALS в файле .env"
        )

    if not isinstance(answers, list) or not answers:
        raise ValueError(
            "Необходимо передать хотя бы один предыдущий ответ."
        )

    context, previous_questions = _extract_answers(answers)
    covered_aspects = _extract_covered_aspects(answers)

    rejected_question = None

    with GigaChat(
        credentials=GIGACHAT_CREDENTIALS,
        scope=GIGACHAT_SCOPE,
        model=GIGACHAT_MODEL,
        ca_bundle_file=str(CERT_PATH),
    ) as client:

        for attempt in range(MAX_GENERATION_ATTEMPTS):
            prompt = _build_prompt(
                context=context,
                previous_questions=previous_questions,
                rejected_question=rejected_question,
                covered_aspects=covered_aspects,
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
                    response_format=ChatResponseFormat(
                        type="json_schema",
                        schema_=NEXT_QUESTION_JSON_SCHEMA,
                        strict=True,
                    )
                ),
            )

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

            question = payload.question.strip()

            if not question:
                raise RuntimeError(
                    "GigaChat вернул пустой вопрос."
                )

            if _is_duplicate_question(
                question,
                previous_questions,
            ):
                rejected_question = question
                continue

            question_aspects = _detect_aspects(question)

            if question_aspects & covered_aspects:
                rejected_question = question
                continue

            # Убираем пустые и повторяющиеся варианты ответа.
            unique_options = []
            seen_options = set()

            for option in payload.options:
                option = option.strip()

                if not option:
                    continue

                normalized_option = _normalize_question(option)

                if normalized_option in seen_options:
                    continue

                seen_options.add(normalized_option)
                unique_options.append(option)

            return {
                "question": question,
                "options": unique_options[:5],
            }

    raise RuntimeError(
        "Не удалось сгенерировать новый вопрос без повторов "
        f"за {MAX_GENERATION_ATTEMPTS} попытки."
    )
