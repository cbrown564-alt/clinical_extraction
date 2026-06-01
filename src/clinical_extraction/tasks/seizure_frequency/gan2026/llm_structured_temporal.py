"""Temporal helpers for Gan 2026 LLM structured-events repair."""

from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import date
from typing import Protocol


class StructuredEventLike(Protocol):
    @property
    def kind(self) -> str: ...

    @property
    def evidence(self) -> str: ...

    @property
    def raw_value(self) -> str | None: ...

    @property
    def time_window(self) -> str | None: ...

    @property
    def notes(self) -> str | None: ...


MONTH_PATTERN = (
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
)


def event_text(event: StructuredEventLike) -> str:
    return " ".join(
        part
        for part in (event.evidence, event.raw_value, event.time_window, event.notes)
        if part
    ).lower()


def month_number(month_text: str) -> int:
    month_key = month_text[:3].lower()
    return {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }[month_key]


def small_number_words_to_digits(text: str) -> str:
    replacements = {
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
    }
    for word, digit in replacements.items():
        text = re.sub(rf"\b{word}\b", digit, text)
    return text


def clinic_month_year(note_text: str) -> tuple[int, int] | None:
    match = re.search(
        rf"\bclinic date:\s*\d{{1,2}}\s+(?P<month>{MONTH_PATTERN})\s+(?P<year>\d{{4}})",
        note_text.lower(),
    )
    if not match:
        match = re.search(
            rf"\bsent:\s*\d{{1,2}}\s+(?P<month>{MONTH_PATTERN})\s+(?P<year>\d{{4}})",
            note_text.lower(),
        )
    if not match:
        match = re.search(
            rf"\bdate:\s*\d{{1,2}}\s+(?P<month>{MONTH_PATTERN})\s+(?P<year>\d{{4}})",
            note_text.lower(),
        )
    if not match:
        return None
    return month_number(match.group("month")), int(match.group("year"))


def clinic_date(note_text: str) -> date | None:
    match = re.search(
        rf"\bclinic date:\s*(?P<day>\d{{1,2}})\s+"
        rf"(?P<month>{MONTH_PATTERN})\s+(?P<year>\d{{4}})",
        note_text.lower(),
    )
    if not match:
        match = re.search(
            rf"\bsent:\s*(?P<day>\d{{1,2}})\s+"
            rf"(?P<month>{MONTH_PATTERN})\s+(?P<year>\d{{4}})",
            note_text.lower(),
        )
    if not match:
        match = re.search(
            rf"\bdate:\s*(?P<day>\d{{1,2}})\s+"
            rf"(?P<month>{MONTH_PATTERN})\s+(?P<year>\d{{4}})",
            note_text.lower(),
        )
    if not match:
        return None
    return date(
        int(match.group("year")),
        month_number(match.group("month")),
        int(match.group("day")),
    )


def event_date(text: str, *, clinic: date) -> date | None:
    normalized = text.lower()
    candidates: list[date] = []
    for numeric in re.finditer(
        r"\b(?P<day>\d{1,2})[-/](?P<month>\d{1,2})(?:[-/](?P<year>\d{2,4}))?\b",
        normalized,
    ):
        year = event_year_from_optional_text(
            numeric.group("year"),
            month=int(numeric.group("month")),
            clinic=clinic,
        )
        candidates.append(date(year, int(numeric.group("month")), int(numeric.group("day"))))
    for named in re.finditer(
        rf"\b(?P<day>\d{{1,2}})[-/ ](?P<month>{MONTH_PATTERN})"
        rf"(?:[-/ ](?P<year>\d{{2,4}}))?\b",
        normalized,
    ):
        month = month_number(named.group("month"))
        year = event_year_from_optional_text(named.group("year"), month=month, clinic=clinic)
        candidates.append(date(year, month, int(named.group("day"))))
    candidates = [candidate for candidate in candidates if candidate <= clinic]
    if not candidates:
        return None
    return min(candidates, key=lambda candidate: (clinic - candidate).days)


def event_year_from_optional_text(
    year_text: str | None,
    *,
    month: int,
    clinic: date,
) -> int:
    if year_text:
        year = int(year_text)
        return year + 2000 if year < 100 else year
    return clinic.year - 1 if month > clinic.month else clinic.year


def event_month_year(text: str, *, clinic_year: int) -> tuple[int, int] | None:
    normalized = text.lower()
    month_year = re.search(
        r"\b(?P<month>\d{1,2})\s*[-/]\s*(?P<year>\d{4})\b",
        normalized,
    )
    if month_year:
        month = int(month_year.group("month"))
        if 1 <= month <= 12:
            return month, int(month_year.group("year"))
    named_month_year = re.search(
        rf"\b(?P<month>{MONTH_PATTERN})\s*[-/]\s*(?P<year>\d{{4}})\b",
        normalized,
    )
    if named_month_year:
        return month_number(named_month_year.group("month")), int(
            named_month_year.group("year")
        )
    numeric = re.search(r"\b\d{1,2}[-/](?P<month>\d{1,2})(?:[-/](?P<year>\d{2,4}))?\b", normalized)
    if numeric:
        month = int(numeric.group("month"))
        year_text = numeric.group("year")
        year = clinic_year if year_text is None else int(year_text)
        if year < 100:
            year += 2000
        return month, year
    named = re.search(
        rf"\b(?:early|mid|late)?\s*(?P<month>{MONTH_PATTERN})(?:\s+(?P<year>\d{{4}}))?\b",
        normalized,
    )
    if named:
        return month_number(named.group("month")), int(named.group("year") or clinic_year)
    return None


def elapsed_months(
    anchor: tuple[int, int],
    clinic: tuple[int, int],
) -> int | None:
    anchor_month, anchor_year = anchor
    clinic_month, clinic_year = clinic
    months = (clinic_year - anchor_year) * 12 + (clinic_month - anchor_month)
    return months if months > 0 else None


def nearest_event_date(
    events: Sequence[StructuredEventLike],
    *,
    clinic: date,
    event_kinds: set[str],
    max_months: int,
) -> date | None:
    dates = [
        parsed_event_date
        for event in events
        if event.kind in event_kinds
        for parsed_event_date in [event_date(event_text(event), clinic=clinic)]
        if parsed_event_date is not None
        and 0 <= (clinic - parsed_event_date).days <= max_months * 31
    ]
    if not dates:
        return None
    return min(dates, key=lambda parsed_event_date: (clinic - parsed_event_date).days)


def nearest_event_month_year(
    events: Sequence[StructuredEventLike],
    *,
    clinic: tuple[int, int],
    event_kinds: set[str],
    max_months: int,
) -> tuple[int, int] | None:
    clinic_month, clinic_year = clinic
    dated = [
        parsed_event_month_year
        for event in events
        if event.kind in event_kinds
        for parsed_event_month_year in [
            event_month_year(event_text(event), clinic_year=clinic_year)
        ]
        if parsed_event_month_year is not None
        and 0
        <= (clinic_year - parsed_event_month_year[1]) * 12
        + (clinic_month - parsed_event_month_year[0])
        <= max_months
    ]
    if not dated:
        return None
    return min(
        dated,
        key=lambda item: (clinic_year - item[1]) * 12 + (clinic_month - item[0]),
    )


def elapsed_months_from_nearest_event_date(
    events: Sequence[StructuredEventLike],
    *,
    clinic: tuple[int, int],
    event_kinds: set[str],
    max_months: int,
) -> int | None:
    anchor = nearest_event_month_year(
        events,
        clinic=clinic,
        event_kinds=event_kinds,
        max_months=max_months,
    )
    if anchor is None:
        return None
    return elapsed_months(anchor, clinic)


def elapsed_months_from_nearest_event_date_precise(
    events: Sequence[StructuredEventLike],
    *,
    note_text: str | None,
    event_kinds: set[str],
    max_months: int,
) -> int | None:
    clinic = clinic_date(note_text or "")
    if clinic is None:
        return None
    nearest = nearest_event_date(
        events,
        clinic=clinic,
        event_kinds=event_kinds,
        max_months=max_months,
    )
    if nearest is None:
        return None
    days = (clinic - nearest).days
    if days <= 0:
        return None
    return max(1, (days + 29) // 30)


def duration_from_events(events: Sequence[StructuredEventLike]) -> str | None:
    for event in events:
        text = " ".join(part for part in (event.time_window, event.notes) if part)
        duration = duration_from_text(text)
        if duration:
            return duration
    return None


def duration_from_text(text: str) -> str | None:
    text = small_number_words_to_digits(text.lower())
    match = re.search(r"\b(?P<count>\d+)\s*(?:-|\s+)?(?P<unit>week|month|year)s?\b", text)
    if match:
        return f"{match.group('count')} {match.group('unit')}"
    return None


def duration_from_event_dates(
    events: Sequence[StructuredEventLike],
    note_text: str | None,
) -> str | None:
    clinic_anchor = clinic_month_year(note_text or "")
    if clinic_anchor is None:
        return None
    clinic_month, clinic_year = clinic_anchor
    event_month_years = [
        parsed_event_month_year
        for event in events
        for parsed_event_month_year in [
            event_month_year(
                " ".join(
                    part
                    for part in (event.evidence, event.raw_value, event.time_window, event.notes)
                    if part
                ),
                clinic_year=clinic_year,
            )
        ]
        if parsed_event_month_year is not None
    ]
    if not event_month_years:
        return None
    event_month, event_year = min(
        event_month_years,
        key=lambda item: abs((clinic_year - item[1]) * 12 + (clinic_month - item[0])),
    )
    months = (clinic_year - event_year) * 12 + (clinic_month - event_month)
    if months <= 0:
        return None
    return f"{months} month"
