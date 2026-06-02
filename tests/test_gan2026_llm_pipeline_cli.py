from pathlib import Path
from typing import Any

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.cli import llm_pipeline_cli
from clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli import (
    GanLlmPipelineCliSpec,
)


def test_general_llm_pipeline_cli_delegates_to_pipeline_spec(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    calls: dict[str, Any] = {}
    jsonl_path = tmp_path / "rows.jsonl"
    markdown_path = tmp_path / "report.md"

    monkeypatch.setattr(
        llm_pipeline_cli,
        "load_records_for_split",
        lambda split: ["row-1", "row-2", "row-3"],
    )
    monkeypatch.setattr(
        llm_pipeline_cli,
        "load_split_manifest",
        lambda: {"manifest_version": "test_manifest_v1"},
    )

    def run_split(records, **kwargs):
        calls["records"] = records
        calls["kwargs"] = kwargs
        return [{"source_row_index": 101}], {"summary": {"purist_accuracy": 1.0}}

    def write_jsonl(rows, path):
        calls["jsonl"] = (rows, path)

    def write_report(rows, metadata, path, *, jsonl_path):
        calls["report"] = (rows, metadata, path, jsonl_path)

    spec = GanLlmPipelineCliSpec(
        description="Run a dummy Gan LLM pipeline.",
        default_jsonl_path=jsonl_path,
        default_report_path=markdown_path,
        run_split=run_split,
        write_jsonl=write_jsonl,
        write_report=write_report,
    )
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})

    llm_pipeline_cli.run_cli(
        [
            "--pipeline",
            "dummy",
            "--limit",
            "2",
            "--mode",
            "prompt-only",
            "--disable-dspy-cache",
            "--api-base",
            "http://localhost:11434/v1",
        ],
    )

    assert calls["records"] == ["row-1", "row-2"]
    assert calls["kwargs"]["split"] == "validation"
    assert calls["kwargs"]["split_manifest"] == "test_manifest_v1"
    assert calls["kwargs"]["mode"] == "prompt-only"
    assert calls["kwargs"]["dspy_cache"] is False
    assert calls["kwargs"]["api_base"] == "http://localhost:11434/v1"
    assert calls["kwargs"]["progress_every"] == 10
    assert calls["kwargs"]["checkpoint_jsonl_path"] == jsonl_path
    assert calls["kwargs"]["checkpoint_report_path"] == markdown_path
    assert calls["jsonl"] == ([{"source_row_index": 101}], jsonl_path)
    report_rows, report_metadata, report_path, report_jsonl_path = calls["report"]
    assert report_rows == [{"source_row_index": 101}]
    assert report_path == markdown_path
    assert report_jsonl_path == jsonl_path
    assert report_metadata["summary"] == {"purist_accuracy": 1.0}
    assert report_metadata["run_started_at_utc"].endswith("+00:00")
    assert report_metadata["run_finished_at_utc"].endswith("+00:00")
    assert report_metadata["elapsed_seconds"] >= 0.0
    assert report_metadata["elapsed_minutes"] >= 0.0
    assert report_metadata["rows_per_second"] is not None
    assert report_metadata["seconds_per_row"] >= 0.0
    assert capsys.readouterr().out.strip() == '{"purist_accuracy": 1.0}'


def test_general_llm_pipeline_cli_rejects_uncapped_validation_without_escalation(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(["--pipeline", "dummy", "--mode", "prompt-only"])

    assert exc_info.value.code == 2
    assert "validation runs above 250 rows require --escalation-reason" in capsys.readouterr().err


def test_general_llm_pipeline_cli_rejects_broad_validation_without_escalation(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(["--pipeline", "dummy", "--mode", "prompt-only", "--limit", "251"])

    assert exc_info.value.code == 2
    assert "validation runs above 250 rows require --escalation-reason" in capsys.readouterr().err


def test_general_llm_pipeline_cli_allows_broad_validation_with_escalation(
    tmp_path: Path, monkeypatch
) -> None:
    calls: dict[str, Any] = {}
    spec = _dummy_spec(tmp_path, calls)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])
    monkeypatch.setattr(
        llm_pipeline_cli,
        "load_split_manifest",
        lambda: {"manifest_version": "test_manifest_v1"},
    )

    llm_pipeline_cli.run_cli(
        [
            "--pipeline",
            "dummy",
            "--mode",
            "prompt-only",
            "--limit",
            "251",
            "--escalation-reason",
            "single justified validation ladder promotion",
        ]
    )

    assert calls["kwargs"]["escalation_reason"] == ("single justified validation ladder promotion")


def test_pipeline_registry_exposes_routine_llm_experiments() -> None:
    specs = llm_pipeline_cli.pipeline_specs()

    assert set(specs) == {
        "hybrid_rules_candidates_llm_adjudicator",
        "llm_heavy_clinical_frequency_reasoner",
        "llm_only_claim_table_selector",
        "llm_only_direct_labeler",
        "llm_only_minimal_evidence_selector",
        "llm_only_structured_events",
        "llm_only_typed_adapter_reasoner",
    }
    assert specs["hybrid_rules_candidates_llm_adjudicator"].default_max_tokens == 1100
    assert specs["llm_only_claim_table_selector"].default_max_tokens == 1400
    assert specs["llm_heavy_clinical_frequency_reasoner"].default_max_tokens == 1800
    assert specs["llm_only_minimal_evidence_selector"].default_max_tokens == 900
    assert specs["llm_only_typed_adapter_reasoner"].default_max_tokens == 1800


def _dummy_spec(tmp_path: Path, calls: dict[str, Any] | None = None) -> GanLlmPipelineCliSpec:
    calls = calls if calls is not None else {}

    def run_split(records, **kwargs):
        calls["records"] = records
        calls["kwargs"] = kwargs
        return [{"source_row_index": 101}], {"summary": {"purist_accuracy": 1.0}}

    def write_jsonl(rows, path):
        calls["jsonl"] = (rows, path)

    def write_report(rows, metadata, path, *, jsonl_path):
        calls["report"] = (rows, metadata, path, jsonl_path)

    return GanLlmPipelineCliSpec(
        description="Run a dummy Gan LLM pipeline.",
        default_jsonl_path=tmp_path / "rows.jsonl",
        default_report_path=tmp_path / "report.md",
        run_split=run_split,
        write_jsonl=write_jsonl,
        write_report=write_report,
    )
