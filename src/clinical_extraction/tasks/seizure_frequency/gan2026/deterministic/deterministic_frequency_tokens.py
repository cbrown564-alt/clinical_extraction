from __future__ import annotations

import re

from clinical_extraction.tasks.shared.epilepsy.terms import NUMBER_WORDS

NUMBER_WORD_PATTERN = "|".join(NUMBER_WORDS)
NUMBER_VALUE_TOKEN = rf"(?:multiple|\d+|{NUMBER_WORD_PATTERN})"
NUMBER_TOKEN = (
    rf"(?:{NUMBER_VALUE_TOKEN}(?:\s+(?:to|or)\s+{NUMBER_VALUE_TOKEN}|"
    rf"\s*[-–—]\s*{NUMBER_VALUE_TOKEN})?)"
)
UNIT_TOKEN = r"day|week|month|quarter|year|days|weeks|months|quarters|years"
ADJECTIVE_PERIOD_TOKEN = r"daily|weekly|monthly|yearly|bimonthly"


def rate_label(count: str, unit: str, denominator: str | None = None) -> str:
    count_value = number_token(count)
    unit_value = singular_unit(unit)
    denominator_value = number_token(denominator) if denominator else None
    if unit_value == "fortnight":
        unit_value = "week"
        denominator_value = "2"
    if unit_value == "quarter":
        unit_value = "month"
        denominator_value = quarter_month_denominator(denominator_value)
    if denominator_value in {None, "1"}:
        return f"{count_value} per {unit_value}"
    return f"{count_value} per {denominator_value} {unit_value}"


def number_token(value: str | None) -> str:
    if value is None:
        return "1"
    normalized = re.sub(r"\s*[-–—]\s*", " to ", value.lower())
    normalized = " ".join(normalized.split())
    if " to " in normalized:
        return " to ".join(number_token(part) for part in normalized.split(" to "))
    if " or " in normalized:
        return " to ".join(number_token(part) for part in normalized.split(" or "))
    return NUMBER_WORDS.get(normalized, normalized)


def cluster_size_token(value: str | None) -> str:
    if value is None:
        return "multiple"
    normalized = re.sub(r"\bor more\b", "", value, flags=re.IGNORECASE)
    normalized = re.sub(r"[≈~]", "", normalized)
    normalized = re.sub(r"\s*-\s*", " to ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if normalized == "":
        return "multiple"
    return number_token(normalized)


def integer_number_token(value: str) -> int | None:
    normalized = number_token(value)
    if normalized.isdigit():
        return int(normalized)
    return None


def increment_number_token(value: str) -> str | None:
    normalized = number_token(value)
    if " to " in normalized:
        parts = normalized.split(" to ")
        increments = []
        for part in parts:
            if not part.isdigit():
                return None
            increments.append(str(int(part) + 1))
        return " to ".join(increments)
    if normalized.isdigit():
        return str(int(normalized) + 1)
    return None


def singular_unit(value: str) -> str:
    normalized = value.lower().strip()
    return normalized[:-1] if normalized.endswith("s") else normalized


def period_unit_label(value: str) -> str:
    normalized = value.lower().strip()
    if normalized == "fortnight":
        return "2 week"
    return singular_unit(normalized)


def period_label(unit: str, denominator: str | None = None) -> str:
    denominator_value = number_token(denominator) if denominator else None
    unit_value = singular_unit(unit)
    if denominator_value in {None, "1"}:
        return unit_value
    return f"{denominator_value} {unit_value}"


def cluster_period_label(unit: str) -> str:
    unit_value = singular_unit(unit)
    if unit_value in {"daily", "weekly", "monthly", "yearly", "fortnightly"}:
        return unit_value[:-2] if unit_value.endswith("ly") else unit_value
    if unit_value == "fortnight":
        return "2 week"
    if unit_value == "quarter":
        return "3 month"
    return unit_value


def expanded_compact_unit(value: str) -> str:
    return {
        "d": "day",
        "day": "day",
        "wk": "week",
        "week": "week",
        "mo": "month",
        "month": "month",
        "yr": "year",
        "year": "year",
    }[value.lower()]


def adverbial_period_unit(value: str) -> str:
    return {
        "daily": "day",
        "weekly": "week",
        "monthly": "month",
        "yearly": "year",
    }[value.lower()]


def quarter_month_denominator(denominator: str | None) -> str:
    if denominator in {None, "1"}:
        return "3"
    if denominator and denominator.isdigit():
        return str(int(denominator) * 3)
    return f"3 {denominator}"
