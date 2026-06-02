import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_heavy_clinical_frequency_reasoner as reasoner,
)

PIPELINE_FAMILY = reasoner.PIPELINE_FAMILY
PROMPT_VERSION = reasoner.PROMPT_VERSION
LlmHeavyExtractionRecord = reasoner.LlmHeavyExtractionRecord
build_prompt_input = reasoner.build_prompt_input
load_reusable_raw_outputs = reasoner.load_reusable_raw_outputs
parse_llm_heavy_reasoner_json = reasoner.parse_llm_heavy_reasoner_json
run_split = reasoner.run_split
summarize_records = reasoner.summarize_records
write_report = reasoner.write_report


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=10,
        note_text=(
            "Interval history: Present seizure frequency is two focal seizures per month. "
            "Past history included daily seizures in 2020."
        ),
        gold_label="2 per month",
        gold_reference="two focal seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per month",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(24.0, 24.0),
        gold_monthly_frequency=2.0,
    )


def _raw_reasoner(final_label: str = "2 per months") -> str:
    return json.dumps(
        {
            "events": [
                {
                    "event_id": "sf-1",
                    "kind": "frequency",
                    "applies_to": "focal seizures",
                    "raw_phrase": "two focal seizures per month",
                    "evidence": "two focal seizures per month",
                    "assertion_status": "asserted",
                    "temporality": "ongoing",
                    "certainty": "high",
                    "clinical_quantity": {
                        "occurrences_low": 2,
                        "occurrences_high": 2,
                        "period_low": 1,
                        "period_high": 1,
                        "period_unit": "month",
                    },
                    "model_normalized_clinical_label": "2 per month",
                    "notes": "Current quantified focal-seizure rate.",
                },
                {
                    "event_id": "sf-2",
                    "kind": "frequency_rate",
                    "applies_to": "seizures",
                    "raw_phrase": "daily seizures in 2020",
                    "evidence": "daily seizures in 2020",
                    "assertion_status": "asserted",
                    "temporality": "historical",
                    "certainty": "high",
                    "clinical_quantity": {},
                    "model_normalized_clinical_label": "1 per day",
                    "notes": "Historical only.",
                },
            ],
            "selection": {
                "selected_event_ids": ["sf-1"],
                "rejected_event_ids": ["sf-2"],
                "final_clinical_state": "frequency",
                "aggregation_strategy": "highest_current_frequency",
                "final_clinical_label": "2 per month",
                "rationale": "The current event determines the answer.",
                "uncertainty_flags": [],
            },
            "final_answer": {
                "raw_llm_final_label": final_label,
                "raw_llm_final_kind": "frequency",
                "raw_llm_monthly_frequency": 2.0,
                "selected_evidence": "two focal seizures per month",
                "selected_event_ids": ["sf-1"],
                "final_rationale": "The final label renders the selected current event.",
            },
        }
    )


def test_build_prompt_input_excludes_gold_and_deterministic_candidates() -> None:
    prompt = json.loads(build_prompt_input(_record()))

    assert prompt["prompt_version"] == PROMPT_VERSION
    assert prompt["pipeline_family"] == PIPELINE_FAMILY
    assert prompt["note_text"] == _record().note_text
    assert "clinical_quantity" in prompt["event_schema"]
    assert "final_answer_schema" in prompt
    assert prompt["score_layers_to_report"] == [
        "raw_llm",
        "format_only",
        "selected_evidence_arithmetic",
        "benchmark_aligned",
        "oracle_format_upper_bound",
    ]
    assert "gold_label" not in json.dumps(prompt)
    assert "candidate_events" not in prompt
    assert "deterministic_final_selection" not in prompt


def test_parse_llm_heavy_reasoner_json_repairs_schema_aliases() -> None:
    extraction, errors = parse_llm_heavy_reasoner_json(
        _raw_reasoner("2 per month"),
        note_text=_record().note_text,
    )

    assert isinstance(extraction, LlmHeavyExtractionRecord)
    assert extraction.events[0].kind == "frequency_rate"
    assert extraction.events[0].temporality == "current"
    assert extraction.selection.selected_event_ids == ["sf-1"]
    assert extraction.final_answer.raw_llm_final_label == "2 per month"
    assert errors == []


def test_parse_llm_heavy_reasoner_json_flags_selected_event_trace_mismatch() -> None:
    payload = json.loads(_raw_reasoner("2 per month"))
    payload["final_answer"]["selected_event_ids"] = ["sf-2"]

    extraction, errors = parse_llm_heavy_reasoner_json(
        json.dumps(payload),
        note_text=_record().note_text,
    )

    assert extraction is not None
    assert "selected_event_trace: final_answer ids differ from selection ids" in errors


def test_run_split_records_llm_heavy_score_layers() -> None:
    rows, metadata = run_split(
        [_record()],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=100,
        mode="prompt-only",
        dspy_cache=True,
        reuse_raw_outputs={10: _raw_reasoner("twice per month")},
    )

    row = rows[0]
    assert metadata["pipeline_family"] == PIPELINE_FAMILY
    assert metadata["schema_smoke_stop_rule"]["schema_valid_rows_minimum"] == "24/25"
    assert metadata["repair_mode_layers"]["raw_llm"]["repair_family"] == "none"
    assert row["structured_record"]["final_answer"]["raw_llm_final_label"] == "twice per month"
    assert row["component_status"]["event_extraction"] == "ok"
    assert row["component_status"]["selected_event_trace"] == "ok"
    assert row["score_layers"]["raw_llm"]["scorable"] is False
    assert row["score_layers"]["format_only"]["final_label"] == "2 per month"
    assert row["score_layers"]["format_only"]["purist_correct"] is True
    assert row["score_layers"]["selected_evidence_arithmetic"]["final_label"] == "2 per month"
    assert row["score_layers"]["benchmark_aligned"]["final_label"] == "2 per month"
    assert row["score_layers"]["oracle_format_upper_bound"]["final_label"] == "2 per month"
    assert row["repair_changes"][0] == {
        "layer": "format_only",
        "before": "twice per month",
        "after": "2 per month",
    }
    assert metadata["summary"]["structured_records"] == 1
    assert metadata["summary"]["format_only_purist_correct"] == 1
    assert metadata["summary"]["selected_event_trace_mismatches"] == 0


def test_run_split_prompt_only_writes_not_run_records() -> None:
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

    assert rows[0]["parse_errors"] == ["not_run"]
    assert rows[0]["score_layers"]["raw_llm"]["scorable"] is False
    assert metadata["summary"]["parse_or_validation_failures"] == 1


def test_load_reusable_raw_outputs_and_write_report(tmp_path: Path) -> None:
    reuse_path = tmp_path / "prior.jsonl"
    reuse_path.write_text(
        json.dumps({"source_row_index": 10, "raw_output": _raw_reasoner("2 per month")}) + "\n",
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
    summary = summarize_records(rows)
    report_path = tmp_path / "report.md"

    write_report(rows, metadata, report_path, jsonl_path=tmp_path / "rows.jsonl")

    assert summary["selected_evidence_valid"] == 1
    report = report_path.read_text(encoding="utf-8")
    assert "LLM-Heavy Clinical Frequency Reasoner V0" in report
    assert "`format_only`" in report
