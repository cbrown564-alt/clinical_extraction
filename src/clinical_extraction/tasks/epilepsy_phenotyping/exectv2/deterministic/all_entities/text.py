"""Text and temporal normalization helpers."""

from __future__ import annotations

import re

from clinical_extraction.tasks.shared.epilepsy.terms import FULL_MONTHS, MONTH_ABBREVIATIONS

_FREQUENCY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"\b(?:prn|p\.r\.n\.|as\s+required|when\s+required|as\s+needed|"
            r"rescue|for\s+seizure\s+clusters?)\b",
            re.IGNORECASE,
        ),
        "As_Required",
    ),
    (
        re.compile(
            r"\b(?:bd|b\.d\.|twice\s+(?:a\s+)?day|twice\s+aday|"
            r"twice\s+daily|twice\s+today)\b",
            re.IGNORECASE,
        ),
        "2",
    ),
    (
        re.compile(
            r"\b(?:od|o\.d\.|once\s+(?:a\s+)?day|once\s+daily|daily|mane|nocte|"
            r"nightly|morning|afternoon|evening|am|pm|at\s+night|"
            r"in\s+the\s+(?:morning|afternoon|night|evening)|on|nokte)\b",
            re.IGNORECASE,
        ),
        "1",
    ),
    (re.compile(r"\b(?:tds|t\.d\.s\.|tid|three\s+times\s+(?:a\s+)?day)\b", re.IGNORECASE), "3"),
)
_MONTHS: dict[str, str] = {
    **{name: str(number) for name, number in FULL_MONTHS.items()},
    **{name: str(number) for name, number in MONTH_ABBREVIATIONS.items()},
}
_MONTH_PATTERN = "|".join(sorted(_MONTHS, key=len, reverse=True))

_NUMBER_WORDS: dict[str, str] = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "twenty one": "21",
    "twenty-one": "21",
    "twenty two": "22",
    "twenty-two": "22",
}


def _frequency_from_text(text: str) -> str | None:
    for pattern, value in _FREQUENCY_PATTERNS:
        if pattern.search(text):
            return value
    return None


def _temporal_unit(value: str | None) -> str:
    if value and value.lower().startswith("month"):
        return "Month"
    return "Year"


def _number_value(value: str) -> str:
    normalized = value.lower().replace("-", " ").strip()
    return _NUMBER_WORDS.get(normalized, value)


def _canonical_onset_phrase(value: str) -> str:
    lowered = value.lower()
    if lowered.startswith("seizure"):
        return "seizures"
    return "epilepsy"
