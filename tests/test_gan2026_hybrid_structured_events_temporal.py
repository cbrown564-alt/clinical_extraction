"""Invariant-focused tests for gan2026 hybrid structured events temporal."""

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


def test_parse_structured_json_repairs_post_change_burst_before_seizure_free() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "2 to 3 seizures",
                    "applies_to": "generalised epilepsy",
                    "time_window": "shortly after 10 Jul",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "evidence": (
                        "Shortly afterwards, she experienced 2 to 3 seizures, "
                        "one triggered by missed medication."
                    ),
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "seizure_free",
                    "raw_value": "seizure-free since then",
                    "applies_to": "generalised epilepsy",
                    "time_window": "since shortly after 10 Jul",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "She has remained seizure-free since then.",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "seizure_free",
                "final_label": "seizure free for 1 month",
                "evidence": "She has remained seizure-free since then.",
                "confidence": "high",
                "rationale": (
                    "The patient had 2 to 3 seizures shortly afterwards but has "
                    "remained seizure-free since then."
                ),
            },
        }
    )

    extraction, _, errors = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "2 to 3 per 1 month"
    assert errors == ["final_label_repaired: 'seizure free for 1 month' -> '2 to 3 per 1 month'"]


def test_parse_structured_json_repairs_since_then_burst_using_clinic_date() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "4 seizures",
                    "applies_to": None,
                    "time_window": "around early April 2017",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "evidence": "Around that period, she had 4 seizures.",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "seizure_free",
                    "raw_value": "no further events since early April",
                    "applies_to": None,
                    "time_window": "since early April 2017",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "She has not had any further events since.",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "seizure_free",
                "final_label": "seizure free for 2 months",
                "evidence": "She has not had any further events since.",
                "confidence": "high",
                "rationale": "She has been seizure free since early April.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(
        raw,
        note_text="Clinic Date: 05 June 2017",
    )

    assert extraction is not None
    assert extraction.selection.final_label == "4 per 2 month"
    assert errors == [
        "final_label_repaired: 'seizure free for 2 months' -> 'seizure free for 2 month'",
        "final_label_repaired: 'seizure free for 2 month' -> '4 per 2 month'",
    ]


def test_parse_structured_json_repairs_following_week_to_elapsed_month_window() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "two to three seizures in the following week",
                    "applies_to": None,
                    "time_window": "following week after 21-Feb",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "In the following week, he had two to three seizures",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "seizure_free",
                    "raw_value": "No further seizures have occurred since",
                    "applies_to": None,
                    "time_window": "since the following week after 21-Feb",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "No further seizures have occurred since",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "2 to 3 per week",
                "evidence": "In the following week, he had two to three seizures",
                "confidence": "high",
                "rationale": "No further seizures have occurred since.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(
        raw,
        note_text="Clinic Date: 24 March 2017",
    )

    assert extraction is not None
    assert extraction.selection.final_label == "2 to 3 per 1 month"
    assert errors == ["final_label_repaired: '2 to 3 per week' -> '2 to 3 per 1 month'"]


def test_parse_structured_json_repairs_dated_first_second_sequence() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "last_event_only",
                    "raw_value": "initial event in March 2019",
                    "applies_to": None,
                    "time_window": "March 2019",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "evidence": "His initial event was in March 2019 in Germany.",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "last_event_only",
                    "raw_value": "second event in May 2019",
                    "applies_to": None,
                    "time_window": "May 2019",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "evidence": "A second event occurred in Italy the following May 2019.",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e1", "e2"],
                "final_kind": "unknown",
                "final_label": "unknown",
                "evidence": "There have been no further daytime episodes.",
                "confidence": "medium",
                "rationale": "Two dated nocturnal events are described historically.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "2 per 2 month"
    assert errors == ["final_label_repaired: 'unknown' -> '2 per 2 month'"]


def test_parse_structured_json_repairs_near_clinic_dated_sequence_over_seizure_free() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "last_event_only",
                    "raw_value": "first seizure in July 2014",
                    "applies_to": None,
                    "time_window": "July 2014",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "His initial event was in July 2014 in Germany.",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "last_event_only",
                    "raw_value": "second event in October 2014",
                    "applies_to": None,
                    "time_window": "October 2014",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "A second event occurred in Italy the following October 2014.",
                    "notes": None,
                },
                {
                    "event_id": "e3",
                    "kind": "seizure_free",
                    "raw_value": "no further events since",
                    "applies_to": None,
                    "time_window": "since late October 2014",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "He has had no further events since surgical intervention.",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e3"],
                "final_kind": "seizure_free",
                "final_label": "seizure free since late October 2014",
                "evidence": "He has had no further events since surgical intervention.",
                "confidence": "high",
                "rationale": "He has had no further events since October.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(
        raw,
        note_text="Clinic Date: 14 November 2014",
    )

    assert extraction is not None
    assert extraction.selection.final_label == "2 per 3 month"
    assert errors == [
        "final_label_repaired: 'seizure free since late October 2014' -> "
        "'seizure free for multiple year'",
        "final_label_repaired: 'seizure free for multiple year' -> '2 per 3 month'",
    ]


def test_parse_structured_json_does_not_rewrite_remote_contextual_dated_sequence() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "seizure_free",
                    "raw_value": "sustained period without recurrence",
                    "applies_to": None,
                    "time_window": "recent months",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "she reports a sustained period without any recurrence",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "last_event_only",
                    "raw_value": "first seizure in February 2017",
                    "applies_to": None,
                    "time_window": "2017",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "evidence": (
                        "prior to this improvement she experienced her first seizure "
                        "in February 2017"
                    ),
                    "notes": None,
                },
                {
                    "event_id": "e3",
                    "kind": "last_event_only",
                    "raw_value": "second event occurred in June 2017",
                    "applies_to": None,
                    "time_window": "2017",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "evidence": "A second event occurred in June 2017",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "seizure_free",
                "final_label": "seizure free for multiple year",
                "evidence": "she reports a sustained period without any recurrence",
                "confidence": "high",
                "rationale": "Historical seizures are noted but not current.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(
        raw,
        note_text="Clinic Date: 02 October 2025",
    )

    assert extraction is not None
    assert extraction.selection.final_label == "seizure free for multiple year"
    assert errors == []


def test_parse_structured_json_repairs_second_and_third_event_window() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "last_event_only",
                    "raw_value": "first seizure in October 2017",
                    "applies_to": None,
                    "time_window": "October 2017",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "She experienced her first seizure in October 2017.",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "second and third seizure was in January 2018",
                    "applies_to": None,
                    "time_window": "January 2018",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": "Her second and third seizure was in January 2018.",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "frequency",
                "final_label": "2 to 3 per month",
                "evidence": "Her second and third seizure was in January 2018.",
                "confidence": "high",
                "rationale": "Two seizures occurred in January.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(
        raw,
        note_text="Clinic Date: 14 January 2018",
    )

    assert extraction is not None
    assert extraction.selection.final_label == "3 per 3 month"
    assert errors == ["final_label_repaired: '2 to 3 per month' -> '3 per 3 month'"]


def test_parse_structured_json_repairs_recent_last_event_window_over_seizure_free() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "last_event_only",
                    "raw_value": "last event on 30/Jan",
                    "applies_to": None,
                    "time_window": "30/Jan",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": (
                        "On 25/Jan his absences improved after medication adjustment. "
                        "His last event was on 30/Jan and he has remained well since."
                    ),
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "seizure_free",
                    "raw_value": "no further episodes in the past month",
                    "applies_to": None,
                    "time_window": "past month",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "there have been no further episodes in the past month",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "seizure_free",
                "final_label": "seizure free for 1 month",
                "evidence": "there have been no further episodes in the past month",
                "confidence": "high",
                "rationale": "The last event was 30 January and he has been well since.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(
        raw,
        note_text="Clinic Date: 25 February 2022",
    )

    assert extraction is not None
    assert extraction.selection.final_label == "1 per 1 month"
    assert errors == ["final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month'"]


def test_parse_structured_json_preserves_sustained_selected_seizure_free_interval() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "last_event_only",
                    "raw_value": "18 May 2025",
                    "applies_to": None,
                    "time_window": "18 May 2025",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "The last capture of a typical episode was on 18 May 2025",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "seizure_free",
                    "raw_value": "over four months",
                    "applies_to": None,
                    "time_window": "18 May 2025 to 02 October 2025",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": ("they have maintained an absence of events for over four months"),
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "seizure_free",
                "final_label": "seizure free for 4+ months",
                "evidence": "they have maintained an absence of events for over four months",
                "confidence": "high",
                "rationale": "This sustained remission supersedes the last event date.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(
        raw,
        note_text="Clinic Date: 02 October 2025",
    )

    assert extraction is not None
    assert extraction.selection.final_label == "seizure free for multiple year"
    assert errors == [
        "final_label_repaired: 'seizure free for 4+ months' -> 'seizure free for multiple year'"
    ]


def test_parse_structured_json_repairs_count_since_dated_last_event() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "last_event_only",
                    "raw_value": "Last tonic-clonic seizure was in 05/2020",
                    "applies_to": "tonic-clonic seizure",
                    "time_window": "05/2020",
                    "temporality": "historical",
                    "assertion_status": "historical",
                    "evidence": "Last tonic-clonic seizure was in 05/2020",
                    "notes": None,
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "3 or 4 morning jerks since then",
                    "applies_to": "morning jerks",
                    "time_window": "since then",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "with 3 or 4 morning jerks since then",
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e2"],
                "final_kind": "frequency",
                "final_label": "3 to 4 per day",
                "evidence": "with 3 or 4 morning jerks since then",
                "confidence": "high",
                "rationale": "There have been 3 or 4 morning jerks since then.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(
        raw,
        note_text="Clinic Date: 09 August 2021",
    )

    assert extraction is not None
    assert extraction.selection.final_label == "3 to 4 per 15 month"
    assert errors == ["final_label_repaired: '3 to 4 per day' -> '3 to 4 per 15 month'"]


def test_parse_structured_json_does_not_repair_perimenstrual_window_to_breakthrough_count() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "cluster_frequency",
                    "raw_value": "perimenstrual only (days -3 to +3)",
                    "applies_to": None,
                    "time_window": "last six months",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": (
                        "Seizures happen when perimenstrual only (days -3 to +3). "
                        "Outside this window she and the group report no events over "
                        "the last six months."
                    ),
                    "notes": "Seizures clustered perimenstrually",
                },
                {
                    "event_id": "e2",
                    "kind": "seizure_free",
                    "raw_value": "no events over the last six months",
                    "applies_to": None,
                    "time_window": "last six months",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "evidence": (
                        "Outside this window she and the group report no events over "
                        "the last six months."
                    ),
                    "notes": None,
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "perimenstrual cluster",
                "evidence": (
                    "Seizures happen when perimenstrual only (days -3 to +3). "
                    "Outside this window she and the group report no events over "
                    "the last six months."
                ),
                "confidence": "high",
                "rationale": "Events are confined to the perimenstrual window.",
            },
        }
    )

    extraction, _, errors = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "unknown"
    assert errors == ["final_label_repaired: 'perimenstrual cluster' -> 'unknown'"]
