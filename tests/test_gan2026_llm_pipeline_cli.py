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
    reuse_path = tmp_path / "reuse.jsonl"
    reuse_path.write_text("{}", encoding="utf-8")

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

    def load_reusable_raw_outputs(path):
        calls["reuse_path"] = path
        return {101: '{"prediction":"1 per week"}'}

    spec = GanLlmPipelineCliSpec(
        description="Run a dummy Gan LLM pipeline.",
        default_jsonl_path=jsonl_path,
        default_report_path=markdown_path,
        run_split=run_split,
        write_jsonl=write_jsonl,
        write_report=write_report,
        load_reusable_raw_outputs=load_reusable_raw_outputs,
    )

    llm_pipeline_cli.run_cli(
        spec,
        [
            "--limit",
            "2",
            "--mode",
            "prompt-only",
            "--reuse-jsonl",
            str(reuse_path),
            "--disable-dspy-cache",
        ],
    )

    assert calls["records"] == ["row-1", "row-2"]
    assert calls["reuse_path"] == reuse_path
    assert calls["kwargs"]["split"] == "validation"
    assert calls["kwargs"]["split_manifest"] == "test_manifest_v1"
    assert calls["kwargs"]["mode"] == "prompt-only"
    assert calls["kwargs"]["dspy_cache"] is False
    assert calls["kwargs"]["reuse_raw_outputs"] == {101: '{"prediction":"1 per week"}'}
    assert calls["kwargs"]["reuse_source"] == str(reuse_path)
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


def test_old_llm_pipeline_cli_spec_name_remains_compatible() -> None:
    assert llm_pipeline_cli.LlmPipelineCliSpec is GanLlmPipelineCliSpec
