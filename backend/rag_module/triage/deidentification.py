import re
from collections.abc import Mapping


_EMAIL_RE = re.compile(r'\b[\w.+-]+@[\w-]+\.[\w.-]+\b', re.IGNORECASE)
_PHONE_RE = re.compile(
    r'(?<!\w)(?:\+7|8)[\s()\-]*\d{3}[\s()\-]*\d{3}[\s()\-]*\d{2}[\s()\-]*\d{2}(?!\w)'
)
_SNILS_RE = re.compile(r'\b\d{3}-\d{3}-\d{3}\s{1,2}\d{2}\b')
_PASSPORT_RE = re.compile(r'\b\d{4}\s\d{6}\b')
_LONG_NUMBER_RE = re.compile(r'\b\d{10,}\b')


def _replace_values(text, values):
    if isinstance(values, Mapping):
        items = values.items()
    else:
        items = ((value, '[ЗНАЧЕНИЕ]') for value in values)

    result = text
    for value, replacement in items:
        if not isinstance(value, str) or len(value.strip()) < 3:
            continue
        pattern = re.compile(
            r'(?<!\w)' + re.escape(value.strip()) + r'(?!\w)',
            re.IGNORECASE,
        )
        result = pattern.sub(replacement, result)
    return result


def deidentify(text: str, values=()) -> str:
    if not isinstance(text, str) or not text:
        return text

    result = _replace_values(text, values)
    result = _EMAIL_RE.sub('[EMAIL]', result)
    result = _PHONE_RE.sub('[ТЕЛЕФОН]', result)
    result = _SNILS_RE.sub('[СНИЛС]', result)
    result = _PASSPORT_RE.sub('[ПАСПОРТ]', result)
    result = _LONG_NUMBER_RE.sub('[НОМЕР]', result)
    return result
