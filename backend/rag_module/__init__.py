
from rag_module.triage import check_answers, TriageResult
from rag_module.triage.deidentification import deidentify
from rag_module.triage.errors import TriageBlockedError


def _clean_text(value):
    return deidentify(value) if isinstance(value, str) else value


def _clean_answers(answers: list[dict]) -> list[dict]:
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
    Проверяет все сообщения пациента новым механизмом безопасности.

    Повторная проверка всей истории нужна, поскольку публичный API
    пока не хранит состояние предыдущих проверок.
    """

    from rag_module.triage.message_safety_checker import (
        check_message_safety,
    )
    from rag_module.triage.safety_integration import (
        convert_safety_result,
    )

    valid_messages = [
        _clean_text(item["answer"]).strip()
        for item in answers
        if (
            isinstance(item, dict)
            and isinstance(item.get("answer"), str)
            and item["answer"].strip()
        )
    ]

    if not valid_messages:
        raise ValueError(
            "Не найдено корректных ответов пользователя."
        )

    for message in valid_messages:
        safety_result = check_message_safety(message)

        if safety_result.should_stop:
            triage_result = convert_safety_result(safety_result)
            raise TriageBlockedError(triage_result)


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

    # Сохраняем старую проверку как дополнительный защитный слой.
    result = _check_triage(answers)

    if result.status in ("emergency", "urgent"):
        raise TriageBlockedError(result)

    # Новая проверка безопасности каждого сообщения.
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
    Генерирует рекомендацию только после полноценной
    клинической оценки.
    """

    answers = _clean_answers(answers)

    result = _check_triage(answers)

    if result.status != "no_red_flags_detected":
        raise TriageBlockedError(result)

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
