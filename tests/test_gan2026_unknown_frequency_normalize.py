"""unknown_frequency events should normalize from raw_value when parseable."""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredEventRecord,
    _normalize_event,
)


def _event(*, kind: str, raw_value: str | None, evidence: str = "") -> StructuredEventRecord:
    return StructuredEventRecord.model_validate(
        {
            "event_id": "e1",
            "kind": kind,
            "raw_value": raw_value,
            "evidence": evidence,
            "assertion_status": "asserted",
            "temporality": "current",
        }
    )


def test_unknown_frequency_uses_parseable_raw_value_not_forced_unknown() -> None:
    event = _event(
        kind="unknown_frequency",
        raw_value="abs monthly",
        evidence="Seizure frequency is described as abs monthly",
    )
    normalized = _normalize_event(event)
    assert normalized.normalized_label == "1 per month"
    assert normalized.validation_errors == []


def test_unknown_frequency_most_shifts_maps_like_most_days() -> None:
    event = _event(
        kind="unknown_frequency",
        raw_value="most shifts",
        evidence="these episodes crop up most shifts",
    )
    normalized = _normalize_event(event)
    assert normalized.normalized_label == "multiple per week"
    assert normalized.validation_errors == []


def test_unknown_frequency_empty_raw_still_unknown() -> None:
    event = _event(kind="unknown_frequency", raw_value=None)
    normalized = _normalize_event(event)
    assert normalized.normalized_label == "unknown"


def test_last_event_only_still_forces_unknown() -> None:
    event = _event(kind="last_event_only", raw_value="3 weeks ago")
    normalized = _normalize_event(event)
    assert normalized.normalized_label == "unknown"
