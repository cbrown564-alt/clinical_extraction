from __future__ import annotations

import re

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    normalize_frequency_label,
)
from clinical_extraction.tasks.shared.epilepsy.terms import FULL_MONTHS

from ._shared_tokens import GAP_WORDS_TOKEN
from .selected_evidence_text import (
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
    if re.search(
        r"\bmultiple\s+times?\s+"
        r"(?:in|over|during|for)\s+(?:the\s+)?(?:past|last)\s+"
        r"(?:\d+\s+)?(?:day|week|month|year)s?\b.{0,80}"
        rf"\bincluding\s+\d+\s+{GAP_WORDS_TOKEN}"
        r"(?:seizure|attack|convulsion|spasm|mal|event|episode|aura)",
        text,
    ):
        return None

    prefix = text
    counts = [
        int(value)
        for value in re.findall(
            r"\b(\d+)\s+(?!(?:day|week|month|year)s?\b)"
            r"(?!(?:seizure[- ]free|free)\b)"
            r"(?=(?:tonic(?:-clonic)?|drop|absence|"
            rf"{GAP_WORDS_TOKEN}"
            r"(?:seizure|attack|convulsion|spasm|mal|event|episode|aura)))",
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
        # Also accept bare ``last month`` / ``past week`` after a count range.
        window = re.search(
            r"\b(?:past|last)\s+(?:(?P<count>\d+)\s+)?(?P<unit>day|week|month|year)s?\b",
            text,
        )
    if not window:
        return None

    range_match = re.search(
        r"\b(?P<low>\d+)\s*(?:to|-|–|—|or)\s*(?P<high>\d+)\s+"
        rf"(?={GAP_WORDS_TOKEN}"
        r"(?:seizure|attack|convulsion|spasm|mal|event|episode|tonic))",
        text,
    )
    if not range_match:
        return None

    # An explicit ``per <unit>`` after the range is already a rate, not a
    # count-over-window. Do not rebind it to a distant observation window.
    after_range = text[range_match.end() : range_match.end() + 80]
    if re.search(
        r"^(?:\s+[a-z]+(?:-[a-z]+)?){0,6}\s+per\s+(?:day|week|month|year)s?\b",
        after_range,
    ):
        return None

    denominator = window.group("count") or "1"
    unit = window.group("unit")
    return _format_prediction_rate(
        f"{range_match.group('low')} to {range_match.group('high')} per {denominator}",
        unit,
    )


def single_count_over_window(text: str) -> str | None:
    match = re.search(
        rf"\b(?P<count>\d+)\s+{GAP_WORDS_TOKEN}"
        r"(?:seizure|attack|convulsion|spasm|mal|event|episode)s?\s+"
        r"(?:in|within|over|during|for)\s+(?:the\s+)?(?:past|last)?\s*"
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
    month_pattern = "|".join(FULL_MONTHS)
    match = re.search(
        rf"\b(?:clinic\s+date|sent)\s*:\s*\d{{1,2}}\s+({month_pattern})\s+\d{{4}}\b",
        text,
    )
    if not match:
        return None
    return FULL_MONTHS[match.group(1)]
