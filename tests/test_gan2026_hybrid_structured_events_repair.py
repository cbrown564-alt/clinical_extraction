"""Invariant-focused tests for gan2026 hybrid structured events repair."""

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
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


def test_parse_structured_json_repairs_breakthrough_after_seizure_free_interval() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "seizure_free",
                    "raw_value": "seizure-free for 6 months",
                    "applies_to": None,
                    "time_window": "prior interval",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "he was seizure-free for 6 months",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "last_event_only",
                    "raw_value": "a focal impaired-awareness seizure occurred 2 Thursdays ago",
                    "applies_to": "focal impaired-awareness seizure",
                    "time_window": "2 Thursdays ago",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "a focal impaired-awareness seizure occurred 2 Thursdays ago",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "last_event_only",
                "final_label": "1 event 2 weeks ago",
                "evidence": "a focal impaired-awareness seizure occurred 2 Thursdays ago",
                "confidence": "high",
                "rationale": "A single recent breakthrough event after seizure freedom.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(
        raw,
        note_text="Clinic Date: 10 August 2020",
    )

    assert extraction is not None
    assert extraction.selection.final_label == "1 per 6 month"
    assert errors == [
        "final_label_repaired: '1 event 2 weeks ago' -> 'no seizure frequency reference'",
        "final_label_repaired: 'no seizure frequency reference' -> '1 per 6 month'",
    ]


def test_parse_structured_json_can_disable_selected_evidence_repair() -> None:
    raw = _raw_structured("1 event 2 weeks ago")

    extraction, _, errors = parse_structured_json(
        raw,
        repair_config=StructuredRepairConfig(selected_evidence_repair=False),
    )

    assert extraction is not None
    assert extraction.selection.final_label == "no seizure frequency reference"
    assert errors == [
        "final_label_repaired: '1 event 2 weeks ago' -> 'no seizure frequency reference'"
    ]


def test_parse_structured_json_can_limit_basic_repair_to_format_preserving() -> None:
    raw = _raw_structured("several per week")

    extraction, _, errors = parse_structured_json(
        raw,
        repair_config=StructuredRepairConfig(
            selected_evidence_repair=False,
            basic_label_repair_format_only=True,
        ),
    )

    assert extraction is not None
    assert extraction.selection.final_label == "several per week"
    assert errors == [
        "unscorable_final_label: Unparsable label (raw: 'several per week' / "
        "normalized: 'several per week')"
    ]


def test_parse_structured_json_can_disable_all_final_label_repairs() -> None:
    raw = _raw_structured("1 event 2 weeks ago")

    extraction, _, errors = parse_structured_json(
        raw,
        repair_config=StructuredRepairConfig(
            basic_label_repair=False,
            selected_evidence_repair=False,
            monthly_diary_repair=False,
            usual_interval_repair=False,
            breakthrough_repair=False,
            non_epileptic_repair=False,
            residual_jerk_repair=False,
            post_change_burst_repair=False,
            dated_sequence_repair=False,
            elapsed_anchor_repair=False,
        ),
    )

    assert extraction is not None
    assert extraction.selection.final_label == "1 event 2 weeks ago"
    assert len(errors) == 1
    assert errors[0].startswith("unscorable_final_label:")
    assert "1 event 2 weeks ago" in errors[0]


def test_parse_structured_json_can_disable_breakthrough_repair_family() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "seizure_free",
                    "raw_value": "seizure-free for 6 months",
                    "applies_to": None,
                    "time_window": "prior interval",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "he was seizure-free for 6 months",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "last_event_only",
                    "raw_value": "a focal impaired-awareness seizure occurred 2 Thursdays ago",
                    "applies_to": "focal impaired-awareness seizure",
                    "time_window": "2 Thursdays ago",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "a focal impaired-awareness seizure occurred 2 Thursdays ago",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "last_event_only",
                "final_label": "1 event 2 weeks ago",
                "evidence": "a focal impaired-awareness seizure occurred 2 Thursdays ago",
                "confidence": "high",
                "rationale": "A single recent breakthrough event after seizure freedom.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(
        raw,
        note_text="Clinic Date: 10 August 2020",
        repair_config=StructuredRepairConfig(breakthrough_repair=False),
    )

    assert extraction is not None
    assert extraction.selection.final_label == "no seizure frequency reference"
    assert errors == [
        "final_label_repaired: '1 event 2 weeks ago' -> 'no seizure frequency reference'"
    ]


def test_parse_structured_json_prefers_explicit_breakthrough_count() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "seizure_free",
                    "raw_value": "no seizures for nearly a year",
                    "applies_to": None,
                    "time_window": "prior year",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "She had no seizures for nearly a year",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "3 tonic seizure two Saturdays ago",
                    "applies_to": "tonic seizure",
                    "time_window": "two Saturdays ago",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "then developed myoclonic jerks leading to 3 tonic seizure",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "frequency",
                "final_label": "3 seizures 2 weeks ago",
                "evidence": "then developed myoclonic jerks leading to 3 tonic seizure",
                "confidence": "high",
                "rationale": "The recent cluster had 3 tonic seizures.",
            },
        }
    )

    extraction, _, _ = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "3 per 1 year"


def test_parse_structured_json_repairs_current_non_epileptic_event_selection() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "unknown_frequency",
                    "raw_value": "intermittent brief episodes over the past year",
                    "applies_to": None,
                    "time_window": "past year",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "intermittent brief episodes over the past year",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "unknown_frequency",
                    "raw_value": "currently non-epileptic in nature",
                    "applies_to": None,
                    "time_window": "current",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": (
                        "Seizure-like episodes are currently non-epileptic in nature "
                        "and appear less troublesome"
                    ),
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "unknown",
                "final_label": "unknown",
                "evidence": "intermittent brief episodes over the past year",
                "confidence": "high",
                "rationale": (
                    "The episodes are seizure-like but currently non-epileptic in "
                    "nature, so no current epileptic seizure frequency is present."
                ),
            },
        }
    )

    extraction, _, errors = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "seizure free for multiple year"
    assert errors == ["final_label_repaired: 'unknown' -> 'seizure free for multiple year'"]


def test_parse_structured_json_aggregates_llm_monthly_diary_events_by_span() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "1 nocturnal seizure in June",
                    "applies_to": None,
                    "time_window": "June 2014",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "In Jun he had a nocturnal seizure but no daytime events.",
                    "notes": "One nocturnal seizure in June, no daytime events",
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "3 nocturnal seizures and 5 while awake in July",
                    "applies_to": None,
                    "time_window": "July 2014",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "In July he had three nocturnal seizures and 5 while awake.",
                    "notes": "Multiple seizures in July, nocturnal and daytime",
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "frequency",
                "final_label": "8 per month",
                "evidence": "In July he had three nocturnal seizures and 5 while awake.",
                "confidence": "high",
                "rationale": "The July count is the most recent.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "9 per 2 month"
    assert errors == ["final_label_repaired: '8 per month' -> '9 per 2 month'"]


def test_parse_structured_json_monthly_diary_span_includes_missing_months() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "5 seizures during sleep and 5 while awake in Mar",
                    "applies_to": "overall seizures",
                    "time_window": "March 2025",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "In Mar she had five seizures during sleep and 5 while awake.",
                    "notes": "March seizure count",
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "1 seizure while awake in May",
                    "applies_to": "overall seizures",
                    "time_window": "May 2025",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "In May she had no in sleep and one while awake.",
                    "notes": "May seizure count",
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "frequency",
                "final_label": "1 per month",
                "evidence": "In May she had no in sleep and one while awake.",
                "confidence": "high",
                "rationale": "The May count is most recent.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "11 per 3 month"
    assert errors == ["final_label_repaired: '1 per month' -> '11 per 3 month'"]
