from __future__ import annotations

from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.runner import (
    DEFAULT_CONDITIONS,
    run_split,
    summarize_rows,
    write_report,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli import (
    pipeline_specs,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)


def test_agentic_pipeline_is_registered_on_shared_cli_surface() -> None:
    spec = pipeline_specs()["agentic_matched_budget"]

    assert "matched-budget" in spec.description
    assert spec.default_jsonl_path.name == "gan2026_agentic_matched_budget_validation.jsonl"
    assert spec.default_max_tokens == 900


def test_prompt_only_runner_emits_matched_budget_traces_without_predictions() -> None:
    rows, metadata = run_split(
        [_record(101, "Clinic Date: 12 June 2026\nShe has 2 seizures per week.")],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        mode="prompt-only",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    assert metadata["artifact_kind"] == "gan2026_agentic_matched_budget_trace"
    assert metadata["summary"]["rows"] == 1
    assert metadata["summary"]["conditions"] == list(DEFAULT_CONDITIONS)
    assert metadata["summary"]["prediction_bearing_rows"] == 0

    row = rows[0]
    assert row["source_row_index"] == 101
    assert row["split"] == "validation"
    assert row["final_label"] is None
    assert set(row["condition_traces"]) == set(DEFAULT_CONDITIONS)

    single_agent = row["condition_traces"]["single_agent_tools"]
    assert single_agent["budget"]["model_calls_per_row"] == 4
    assert single_agent["attribution_layer"] == "no_prediction"
    assert single_agent["model_call_plans"][0]["call_role"] == "agent_loop"
    assert single_agent["tool_calls"][0]["tool_name"] == "parse_seizure_frequency_candidates"
    assert single_agent["tool_calls"][0]["status"] == "contract_smoke"
    assert single_agent["tool_calls"][0]["result"]["candidates"]

    multi_agent = row["condition_traces"]["multi_agent_matched"]
    assert multi_agent["budget"] == single_agent["budget"]
    assert [call["call_role"] for call in multi_agent["model_call_plans"]] == [
        "extractor_agent",
        "boundary_agent",
        "adjudicator_agent",
        "coordinator_agent",
    ]

    payload_text = str(row).lower()
    assert "gold_label" not in payload_text
    assert "gold_normalized_label" not in payload_text


def test_runner_writes_jsonl_and_markdown_report(tmp_path: Path) -> None:
    rows, metadata = run_split(
        [_record(102, "Clinic Date: 12 June 2026\nMedication reviewed.")],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        mode="prompt-only",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )
    jsonl_path = tmp_path / "agentic.jsonl"
    report_path = tmp_path / "agentic.md"

    write_jsonl_rows(rows, jsonl_path)
    write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    assert jsonl_path.read_text(encoding="utf-8").count("\n") == 1
    report = report_path.read_text(encoding="utf-8")
    assert "# Gan 2026 Agentic Matched-Budget Prompt-Only Trace" in report
    assert "single_agent_tools" in report
    assert "no-call contract smoke" in report


def test_summarize_rows_counts_tool_smoke_activity() -> None:
    rows, _ = run_split(
        [_record(103, "Clinic Date: 12 June 2026\nShe has cluster seizures twice per month.")],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        mode="prompt-only",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    summary = summarize_rows(rows)

    assert summary["rows"] == 1
    assert summary["tool_smoke_calls"] >= 1
    assert summary["prediction_bearing_rows"] == 0


def _record(source_row_index: int, note_text: str) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label="unknown",
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="unknown",
        gold_label_kind=FrequencyLabelKind.UNKNOWN,
        gold_yearly_bounds=None,
        gold_monthly_frequency=-1.0,
    )
