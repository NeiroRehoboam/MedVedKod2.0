
from rag_module.triage import check_answers, TriageResult
from rag_module.triage.deidentification import deidentify
from rag_module.triage.errors import TriageBlockedError


def _clean_text(value):
    """Удаляет персональные данные из текстового значения."""
    return deidentify(value) if isinstance(value, str) else value


def _clean_answers(answers: list[dict]) -> list[dict]:
    """Удаляет персональные данные из вопросов и ответов."""
    if not isinstance(answers, list):
        return answers

    return [
        {key: _clean_text(value) for key, value in item.items()}
        if isinstance(item, dict)
        else item
        for item in answers
    ]


def search(question: str, limit: int = 5) -> list[dict]:
    """Ищет наиболее релевантные фрагменты документов."""
    from rag_module.retrieval.retriever import search_documents

    return search_documents(_clean_text(question), limit)


def _check_triage(answers: list[dict]) -> TriageResult:
    """Выполняет проверку старым механизмом Triage."""
    return check_answers(_clean_answers(answers))


def _check_safety_history(answers: list[dict]) -> None:
    """
    Проверяет историю ответов на экстренные признаки.

    Краткие утвердительные ответы на вопросы о прошлых
    эпизодах не проверяются отдельно от контекста.
    """

    from rag_module.triage.message_safety_checker import (
        check_message_safety,
    )
    from rag_module.triage.safety_integration import (
        convert_safety_result,
    )

    answers = _clean_answers(answers)
    has_previous_answer = False

    for item in answers:
        if not isinstance(item, dict):
            continue

        answer = item.get("answer")
        question = item.get("question", "")

        if not isinstance(answer, str) or not answer.strip():
            continue

        answer = answer.strip()

        if not isinstance(question, str):
            question = ""

        question = question.strip().lower().replace("ё", "е")

        normalized_answer = answer.lower().strip(" .,!?:;")

        # Определяем, спрашивали ли о прошлых симптомах.
        is_history_question = (
            any(
                word in question
                for word in ("раньше", "ранее", "в прошлом")
            )
            and any(
                word in question
                for word in ("подобн", "такие", "симптом", "боль")
            )
        )

        # Краткие ответы на вопросы о прошлых эпизодах.
        is_generic_yes = normalized_answer in (
            "да",
            "да, иногда такое бывало",
            "да, такое бывало",
            "да, иногда бывало",
            "да, подобное бывало",
            "да, такое случалось",
        )

        if (
            is_history_question
            and is_generic_yes
            and has_previous_answer
        ):
            has_previous_answer = True
            continue

        safety_result = check_message_safety(answer)

        # Экстренные признаки.
        if safety_result.danger_status == "dangerous":
            raise TriageBlockedError(
                convert_safety_result(safety_result)
            )

        # Ошибка проверки безопасности.
        if (
            safety_result.reason
            == "Не удалось надёжно выполнить проверку сообщения."
        ):
            raise TriageBlockedError(
                convert_safety_result(safety_result)
            )

        # Неоднозначный результат требует уточнения.
        if safety_result.danger_status == "uncertain":
            raise TriageBlockedError(
                convert_safety_result(safety_result)
            )

        has_previous_answer = True


def ask(question: str, limit: int = 5) -> dict:
    """Ищет информацию в документах и формирует ответ."""

    question = _clean_text(question)

    from rag_module.retrieval.retriever import search_documents
    from rag_module.generation.generator import generate_answer

    result = _check_triage([
        {
            "question": "Запрос пользователя",
            "answer": question,
        }
    ])

    if result.status in ("emergency", "urgent"):
        raise TriageBlockedError(result)

    search_results = search_documents(question, limit)

    return generate_answer(question, search_results)


def index_document(filename: str) -> dict:
    """Индексирует PDF-документ."""
    from rag_module.processing.indexer import index_pdf

    return index_pdf(filename)


def generate_next_question(answers: list[dict]) -> dict:
    """Проверяет безопасность истории и генерирует следующий вопрос."""

    answers = _clean_answers(answers)

    # Первый защитный слой: старый механизм Triage.
    result = _check_triage(answers)

    if result.status in ("emergency", "urgent"):
        raise TriageBlockedError(result)

    # Второй защитный слой: проверка каждого ответа.
    _check_safety_history(answers)

    from rag_module.generation.question_generator import (
        generate_next_question as generate,
    )

    return generate(answers)


def generate_recommendation(
    answers: list[dict],
    search_results: list[dict],
) -> dict:
    """
    Генерирует рекомендацию после полной проверки безопасности.
    """

    answers = _clean_answers(answers)

    # Старый Triage: рекомендация только при отсутствии
    # обнаруженных тревожных признаков.
    result = _check_triage(answers)

    if result.status != "no_red_flags_detected":
        raise TriageBlockedError(result)

    # Проверка безопасности отдельных сообщений.
    _check_safety_history(answers)

    from rag_module.generation.recommendation_generator import (
        generate_recommendation as generate,
    )

    return generate(answers, search_results)


def process_patient_answers(
    answers: list[dict],
    limit: int = 5,
) -> dict:
    """
    Выполняет полный конвейер обработки ответов пациента:
    проверку безопасности, извлечение симптомов,
    клиническую оценку и RAG-рекомендацию.
    """

    from rag_module.triage.patient_pipeline import (
        process_patient_answers as process,
    )

    return process(_clean_answers(answers), limit)


__all__ = [
    "search",
    "ask",
    "index_document",
    "generate_next_question",
    "generate_recommendation",
    "process_patient_answers",
    "check_answers",
    "TriageResult",
    "TriageBlockedError",
]
