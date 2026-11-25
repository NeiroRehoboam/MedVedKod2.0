
import re
from dataclasses import dataclass
from typing import Literal


SafetyRuleStatus = Literal[
    "dangerous",
    "no_critical_signs_detected",
    "uncertain",
]


@dataclass(frozen=True)
class SafetyRule:
    """Правило поиска явно описанного опасного признака."""

    code: str
    description: str
    patterns: tuple[str, ...]


@dataclass(frozen=True)
class SafetyRuleResult:
    """Результат независимой проверки одного сообщения."""

    danger_status: SafetyRuleStatus
    matched_rules: tuple[str, ...]
    reason: str


SAFETY_RULES = (
    SafetyRule(
        code="breathing_emergency",
        description="Возможное тяжёлое нарушение дыхания",
        patterns=(
            r"\bзадыхаюсь\b",
            r"\bзадыхается\b",
            r"\bне хватает воздуха\b",
            r"\bтяжело дыш(?:ать|у)\b",
            r"\bтрудно дыш(?:ать|у)\b",
            r"\bне могу вдохнуть\b",
            r"\bне могу дышать\b",
            r"\bодышка в покое\b",
            r"\bзадыхался\b",
            r"\bзадыхалась\b",
            r"\bзадыхался раньше\b",
        ),
    ),
    SafetyRule(
        code="cardiac_emergency",
        description="Возможная острая боль в груди",
        patterns=(
            r"\bсильная боль в груди\b",
            r"\bсильно болит грудь\b",
            r"\bсильно болела грудь\b",
            r"\bсильная боль за грудиной\b",
            r"\bдавит в груди\b",
            r"\bсдавливает грудь\b",
            r"\bсильное давление в груди\b",
            r"\bжжение за грудиной\b",
        ),
    ),
    SafetyRule(
        code="stroke_emergency",
        description="Возможные признаки инсульта",
        patterns=(
            r"\bперекосило лицо\b",
            r"\bперекос лица\b",
            r"\bвнезапно нарушилась речь\b",
            r"\bречь стала невнятной\b",
            r"\bне могу говорить\b",
            r"\bвнезапно онемела одна сторона\b",
            r"\bвнезапная слабость в одной руке\b",
            r"\bвнезапно ослабла рука\b",
        ),
    ),
    SafetyRule(
        code="consciousness_emergency",
        description="Возможная потеря сознания",
        patterns=(
            r"\bпотерял сознание\b",
            r"\bпотеряла сознание\b",
            r"\bтеряю сознание\b",
            r"\bбез сознания\b",
            r"\bне приходит в сознание\b",
        ),
    ),
    SafetyRule(
        code="bleeding_emergency",
        description="Возможное опасное кровотечение",
        patterns=(
            r"\bсильное кровотечение\b",
            r"\bкровь не останавливается\b",
            r"\bкровотечение не прекращается\b",
            r"\bочень сильная кровопотеря\b",
        ),
    ),
    SafetyRule(
        code="allergic_emergency",
        description="Возможная тяжёлая аллергическая реакция",
        patterns=(
            r"\bотёк языка\b",
            r"\bотек(?:ло|ает) язык\b",
            r"\bотёк горла\b",
            r"\bотек(?:ло|ает) горло\b",
            r"\bотёк лица.*трудно дышать\b",
            r"\bотёк лица.*тяжело дышать\b",
        ),
    ),
    SafetyRule(
        code="seizure_emergency",
        description="Возможный продолжающийся судорожный приступ",
        patterns=(
            r"\bсудороги не прекращаются\b",
            r"\bдлительный судорожный приступ\b",
            r"\bприступ судорог продолжается\b",
            r"\bсудорожный приступ продолжается\b",
            r"\bначались судороги\b",
            r"\bсудороги начались\b",
        ),
    ),
    SafetyRule(
        code="abdominal_emergency",
        description="Возможная острая сильная боль в животе",
        patterns=(
            r"\bрезкая сильная боль в животе\b",
            r"\bвнезапная сильная боль в животе\b",
            r"\bнестерпимая боль в животе\b",
            r"\bочень сильная боль в животе\b",
        ),
    ),
    SafetyRule(
        code="child_fever_emergency",
        description="Температура выше 39,5 °C у ребёнка",
        patterns=(
            r"\b(?:ребён(?:ку|ок|ка)|ребен(?:ку|ок|ка)|сыну|дочери)"
            r".{0,50}\b(?:39[,.][6-9]|40(?:[,.]\d+)?)\s*°?\s*(?:c|с)?\b",

            r"\b(?:39[,.][6-9]|40(?:[,.]\d+)?)\s*°?\s*(?:c|с)?"
            r".{0,50}\b(?:ребён(?:ку|ок|ка)|ребен(?:ку|ок|ка)|сыну|дочери)",
        ),
    ),
    SafetyRule(
        code="head_injury_emergency",
        description="Травма головы с потерей сознания",
        patterns=(
            r"\bударил(?:ся|ась) головой.{0,80}потерял(?:а)? сознание\b",
            r"\bпосле удара по голове.{0,80}потерял(?:а)? сознание\b",
            r"\bтравма головы.{0,80}потеря сознания\b",
        ),
    ),
    SafetyRule(
        code="poisoning_emergency",
        description="Возможное отравление или передозировка",
        patterns=(
            r"\bпередозировка\b",
            r"\bпринял(?:а)? слишком много таблеток\b",
            r"\bвыпил(?:а)? слишком много лекарства\b",
            r"\bотравился\b",
            r"\bотравилась\b",
            r"\bслучайно принял(?:а)? лишн(?:юю|ую) дозу\b",
        ),
    ),
)

SAFETY_RULE_EXPLANATIONS = {
    "breathing_emergency": (
        "Выраженное затруднение дыхания или ощущение нехватки воздуха "
        "может свидетельствовать о серьёзном нарушении дыхательной функции. "
        "В таком состоянии организму может не хватать кислорода."
    ),
    "cardiac_emergency": (
        "Сильная боль, давление или сдавливание в груди могут быть признаками "
        "острого сердечно-сосудистого состояния. Некоторые такие состояния "
        "требуют немедленной медицинской помощи."
    ),
    "stroke_emergency": (
        "Внезапное нарушение речи, асимметрия лица или слабость одной стороны "
        "тела могут указывать на инсульт. При таких симптомах важна "
        "максимально быстрая медицинская помощь."
    ),
    "consciousness_emergency": (
        "Потеря сознания может быть связана с серьёзными нарушениями работы "
        "нервной системы, сердца или других органов. Необходимо срочно "
        "оценить состояние человека."
    ),
    "bleeding_emergency": (
        "Сильное или неостанавливающееся кровотечение может привести "
        "к значительной кровопотере и опасному ухудшению состояния."
    ),
    "allergic_emergency": (
        "Отёк языка или горла, особенно при затруднении дыхания, может "
        "указывать на тяжёлую аллергическую реакцию с риском нарушения "
        "проходимости дыхательных путей."
    ),
    "seizure_emergency": (
        "Продолжающиеся судороги могут быть признаком длительного "
        "судорожного приступа, который способен представлять непосредственную "
        "опасность для жизни."
    ),
    "abdominal_emergency": (
        "Внезапная или нестерпимая боль в животе может быть связана "
        "с острым состоянием органов брюшной полости, требующим "
        "срочного медицинского обследования."
    ),
    "child_fever_emergency": (
        "Температура выше 39,5 °C у ребёнка может сопровождать серьёзное "
        "заболевание. Важно своевременно оценить общее состояние ребёнка "
        "и получить медицинскую помощь."
    ),
    "head_injury_emergency": (
        "Потеря сознания после удара головой может указывать на серьёзную "
        "черепно-мозговую травму. Необходимо срочно исключить опасные "
        "внутренние повреждения."
    ),
    "poisoning_emergency": (
        "Передозировка или случайный приём лишней дозы лекарства могут "
        "вызвать токсическое воздействие на организм. Опасные последствия "
        "могут проявиться не сразу."
    ),
}

def _build_reason(rule_codes: tuple[str, ...], prefix: str) -> str:
    """Формирует подробное объяснение обнаруженных признаков."""

    explanations = []

    for code in rule_codes:
        explanation = SAFETY_RULE_EXPLANATIONS.get(code)

        if explanation:
            explanations.append(f"- {explanation}")

    if not explanations:
        return prefix

    return prefix + "\n\n" + "\n".join(explanations)

# Эти выражения помогают определить, что симптом отрицается.
# Намеренно не используем простое правило "есть слово не":
# например, "не могу дышать" — это опасная жалоба, а не отрицание.
NEGATION_PATTERNS = (
    r"\bнет\s+(?:сейчас\s+)?",
    r"\bне\s+(?:испытываю|чувствую|наблюдаю|было|было никаких)\s+",
    r"\bотсутствует\s+",
)

PAST_MARKERS = (
    r"\bвчера\b",
    r"\bпозавчера\b",
    r"\bраньше\b",
    r"\bв прошлом\b",
    r"\bтогда\b",
    r"\bуже прошло\b",
    r"\bсейчас прошло\b",
    r"\bбольше не\b",
    r"\bбыло\b",
)

HYPOTHETICAL_MARKERS = (
    r"\bесли бы\b",
    r"\bчто делать если\b",
    r"\bчто делать, если\b",
    r"\bпредставим, что\b",
    r"\bдопустим, что\b",
    r"\bнапример, если\b",
    r"\bможет ли человек\b",
    r"\bесли у человека\b",
    r"\bесли у меня\b",
    r"\bесли у ребёнка\b",
    r"\bесли у ребенка\b",
)


def normalize_text(text: str) -> str:
    """Приводит текст к единому формату."""

    return " ".join(text.casefold().split())


def _has_nearby_negation(text: str, start: int, end: int) -> bool:
    """Проверяет отрицание непосредственно перед или после совпадения."""

    prefix = text[max(0, start - 45):start]
    suffix = text[end:min(len(text), end + 25)]

    # "не тяжело дышать", "не трудно дышать".
    # Проверяем отрицание непосредственно перед совпадением.
    if re.search(r"\bне\s*$", prefix):
        return True

    if any(
        re.search(pattern + r"(?:\w+\s+){0,2}$", prefix)
        for pattern in NEGATION_PATTERNS
    ):
        return True

    # "одышка в покое отсутствует", "одышка в покое нет".
    if re.match(r"^\s*(?:нет|отсутствует)\b", suffix):
        return True

    return False

def _has_nearby_past_marker(text: str, start: int, end: int) -> bool:
    """Определяет, относится ли временной маркер к найденному симптому."""

    before = text[max(0, start - 60):start]
    after = text[end:min(len(text), end + 60)]

    current_markers = (
        r"\bсейчас\b",
        r"\bпрямо сейчас\b",
        r"\bв данный момент\b",
    )

    past_before = (
        r"\bвчера\b",
        r"\bпозавчера\b",
        r"\bраньше\b",
        r"\bв прошлом\b",
        r"\bтогда\b",
        r"\bбыло\b",
        r"\bбыла\b",
        r"\bбыли\b",
    )

    past_after = (
        r"\bвчера\b",
        r"\bпозавчера\b",
        r"\bуже прошло\b",
        r"\bуже прошла\b",
        r"\bуже прошли\b",
        r"\bсейчас прошло\b",
        r"\bсейчас прошла\b",
    )

    if any(re.search(marker, before) for marker in current_markers):
        return False

    if any(re.search(marker, before) for marker in past_before):
        return True

    if any(re.search(marker, after) for marker in past_after):
        return True

    return False

def _is_hypothetical(text: str) -> bool:
    """Проверяет, похоже ли сообщение на гипотетический вопрос."""

    return any(re.search(marker, text) for marker in HYPOTHETICAL_MARKERS)


def check_message_with_rules(message: str) -> SafetyRuleResult:
    """
    Независимо проверяет одно сообщение на известные опасные признаки.

    Это консервативный технический фильтр, а не медицинская диагностика.
    """

    if not isinstance(message, str) or not message.strip():
        raise ValueError("Сообщение пациента не должно быть пустым.")

    text = normalize_text(message)

    matched_rules = []
    uncertain_rules = []

    hypothetical = _is_hypothetical(text)

    for rule in SAFETY_RULES:
        for pattern in rule.patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                if _has_nearby_negation(text, match.start(), match.end()):
                    continue

                if hypothetical:
                    uncertain_rules.append(rule.code)
                    continue

                if _has_nearby_past_marker(
                    text,
                    match.start(),
                    match.end(),
                ):
                    uncertain_rules.append(rule.code)
                    continue

                matched_rules.append(rule.code)
                break

            if rule.code in matched_rules:
                break

    matched_rules = list(dict.fromkeys(matched_rules))
    uncertain_rules = list(dict.fromkeys(uncertain_rules))

    # Однозначный текущий опасный признак имеет приоритет.
    if matched_rules:
        matched_rules_tuple = tuple(matched_rules)

        return SafetyRuleResult(
            danger_status="dangerous",
            matched_rules=matched_rules_tuple,
            reason=_build_reason(
                matched_rules_tuple,
                "Обнаружены признаки, которые могут указывать "
                "на состояние, требующее экстренной медицинской помощи.",
            ),
        )

    if uncertain_rules:
        uncertain_rules_tuple = tuple(uncertain_rules)

        return SafetyRuleResult(
            danger_status="uncertain",
            matched_rules=uncertain_rules_tuple,
            reason=_build_reason(
                uncertain_rules_tuple,
                "Обнаружен возможный опасный признак, "
                "но его время или контекст требуют уточнения. "
                "Необходимо проверить, сохраняется ли симптом сейчас.",
            ),
        )

    return SafetyRuleResult(
        danger_status="no_critical_signs_detected",
        matched_rules=(),
        reason=(
            "Настроенные правила не обнаружили явных совпадений. "
            "Это не исключает опасное состояние."
        ),
    )
