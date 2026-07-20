"""Invariant-focused tests for gan2026 hybrid structured events contract."""

import json
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import llm_structured_temporal
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    PROMPT_VERSION,
    PROMPT_VERSION_V0_5,
    PROMPT_VERSION_V0_6,
    PROMPT_VERSION_V0_7,
    StructuredExtractionRecord,
    StructuredRepairConfig,
    _clinic_date,
    _clinic_month_year,
    _elapsed_months_from_nearest_event_date_precise,
    _event_month_year,
    _event_text,
    _nearest_event_date,
    build_prompt_input,
    load_reusable_raw_outputs,
    parse_structured_json,
    run_split,
    set_active_prompt_version,
    summarize_records,
    write_jsonl,
    write_report,
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


def test_structured_events_uses_shared_temporal_helpers() -> None:
    assert _clinic_date is llm_structured_temporal.clinic_date
    assert _clinic_month_year is llm_structured_temporal.clinic_month_year
    assert _event_month_year is llm_structured_temporal.event_month_year
    assert (
        _elapsed_months_from_nearest_event_date_precise
        is llm_structured_temporal.elapsed_months_from_nearest_event_date_precise
    )

    note_text = "Clinic Date: 25 February 2022. His last event was on 30/Jan."
    assert _clinic_date(note_text) == date(2022, 2, 25)
    assert _clinic_month_year(note_text) == (2, 2022)
    assert _event_month_year("last event in 05/2020", clinic_year=2022) == (5, 2020)


def test_temporal_helpers_ignore_invalid_numeric_date_fragments() -> None:
    class Event:
        kind = "last_event_only"
        evidence = "Seizure events on 06-03, 06-13, 09-23"
        raw_value = None
        time_window = None
        notes = None

    clinic = date(2025, 10, 2)

    assert _event_text(Event()) == "seizure events on 06-03, 06-13, 09-23"
    assert _nearest_event_date(
        [Event()],
        clinic=clinic,
        event_kinds={"last_event_only"},
        max_months=240,
    ) == date(2025, 3, 6)


def test_build_prompt_input_excludes_gold_and_deterministic_candidates() -> None:
    prompt = json.loads(build_prompt_input(_record()))

    assert prompt["prompt_version"] == PROMPT_VERSION
    assert prompt["prompt_version"] == PROMPT_VERSION_V0_7
    assert prompt["note_text"] == _record().note_text
    assert "gold_label" not in json.dumps(prompt)
    assert "candidate_events" not in prompt
    assert "deterministic_final_selection" not in prompt


def test_deepseek_reasoner_prompt_conserves_countable_frequency_facts() -> None:
    prompt = json.loads(build_prompt_input(_record()))
    instructions = " ".join(prompt["instructions"])

    assert "Use any extra checking silently" in instructions
    assert "countable-fact check" in instructions
    assert "Do not demote countable frequency evidence to unknown" in instructions
    assert "Preserve the full observed window for dated counts" in instructions
    assert "keep cluster cadence and events-per-cluster separate" in instructions
    assert "Keep the useful remission boundary behavior" in instructions
    assert "Do not let a general 'no seizures since review'" in instructions
    assert "Use no_reference only when the note truly has no seizure-frequency" in instructions


def test_structured_events_prompt_version_selector_preserves_v06() -> None:
    try:
        set_active_prompt_version(PROMPT_VERSION_V0_6)
        v06_prompt = json.loads(build_prompt_input(_record()))

        assert v06_prompt["prompt_version"] == PROMPT_VERSION_V0_6
        assert "countable-fact check" not in " ".join(v06_prompt["instructions"])
    finally:
        set_active_prompt_version(PROMPT_VERSION_V0_7)


def test_restored_v05_prompt_has_the_historical_instruction_set() -> None:
    prompt = json.loads(build_prompt_input(_record(), prompt_version=PROMPT_VERSION_V0_5))
    instructions = prompt["instructions"]

    assert prompt["prompt_version"] == PROMPT_VERSION_V0_5
    assert len(instructions) == 13
    assert "When both a frequency_rate or cluster_frequency event" not in " ".join(
        instructions
    )
    assert "Use any extra checking silently" not in " ".join(instructions)


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


def test_parse_structured_json_records_python_literal_json_dialect_repair() -> None:
    raw = (
        "{'events': [{'event_id': 'e1', 'kind': 'frequency_rate', "
        "'raw_value': 'two seizures per month', 'applies_to': 'seizures', "
        "'time_window': 'present', 'temporality': 'current', "
        "'assertion_status': 'asserted', 'evidence': 'two seizures per month', "
        "'notes': None}], 'selection': {'selected_event_ids': ['e1'], "
        "'final_kind': 'frequency', 'final_label': '2 per month', "
        "'evidence': 'two seizures per month', 'confidence': 'high', "
        "'rationale': 'The note states the present seizure frequency.'}}"
    )

    extraction, normalized_events, errors = parse_structured_json(raw)

    assert extraction is not None
    assert extraction.selection.final_label == "2 per month"
    assert normalized_events[0].normalized_label == "2 per month"
    assert errors == ["json_dialect_repaired: python_literal"]


def test_parse_structured_json_can_disable_python_literal_json_dialect_repair() -> None:
    raw = (
        "{'events': [{'event_id': 'e1', 'kind': 'frequency_rate', "
        "'raw_value': 'two seizures per month', 'applies_to': 'seizures', "
        "'time_window': 'present', 'temporality': 'current', "
        "'assertion_status': 'asserted', 'evidence': 'two seizures per month', "
        "'notes': None}], 'selection': {'selected_event_ids': ['e1'], "
        "'final_kind': 'frequency', 'final_label': '2 per month', "
        "'evidence': 'two seizures per month', 'confidence': 'high', "
        "'rationale': 'The note states the present seizure frequency.'}}"
    )

    extraction, normalized_events, errors = parse_structured_json(
        raw,
        repair_config=StructuredRepairConfig.for_mode("strict_json_raw_model"),
    )

    assert extraction is None
    assert normalized_events == []
    assert errors == ["invalid_json: Expecting property name enclosed in double quotes"]


def test_parse_structured_json_repairs_event_mapping_container() -> None:
    payload = json.loads(_raw_structured())
    payload["events"] = {event["event_id"]: event for event in payload["events"]}

    extraction, _, errors = parse_structured_json(json.dumps(payload))

    assert extraction is not None
    assert "container_shape_repaired: events_mapping_to_list" in errors


def test_parse_structured_json_quarantines_schema_invalid_unselected_event() -> None:
    payload = json.loads(_raw_structured())
    payload["events"].append(
        {
            "event_id": "bad",
            "kind": "invented_kind",
            "temporality": "historical",
            "assertion_status": "asserted",
            "evidence": "years ago",
        }
    )

    extraction, _, errors = parse_structured_json(json.dumps(payload))

    assert extraction is not None
    assert all(event.event_id != "bad" for event in extraction.events)
    assert "unselected_event_quarantined: bad" in errors


def test_parse_structured_json_rejects_schema_invalid_selected_event() -> None:
    payload = json.loads(_raw_structured())
    payload["events"][0]["kind"] = "invented_kind"

    extraction, _, errors = parse_structured_json(json.dumps(payload))

    assert extraction is None
    assert errors[-1].startswith("schema_validation_error:")


def test_json_dialect_only_mode_repairs_dialect_without_final_label_repair() -> None:
    raw = (
        "{'events': [{'event_id': 'e1', 'kind': 'frequency_rate', "
        "'raw_value': 'two seizures per month', 'applies_to': 'seizures', "
        "'time_window': 'present', 'temporality': 'current', "
        "'assertion_status': 'asserted', 'evidence': 'two seizures per month', "
        "'notes': None}], 'selection': {'selected_event_ids': ['e1'], "
        "'final_kind': 'frequency', 'final_label': 'several per week', "
        "'evidence': 'two seizures per month', 'confidence': 'high', "
        "'rationale': 'The note states the present seizure frequency.'}}"
    )

    extraction, normalized_events, errors = parse_structured_json(
        raw,
        repair_config=StructuredRepairConfig.for_mode("json_dialect_only"),
    )

    assert extraction is not None
    assert extraction.selection.final_label == "several per week"
    assert normalized_events[0].normalized_label == "2 per month"
    assert errors == [
        "json_dialect_repaired: python_literal",
        "unscorable_final_label: Unparsable label (raw: 'several per week' / "
        "normalized: 'several per week')",
    ]


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


def test_run_split_retains_explorer_compatible_hybrid_boundary(tmp_path: Path) -> None:
    raw_output = _raw_structured(" 2 PER MONTH ")

    rows, _ = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        reuse_raw_outputs={10: raw_output},
        reuse_source="test fixture",
    )

    trace = rows[0]["row_trace"]
    assert trace["schema_version"] == "gan2026.row_trace.v1"
    assert trace["method"] == "llm_with_rules"
    assert trace["model_prediction"]["record"]["selection"]["final_label"] == (
        " 2 PER MONTH "
    )
    assert trace["model_prediction"]["raw_output_field"] == "raw_output"
    assert trace["deterministic_selection"]["selected_event_ids"] == ["e1"]
    assert trace["deterministic_selection"]["resolved_label"] == " 2 PER MONTH "
    assert trace["deterministic_semantic"]["before_label"] == " 2 PER MONTH "
    assert trace["deterministic_semantic"]["after_label"] == "2 per month"
    assert trace["deterministic_semantic"]["events"] == [
        "final_label_repaired: ' 2 PER MONTH ' -> '2 per month'"
    ]
    assert trace["evidence_validation"] == {
        "evidence": "two seizures per month",
        "exact_substring": True,
    }
    assert trace["scoring"] == rows[0]["comparison"]


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


def test_write_report_records_repair_config(tmp_path: Path) -> None:
    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs={10: _raw_structured("2 per months")},
        repair_config=StructuredRepairConfig.for_mode("strict_format"),
    )
    report_path = tmp_path / "report.md"

    write_report(rows, metadata, report_path, jsonl_path=tmp_path / "rows.jsonl")

    report = report_path.read_text(encoding="utf-8")
    assert "- Repair mode: `strict_format`" in report
    assert "- Repair policy: raw structured model selection plus strict format-preserving" in report
    assert "`basic_label_repair_format_only=True`" in report
    assert "`selected_evidence_repair=False`" in report


def test_parse_structured_json_can_use_clean_scorer_facing_gold_policy() -> None:
    raw = _raw_structured("most weekdays")

    extraction, _, errors = parse_structured_json(
        raw,
        repair_config=StructuredRepairConfig(
            selected_evidence_repair=False,
            basic_label_repair_format_only=True,
            clean_scorer_facing_gold_policy=True,
        ),
    )

    assert extraction is not None
    assert extraction.selection.final_label == "multiple per week"
    assert errors == ["final_label_repaired: 'most weekdays' -> 'multiple per week'"]


def test_named_clean_scorer_mode_does_not_use_hybrid_semantic_repair() -> None:
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

    clean_extraction, _, clean_errors = parse_structured_json(
        raw,
        note_text="Clinic Date: 10 August 2020",
        repair_config=StructuredRepairConfig.for_mode("clean_scorer_facing"),
    )
    hybrid_extraction, _, hybrid_errors = parse_structured_json(
        raw,
        note_text="Clinic Date: 10 August 2020",
        repair_config=StructuredRepairConfig.for_mode("hybrid_full_stack"),
    )

    assert clean_extraction is not None
    assert clean_extraction.selection.final_label == "1 2 week ago"
    assert clean_errors == [
        "final_label_repaired: '1 event 2 weeks ago' -> '1 2 week ago'",
        "unscorable_final_label: Unparsable label "
        "(raw: '1 2 week ago' / normalized: '1 2 week ago')",
    ]
    assert hybrid_extraction is not None
    assert hybrid_extraction.selection.final_label == "1 per 6 month"
    assert hybrid_errors == [
        "final_label_repaired: '1 event 2 weeks ago' -> 'no seizure frequency reference'",
        "final_label_repaired: 'no seizure frequency reference' -> '1 per 6 month'",
    ]


def test_write_report_names_clean_scorer_facing_gold_policy(tmp_path: Path) -> None:
    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs={10: _raw_structured("most weekdays")},
        repair_config=StructuredRepairConfig.for_mode("clean_scorer_facing"),
    )
    report_path = tmp_path / "report.md"

    write_report(rows, metadata, report_path, jsonl_path=tmp_path / "rows.jsonl")

    report = report_path.read_text(encoding="utf-8")
    assert metadata["repair_mode"] == "clean_scorer_facing"
    assert "- Repair mode: `clean_scorer_facing`" in report
    assert "- Repair policy: raw structured model selection plus clean scorer-facing" in report
    assert "`clean_scorer_facing_gold_policy=True`" in report


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


def test_summary_counts_json_dialect_repairs_without_counting_them_as_failures() -> None:
    summary = summarize_records(
        [
            {
                "structured_record": {"selection": {"final_label": "2 per month"}},
                "parse_errors": ["json_dialect_repaired: python_literal"],
                "call_error": None,
                "reused_raw_output": False,
                "comparison": {"purist_correct": True, "pragmatic_correct": True},
                "evidence_valid": True,
            }
        ]
    )

    assert summary["parse_or_validation_failures"] == 0
    assert summary["json_dialect_repairs"] == 1
    assert summary["repair_notes"] == 0
