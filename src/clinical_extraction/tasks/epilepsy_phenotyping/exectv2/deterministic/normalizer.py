"""Number and unit normalization for the ExECTv2 SF deterministic extractor.

Converts matched text tokens to the closed-vocab attribute values required by
the SeizureFrequency EntitySpec (e.g. "twice" → "2", "months" → "Month").
"""

from __future__ import annotations

from clinical_extraction.tasks.shared.epilepsy.terms import (
    FULL_MONTHS,
    MONTH_ABBREVIATIONS,
    NUMBER_WORDS,
)

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


# Transcription typos for month names observed in this corpus, shared by every
# ExECTv2 module that normalizes a matched month token (sf_state_projection,
# statement_parser). Keep new typo aliases here rather than re-adding them
# per-callsite.
MONTH_TYPO_ALIASES: dict[str, str] = {
    "novemebr": "11",
    "devember": "12",
    "feburary": "2",
    "christmas": "12",
}

MONTH_MAP: dict[str, str] = {
    **{name: str(number) for name, number in FULL_MONTHS.items()},
    **{name: str(number) for name, number in MONTH_ABBREVIATIONS.items()},
    **MONTH_TYPO_ALIASES,
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
    if lower in MONTH_MAP:
        return MONTH_MAP[lower]
    if lower.isdigit():
        return lower
    return value


def clean_span(text: str) -> str:
    """Strip trailing sentence-ending punctuation from a matched span."""
    return text.strip(" .;:\n\t")


def since_date_attrs(
    *,
    day: str | None,
    month: str | None,
    year: str | None,
    christmas: str | None,
    christmas_qualifier: str | None,
) -> dict[str, str] | None:
    """Build NumberOfSeizures=0/Since attrs from a matched last-event date.

    ``christmas`` normalizes to December (day 25 if ``christmas_qualifier`` is
    "day"), matching how "last event ... Christmas" phrasing is scored.
    """
    if christmas:
        month = "December"
        if christmas_qualifier and christmas_qualifier.lower() == "day":
            day = "25"
    if not (month or year):
        return None

    attrs: dict[str, str] = {"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"}
    if day:
        attrs["DayDate"] = day
    if month:
        attrs["MonthDate"] = normalize_month(month)
    if year:
        attrs["YearDate"] = year
    return attrs
