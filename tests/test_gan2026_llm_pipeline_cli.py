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


def test_general_llm_pipeline_cli_rejects_test_without_confirmation(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--split",
                "test",
                "--mode",
                "prompt-only",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert "test split runs require --confirm-test-audit" in capsys.readouterr().err


def test_general_llm_pipeline_cli_rejects_test_confirmation_without_escalation(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--split",
                "test",
                "--mode",
                "prompt-only",
                "--confirm-test-audit",
            ]
        )

    assert exc_info.value.code == 2
    assert "test split runs require --escalation-reason" in capsys.readouterr().err


def test_general_llm_pipeline_cli_rejects_partial_test_audit(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["a", "b"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--split",
                "test",
                "--mode",
                "prompt-only",
                "--limit",
                "1",
                "--confirm-test-audit",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert "test split runs must cover the full locked split" in capsys.readouterr().err


def test_general_llm_pipeline_cli_allows_confirmed_full_test_audit(
    tmp_path: Path, monkeypatch
) -> None:
    calls: dict[str, Any] = {}
    spec = _dummy_spec(tmp_path, calls)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["a", "b"])
    monkeypatch.setattr(
        llm_pipeline_cli,
        "load_split_manifest",
        lambda: {"manifest_version": "test_manifest_v1"},
    )

    llm_pipeline_cli.run_cli(
        [
            "--pipeline",
            "dummy",
            "--split",
            "test",
            "--mode",
            "live",
            "--confirm-test-audit",
            "--progress-every",
            "0",
            "--escalation-reason",
            "user-authorized frozen aggregate audit",
        ]
    )

    assert calls["records"] == ["a", "b"]
    assert calls["kwargs"]["split"] == "test"
    assert calls["kwargs"]["escalation_reason"] == "user-authorized frozen aggregate audit"


def test_general_llm_pipeline_cli_rejects_test_prompt_only_mode(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--split",
                "test",
                "--mode",
                "prompt-only",
                "--confirm-test-audit",
                "--progress-every",
                "0",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert "test split runs must use --mode live" in capsys.readouterr().err


def test_general_llm_pipeline_cli_rejects_test_nonzero_temperature(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--split",
                "test",
                "--mode",
                "live",
                "--confirm-test-audit",
                "--temperature",
                "0.2",
                "--progress-every",
                "0",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert "test split runs must use --temperature 0.0" in capsys.readouterr().err


def test_general_llm_pipeline_cli_rejects_test_api_base(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--split",
                "test",
                "--mode",
                "live",
                "--confirm-test-audit",
                "--api-base",
                "http://localhost:11434/v1",
                "--progress-every",
                "0",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert "test split runs must not use --api-base" in capsys.readouterr().err


def test_general_llm_pipeline_cli_rejects_test_disable_dspy_cache(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--split",
                "test",
                "--mode",
                "live",
                "--confirm-test-audit",
                "--disable-dspy-cache",
                "--progress-every",
                "0",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert "test split runs must not use --disable-dspy-cache" in capsys.readouterr().err


def test_general_llm_pipeline_cli_rejects_fresh_evidence_test_model_drift(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(
        tmp_path,
        default_model="openai/gpt-4.1",
        default_max_tokens=2800,
    )
    monkeypatch.setattr(
        llm_pipeline_cli,
        "pipeline_specs",
        lambda: {"fresh_evidence_reasoner": spec},
    )
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "fresh_evidence_reasoner",
                "--split",
                "test",
                "--mode",
                "live",
                "--model",
                "openai/gpt-4.1-mini",
                "--confirm-test-audit",
                "--progress-every",
                "0",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert (
        "fresh_evidence_reasoner test split runs must use --model openai/gpt-4.1"
        in capsys.readouterr().err
    )


def test_general_llm_pipeline_cli_rejects_fresh_evidence_test_max_token_drift(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(
        tmp_path,
        default_model="openai/gpt-4.1",
        default_max_tokens=2800,
    )
    monkeypatch.setattr(
        llm_pipeline_cli,
        "pipeline_specs",
        lambda: {"fresh_evidence_reasoner": spec},
    )
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "fresh_evidence_reasoner",
                "--split",
                "test",
                "--mode",
                "live",
                "--model",
                "openai/gpt-4.1",
                "--max-tokens",
                "2799",
                "--confirm-test-audit",
                "--progress-every",
                "0",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert (
        "fresh_evidence_reasoner test split runs must use --max-tokens 2800"
        in capsys.readouterr().err
    )


def test_general_llm_pipeline_cli_rejects_fresh_evidence_test_jsonl_path_drift(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(
        tmp_path,
        default_model="openai/gpt-4.1",
        default_max_tokens=2800,
    )
    monkeypatch.setattr(
        llm_pipeline_cli,
        "pipeline_specs",
        lambda: {"fresh_evidence_reasoner": spec},
    )
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "fresh_evidence_reasoner",
                "--split",
                "test",
                "--mode",
                "live",
                "--model",
                "openai/gpt-4.1",
                "--max-tokens",
                "2800",
                "--jsonl",
                str(tmp_path / "alternate.jsonl"),
                "--confirm-test-audit",
                "--progress-every",
                "0",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert (
        "fresh_evidence_reasoner test split runs must use --jsonl "
        "experiments\\gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15.jsonl"
        in capsys.readouterr().err
    )


def test_general_llm_pipeline_cli_rejects_fresh_evidence_test_markdown_path_drift(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(
        tmp_path,
        default_model="openai/gpt-4.1",
        default_max_tokens=2800,
    )
    monkeypatch.setattr(
        llm_pipeline_cli,
        "pipeline_specs",
        lambda: {"fresh_evidence_reasoner": spec},
    )
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "fresh_evidence_reasoner",
                "--split",
                "test",
                "--mode",
                "live",
                "--model",
                "openai/gpt-4.1",
                "--max-tokens",
                "2800",
                "--jsonl",
                "experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15.jsonl",
                "--markdown",
                str(tmp_path / "alternate.md"),
                "--confirm-test-audit",
                "--progress-every",
                "0",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert (
        "fresh_evidence_reasoner test split runs must use --markdown "
        "experiments\\gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15.md"
        in capsys.readouterr().err
    )


def test_general_llm_pipeline_cli_rejects_test_progress_checkpoints(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--split",
                "test",
                "--mode",
                "live",
                "--confirm-test-audit",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert "test split runs must use --progress-every 0" in capsys.readouterr().err


def test_general_llm_pipeline_cli_rejects_test_overwrite_existing(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--split",
                "test",
                "--mode",
                "live",
                "--confirm-test-audit",
                "--overwrite-existing",
                "--progress-every",
                "0",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert "test split runs must not use --overwrite-existing" in capsys.readouterr().err


def test_general_llm_pipeline_cli_rejects_test_structured_event_source_override(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    spec = _dummy_spec(
        tmp_path,
        default_structured_event_jsonl_path=tmp_path / "default_structured_events.jsonl",
    )
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--split",
                "test",
                "--mode",
                "live",
                "--confirm-test-audit",
                "--structured-event-jsonl",
                str(tmp_path / "override_structured_events.jsonl"),
                "--progress-every",
                "0",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    stderr = capsys.readouterr().err
    assert "test split runs must not use source-artifact override option(s)" in stderr
    assert "--structured-event-jsonl" in stderr


def test_general_llm_pipeline_cli_rejects_test_candidate_set_source_override(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    spec = _dummy_spec(
        tmp_path,
        default_candidate_set_jsonl_path=tmp_path / "default_candidate_sets.jsonl",
    )
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--split",
                "test",
                "--mode",
                "live",
                "--confirm-test-audit",
                "--candidate-set-jsonl",
                str(tmp_path / "override_candidate_sets.jsonl"),
                "--progress-every",
                "0",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    stderr = capsys.readouterr().err
    assert "test split runs must not use source-artifact override option(s)" in stderr
    assert "--candidate-set-jsonl" in stderr


def test_general_llm_pipeline_cli_rejects_test_resume_without_existing_jsonl(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--split",
                "test",
                "--mode",
                "live",
                "--confirm-test-audit",
                "--resume-existing",
                "--progress-every",
                "0",
                "--escalation-reason",
                "technical recovery for user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert "test split --resume-existing requires an existing JSONL artifact" in (
        capsys.readouterr().err
    )


def test_general_llm_pipeline_cli_rejects_test_resume_without_recovery_reason(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    spec.default_jsonl_path.write_text('{"source_row_index": 101}\n', encoding="utf-8")
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(
        llm_pipeline_cli,
        "load_records_for_split",
        lambda split: [SimpleNamespace(source_row_index=101)],
    )

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--split",
                "test",
                "--mode",
                "live",
                "--confirm-test-audit",
                "--resume-existing",
                "--progress-every",
                "0",
                "--escalation-reason",
                "user-authorized frozen aggregate audit",
            ]
        )

    assert exc_info.value.code == 2
    assert "requires --escalation-reason to describe technical recovery" in (
        capsys.readouterr().err
    )


def test_general_llm_pipeline_cli_allows_test_resume_for_technical_recovery(
    tmp_path: Path, monkeypatch
) -> None:
    calls: dict[str, Any] = {}
    spec = _dummy_spec(tmp_path, calls)
    spec.default_jsonl_path.write_text(
        '{"source_row_index": 101, "value": "existing"}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(
        llm_pipeline_cli,
        "load_records_for_split",
        lambda split: [SimpleNamespace(source_row_index=101)],
    )
    monkeypatch.setattr(
        llm_pipeline_cli,
        "load_split_manifest",
        lambda: {"manifest_version": "test_manifest_v1"},
    )

    llm_pipeline_cli.run_cli(
        [
            "--pipeline",
            "dummy",
            "--split",
            "test",
            "--mode",
            "live",
            "--confirm-test-audit",
            "--resume-existing",
            "--progress-every",
            "0",
            "--escalation-reason",
            "technical recovery for user-authorized frozen aggregate audit",
        ]
    )

    assert calls["jsonl"] == (
        [{"source_row_index": 101, "value": "existing"}],
        spec.default_jsonl_path,
    )
    assert calls["report"][1]["resume"]["rows_run"] == 0


def test_general_llm_pipeline_cli_passes_test_split_to_resume_summarizer(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    calls: dict[str, Any] = {}
    jsonl_path = tmp_path / "rows.jsonl"
    markdown_path = tmp_path / "report.md"
    jsonl_path.write_text(
        '{"source_row_index": 101, "fresh_evidence_profiles": {"secret": 1}}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        llm_pipeline_cli,
        "load_records_for_split",
        lambda split: [SimpleNamespace(source_row_index=101)],
    )
    monkeypatch.setattr(
        llm_pipeline_cli,
        "load_split_manifest",
        lambda: {"manifest_version": "test_manifest_v1"},
    )

    def run_split(records, **kwargs):
        raise AssertionError("complete recovery artifact should not rerun rows")

    def write_jsonl(rows, path):
        calls["jsonl"] = (rows, path)

    def write_report(rows, metadata, path, *, jsonl_path):
        calls["report"] = (rows, metadata, path, jsonl_path)

    def summarize_rows(rows, *, split=None):
        return {"rows": len(rows), "split": split}

    spec = GanLlmPipelineCliSpec(
        description="Run a dummy Gan LLM pipeline.",
        default_jsonl_path=jsonl_path,
        default_report_path=markdown_path,
        run_split=run_split,
        write_jsonl=write_jsonl,
        write_report=write_report,
        summarize_rows=summarize_rows,
    )
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})

    llm_pipeline_cli.run_cli(
        [
            "--pipeline",
            "dummy",
            "--split",
            "test",
            "--mode",
            "live",
            "--confirm-test-audit",
            "--resume-existing",
            "--progress-every",
            "0",
            "--escalation-reason",
            "technical recovery for user-authorized frozen aggregate audit",
        ]
    )

    assert calls["report"][1]["summary"] == {"rows": 1, "split": "test"}
    assert capsys.readouterr().out.strip() == '{"rows": 1, "split": "test"}'


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


def test_agentic_cli_passes_condition_filter(tmp_path: Path, monkeypatch) -> None:
    calls: dict[str, Any] = {}
    spec = _dummy_spec(tmp_path, calls)
    monkeypatch.setattr(
        llm_pipeline_cli,
        "pipeline_specs",
        lambda: {"agentic_matched_budget": spec},
    )
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: ["row"])
    monkeypatch.setattr(
        llm_pipeline_cli,
        "load_split_manifest",
        lambda: {"manifest_version": "test_manifest_v1"},
    )

    llm_pipeline_cli.run_cli(
        [
            "--pipeline",
            "agentic_matched_budget",
            "--mode",
            "prompt-only",
            "--limit",
            "1",
            "--conditions",
            "single_greedy,single_agent_tools",
        ]
    )

    assert calls["kwargs"]["conditions"] == ["single_greedy", "single_agent_tools"]


def test_general_llm_pipeline_cli_filters_source_row_indices_in_requested_order(
    tmp_path: Path, monkeypatch
) -> None:
    calls: dict[str, Any] = {}
    spec = _dummy_spec(tmp_path, calls)
    records = [
        SimpleNamespace(source_row_index=101),
        SimpleNamespace(source_row_index=102),
        SimpleNamespace(source_row_index=103),
    ]
    index_file = tmp_path / "indices.txt"
    index_file.write_text("# fixed hard slice\n103\n101\n", encoding="utf-8")
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: records)
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
            "--source-row-index-file",
            str(index_file),
        ]
    )

    assert [record.source_row_index for record in calls["records"]] == [103, 101]


def test_general_llm_pipeline_cli_rejects_source_indices_outside_split(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    spec = _dummy_spec(tmp_path)
    records = [SimpleNamespace(source_row_index=101)]
    monkeypatch.setattr(llm_pipeline_cli, "pipeline_specs", lambda: {"dummy": spec})
    monkeypatch.setattr(llm_pipeline_cli, "load_records_for_split", lambda split: records)

    with pytest.raises(SystemExit) as exc_info:
        llm_pipeline_cli.run_cli(
            [
                "--pipeline",
                "dummy",
                "--mode",
                "prompt-only",
                "--source-row-indices",
                "102",
            ]
        )

    assert exc_info.value.code == 2
    assert "not present in the selected split" in capsys.readouterr().err


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
        "agentic_matched_budget",
        "cross_model_challenge_adjudicator",
        "cross_model_challenge_gated_adjudicator",
        "cross_model_structured_event_adjudicator",
        "deterministic",
        "deterministic_canonical_pipeline",
        "event_completion_reasoner",
        "fresh_evidence_reasoner",
        "hybrid",
        "llm_only_direct_labeler",
        "hybrid_structured_events",
        "llm_event_reasoner",
        "llm_only_canonical_pipeline",
        "represented_event_normalizer",
        "structured_event_verifier",
        "targeted_boundary_router",
        "temporal_sentinel_specialist",
    }

    assert specs["agentic_matched_budget"].default_max_tokens == 900
    assert specs["llm_event_reasoner"].default_max_tokens == 1600
    assert specs["structured_event_verifier"].default_max_tokens == 1800
    assert specs["targeted_boundary_router"].default_max_tokens == 2000
    assert specs["event_completion_reasoner"].default_max_tokens == 2200
    assert specs["represented_event_normalizer"].default_max_tokens == 2200
    assert specs["temporal_sentinel_specialist"].default_max_tokens == 2400
    assert specs["cross_model_structured_event_adjudicator"].default_max_tokens == 1800
    assert specs["cross_model_challenge_adjudicator"].default_max_tokens == 2000
    assert specs["cross_model_challenge_gated_adjudicator"].default_max_tokens == 2000
    assert specs["fresh_evidence_reasoner"].default_max_tokens == 2800
    assert specs["deterministic"].default_max_tokens == 900
    assert specs["hybrid"].default_max_tokens == 2400
    # hybrid builds CandidateSets live by default (no static-artifact dependency).
    assert specs["hybrid"].default_candidate_set_jsonl_path is None
    assert specs["llm_only_direct_labeler"].default_max_tokens == 900
    assert specs["hybrid_structured_events"].default_max_tokens == 5000
    assert specs["llm_only_canonical_pipeline"].default_max_tokens == 1200


def _dummy_spec(
    tmp_path: Path,
    calls: dict[str, Any] | None = None,
    *,
    default_model: str = "openai/gpt-4.1-mini",
    default_max_tokens: int = 900,
    default_candidate_set_jsonl_path: Path | None = None,
    default_structured_event_jsonl_path: Path | None = None,
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
        default_model=default_model,
        default_max_tokens=default_max_tokens,
        default_candidate_set_jsonl_path=default_candidate_set_jsonl_path,
        default_structured_event_jsonl_path=default_structured_event_jsonl_path,
    )
