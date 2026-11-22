"""
Сервисный слой для интеграции внешнего модуля ИИ.

Контракт:
process_user_message(consultation, user_message_text, history) -> dict
  Возвращает:
  {
      "reply": str,
      "is_emergency": bool,
      "emergency_reason": str | None,
      "is_final": bool,
  }

Пока модуль ИИ не подключен, выбрасываем NotImplementedError.
"""

def process_user_message(consultation, user_message_text: str, history: list = None) -> dict:
    raise NotImplementedError(
        "Модуль ИИ ещё не подключён. "
        "Замените тело функции в ai_assis/services.py."
    )