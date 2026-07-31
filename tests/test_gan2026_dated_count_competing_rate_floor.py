"""Dated-count no_reference rescue and typical-over-YTD competing-rate policy."""

from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    Portability,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    parse_structured_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    BENCHMARK_REPAIR_STEPS,
    repair_prediction_label,
    repair_prediction_label_with_evidence,
)


def test_dated_count_projection_step_is_benchmark_format() -> None:
    matched = [
        step
        for step in BENCHMARK_REPAIR_STEPS
        if step.rule_id == "benchmark_repair.in_period_count_to_per"
    ]
    assert len(matched) == 1
    assert matched[0].portability is Portability.BENCHMARK_FORMAT


def test_repair_projects_in_period_count_to_per_period() -> None:
    assert repair_prediction_label("2 in 3 months") == "2 per 3 month"
    assert repair_prediction_label("2 seizures in 3 months") == "2 per 3 month"


def test_repair_with_evidence_projects_within_period_count() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 in 3 months",
            "Two nocturnal events within three months",
        )
        == "2 per 3 month"
    )


def test_dated_sequence_mines_note_when_events_repeat_one_month() -> None:
    """C-like case: last_event evidence repeats June 2015; April lives only in note."""
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "two recent events",
                    "applies_to": None,
                    "time_window": "recent",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "following two recent events suggestive of seizures",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "last_event_only",
                    "raw_value": "second event took place in June 2015",
                    "applies_to": None,
                    "time_window": None,
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "The second event took place in June 2015 in the USA",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "2 recent seizures",
                "evidence": "following two recent events suggestive of seizures",
                "confidence": "high",
                "rationale": "Two recent events without an explicit rate.",
            },
        }
    )
    note = (
        "Clinic Date: 14 June 2015. "
        "The first seizure was reported in April 2015 while visiting relatives. "
        "The second event took place in June 2015 in the USA."
    )
    extraction, _, _errors = parse_structured_json(raw, note_text=note)
    assert extraction is not None
    assert extraction.selection.final_label == "2 per 2 month"


def test_dated_sequence_uses_note_text_when_events_lack_dates() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "Two unprovoked seizures",
                    "applies_to": None,
                    "time_window": "recent",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "Two unprovoked seizures under evaluation",
                    "notes": None,
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "2 seizures in recent period",
                "evidence": "Two unprovoked seizures under evaluation",
                "confidence": "high",
                "rationale": "Overall count of two recent unprovoked seizures.",
            },
        }
    )
    note = (
        "Clinic Date: 14 June 2015. "
        "The first seizure was reported in April 2015 while visiting relatives. "
        "The second event took place in June 2015 in the USA."
    )
    extraction, _, _errors = parse_structured_json(raw, note_text=note)
    assert extraction is not None
    assert extraction.selection.final_label == "2 per 2 month"


def test_typical_monthly_beats_year_to_date_observation_total() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "seven seizures so far this year",
                    "applies_to": None,
                    "time_window": "this year",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": (
                        "only seven focal impaired-awareness seizures reported "
                        "so far this year"
                    ),
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "a focal seizure monthly",
                    "applies_to": None,
                    "time_window": "present",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": (
                        "At present, his typical pattern is a focal seizure monthly"
                    ),
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "7 so far this year",
                "evidence": (
                    "only seven focal impaired-awareness seizures reported so far this year"
                ),
                "confidence": "high",
                "rationale": "Overall current seizure count selected.",
            },
        }
    )
    note = (
        "Clinic Date: 02 October 2025. "
        "only seven focal impaired-awareness seizures reported so far this year. "
        "At present, his typical pattern is a focal seizure monthly."
    )
    extraction, _, _errors = parse_structured_json(raw, note_text=note)
    assert extraction is not None
    assert extraction.selection.final_label == "1 per month"
