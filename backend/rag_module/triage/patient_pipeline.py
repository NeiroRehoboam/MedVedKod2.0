
from rag_module.triage.deidentification import deidentify
from rag_module.triage.errors import TriageBlockedError
from rag_module.triage.message_safety_checker import check_message_safety
from rag_module.triage.safety_integration import convert_safety_result
from rag_module.triage.symptom_extractor import extract_symptoms
from rag_module.triage.symptom_validator import validate_symptom_extraction
from rag_module.triage.triage_engine import evaluate_symptoms


def _check_safety_history(answers: list[dict]) -> None:
    """Проверяет каждый ответ пациента на опасные признаки."""

    messages = [
        deidentify(item["answer"]).strip()
        for item in answers
        if isinstance(item, dict)
        and isinstance(item.get("answer"), str)
        and item["answer"].strip()
    ]

    if not messages:
        raise ValueError("Не найдены ответы пациента для проверки.")

    for message in messages:
        safety_result = check_message_safety(message)

        if safety_result.should_stop:
            raise TriageBlockedError(
                convert_safety_result(safety_result)
            )


def _build_search_query(extraction) -> str:
    """Формирует поисковый запрос из проверенных симптомов."""

    query_parts = []

    for symptom in extraction.symptoms:
        if symptom.status != "present":
            continue

        if symptom.subject != "user":
            continue

        if symptom.time == "future":
            continue

        parts = [deidentify(symptom.name)]

        if symptom.time != "unknown":
            parts.append(f"время: {symptom.time}")

        if symptom.severity != "unknown":
            parts.append(f"тяжесть: {symptom.severity}")

        if symptom.onset:
            parts.append(f"начало: {deidentify(symptom.onset)}")

        if symptom.frequency != "unknown":
            parts.append(f"частота: {symptom.frequency}")

        parts.extend(deidentify(str(detail)) for detail in symptom.details)

        query_parts.append("; ".join(parts))

    if not query_parts:
        raise ValueError(
            "Не удалось сформировать поисковый запрос "
            "из подтверждённых симптомов пациента."
        )

    return "Симптомы пациента: " + ". ".join(query_parts)


def process_patient_answers(
    answers: list[dict],
    limit: int = 5,
):
    """
    Полный конвейер обработки ответов пациента.

    1. Проверка опасных признаков.
    2. Извлечение симптомов.
    3. Валидация извлечения.
    4. Клиническая оценка.
    5. Поиск медицинских документов.
    6. Генерация рекомендации.
    """

    if not isinstance(answers, list) or not answers:
        raise ValueError("История ответов пациента пуста.")

    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("limit должен быть положительным целым числом.")

    answers = [
        {
            key: deidentify(value) if isinstance(value, str) else value
            for key, value in item.items()
        }
        if isinstance(item, dict)
        else item
        for item in answers
    ]

    # 1. Проверяем все сообщения пациента.
    _check_safety_history(answers)

    # 2. Извлекаем симптомы из всей истории.
    extraction_data = extract_symptoms(answers)

    # 3. Проверяем результат извлечения.
    validation = validate_symptom_extraction(extraction_data)

    # 4. Выполняем клиническую оценку.
    triage_result = evaluate_symptoms(validation)

    if triage_result.should_stop:
        raise TriageBlockedError(triage_result)

    # 5. Формируем запрос для Qdrant.
    search_query = _build_search_query(validation.extraction)

    from rag_module.retrieval.retriever import search_documents

    search_results = search_documents(
        question=search_query,
        limit=limit,
    )

    if not search_results:
        raise ValueError(
            "Не найдены медицинские документы, "
            "подтверждающие информацию для рекомендации."
        )

    # 6. Генерируем итоговую рекомендацию.
    from rag_module.generation.recommendation_generator import (
        generate_recommendation,
    )

    return generate_recommendation(
        answers=answers,
        search_results=search_results,
    )
