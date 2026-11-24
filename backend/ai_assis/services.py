def process_user_message(
    consultation,
    user_message_text: str,
    history: list = None,
) -> dict:
    """
    Формирует итоговую медицинскую рекомендацию через RAG.

    history — список ответов:
    [
        {"question": "Вопрос", "answer": "Ответ"},
        ...
    ]
    """

    from rag_module import process_patient_answers

    answers = history or []

    result = process_patient_answers(answers)

    # Поддерживаем как Pydantic-модель, так и обычный dict.
    if hasattr(result, "model_dump"):
        recommendation = result.model_dump()
    elif isinstance(result, dict):
        recommendation = result
    else:
        raise TypeError(
            f"Неожиданный тип результата RAG: {type(result).__name__}"
        )

    return {
        "reply": recommendation.get(
            "recommendation",
            "Рекомендация сформирована.",
        ),
        "is_emergency": recommendation.get("urgency") == "emergency",
        "emergency_reason": None,
        "is_final": True,
        "recommendation": recommendation,
    }