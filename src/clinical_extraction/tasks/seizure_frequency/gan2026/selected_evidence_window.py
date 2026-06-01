from __future__ import annotations

import re

from clinical_extraction.tasks.seizure_frequency.gan2026.label_parser import (
    normalize_frequency_label,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence_text import (
    format_prediction_rate as _format_prediction_rate,
)


def sum_counts_over_window(text: str) -> str | None:
    window = re.search(
        r"\b(?:in|over|during|for)\s+(?:the\s+)?(?:past|last)\s+"
        r"(?:(?P<count>\d+)\s+)?(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if not window:
        return None

    prefix = text
    counts = [
        int(value)
        for value in re.findall(
            r"\b(\d+)\s+(?!(?:day|week|month|year)s?\b)"
            r"(?!(?:seizure[- ]free|free)\b)"
            r"(?=(?:tonic(?:-clonic)?|drop|absence|"
            r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
            r"(?:seizure|attack|convulsion|spasm|mal|event)))",
            prefix,
        )
    ]
    if not counts:
        return None

    denominator = window.group("count") or "1"
    unit = window.group("unit")
    return _format_prediction_rate(f"{sum(counts)} per {denominator}", unit)


def range_count_over_window(text: str) -> str | None:
    window = re.search(
        r"\b(?:in|over|during|for)\s+(?:the\s+)?(?:past|last)\s+"
        r"(?:(?P<count>\d+)\s+)?(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if not window:
        return None

    range_match = re.search(
        r"\b(?P<low>\d+)\s*(?:to|-|–|—|or)\s*(?P<high>\d+)\s+"
        r"(?=(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizure|attack|convulsion|spasm|mal|event|tonic))",
        text,
    )
    if not range_match:
        return None

    denominator = window.group("count") or "1"
    unit = window.group("unit")
    return _format_prediction_rate(
        f"{range_match.group('low')} to {range_match.group('high')} per {denominator}",
        unit,
    )


def single_count_over_window(text: str) -> str | None:
    match = re.search(
        r"\b(?P<count>\d+)\s+(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizure|attack|convulsion|spasm|mal|event|episode)s?\s+"
        r"(?:in|over|during|for)\s+(?:the\s+)?(?:past|last)?\s*"
        r"(?P<denominator>\d+)\s+(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if not match:
        return None
    return _format_prediction_rate(
        f"{match.group('count')} per {match.group('denominator')}",
        match.group("unit"),
    )


def elapsed_months_in_year_context(context_text: str | None) -> int | None:
    if not context_text:
        return None
    text = normalize_frequency_label(context_text)
    month_names = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }
    month_pattern = "|".join(month_names)
    match = re.search(
        rf"\b(?:clinic\s+date|sent)\s*:\s*\d{{1,2}}\s+({month_pattern})\s+\d{{4}}\b",
        text,
    )
    if not match:
        return None
    return month_names[match.group(1)]
