from pathlib import Path
from types import SimpleNamespace
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


def test_general_llm_pipeline_cli_passes_candidate_set_jsonl_for_supported_specs(
    tmp_path: Path, monkeypatch
) -> None:
    calls: dict[str, Any] = {}
    candidate_set_path = tmp_path / "candidate_sets.jsonl"
    spec = _dummy_spec(
        tmp_path,
        calls,
        default_candidate_set_jsonl_path=tmp_path / "default_candidate_sets.jsonl",
    )
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
            "1",
            "--candidate-set-jsonl",
            str(candidate_set_path),
        ]
    )

    assert calls["kwargs"]["candidate_set_jsonl_path"] == candidate_set_path


def test_general_llm_pipeline_cli_resume_existing_skips_completed_rows(
    tmp_path: Path, monkeypatch
) -> None:
    calls: dict[str, Any] = {}
    jsonl_path = tmp_path / "rows.jsonl"
    markdown_path = tmp_path / "report.md"
    jsonl_path.write_text('{"source_row_index": 101, "value": "existing"}\n')
    records = [
        SimpleNamespace(source_row_index=101),
        SimpleNamespace(source_row_index=102),
        SimpleNamespace(source_row_index=103),
    ]
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: records)
    monkeypatch.setattr(
        llm_pipeline_cli,
        "load_split_manifest",
        lambda: {"manifest_version": "test_manifest_v1"},
    )

    def run_split(records_to_run, **kwargs):
        calls["records"] = records_to_run
        calls["kwargs"] = kwargs
        return [
            {"source_row_index": 102, "value": "new-102"},
            {"source_row_index": 103, "value": "new-103"},
        ], {"summary": {"examples": 2}}

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
        summarize_rows=lambda rows: {"examples": len(rows)},
    )
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})

    llm_pipeline_cli.run_cli(
        [
            "--pipeline",
            "dummy",
            "--limit",
            "3",
            "--mode",
            "prompt-only",
            "--resume-existing",
        ]
    )

    assert [record.source_row_index for record in calls["records"]] == [102, 103]
    assert calls["kwargs"]["checkpoint_jsonl_path"] == tmp_path / "rows.resume-part.jsonl"
    assert calls["kwargs"]["checkpoint_report_path"] == tmp_path / "report.resume-part.md"
    assert calls["jsonl"] == (
        [
            {"source_row_index": 101, "value": "existing"},
            {"source_row_index": 102, "value": "new-102"},
            {"source_row_index": 103, "value": "new-103"},
        ],
        jsonl_path,
    )
    assert calls["report"][1]["summary"] == {"examples": 3}
    assert calls["report"][1]["resume"]["rows_run"] == 2


def test_general_llm_pipeline_cli_rejects_existing_outputs_without_resume_or_overwrite(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    calls: dict[str, Any] = {}
    spec = _dummy_spec(tmp_path, calls)
    spec.default_jsonl_path.write_text('{"source_row_index": 101}\n')
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            ["--pipeline", "dummy", "--mode", "prompt-only", "--limit", "1"]
        )

    assert exc_info.value.code == 2
    assert calls == {}
    stderr = capsys.readouterr().err
    assert "output artifact already exists" in stderr
    assert "--resume-existing" in stderr


def test_general_llm_pipeline_cli_allows_deliberate_overwrite(
    tmp_path: Path, monkeypatch
) -> None:
    calls: dict[str, Any] = {}
    spec = _dummy_spec(tmp_path, calls)
    spec.default_jsonl_path.write_text('{"source_row_index": 101}\n')
    spec.default_report_path.write_text("# Old report\n")
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
            "1",
            "--overwrite-existing",
        ]
    )

    assert calls["records"] == ["row"]
    assert calls["jsonl"] == ([{"source_row_index": 101}], spec.default_jsonl_path)


def test_pipeline_registry_exposes_routine_llm_experiments() -> None:
    specs = llm_pipeline_cli.pipeline_specs()

    assert set(specs) == {
        "hybrid_parallel_state_candidate_reasoner",
        "llm_heavy_evidence_selection_with_deterministic_adapters",
        "llm_heavy_clinical_frequency_reasoner",
        "llm_candidate_set_clinical_assessment_probe",
        "llm_candidate_set_selector_schema_probe",
        "llm_extracted_candidate_schema_probe",
        "llm_only_claim_table_selector",
        "llm_only_direct_labeler",
        "llm_only_minimal_evidence_selector",
        "llm_only_sparse_operands_selected_state_reasoner",
        "llm_only_simplified_selected_state_reasoner",
        "llm_only_structured_events",
        "llm_only_typed_adapter_reasoner",
        "llm_only_typed_operations_reasoner",
    }
    assert specs["hybrid_parallel_state_candidate_reasoner"].default_max_tokens == 1800
    assert (
        specs["llm_heavy_evidence_selection_with_deterministic_adapters"].default_max_tokens
        == 1800
    )
    assert specs["llm_only_claim_table_selector"].default_max_tokens == 1400
    assert specs["llm_heavy_clinical_frequency_reasoner"].default_max_tokens == 1800
    assert specs["llm_candidate_set_clinical_assessment_probe"].default_max_tokens == 2400
    assert (
        specs[
            "llm_candidate_set_clinical_assessment_probe"
        ].default_candidate_set_jsonl_path
        is not None
    )
    assert specs["llm_candidate_set_selector_schema_probe"].default_max_tokens == 1800
    assert specs["llm_extracted_candidate_schema_probe"].default_max_tokens == 5000
    assert specs["llm_only_minimal_evidence_selector"].default_max_tokens == 900
    assert specs["llm_only_sparse_operands_selected_state_reasoner"].default_max_tokens == 1400
    assert specs["llm_only_structured_events"].default_max_tokens == 5000
    assert specs["llm_only_typed_adapter_reasoner"].default_max_tokens == 1800
    assert specs["llm_only_typed_operations_reasoner"].default_max_tokens == 4800


def _dummy_spec(
    tmp_path: Path,
    calls: dict[str, Any] | None = None,
    *,
    default_candidate_set_jsonl_path: Path | None = None,
) -> GanLlmPipelineCliSpec:
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
        default_candidate_set_jsonl_path=default_candidate_set_jsonl_path,
    )
