"""Monthly-diary repair helpers for Gan 2026 LLM structured-events output."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Protocol

from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_temporal import (
    clinic_month_year,
    month_number,
    small_number_words_to_digits,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.post_stack_fix_flags import (
    post_stack_fix_flags,
)

from ..selected_evidence._shared_tokens import GAP_WORDS_TOKEN
from ..selected_evidence.selected_evidence_monthly_diary import (
    _date_list_diary_label_from_selected_evidence,
    monthly_diary_label_from_text,
)

MonthlyDiaryMonthKey = tuple[int, int | None]
_MONTHLY_DIARY_EVENT_KINDS = {
    "frequency_rate",
    "cluster_frequency",
    "seizure_free",
    "last_event_only",
}


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
    flags = post_stack_fix_flags()
    if flags.date_list_span:
        for event in extraction.events:
            if not _is_monthly_diary_event(event):
                continue
            date_list_label = _date_list_diary_label_from_selected_evidence(
                small_number_words_to_digits(_event_text(event))
            )
            if date_list_label:
                return date_list_label

    merged: dict[MonthlyDiaryMonthKey, tuple[int, str, frozenset[str]]] = {}
    for event in extraction.events:
        if not _is_monthly_diary_event(event):
            continue
        event_text = _event_text(event)
        cover_text = (event.evidence or event_text).lower()
        states = _diary_state_terms(event_text)
        for month_key, count in _monthly_diary_event_counts(event, note_text=note_text).items():
            if flags.diary_sum_all_months:
                _merge_diary_month_count(merged, month_key, count, cover_text, states)
            else:
                merged.setdefault(month_key, (count, cover_text, states))
    counts_by_month = {key: value[0] for key, value in merged.items()}

    if len(counts_by_month) >= 2:
        total = sum(counts_by_month.values())
        months = _monthly_diary_span_months(counts_by_month)
        return f"{total} per {months} month"

    for event in extraction.events:
        if event.kind not in _MONTHLY_DIARY_EVENT_KINDS:
            continue
        text = _event_text(event)
        label = monthly_diary_label_from_text(text)
        if label:
            return label
    return None


def _is_monthly_diary_event(event: StructuredMonthlyDiaryEventLike) -> bool:
    return (
        event.kind in _MONTHLY_DIARY_EVENT_KINDS
        and event.assertion_status in {"asserted", "historical"}
    )


_DIARY_STATE_TERMS = (
    "sleep",
    "asleep",
    "night",
    "nocturnal",
    "awake",
    "waking",
    "daytime",
    "day",
)


def _diary_state_terms(text: str) -> frozenset[str]:
    return frozenset(
        match.group(0)
        for match in re.finditer(
            rf"\b(?:{'|'.join(_DIARY_STATE_TERMS)})\b",
            text,
        )
    )


def _merge_diary_month_count(
    merged: dict[MonthlyDiaryMonthKey, tuple[int, str, frozenset[str]]],
    month_key: MonthlyDiaryMonthKey,
    count: int,
    source_text: str,
    states: frozenset[str],
) -> None:
    if month_key not in merged:
        merged[month_key] = (count, source_text, states)
        return
    old_count, old_text, old_states = merged[month_key]
    if source_text in old_text or old_text in source_text:
        if len(source_text) > len(old_text) or (
            len(source_text) == len(old_text) and count > old_count
        ):
            merged[month_key] = (count, source_text, states)
        return
    if old_states < states and count >= old_count:
        merged[month_key] = (count, source_text, states)
        return
    if states < old_states and old_count >= count:
        return
    if states and old_states and states.isdisjoint(old_states):
        merged[month_key] = (
            old_count + count,
            f"{old_text} {source_text}",
            old_states | states,
        )


def _monthly_diary_event_counts(
    event: StructuredMonthlyDiaryEventLike,
    *,
    note_text: str | None,
) -> dict[MonthlyDiaryMonthKey, int]:
    flags = post_stack_fix_flags()
    joined_text = small_number_words_to_digits(_event_text(event))
    if flags.date_list_span and _date_list_diary_label_from_selected_evidence(joined_text):
        return {}
    count_source = event.evidence or event.raw_value or event.notes or ""
    text = small_number_words_to_digits(count_source.lower())
    if flags.date_list_span:
        text = re.sub(r"\b\d{2}-\d{2}\b", " ", text)
    month_pattern = (
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
        r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
        r"nov(?:ember)?|dec(?:ember)?"
    )
    state_count = _monthly_diary_state_count(text)
    month_key = _monthly_diary_event_month(event)
    skip_collapsed_state = flags.diary_sum_all_months and len(_month_stems(text)) >= 2
    if state_count is not None and month_key is not None and not skip_collapsed_state:
        return {month_key: state_count}
    count_terms = r"\d+|no|zero|a|an"
    med_unit_filter = r"(?!\s*(?:mg|mcg|g|ml|tablets?|pills?|capsules?|doses?|prn|bd|tds|qds)\b)"
    counts: dict[MonthlyDiaryMonthKey, int] = {}
    in_month_bridge = (
        r"(?:were\s+)?(?:so\s+far\s+)?" if flags.diary_sum_all_months else ""
    )

    for match in re.finditer(
        rf"\b(?P<count>{count_terms}){med_unit_filter}\s+"
        rf"(?:{GAP_WORDS_TOKEN}(?:seizures?|events?|convulsions?)\s+)?"
        rf"{in_month_bridge}in\s+(?:early|mid|late)?\s*(?P<month>{month_pattern})"
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
        rf"(?P<count>{count_terms}){med_unit_filter}\s+"
        rf"{GAP_WORDS_TOKEN}"
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
        rf"\b(?P<count>{count_terms}){med_unit_filter}\s+"
        rf"{GAP_WORDS_TOKEN}"
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
        if post_stack_fix_flags().date_list_span:
            text = re.sub(r"\b\d{2}-\d{2}\b", " ", text)
        state_count = _monthly_diary_state_count(text)
        if state_count is not None:
            return state_count
        event_count = re.search(
            r"\b(?P<count>\d+|a|an|no|zero)\s+"
            rf"{GAP_WORDS_TOKEN}"
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
    med_unit_filter = r"(?!\s*(?:mg|mcg|g|ml|tablets?|pills?|capsules?|doses?|prn|bd|tds|qds)\b)"
    counts: list[int] = []
    for pattern in (
        rf"\b(?P<count>{count_terms}){med_unit_filter}\s+(?!in\s+)(?:\w+\s+){{0,3}}(?:{state_terms})\b",
        rf"\b(?P<count>{count_terms}){med_unit_filter}\s+in\s+(?:{state_terms})\b",
    ):
        for match in re.finditer(pattern, text):
            count = _monthly_diary_count_value(match.group("count"))
            if count <= 100:
                counts.append(count)
    if counts:
        return sum(counts)
    return None


def _month_stems(text: str) -> set[str]:
    return {
        match.group(0)[:3].lower()
        for match in re.finditer(
            r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
            r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
            r"nov(?:ember)?|dec(?:ember)?)\b",
            text.lower(),
        )
    }


def _monthly_diary_event_month_text(text: str) -> bool:
    return bool(_month_stems(text))


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
    if not keys:
        return 0
    if all(year is not None for _, year in keys):
        ordinals = [year * 12 + month for month, year in keys if year is not None]
        return max(ordinals) - min(ordinals) + 1
    months = {month for month, _ in keys}
    if not months:
        return 0
    spans = [1 + max((m - start) % 12 for m in months) for start in months]
    return min(spans)


def _event_text(event: StructuredMonthlyDiaryEventLike) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for part in (event.evidence, event.raw_value, event.time_window, event.notes):
        if not part:
            continue
        key = part.lower().strip()
        if key in seen:
            continue
        seen.add(key)
        parts.append(part)
    return " ".join(parts).lower()
