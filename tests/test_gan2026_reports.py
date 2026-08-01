from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_only_canonical_pipeline,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports import (
    llm_structured_events_report,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    llm_model_metadata_lines,
    write_markdown_report,
)

write_structured_report = llm_structured_events_report.write_report
write_llm_only_report = llm_only_canonical_pipeline.write_report


def test_llm_model_metadata_lines_include_common_provenance() -> None:
    metadata = {
        "dspy_version": "3.0.0",
        "model": "openai/gpt-4.1-mini",
        "prompt_version": "prompt_v1",
        "temperature": 0.0,
        "max_tokens": 900,
        "mode": "prompt-only",
        "dspy_cache": True,
        "reuse_source": "cache",
        "git_commit": "abc123",
        "working_tree_note": "dirty",
    }
    summary = {"reused_raw_outputs": 2}

    lines = llm_model_metadata_lines(
        metadata,
        Path("experiments/run.jsonl"),
        model_role="test role",
        deterministic_rule_configuration="test rules",
        summary=summary,
        leading_lines=["- Pipeline: `test_pipeline`"],
        extra_before_deterministic=["- Prompt policy taxonomy: `policy.v1`"],
        extra_lines=["- Repair mode: `strict_format`"],
    )

    assert lines == [
        "- Pipeline: `test_pipeline`",
        "- DSPy version: `3.0.0`",
        "- Runtime model display/API identifier: `openai/gpt-4.1-mini`",
        "- Provider/execution: hosted OpenAI via DSPy/LiteLLM",
        "- Model role: test role",
        "- Prompt/program version: `prompt_v1`",
        "- Temperature: `0.0`",
        "- Max tokens: `900`",
        "- Mode: `prompt-only`",
        "- DSPy cache enabled: `True`",
        "- Reused raw model outputs: `2`",
        "- Reuse source: `cache`",
        "- Optimizer: none",
        "- Prompt policy taxonomy: `policy.v1`",
        "- Deterministic rule configuration: test rules",
        "- Repair mode: `strict_format`",
        "- Git commit: `abc123`",
        "- Working tree note: `dirty`",
        "- JSONL artifact: `experiments/run.jsonl`",
    ]


def test_write_markdown_report_creates_parent_and_trailing_newline(tmp_path: Path) -> None:
    report_path = tmp_path / "nested" / "report.md"

    write_markdown_report(report_path, ["# Title", "", "Body"])

    assert report_path.read_text(encoding="utf-8") == "# Title\n\nBody\n"


def test_llm_model_metadata_lines_identify_native_ollama_chat_route() -> None:
    metadata = {
        "dspy_version": "3.2.1",
        "model": "ollama_chat/qwen3.6:35b",
        "api_base": "http://localhost:11434",
        "prompt_version": "prompt_v1",
        "temperature": 0.0,
        "max_tokens": 1400,
        "mode": "live",
        "dspy_cache": False,
        "git_commit": "abc123",
        "working_tree_note": "dirty",
    }

    lines = llm_model_metadata_lines(
        metadata,
        Path("experiments/qwen.jsonl"),
        model_role="local selector",
        deterministic_rule_configuration="frozen",
    )

    assert (
        "- Provider/execution: native Ollama chat endpoint via DSPy/LiteLLM: "
        "`http://localhost:11434`"
    ) in lines
    assert "- Ollama Qwen thinking mode: `disabled` (`think=false`)" in lines


def test_llm_model_metadata_lines_include_run_timing_when_available() -> None:
    metadata = {
        "dspy_version": "3.2.1",
        "model": "ollama_chat/qwen3.6:35b",
        "api_base": "http://localhost:11434",
        "prompt_version": "prompt_v1",
        "temperature": 0.0,
        "max_tokens": 5000,
        "mode": "live",
        "git_commit": "abc123",
        "working_tree_note": "dirty",
        "run_started_at_utc": "2026-06-02T00:14:40+00:00",
        "run_finished_at_utc": "2026-06-02T05:43:58+00:00",
        "elapsed_seconds": 19758.0,
        "elapsed_minutes": 329.3,
        "rows_per_second": 0.012653,
        "seconds_per_row": 79.032,
    }

    lines = llm_model_metadata_lines(
        metadata,
        Path("experiments/qwen.jsonl"),
        model_role="local selector",
        deterministic_rule_configuration="frozen",
    )

    assert "- Run started UTC: `2026-06-02T00:14:40+00:00`" in lines
    assert "- Run finished UTC: `2026-06-02T05:43:58+00:00`" in lines
    assert "- Wall-clock elapsed: `19758.0` seconds (`329.3` minutes)" in lines
    assert "- Throughput: `0.012653` rows/sec (`79.032` sec/row)" in lines


def test_structured_holdout_report_is_aggregate_only(tmp_path: Path) -> None:
    report_path = tmp_path / "holdout.md"
    metadata = {
        "summary": {
            "examples": 1,
            "structured_records": 1,
            "call_failures": 0,
            "parse_or_validation_failures": 0,
            "json_dialect_repairs": 0,
            "repair_notes": 0,
            "evidence_valid": 1,
            "purist_accuracy": 1.0,
            "purist_correct": 1,
            "pragmatic_accuracy": 1.0,
            "pragmatic_correct": 1,
            "reused_raw_outputs": 0,
        },
        "repair_mode": "hybrid_full_stack",
        "repair_config": {},
        "split": "test",
        "split_manifest": "gan2026_split_v1",
        "date": "2026-07-15",
        "escalation_reason": None,
        "dspy_version": "3.0.0",
        "model": "openai/gpt-4.1-mini",
        "prompt_version": "gan2026_hybrid_structured_events_v0.7",
        "temperature": 0.0,
        "max_tokens": 10000,
        "mode": "live",
        "dspy_cache": False,
        "git_commit": "abc123",
        "working_tree_note": "dirty",
    }
    rows = [
        {
            "source_row_index": 123,
            "reference": {"gold_label": "held-out-gold"},
            "structured_record": {"selection": {"final_label": "held-out-prediction"}},
            "comparison": {"purist_correct": True},
            "parse_errors": [],
            "evidence_valid": True,
        }
    ]

    write_structured_report(
        rows,
        metadata,
        report_path,
        jsonl_path=tmp_path / "sealed.jsonl",
    )

    report = report_path.read_text(encoding="utf-8")
    assert "Holdout Aggregate" in report
    assert "aggregate-only locked-holdout result" in report
    assert "## Rows" not in report
    assert "held-out-gold" not in report
    assert "held-out-prediction" not in report


def test_llm_only_holdout_report_is_aggregate_only(tmp_path: Path) -> None:
    report_path = tmp_path / "holdout.md"
    metadata = {
        "summary": {
            "examples": 1,
            "decision_records": 1,
            "call_failures": 0,
            "parse_or_validation_failures": 0,
            "repair_notes": 0,
            "evidence_text_contained": 1,
            "evidence_text_containment_rate": 1.0,
            "purist_accuracy": 1.0,
            "purist_correct": 1,
            "pragmatic_accuracy": 1.0,
            "pragmatic_correct": 1,
            "applied_rule_family_counts": {},
            "reused_raw_outputs": 0,
        },
        "split": "test",
        "split_manifest": "gan2026_split_v1",
        "date": "2026-08-01",
        "escalation_reason": None,
        "dspy_version": "3.0.0",
        "model": "openai/gpt-4.1-mini",
        "prompt_version": "gan2026_llm_only_canonical_pipeline_v0.8",
        "temperature": 0.0,
        "max_tokens": 10000,
        "mode": "live",
        "dspy_cache": False,
        "git_commit": "abc123",
        "working_tree_note": "dirty",
    }
    rows = [
        {
            "source_row_index": 123,
            "reference": {"gold_label": "held-out-gold"},
            "decision_record": {"final_label": "held-out-prediction"},
            "comparison": {"purist_correct": True},
            "parse_errors": [],
            "evidence_text_contained": True,
        }
    ]

    write_llm_only_report(
        rows,
        metadata,
        report_path,
        jsonl_path=tmp_path / "sealed.jsonl",
    )

    report = report_path.read_text(encoding="utf-8")
    assert "Holdout Aggregate" in report
    assert "aggregate-only locked-holdout result" in report
    assert "## Rows" not in report
    assert "held-out-gold" not in report
    assert "held-out-prediction" not in report
