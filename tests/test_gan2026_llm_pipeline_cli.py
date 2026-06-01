from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026 import llm_pipeline_cli
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_pipeline_cli import (
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
        ],
    )

    assert calls["records"] == ["row-1", "row-2"]
    assert calls["kwargs"]["split"] == "validation"
    assert calls["kwargs"]["split_manifest"] == "test_manifest_v1"
    assert calls["kwargs"]["mode"] == "prompt-only"
    assert calls["kwargs"]["dspy_cache"] is False
    assert calls["kwargs"]["progress_every"] == 10
    assert calls["kwargs"]["checkpoint_jsonl_path"] == jsonl_path
    assert calls["kwargs"]["checkpoint_report_path"] == markdown_path
    assert calls["jsonl"] == ([{"source_row_index": 101}], jsonl_path)
    assert calls["report"] == (
        [{"source_row_index": 101}],
        {"summary": {"purist_accuracy": 1.0}},
        markdown_path,
        jsonl_path,
    )
    assert capsys.readouterr().out.strip() == '{"purist_accuracy": 1.0}'


def test_pipeline_registry_exposes_routine_llm_experiments() -> None:
    specs = llm_pipeline_cli.pipeline_specs()

    assert set(specs) == {
        "architecture2",
        "llm-first",
        "section-claim-table",
        "structured",
    }
    assert specs["architecture2"].default_max_tokens == 1100
    assert specs["section-claim-table"].default_max_tokens == 1400
