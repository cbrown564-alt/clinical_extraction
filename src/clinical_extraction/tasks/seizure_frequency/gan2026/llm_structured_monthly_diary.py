"""Monthly-diary repair helpers for Gan 2026 LLM structured-events output."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Protocol

from clinical_extraction.tasks.seizure_frequency.gan2026.llm_structured_temporal import (
    clinic_month_year,
    month_number,
    small_number_words_to_digits,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence_derivation import (
    monthly_diary_label_from_text,
)

MonthlyDiaryMonthKey = tuple[int, int | None]


class StructuredMonthlyDiaryEventLike(Protocol):
    @property
    def kind(self) -> str: ...

    @property
    def assertion_status(self) -> str: ...

    @property
    def evidence(self) -> str: ...

    @property
    def raw_value(self) -> str | None: ...

    @property
    def time_window(self) -> str | None: ...

    @property
    def notes(self) -> str | None: ...


class StructuredMonthlyDiaryExtractionLike(Protocol):
    @property
    def events(self) -> Sequence[StructuredMonthlyDiaryEventLike]: ...


def monthly_diary_label_from_events(
    extraction: StructuredMonthlyDiaryExtractionLike,
    *,
    note_text: str | None,
) -> str | None:
    counts_by_month: dict[MonthlyDiaryMonthKey, int] = {}
    for event in extraction.events:
        if event.kind not in {
            "frequency_rate",
            "cluster_frequency",
            "seizure_free",
            "last_event_only",
        }:
            continue
        if event.assertion_status not in {"asserted", "historical"}:
            continue
        for month_key, count in _monthly_diary_event_counts(event, note_text=note_text).items():
            counts_by_month.setdefault(month_key, count)

    if len(counts_by_month) >= 2:
        total = sum(counts_by_month.values())
        months = _monthly_diary_span_months(counts_by_month)
        return f"{total} per {months} month"

    for event in extraction.events:
        if event.kind not in {
            "frequency_rate",
            "cluster_frequency",
            "seizure_free",
            "last_event_only",
        }:
            continue
        text = _event_text(event)
        label = monthly_diary_label_from_text(text)
        if label:
            return label
    return None


def _monthly_diary_event_counts(
    event: StructuredMonthlyDiaryEventLike,
    *,
    note_text: str | None,
) -> dict[MonthlyDiaryMonthKey, int]:
    text = small_number_words_to_digits(
        next(
            (
                part
                for part in (event.evidence, event.raw_value, event.notes)
                if part and _monthly_diary_event_month_text(part)
            ),
            " ".join(part for part in (event.evidence, event.raw_value, event.notes) if part),
        ).lower()
    )
    state_count = _monthly_diary_state_count(text)
    month_key = _monthly_diary_event_month(event)
    if state_count is not None and month_key is not None:
        return {month_key: state_count}

    month_pattern = (
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
        r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
        r"nov(?:ember)?|dec(?:ember)?"
    )
    count_terms = r"\d+|no|zero|a|an"
    counts: dict[MonthlyDiaryMonthKey, int] = {}

    for match in re.finditer(
        rf"\b(?P<count>{count_terms})\s+"
        r"(?:(?:[a-z]+(?:-[a-z]+)?\s+){0,4}(?:seizures?|events?|convulsions?)\s+)?"
        rf"in\s+(?:early|mid|late)?\s*(?P<month>{month_pattern})"
        rf"(?:\s+(?P<year>\d{{4}}))?\b",
        text,
    ):
        count = _monthly_diary_count_value(match.group("count"))
        if count <= 100:
            counts.setdefault(
                _monthly_diary_month_key(match.group("month"), match.group("year"), event),
                count,
            )
    for match in re.finditer(
        rf"\bin\s+(?:early|mid|late)?\s*(?P<month>{month_pattern})"
        rf"(?:\s+(?P<year>\d{{4}}))?\b[^.;]*?\b"
        rf"(?P<count>{count_terms})\s+"
        r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizures?|events?|convulsions?|absences?|attacks?|jerks?)\b",
        text,
    ):
        count = _monthly_diary_count_value(match.group("count"))
        if count <= 100:
            counts.setdefault(
                _monthly_diary_month_key(match.group("month"), match.group("year"), event),
                count,
            )
    for match in re.finditer(
        rf"\b(?P<count>{count_terms})\s+"
        r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizures?|events?|convulsions?|absences?|attacks?|jerks?)\s+"
        rf"(?:in\s+)?(?:early|mid|late)?\s*(?P<month>{month_pattern})"
        rf"(?:\s+(?P<year>\d{{4}}))?\b",
        text,
    ):
        count = _monthly_diary_count_value(match.group("count"))
        if count <= 100:
            counts.setdefault(
                _monthly_diary_month_key(match.group("month"), match.group("year"), event),
                count,
            )

    this_month_count = _monthly_diary_this_month_count(text)
    if this_month_count is not None:
        month_key = _monthly_diary_this_month_key(note_text, counts)
        if month_key is not None:
            counts.setdefault(month_key, this_month_count)

    if counts:
        return counts

    month_key = _monthly_diary_event_month(event)
    event_count = _monthly_diary_event_count(event)
    if month_key is not None and event_count is not None:
        return {month_key: event_count}
    return {}


def _monthly_diary_month_key(
    month_text: str,
    year_text: str | None,
    event: StructuredMonthlyDiaryEventLike,
) -> MonthlyDiaryMonthKey:
    month = month_number(month_text)
    if year_text:
        return month, int(year_text)
    inferred = _monthly_diary_event_month(event)
    if inferred and inferred[0] == month and inferred[1] is not None:
        return month, inferred[1]
    return month, None


def _monthly_diary_this_month_count(text: str) -> int | None:
    match = re.search(
        r"\b(?:(?:this\s+month|as\s+of\s+this\s+month)\b[^.;]*?\b"
        r"(?P<count1>\d+|no|zero|a|an)\s+(?:seizures?|events?|convulsions?)|"
        r"(?P<count2>\d+|no|zero|a|an)\s+(?:seizures?|events?|convulsions?)"
        r"\s+so\s+far\s+this\s+month)\b",
        text,
    )
    if not match:
        return None
    return _monthly_diary_count_value(match.group("count1") or match.group("count2"))


def _monthly_diary_this_month_key(
    note_text: str | None,
    existing_counts: Mapping[MonthlyDiaryMonthKey, int],
) -> MonthlyDiaryMonthKey | None:
    clinic = clinic_month_year(note_text or "")
    if clinic is not None:
        return clinic
    dated = [(month, year) for month, year in existing_counts if year is not None]
    if dated:
        latest_month, latest_year = max(dated, key=lambda item: item[1] * 12 + item[0])
        next_month = latest_month + 1
        next_year = latest_year
        if next_month > 12:
            next_month = 1
            next_year += 1
        return next_month, next_year
    month_only = [month for month, _ in existing_counts]
    if month_only:
        next_month = max(month_only) + 1
        return (1 if next_month > 12 else next_month), None
    return None


def _monthly_diary_event_month(
    event: StructuredMonthlyDiaryEventLike,
) -> tuple[int, int | None] | None:
    text = " ".join(part for part in (event.time_window, event.evidence, event.raw_value) if part)
    match = re.search(
        r"\b(?P<month>jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
        r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
        r"nov(?:ember)?|dec(?:ember)?)(?:\s+(?P<year>\d{4}))?\b",
        text.lower(),
    )
    if not match:
        return None
    month = month_number(match.group("month"))
    year = int(match.group("year")) if match.group("year") else None
    return month, year


def _monthly_diary_event_count(event: StructuredMonthlyDiaryEventLike) -> int | None:
    candidates = [
        part
        for part in (event.evidence, event.raw_value, event.notes)
        if part and _monthly_diary_event_month_text(part)
    ]
    candidates.append(
        " ".join(part for part in (event.evidence, event.raw_value, event.notes) if part)
    )
    for candidate in candidates:
        text = small_number_words_to_digits(candidate.lower())
        state_count = _monthly_diary_state_count(text)
        if state_count is not None:
            return state_count
        event_count = re.search(
            r"\b(?P<count>\d+|a|an|no|zero)\s+"
            r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
            r"(?:seizures?|events?|convulsions?|absences?|attacks?|jerks?)\b",
            text,
        )
        if event_count:
            count = _monthly_diary_count_value(event_count.group("count"))
            return count if count <= 100 else None
    return None


def _monthly_diary_state_count(text: str) -> int | None:
    state_terms = r"sleep|asleep|night|nocturnal|awake|waking|daytime|day"
    count_terms = r"\d+|no|zero|a|an"
    counts: list[int] = []
    for pattern in (
        rf"\b(?P<count>{count_terms})\s+(?!in\s+)(?:\w+\s+){{0,3}}(?:{state_terms})\b",
        rf"\b(?P<count>{count_terms})\s+in\s+(?:{state_terms})\b",
    ):
        for match in re.finditer(pattern, text):
            count = _monthly_diary_count_value(match.group("count"))
            if count <= 100:
                counts.append(count)
    if counts:
        return sum(counts)
    return None


def _monthly_diary_event_month_text(text: str) -> bool:
    return bool(
        re.search(
            r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
            r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
            r"nov(?:ember)?|dec(?:ember)?)\b",
            text.lower(),
        )
    )


def _monthly_diary_count_value(count_text: str) -> int:
    if count_text in {"a", "an"}:
        return 1
    if count_text in {"no", "zero"}:
        return 0
    return int(count_text)


def _monthly_diary_span_months(
    counts_by_month: Mapping[MonthlyDiaryMonthKey, int],
) -> int:
    keys = list(counts_by_month)
    if all(year is not None for _, year in keys):
        ordinals = [year * 12 + month for month, year in keys if year is not None]
        return max(ordinals) - min(ordinals) + 1
    months = sorted({month for month, _ in keys})
    if not months:
        return 0
    linear_span = max(months) - min(months) + 1
    if linear_span > 6:
        return (12 - max(months)) + min(months) + 1
    return linear_span


def _event_text(event: StructuredMonthlyDiaryEventLike) -> str:
    return " ".join(
        part
        for part in (event.evidence, event.raw_value, event.time_window, event.notes)
        if part
    ).lower()
