"""Last-event + short well-since select rewrite.

Family: last_event_well_since. Portability: seizure_frequency.
"""

from __future__ import annotations

from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    DEFAULT_SEMANTIC_FAMILY_ORDER,
    StructuredRepairConfig,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families import (
    last_event_well_since_label_from_events,
)


def _event(
    *,
    kind: str,
    raw_value: str | None = None,
    evidence: str = "",
    time_window: str | None = None,
    notes: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        event_id="e1",
        kind=kind,
        raw_value=raw_value,
        evidence=evidence,
        time_window=time_window,
        notes=notes,
        temporality="current",
        assertion_status="asserted",
        applies_to=None,
    )


def _extraction(*events: SimpleNamespace, evidence: str = "") -> SimpleNamespace:
    return SimpleNamespace(
        events=list(events),
        selection=SimpleNamespace(
            selected_event_ids=[event.event_id for event in events],
            final_kind="seizure_free",
            final_label="seizure free for 1 month",
            evidence=evidence,
            rationale="",
            confidence="medium",
        ),
    )


def test_day_dated_last_event_and_well_since_becomes_one_per_month() -> None:
    extraction = _extraction(
        _event(
            kind="last_event_only",
            raw_value="last event was on 30/Jan",
            evidence="His last event was on 30/Jan and he has remained well since.",
        ),
        _event(
            kind="seizure_free",
            raw_value="no further episodes in the past month",
            evidence="there have been no further episodes in the past month",
        ),
        evidence="His last event was on 30/Jan and he has remained well since.",
    )
    assert (
        last_event_well_since_label_from_events(extraction, "seizure free for 1 month")
        == "1 per month"
    )


def test_explicit_burst_count_keeps_n_over_the_short_interval() -> None:
    extraction = _extraction(
        _event(
            kind="last_event_only",
            raw_value="two seizures",
            evidence="Soon afterwards, she reported two seizures.",
        ),
        _event(
            kind="seizure_free",
            raw_value="no seizures since then",
            evidence="She has had no seizures since then.",
        ),
        evidence="She has had no seizures since then.",
    )
    assert (
        last_event_well_since_label_from_events(extraction, "seizure free for 2 month")
        == "2 per 2 month"
    )


def test_calendar_day_is_not_a_burst_count() -> None:
    extraction = _extraction(
        _event(
            kind="last_event_only",
            raw_value="The last such episode occurred on 21 Feb",
            evidence="The last such episode occurred on 21 Feb and she has been stable since.",
            notes="Last episode was Feb 21; clinic date is 19 May 2018",
        ),
        _event(
            kind="seizure_free",
            raw_value="stable since",
            evidence="she has been stable since",
        ),
        evidence="The last such episode occurred on 21 Feb and she has been stable since.",
    )
    assert (
        last_event_well_since_label_from_events(extraction, "seizure free for 3 month")
        == "1 per 3 month"
    )


def test_short_week_interval_rewrites_to_monthly_not_weekly_rate() -> None:
    extraction = _extraction(
        _event(
            kind="last_event_only",
            raw_value="last reported event was on 24 Jul",
            evidence="Her last reported event was on 24 Jul and she has been seizure-free since.",
        ),
        _event(
            kind="seizure_free",
            raw_value="stable for over 3 weeks",
            evidence="she has now been stable for over 3 weeks",
        ),
        evidence="Her last reported event was on 24 Jul and she has been seizure-free since.",
    )
    assert (
        last_event_well_since_label_from_events(extraction, "seizure free for 3 week")
        == "1 per month"
    )


def test_month_only_last_event_does_not_rewrite_true_seizure_free() -> None:
    extraction = _extraction(
        _event(
            kind="last_event_only",
            raw_value="early August",
            evidence="she describes the last episode as occurring in early August",
        ),
        _event(
            kind="seizure_free",
            raw_value="no further events",
            evidence="there have been no further events suggestive of seizures",
        ),
        evidence="there have been no further events suggestive of seizures",
    )
    assert (
        last_event_well_since_label_from_events(extraction, "seizure free for 2 month")
        is None
    )


def test_short_seizure_free_without_last_event_is_unchanged() -> None:
    extraction = _extraction(
        _event(
            kind="seizure_free",
            raw_value="seizure free for 3 month",
            evidence="no witnessed convulsive events for three months",
        )
    )
    assert (
        last_event_well_since_label_from_events(extraction, "seizure free for 3 month")
        is None
    )


def test_multiple_month_seizure_free_is_not_rewritten() -> None:
    extraction = _extraction(
        _event(
            kind="last_event_only",
            raw_value="most recent episode was on 15-Mar",
            evidence="The most recent episode was on 15-Mar",
        ),
        _event(
            kind="seizure_free",
            raw_value="no recurrence for the past months",
            evidence="With no recurrence for the past months",
        ),
        evidence="The most recent episode was on 15-Mar, and since then he has been well.",
    )
    assert (
        last_event_well_since_label_from_events(
            extraction, "seizure free for multiple month"
        )
        is None
    )


def test_living_select_enables_family_and_encode_does_not() -> None:
    assert "last_event_well_since" in DEFAULT_SEMANTIC_FAMILY_ORDER
    assert StructuredRepairConfig.for_mode("llm_select").last_event_well_since_repair is True
    after = StructuredRepairConfig.for_mode("llm_select_after_codebook")
    assert after.last_event_well_since_repair is True
    assert StructuredRepairConfig.for_mode("gan_rules_encode").last_event_well_since_repair is False
    assert StructuredRepairConfig.for_mode("raw_model").last_event_well_since_repair is False
