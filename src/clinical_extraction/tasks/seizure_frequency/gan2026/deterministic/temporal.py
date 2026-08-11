from __future__ import annotations

import re
from dataclasses import dataclass

from clinical_extraction.tasks.shared.epilepsy.terms import (
    MONTH_ABBREVIATIONS,
    MONTH_NAME_PATTERN,
)


@dataclass(frozen=True)
class ParsedMonthDate:
    year: int
    month: int
    day: int | None = None


MONTH_YEAR_DATE_PATTERN = rf"(?:(?:{MONTH_NAME_PATTERN})|\d{{1,2}})\s*(?:[-/]\s*|\s+)\d{{4}}"


def clinic_date(text: str) -> ParsedMonthDate | None:
    match = re.search(
        rf"\b(?:Clinic Date:|Sent:|Date:)\s*(?P<day>\d{{1,2}})\s+"
        rf"(?P<month>{MONTH_NAME_PATTERN})\s+(?P<year>\d{{4}})\b",
        text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    return ParsedMonthDate(
        year=int(match.group("year")),
        month=month_number(match.group("month")),
        day=int(match.group("day")),
    )


def relative_note_date(
    value: str,
    anchor: ParsedMonthDate | None,
) -> ParsedMonthDate | None:
    normalized = value.strip()
    day_month = re.match(
        rf"(?P<day>\d{{1,2}})[-/ ](?P<month>{MONTH_NAME_PATTERN})$",
        normalized,
        flags=re.IGNORECASE,
    )
    if day_month is not None and anchor is not None:
        month = month_number(day_month.group("month"))
        year = anchor.year - 1 if month > anchor.month else anchor.year
        return ParsedMonthDate(year=year, month=month, day=int(day_month.group("day")))

    month_year = re.match(
        rf"(?P<month>{MONTH_NAME_PATTERN})[-/ ](?P<year>\d{{4}})$",
        normalized,
        flags=re.IGNORECASE,
    )
    if month_year is not None:
        return year_month_date(month_year.group("year"), month_year.group("month"))

    numeric_or_named_month_year = re.match(
        rf"(?P<month>(?:{MONTH_NAME_PATTERN})|\d{{1,2}})\s*[-/]\s*(?P<year>\d{{4}})$",
        normalized,
        flags=re.IGNORECASE,
    )
    if numeric_or_named_month_year is not None:
        return year_month_date(
            numeric_or_named_month_year.group("year"),
            numeric_or_named_month_year.group("month"),
        )

    month_only = re.match(
        rf"(?P<month>{MONTH_NAME_PATTERN})$",
        normalized,
        flags=re.IGNORECASE,
    )
    if month_only is not None and anchor is not None:
        month = month_number(month_only.group("month"))
        year = anchor.year - 1 if month > anchor.month else anchor.year
        return ParsedMonthDate(year=year, month=month)

    return None


def full_date(value: str) -> ParsedMonthDate | None:
    normalized = value.strip()
    numeric = re.match(
        r"(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4})$",
        normalized,
    )
    if numeric is not None:
        return ParsedMonthDate(
            year=int(numeric.group("year")),
            month=int(numeric.group("month")),
            day=int(numeric.group("day")),
        )

    day_named = re.match(
        rf"(?P<day>\d{{1,2}})[-\s](?P<month>{MONTH_NAME_PATTERN})[-\s](?P<year>\d{{4}})$",
        normalized,
        flags=re.IGNORECASE,
    )
    if day_named is not None:
        return ParsedMonthDate(
            year=int(day_named.group("year")),
            month=month_number(day_named.group("month")),
            day=int(day_named.group("day")),
        )
    return None


def year_month_date(year: str, month: str) -> ParsedMonthDate:
    return ParsedMonthDate(year=int(year), month=month_number(month))


def month_number(value: str) -> int:
    stripped = value.strip()
    if stripped.isdigit():
        return int(stripped)
    normalized = stripped.lower()[:3]
    return MONTH_ABBREVIATIONS[normalized]


def month_span(start: ParsedMonthDate | None, end: ParsedMonthDate | None) -> int | None:
    if start is None or end is None:
        return None
    months = (end.year - start.year) * 12 + end.month - start.month
    if months <= 0:
        return None
    return months


def month_span_floor(start: ParsedMonthDate | None, end: ParsedMonthDate | None) -> int | None:
    months = month_span(start, end)
    if months is None:
        return None
    if start is None or end is None:
        return None
    if start.day is not None and end.day is not None and end.day < start.day:
        months -= 1
    return months if months > 0 else None


def month_span_with_terminal_partial(
    start: ParsedMonthDate | None,
    end: ParsedMonthDate | None,
) -> int | None:
    months = month_span(start, end)
    if months is None:
        return None
    if start is None or end is None:
        return None
    if start.day is not None and end.day is not None and end.day > start.day:
        return months + 1
    return months


def month_span_inclusive(
    start: ParsedMonthDate | None,
    end: ParsedMonthDate | None,
) -> int | None:
    if start is None or end is None:
        return None
    months = (end.year - start.year) * 12 + end.month - start.month
    if months < 0:
        return None
    return months + 1
