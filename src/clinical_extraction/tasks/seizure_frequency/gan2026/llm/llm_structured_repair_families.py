"""Semantic repair-family helpers for Gan 2026 LLM structured-events output."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Protocol

from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_temporal import (
    clinic_date,
    clinic_month_year,
    duration_from_event_dates,
    duration_from_events,
    duration_from_text,
    elapsed_months,
    elapsed_months_from_nearest_event_date,
    elapsed_months_from_nearest_event_date_precise,
    event_month_year,
    event_text,
    month_number,
    nearest_event_date,
    nearest_event_month_year,
    small_number_words_to_digits,
)

from ..selected_evidence.selected_evidence_derivation import (
    evidence_describes_current_non_epileptic_events,
)


class StructuredRepairEventLike(Protocol):
    @property
    def event_id(self) -> str: ...

    @property
    def kind(self) -> str: ...

    @property
    def raw_value(self) -> str | None: ...

    @property
    def time_window(self) -> str | None: ...

    @property
    def temporality(self) -> str: ...

    @property
    def assertion_status(self) -> str: ...

    @property
    def evidence(self) -> str: ...

    @property
    def notes(self) -> str | None: ...


class StructuredRepairSelectionLike(Protocol):
    @property
    def selected_event_ids(self) -> Sequence[str]: ...

    @property
    def final_kind(self) -> str: ...

    @property
    def final_label(self) -> str | None: ...

    @property
    def evidence(self) -> str: ...

    @property
    def rationale(self) -> str: ...


class StructuredRepairExtractionLike(Protocol):
    @property
    def events(self) -> Sequence[StructuredRepairEventLike]: ...

    @property
    def selection(self) -> StructuredRepairSelectionLike: ...


def usual_interval_label_from_events(
    extraction: StructuredRepairExtractionLike,
    repaired_label: str,
) -> str | None:
    selected_text = " ".join(
        part
        for part in (
            extraction.selection.evidence,
            extraction.selection.rationale,
            extraction.selection.final_label,
        )
        if part
    ).lower()
    selected_is_brief_daily = (
        repaired_label in {"1 per day", "multiple per day", "unknown"}
        and re.search(r"\b(?:occasionally|brief periods?|periods? of)\b", selected_text)
        and re.search(r"\bdaily\b", selected_text)
    )
    for event in extraction.events:
        label = _interval_label_from_event_text(event_text(event))
        if not label:
            continue
        if repaired_label in {"unknown", "no seizure frequency reference"}:
            return label
        if selected_is_brief_daily:
            return label
    return None


def breakthrough_label_from_events(
    extraction: StructuredRepairExtractionLike,
    repaired_label: str,
) -> str | None:
    if repaired_label not in {"unknown", "no seizure frequency reference"}:
        return None
    joined_text = " ".join(event_text(event) for event in extraction.events)
    if re.search(r"\b(?:perimenstrual|catamenial|outside this window)\b", joined_text):
        return None
    duration = _seizure_free_duration_from_events(extraction.events)
    if duration is None:
        return None
    count = _recent_breakthrough_count(extraction)
    if count is None:
        return None
    return f"{count} per {duration}"


def non_epileptic_label_from_events(
    extraction: StructuredRepairExtractionLike,
    repaired_label: str,
) -> str | None:
    if repaired_label not in {"unknown", "no seizure frequency reference"}:
        return None
    selected_ids = set(extraction.selection.selected_event_ids)
    texts = [
        extraction.selection.evidence,
        extraction.selection.rationale,
        *(
            " ".join(part for part in (event.evidence, event.raw_value, event.notes) if part)
            for event in extraction.events
            if not selected_ids or event.event_id in selected_ids
        ),
        *(
            " ".join(part for part in (event.evidence, event.raw_value, event.notes) if part)
            for event in extraction.events
            if event.temporality in {"current", "recent"}
        ),
    ]
    if any(evidence_describes_current_non_epileptic_events(text.lower()) for text in texts if text):
        return "seizure free for multiple year"
    return None


def residual_jerk_label_from_events(
    extraction: StructuredRepairExtractionLike,
    repaired_label: str,
    *,
    note_text: str | None,
) -> str | None:
    if repaired_label not in {
        "unknown",
        "no seizure frequency reference",
        "multiple per month",
        "multiple per week",
    } and not re.search(r"\bper\s+(?:day|month)\b", repaired_label):
        return None
    clinic = clinic_date(note_text or "")
    clinic_month_year_value = clinic_month_year(note_text or "")
    if clinic is None and clinic_month_year_value is None:
        return None
    anchor = (
        nearest_event_date(
            extraction.events,
            clinic=clinic,
            event_kinds={"last_event_only", "seizure_free"},
            max_months=240,
        )
        if clinic is not None
        else None
    )
    month_anchor = (
        nearest_event_month_year(
            extraction.events,
            clinic=clinic_month_year_value,
            event_kinds={"last_event_only", "seizure_free"},
            max_months=240,
        )
        if clinic_month_year_value is not None
        else None
    )
    if anchor is None and month_anchor is None:
        return None
    months = (
        elapsed_months(month_anchor, clinic_month_year_value)
        if month_anchor is not None and clinic_month_year_value is not None
        else None
    )
    if months is None and anchor is not None and clinic is not None:
        months = max(1, ((clinic - anchor).days + 29) // 30)
    if months is None:
        return None
    selected_ids = set(extraction.selection.selected_event_ids)
    for event in extraction.events:
        if event.kind not in {"frequency_rate", "cluster_frequency"}:
            continue
        if selected_ids and event.event_id not in selected_ids:
            continue
        text = event_text(event)
        if not re.search(r"\b(?:jerks?|myoclonic)\b", text):
            continue
        if not re.search(r"\b(?:remain|persist|persisting|since then)\b", text):
            continue
        if "cluster" in text:
            return f"multiple cluster per {months} month, multiple per cluster"
        count = _count_from_event_text(text)
        if count:
            return f"{count} per {months} month"
    return None


def post_change_burst_label_from_events(
    extraction: StructuredRepairExtractionLike,
    repaired_label: str,
    *,
    note_text: str | None = None,
) -> str | None:
    if "seizure free" not in repaired_label and not re.search(
        r"\bper\s+(?:week|day)\b",
        repaired_label,
    ):
        return None
    selection_text = " ".join(
        part
        for part in (
            extraction.selection.final_label,
            extraction.selection.evidence,
            extraction.selection.rationale,
        )
        if part
    ).lower()
    marker_text = " ".join(
        [
            selection_text,
            *(
                " ".join(part for part in (event.evidence, event.raw_value, event.notes) if part)
                for event in extraction.events
                if event.kind == "seizure_free"
            ),
        ]
    )
    if not re.search(
        r"\b(?:since then|no further|not had any further|had no seizures since|"
        r"without seizures since|remained seizure-free since|remained stable without)\b",
        marker_text,
    ):
        return None
    duration = (
        duration_from_text(selection_text)
        or duration_from_events(extraction.events)
        or duration_from_event_dates(extraction.events, note_text)
    )
    if duration is None:
        return None
    count = _post_change_burst_count(extraction.events)
    if count is None:
        return None
    return f"{count} per {duration}"


def elapsed_since_anchor_label_from_events(
    extraction: StructuredRepairExtractionLike,
    repaired_label: str,
    *,
    note_text: str | None = None,
) -> str | None:
    clinic = clinic_month_year(note_text or "")
    if clinic is None:
        return None
    count_label = _since_anchor_count_label(extraction, clinic)
    if count_label:
        return count_label
    if "seizure free" not in repaired_label:
        return None
    if not _has_benchmark_last_event_context(extraction.events, note_text=note_text):
        return None
    marker_text = " ".join(
        part
        for part in (
            extraction.selection.evidence,
            extraction.selection.rationale,
            extraction.selection.final_label,
            *(
                event.evidence
                for event in extraction.events
                if event.kind in {"seizure_free", "last_event_only"}
            ),
        )
        if part
    ).lower()
    if not re.search(
        r"\b(?:last|most recent)\s+(?:event|episode|seizure)|"
        r"\b(?:remained|been|has been)\s+(?:well|stable|seizure-free)|"
        r"\bno further\b",
        marker_text,
    ):
        return None
    months = elapsed_months_from_nearest_event_date_precise(
        extraction.events,
        note_text=note_text,
        event_kinds={"last_event_only", "seizure_free"},
        max_months=18,
    ) or elapsed_months_from_nearest_event_date(
        extraction.events,
        clinic=clinic,
        event_kinds={"last_event_only", "seizure_free"},
        max_months=18,
    )
    if months is None:
        return None
    return f"1 per {months} month"


def _distinct_dated_months(
    mentions: list[tuple[int, int, int]],
) -> list[tuple[int, int, int]]:
    """Collapse repeated same-month mentions; keep one entry per calendar month."""
    by_month: dict[tuple[int, int], int] = {}
    for month, year, count in mentions:
        key = (month, year)
        by_month[key] = max(by_month.get(key, 0), count)
    return [(month, year, count) for (month, year), count in by_month.items()]


def dated_sequence_label_from_events(
    extraction: StructuredRepairExtractionLike,
    repaired_label: str,
    *,
    note_text: str | None = None,
) -> str | None:
    texts = [
        " ".join(part for part in (event.evidence, event.raw_value, event.time_window) if part)
        for event in extraction.events
    ]
    raw_joined = " ".join(texts).lower()
    if "prior to this improvement" in raw_joined:
        return None
    explicit = re.search(
        r"\b(?P<count>\d+)\s+(?:seizures?|events?|episodes?)\s+"
        r"(?:in|within)\s+(?P<months>\d+)\s+months?\b",
        small_number_words_to_digits(raw_joined),
    )
    if not explicit:
        explicit = re.search(
            r"\b(?P<count>\d+)\s+(?:in|within)\s+(?P<months>\d+)\s+months?\b",
            small_number_words_to_digits(raw_joined),
        )
    if explicit:
        if not _dated_sequence_can_override(repaired_label, int(explicit.group("months"))):
            return None
        return f"{explicit.group('count')} per {explicit.group('months')} month"

    dated_events = _distinct_dated_months(
        [mention for text in texts for mention in _dated_event_mentions(text)]
    )
    # When events only repeat one calendar month (or omit dates), mine the note.
    if (
        len(dated_events) < 2
        and note_text
        and repaired_label in {"unknown", "no seizure frequency reference"}
    ):
        dated_events = _distinct_dated_months(_dated_event_mentions(note_text))
    if len(dated_events) < 2:
        return None
    first_month, first_year, _ = min(dated_events, key=lambda item: item[1] * 12 + item[0])
    last_month, last_year, max_count = max(
        dated_events,
        key=lambda item: (item[1] * 12 + item[0], item[2]),
    )
    months = (last_year - first_year) * 12 + (last_month - first_month)
    if months <= 0:
        return None
    if not _dated_sequence_can_override(repaired_label, months):
        return None
    if "seizure free" in repaired_label and not _dated_sequence_is_near_clinic(
        last_month,
        last_year,
        note_text,
    ):
        return None
    count = max(item[2] for item in dated_events)
    if count < 2:
        count = len(dated_events)
    return f"{count} per {months} month"


def typical_recurring_rate_over_ytd_from_events(
    extraction: StructuredRepairExtractionLike,
    repaired_label: str,
) -> str | None:
    """Prefer typical/usual recurring rate over a year-to-date observation total.

    Portability: ``seizure_frequency``. Applies only when selection or the current
    label is an observation-window / so-far-this-year total and another event
    already states a typical recurring rate.
    """
    selection_text = " ".join(
        part
        for part in (
            extraction.selection.final_label,
            extraction.selection.evidence,
            extraction.selection.rationale,
            repaired_label,
        )
        if part
    ).lower()
    selection_text = small_number_words_to_digits(selection_text)
    is_ytd_selection = bool(
        re.search(
            r"\b(?:so\s+far\s+this\s+year|this\s+year\s+to\s+date|"
            r"year\s+to\s+date|\d{4}\s+so\s+far)\b",
            selection_text,
        )
    )
    # Require explicit YTD language in selection; do not treat every multi-month
    # observation total as interchangeable with a typical recurring rate.
    if not is_ytd_selection:
        return None

    for event in extraction.events:
        text = small_number_words_to_digits(event_text(event).lower())
        if not re.search(r"\b(?:typical(?:ly)?|usual(?:ly)?|at present)\b", text):
            continue
        monthly = re.search(
            r"\b(?:a|one|1)?\s*(?:focal\s+)?seizure\s+monthly\b",
            text,
        ) or re.search(
            r"\b(?:typically|usually)\s+(?P<count>\d+(?:\s*to\s*\d+)?)\s+"
            r"(?:[a-z-]+\s+){0,4}(?:seizures?|events?|episodes?)\s+monthly\b",
            text,
        )
        if monthly:
            if monthly.lastindex and monthly.groupdict().get("count"):
                return f"{monthly.group('count')} per month"
            return "1 per month"
        weekly = re.search(
            r"\b(?:a|one|1)?\s*(?:focal\s+)?seizure\s+weekly\b",
            text,
        ) or re.search(
            r"\b(?:typically|usually)\s+(?P<count>\d+(?:\s*to\s*\d+)?)\s+"
            r"(?:[a-z-]+\s+){0,4}(?:seizures?|events?|episodes?)\s+weekly\b",
            text,
        )
        if weekly:
            if weekly.lastindex and weekly.groupdict().get("count"):
                return f"{weekly.group('count')} per week"
            return "1 per week"
        per_month = re.search(
            r"\b(?:typically|usually|at present).{0,40}?"
            r"(?P<count>\d+(?:\s*to\s*\d+)?|multiple)\s+per\s+month\b",
            text,
        )
        if per_month:
            return f"{per_month.group('count')} per month"
    return None


def _interval_label_from_event_text(text: str) -> str | None:
    normalized = small_number_words_to_digits(text.lower())
    interval = r"\d+(?:\s*(?:to|-|–|—)\s*\d+)?|multiple|several"
    match = (
        re.search(
            rf"\b(?:approximately\s+|about\s+|around\s+)?every\s+"
            rf"(?P<interval>{interval})\s+days?\b",
            normalized,
        )
        or re.search(
            rf"\b(?:spaced|spacing)\s+(?P<interval>{interval})\s+days?\s+apart\b",
            normalized,
        )
        or re.search(
            rf"\b(?P<interval>{interval})\s+days?\s+apart\b",
            normalized,
        )
    )
    if not match:
        return None
    interval_text = re.sub(r"\s*(?:-|–|—)\s*", " to ", match.group("interval"))
    interval_text = "multiple" if interval_text == "several" else interval_text
    return f"1 per {interval_text} day"


def _post_change_burst_count(events: Sequence[StructuredRepairEventLike]) -> str | None:
    for event in events:
        text = " ".join(
            part
            for part in (event.evidence, event.raw_value, event.time_window, event.notes)
            if part
        ).lower()
        if event.kind not in {"frequency_rate", "cluster_frequency"}:
            continue
        if not re.search(
            r"\b(?:shortly afterwards?|soon afterwards?|following week|around that period|"
            r"at that time|then)\b",
            text,
        ):
            continue
        text = small_number_words_to_digits(text)
        range_match = re.search(r"\b(?P<low>\d+)\s*(?:to|-|–|—)\s*(?P<high>\d+)\b", text)
        if range_match:
            return f"{range_match.group('low')} to {range_match.group('high')}"
        count_match = re.search(
            r"\b(?P<count>\d+)\s+(?:[a-z-]+\s+){0,4}"
            r"(?:seizures?|events?|attacks?|convulsions?)\b",
            text,
        )
        if count_match:
            return count_match.group("count")
        if re.search(r"\b(?:several|multiple|many)\s+(?:seizures?|events?|attacks?)\b", text):
            return "multiple"
    return None


def _has_benchmark_last_event_context(
    events: Sequence[StructuredRepairEventLike],
    *,
    note_text: str | None,
) -> bool:
    text = " ".join(event_text(event) for event in events)
    if _has_treatment_improvement_context(text):
        return True
    return bool(note_text and _has_treatment_improvement_context(note_text.lower()))


def _has_treatment_improvement_context(text: str) -> bool:
    return bool(
        re.search(
            r"\babsences?\b.{0,80}\b(?:improved|reduced|diminished|settled|became less frequent)\b",
            text,
        )
        or re.search(
            r"\b(?:following|after|with)\b.{0,80}"
            r"\b(?:medication|treatment|dose|lamotrigine|levetiracetam|supportive care|"
            r"prescribed medication)\b",
            text,
        )
        or re.search(
            r"\b(?:medication|treatment|dose|lamotrigine|levetiracetam|supportive care|"
            r"prescribed medication)\b.{0,80}"
            r"\b(?:improved|reduced|diminished|settled|became less frequent)\b",
            text,
        )
    )


def _since_anchor_count_label(
    extraction: StructuredRepairExtractionLike,
    clinic: tuple[int, int],
) -> str | None:
    selected_ids = set(extraction.selection.selected_event_ids)
    candidate_events = [
        event
        for event in extraction.events
        if event.kind in {"frequency_rate", "cluster_frequency"}
        and event.assertion_status == "asserted"
        and (not selected_ids or event.event_id in selected_ids)
    ]
    if extraction.selection.final_kind in {"unknown", "no_reference", "seizure_free"}:
        candidate_events.extend(
            event
            for event in extraction.events
            if event.kind in {"frequency_rate", "cluster_frequency"}
            and event.assertion_status == "asserted"
            and event.event_id not in selected_ids
        )
    for event in candidate_events:
        text = event_text(event)
        if not re.search(r"\bsince\b", text):
            continue
        if not re.search(r"\bjerks?\b", text):
            continue
        if not re.search(
            r"\bsince\s+(?:then|\d|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
            text,
        ):
            continue
        count = _count_from_event_text(text)
        if count is None:
            continue
        anchor = event_month_year(text, clinic_year=clinic[1])
        if anchor is None:
            anchor = nearest_event_month_year(
                extraction.events,
                clinic=clinic,
                event_kinds={"last_event_only"},
                max_months=18,
            )
        if anchor is None:
            continue
        months = elapsed_months(anchor, clinic)
        if months is None or months <= 0 or months > 18:
            continue
        return f"{count} per {months} month"
    return None


def _count_from_event_text(text: str) -> str | None:
    text = small_number_words_to_digits(text.lower())
    count = r"\d+(?:\s*(?:to|-|–|—|or)\s*\d+)?"
    match = re.search(
        rf"\b(?P<count>{count})\s+(?:[a-z-]+\s+){{0,4}}"
        r"(?:jerks?|seizures?|events?|episodes?|attacks?|convulsions?)\b",
        text,
    )
    if not match:
        return None
    return re.sub(r"\s*(?:-|–|—|or)\s*", " to ", match.group("count"))


def _dated_sequence_can_override(repaired_label: str, months: int) -> bool:
    if repaired_label in {"unknown", "no seizure frequency reference"}:
        return True
    if "seizure free" in repaired_label:
        return True
    if re.search(r"\bper\s+(?:\d+(?:\s+to\s+\d+)?\s+)?(?:day|week)\b", repaired_label):
        return False
    if re.search(r"\bper\s+(?:\d+(?:\s+to\s+\d+)?\s+)?(?:month|year)\b", repaired_label):
        return months > 1
    return False


def _dated_sequence_is_near_clinic(
    last_month: int,
    last_year: int,
    note_text: str | None,
) -> bool:
    clinic = clinic_month_year(note_text or "")
    if clinic is None:
        return False
    clinic_month, clinic_year = clinic
    elapsed = (clinic_year - last_year) * 12 + (clinic_month - last_month)
    return 0 <= elapsed <= 18


def _dated_event_mentions(text: str) -> list[tuple[int, int, int]]:
    text = small_number_words_to_digits(text.lower())
    month_pattern = (
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
    )
    ordinal_count = {
        "initial": 1,
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
    }
    mentions: list[tuple[int, int, int]] = []
    last_year: int | None = None
    for match in re.finditer(
        rf"\b(?P<ordinal>initial|first|second|third|fourth|fifth)(?:\s+and\s+"
        rf"(?P<ordinal2>second|third|fourth|fifth))?\s+"
        rf"(?:seizure|event)\w*.*?\b(?P<month>{month_pattern})\s+(?P<year>\d{{4}})?",
        text,
    ):
        year = int(match.group("year")) if match.group("year") else last_year
        if year is None:
            continue
        last_year = year
        count = ordinal_count[match.group("ordinal2") or match.group("ordinal")]
        mentions.append((month_number(match.group("month")), year, count))
    for match in re.finditer(
        rf"\bnext\s+(?P<additional>\d+)\s+(?:seizure|event)\w*.*?"
        rf"\b(?P<month>{month_pattern})\s+(?P<year>\d{{4}})?",
        text,
    ):
        year = int(match.group("year")) if match.group("year") else last_year
        if year is None:
            continue
        last_year = year
        mentions.append(
            (month_number(match.group("month")), year, 1 + int(match.group("additional")))
        )
    return mentions


def _seizure_free_duration_from_events(
    events: Sequence[StructuredRepairEventLike],
) -> str | None:
    for event in events:
        text = " ".join(
            part for part in (event.raw_value, event.evidence, event.time_window) if part
        ).lower()
        if (
            event.kind != "seizure_free"
            and "seizure-free" not in text
            and "seizure free" not in text
        ):
            continue
        text = small_number_words_to_digits(text)
        match = re.search(r"\b(?:for\s+)?(?P<count>\d+)\s+(?P<unit>month|year)s?\b", text)
        if match:
            return f"{match.group('count')} {match.group('unit')}"
        if re.search(r"\b(?:nearly|almost|about|around)?\s*a\s+year\b", text):
            return "1 year"
    return None


def _recent_breakthrough_count(extraction: StructuredRepairExtractionLike) -> str | None:
    text = " ".join(
        part
        for part in (
            extraction.selection.final_label,
            extraction.selection.evidence,
            extraction.selection.rationale,
            *(
                event.evidence
                for event in extraction.events
                if event.event_id in set(extraction.selection.selected_event_ids)
            ),
        )
        if part
    ).lower()
    text = small_number_words_to_digits(text)
    range_match = re.search(r"\b(?P<low>\d+)\s*(?:to|-|–|—)\s*(?P<high>\d+)\b", text)
    if range_match:
        return f"{range_match.group('low')} to {range_match.group('high')}"
    count_match = re.search(
        r"\b(?P<count>\d+)\s+(?:tonic|generalised|generalized|focal|seizures?|events?)",
        text,
    )
    if count_match:
        return count_match.group("count")
    if re.search(r"\bcluster\b", text) and re.search(r"\b(?:preceded|plus|and)\b", text):
        return "2"
    if re.search(r"\b(?:a|single|1)\s+(?:focal|generalised|generalized|tonic|event|seizure)", text):
        return "1"
    return None
