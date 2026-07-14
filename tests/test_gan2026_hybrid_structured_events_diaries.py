"""Invariant-focused tests for gan2026 hybrid structured events diaries."""

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    parse_structured_json,
)


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=10,
        note_text="Present seizure frequency: two seizures per month.",
        gold_label="2 per month",
        gold_reference="two seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per month",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(24.0, 24.0),
        gold_monthly_frequency=2.0,
    )


def _raw_structured(final_label: str | None = "2 per month") -> str:
    return json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency",
                    "raw_value": "two seizures per month",
                    "applies_to": "seizures",
                    "time_window": "present",
                    "temporality": "ongoing",
                    "assertion_status": "asserted",
                    "evidence": "two seizures per month",
                    "notes": None,
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "current frequency",
                "final_label": final_label,
                "evidence": "two seizures per month",
                "confidence": 0.91,
                "rationale": "The note states the present seizure frequency.",
            },
        }
    )


def test_parse_structured_json_does_not_replace_day_interval_with_rescue_months() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "cluster_frequency",
                    "raw_value": "clusters every 4 days",
                    "applies_to": None,
                    "time_window": "current",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "typically occurring in clusters every 4 days",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "unknown_frequency",
                    "raw_value": "Rescue medication was required once in June and twice in August",
                    "applies_to": None,
                    "time_window": "past 3 months",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "Rescue medication was required once in June and twice in August",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "1 cluster per 4 days",
                "evidence": "typically occurring in clusters every 4 days",
                "confidence": "high",
                "rationale": "Clusters every 4 days are the usual seizure pattern.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "1 per 4 day"
    assert errors == ["final_label_repaired: '1 cluster per 4 days' -> '1 per 4 day'"]


def test_parse_structured_json_prefers_usual_interval_over_brief_daily_periods() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "approximately every two to three days",
                    "applies_to": None,
                    "time_window": "past few months",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "events approximately every two to three days",
                    "notes": "Baseline seizure frequency",
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "daily",
                    "applies_to": None,
                    "time_window": "brief periods",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "Occasionally, frequency escalates to daily",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "frequency",
                "final_label": "1 per day",
                "evidence": "Occasionally, frequency escalates to daily",
                "confidence": "high",
                "rationale": "Occasionally daily, but usual events are every two to three days.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "1 per 2 to 3 day"
    assert errors == ["final_label_repaired: '1 per day' -> '1 per 2 to 3 day'"]


def test_parse_structured_json_monthly_diary_counts_cluster_and_last_events() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "cluster_frequency",
                    "raw_value": "cluster of three seizures in August",
                    "applies_to": None,
                    "time_window": "August 2023",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "He had a cluster of three seizures in August",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "last_event_only",
                    "raw_value": "nocturnal seizure in November",
                    "applies_to": None,
                    "time_window": "November 2023",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "In November he had a nocturnal seizure",
                    "notes": None,
                },
                {
                    "event_id": "e3",
                    "kind": "last_event_only",
                    "raw_value": "single tonic seizure in February",
                    "applies_to": None,
                    "time_window": "February 2024",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "in February a single tonic seizure was recorded",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e3"],
                "final_kind": "frequency",
                "final_label": "1 tonic seizure in February",
                "evidence": "in February a single tonic seizure was recorded",
                "confidence": "high",
                "rationale": "The latest single event was in February.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "5 per 7 month"
    assert errors == [
        "final_label_repaired: '1 tonic seizure in February' -> 'unknown'",
        "final_label_repaired: 'unknown' -> '5 per 7 month'",
    ]


def test_parse_structured_json_monthly_diary_counts_month_first_events() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "cluster_frequency",
                    "raw_value": "four short absences in a cluster",
                    "applies_to": "absence seizures",
                    "time_window": "Apr 2011",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "In Apr she experienced four short absences in a cluster",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "2 further brief absences",
                    "applies_to": "absence seizures",
                    "time_window": "Jul 2011",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "In Jul there was 2 further brief absences",
                    "notes": None,
                },
                {
                    "event_id": "e3",
                    "kind": "frequency_rate",
                    "raw_value": "1 absence Sep",
                    "applies_to": "absence seizures",
                    "time_window": "Sep 2011",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "in Sep another at school",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e3"],
                "final_kind": "frequency",
                "final_label": "multiple per month",
                "evidence": "improvement overall with fewer events",
                "confidence": "medium",
                "rationale": "Events improved, but dated counts are available.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "7 per 6 month"
    assert errors == ["final_label_repaired: 'multiple per month' -> '7 per 6 month'"]
