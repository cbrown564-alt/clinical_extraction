from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    llm_model_metadata_lines,
    write_markdown_report,
)


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
