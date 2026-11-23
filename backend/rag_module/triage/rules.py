import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TriageRule:
    """Правило предварительного выявления опасного признака."""

    code: str
    description: str
    patterns: tuple[str, ...]


TRIAGE_RULES = (
    TriageRule(
        code="breathing_emergency",
        description="Возможное тяжёлое нарушение дыхания",
        patterns=(
            r"\bзадыхаюсь\b",
            r"\bне хватает воздуха\b",
            r"\bтяжело дышать\b",
            r"\bне могу вдохнуть\b",
            r"\bне могу дышать\b",
        ),
    ),

    TriageRule(
        code="cardiac_emergency",
        description="Возможная острая сердечная проблема",
        patterns=(
            r"\bсильная боль в груди\b",
            r"\bсильная боль за грудиной\b",
            r"\bдавит в груди\b",
            r"\bсдавливает грудь\b",
            r"\bжжение за грудиной\b",
        ),
    ),

    TriageRule(
        code="stroke_emergency",
        description="Возможные признаки инсульта",
        patterns=(
            r"\bперекосило лицо\b",
            r"\bперекос лица\b",
            r"\bвнезапно нарушилась речь\b",
            r"\bне могу говорить\b",
            r"\bвнезапно онемела одна сторона\b",
            r"\bвнезапная слабость в одной руке\b",
        ),
    ),

    TriageRule(
        code="consciousness_emergency",
        description="Возможная потеря сознания",
        patterns=(
            r"\bпотерял сознание\b",
            r"\bпотеряла сознание\b",
            r"\bбез сознания\b",
            r"\bне приходит в сознание\b",
        ),
    ),

    TriageRule(
        code="bleeding_emergency",
        description="Возможное опасное кровотечение",
        patterns=(
            r"\bсильное кровотечение\b",
            r"\bкровь не останавливается\b",
            r"\bочень сильная кровопотеря\b",
        ),
    ),

    TriageRule(
        code="allergic_emergency",
        description="Возможная тяжёлая аллергическая реакция",
        patterns=(
            r"\bотёк языка\b",
            r"\bотекло горло\b",
            r"\bотёк горла\b",
            r"\bотекает язык\b",
            r"\bотёк лица.*трудно дышать\b",
        ),
    ),

    TriageRule(
        code="seizure_emergency",
        description="Возможный продолжающийся судорожный приступ",
        patterns=(
            r"\bсудороги не прекращаются\b",
            r"\bдлительный судорожный приступ\b",
            r"\bприступ судорог продолжается\b",
        ),
    ),

    TriageRule(
        code="poisoning_emergency",
        description="Возможное отравление или передозировка",
        patterns=(
            r"\bпередозировка\b",
            r"\bпринял слишком много таблеток\b",
            r"\bприняла слишком много таблеток\b",
            r"\bвыпил слишком много лекарства\b",
            r"\bвыпила слишком много лекарства\b",
            r"\bотравился\b",
            r"\bотравилась\b",
        ),
    ),
)

def _is_negated_match(text: str, match_start: int) -> bool:
    """
    Проверяет, не отрицается ли найденный симптом
    непосредственно перед совпадением.
    """
    prefix = text[max(0, match_start - 30):match_start]

    return bool(
        re.search(
            r"\b(?:не|нет)\s+(?:\w+\s+){0,2}$",
            prefix,
            flags=re.IGNORECASE,
        )
    )

def find_matching_rules(text: str) -> list[str]:
    if not isinstance(text, str) or not text.strip():
        return []

    normalized_text = " ".join(text.casefold().split())

    matched_rules = []

    for rule in TRIAGE_RULES:
        for pattern in rule.patterns:
            matches = list(
                re.finditer(
                    pattern,
                    normalized_text,
                    flags=re.IGNORECASE,
                )
            )

            for match in matches:
                # Пока применяем проверку отрицания
                # только к сердечным симптомам.
                if rule.code == "cardiac_emergency":
                    if _is_negated_match(
                        normalized_text,
                        match.start(),
                    ):
                        continue

                matched_rules.append(rule.code)
                break

    return matched_rules