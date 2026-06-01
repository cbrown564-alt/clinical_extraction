import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_structured import (
    PROMPT_VERSION,
    StructuredExtractionRecord,
    StructuredRepairConfig,
    build_prompt_input,
    load_reusable_raw_outputs,
    parse_structured_json,
    run_split,
    summarize_records,
    write_jsonl,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import FrequencyLabelKind


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


def test_build_prompt_input_excludes_gold_and_deterministic_candidates() -> None:
    prompt = json.loads(build_prompt_input(_record()))

    assert prompt["prompt_version"] == PROMPT_VERSION
    assert prompt["note_text"] == _record().note_text
    assert "gold_label" not in json.dumps(prompt)
    assert "candidate_events" not in prompt
    assert "deterministic_final_selection" not in prompt


def test_parse_structured_json_repairs_schema_aliases_and_normalizes_selected_label() -> None:
    extraction, normalized_events, errors = parse_structured_json(_raw_structured())

    assert isinstance(extraction, StructuredExtractionRecord)
    assert extraction.events[0].kind == "frequency_rate"
    assert extraction.events[0].temporality == "current"
    assert extraction.selection.final_kind == "frequency"
    assert extraction.selection.confidence == "high"
    assert extraction.selection.final_label == "2 per month"
    assert normalized_events[0].normalized_label == "2 per month"
    assert errors == []


def test_parse_structured_json_can_compute_final_label_from_selected_event() -> None:
    extraction, normalized_events, errors = parse_structured_json(_raw_structured(None))

    assert extraction is not None
    assert extraction.selection.final_label == "2 per month"
    assert normalized_events[0].normalized_label == "2 per month"
    assert errors == []


def test_prompt_only_run_writes_not_run_records(tmp_path: Path) -> None:
    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
    )

    assert metadata["summary"]["structured_records"] == 0
    assert metadata["dspy_cache"] is True
    assert rows[0]["parse_errors"] == ["not_run"]
    assert rows[0]["prompt_version"] == PROMPT_VERSION

    path = tmp_path / "records.jsonl"
    write_jsonl(rows, path)
    assert json.loads(path.read_text(encoding="utf-8"))["source_row_index"] == 10


def test_run_split_reuses_raw_outputs_without_new_call(tmp_path: Path) -> None:
    reuse_path = tmp_path / "prior.jsonl"
    reuse_path.write_text(
        json.dumps({"source_row_index": 10, "raw_output": _raw_structured()}) + "\n",
        encoding="utf-8",
    )

    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs=load_reusable_raw_outputs(reuse_path),
        reuse_source=str(reuse_path),
    )

    assert metadata["summary"]["structured_records"] == 1
    assert metadata["summary"]["reused_raw_outputs"] == 1
    assert rows[0]["reused_raw_output"] is True
    assert rows[0]["structured_record"]["selection"]["final_label"] == "2 per month"
    assert rows[0]["parse_errors"] == []


def test_run_split_applies_repair_config_to_reused_raw_outputs(tmp_path: Path) -> None:
    reuse_path = tmp_path / "prior.jsonl"
    reuse_path.write_text(
        json.dumps({"source_row_index": 10, "raw_output": _raw_structured("1 event 2 weeks ago")})
        + "\n",
        encoding="utf-8",
    )

    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs=load_reusable_raw_outputs(reuse_path),
        reuse_source=str(reuse_path),
        repair_config=StructuredRepairConfig(selected_evidence_repair=False),
    )

    assert metadata["repair_config"]["selected_evidence_repair"] is False
    assert rows[0]["structured_record"]["selection"]["final_label"] == (
        "no seizure frequency reference"
    )


def test_summary_tolerates_missing_structured_final_label() -> None:
    summary = summarize_records(
        [
            {
                "structured_record": {"selection": {"final_label": None}},
                "parse_errors": ["unscorable_final_label: no selected event"],
                "call_error": None,
                "reused_raw_output": False,
                "comparison": {},
                "evidence_valid": False,
            }
        ]
    )

    assert summary["parse_or_validation_failures"] == 1
    assert summary["final_labels"] == {}


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
    assert errors == [
        "final_label_repaired: 'unknown' -> 'seizure free for multiple year'"
    ]


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
    assert errors == [
        "final_label_repaired: '1 per day' -> '1 per 2 to 3 day'"
    ]


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
        "final_label_repaired: '1 tonic seizure in February' -> "
        "'no seizure frequency reference'",
        "final_label_repaired: 'no seizure frequency reference' -> '5 per 7 month'",
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
    assert errors == [
        "final_label_repaired: 'seizure free for 1 month' -> '2 to 3 per 1 month'"
    ]


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
    assert errors == [
        "final_label_repaired: '2 to 3 per week' -> '2 to 3 per 1 month'"
    ]


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
    assert errors == [
        "final_label_repaired: 'seizure free for 1 month' -> '1 per 1 month'"
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
    assert errors == [
        "final_label_repaired: '3 to 4 per day' -> '3 to 4 per 15 month'"
    ]


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
