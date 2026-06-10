"""Number and unit normalization for the ExECTv2 SF deterministic extractor.

Converts matched text tokens to the closed-vocab attribute values required by
the SeizureFrequency EntitySpec (e.g. "twice" → "2", "months" → "Month").
"""
from __future__ import annotations

from clinical_extraction.tasks.shared.epilepsy.terms import NUMBER_WORDS

# ExECTv2 SeizureFrequency word-numbers (guideline v9 List 11). The shared
# NUMBER_WORDS maps "few"/"several" to a "multiple" sentinel for task 1; the SF
# guideline instead assigns explicit numeric values, so override them here.
_COUNT_MAP: dict[str, str] = {
    **NUMBER_WORDS,
    "few": "2",
    "couple": "2",
    "several": "3",
    "multiple": "2",
    "number": "2",
    "none": "0",
    "0": "0",
}

_UNIT_MAP: dict[str, str] = {
    "day": "Day",
    "days": "Day",
    "week": "Week",
    "weeks": "Week",
    "month": "Month",
    "months": "Month",
    "year": "Year",
    "years": "Year",
}


def normalize_count(value: str) -> str:
    """Convert a number token (word or digit) to a digit string."""
    if not value:
        return "1"
    lower = value.strip().lower()
    # Strip a leading article so "a couple"/"a few"/"a number" map like the noun.
    if lower.startswith(("a ", "an ")):
        lower = lower.split(" ", 1)[1].strip()
    if lower in _COUNT_MAP:
        return _COUNT_MAP[lower]
    # Digit string passthrough
    if lower.isdigit():
        return lower
    return lower


def normalize_unit(value: str) -> str:
    """Convert a time period token to the SeizureFrequency closed-vocab value."""
    return _UNIT_MAP.get(value.strip().lower(), value)


_MONTH_MAP: dict[str, str] = {
    "january": "1", "jan": "1",
    "february": "2", "feb": "2",
    "march": "3", "mar": "3",
    "april": "4", "apr": "4",
    "may": "5",
    "june": "6", "jun": "6",
    "july": "7", "jul": "7",
    "august": "8", "aug": "8",
    "september": "9", "sep": "9", "sept": "9",
    "october": "10", "oct": "10",
    "november": "11", "nov": "11",
    "december": "12", "dec": "12",
}

# Regex alternation of month names (longest first so "sept" beats "sep").
MONTH_NAME_PATTERN = (
    r"January|February|March|April|May|June|July|August|September|October|"
    r"November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec"
)


def normalize_month(value: str) -> str:
    """Convert a month name or numeric month to a '1'..'12' string.

    Guideline Appendix: SeizureFrequency MonthDate is numeric 1–12 (the v9
    examples are internally inconsistent — 'MonthDate = May' vs 'MonthDate = 5';
    the Appendix canonical form is numeric)."""
    lower = value.strip().lower().rstrip(".")
    if lower in _MONTH_MAP:
        return _MONTH_MAP[lower]
    if lower.isdigit():
        return lower
    return value


def clean_span(text: str) -> str:
    """Strip trailing sentence-ending punctuation from a matched span."""
    return text.strip(" .;:\n\t")
