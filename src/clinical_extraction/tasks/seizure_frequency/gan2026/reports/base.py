"""Shared Markdown report helpers for Gan 2026 experiment artifacts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


def llm_model_metadata_lines(
    metadata: Mapping[str, Any],
    jsonl_path: Path,
    *,
    model_role: str,
    deterministic_rule_configuration: str,
    summary: Mapping[str, Any] | None = None,
    leading_lines: Sequence[str] = (),
    extra_before_deterministic: Sequence[str] = (),
    extra_lines: Sequence[str] = (),
) -> list[str]:
    """Build the common model/provenance block for Gan LLM reports."""

    api_base = metadata.get("api_base")
    model = str(metadata.get("model", ""))
    if model.startswith("ollama_chat/"):
        provider_execution = f"native Ollama chat endpoint via DSPy/LiteLLM: `{api_base}`"
    elif api_base:
        provider_execution = f"OpenAI-compatible endpoint via DSPy/LiteLLM: `{api_base}`"
    else:
        provider_execution = "hosted OpenAI via DSPy/LiteLLM"
    lines = [
        *leading_lines,
        f"- DSPy version: `{metadata['dspy_version']}`",
        f"- Runtime model display/API identifier: `{metadata['model']}`",
        f"- Provider/execution: {provider_execution}",
        f"- Model role: {model_role}",
        f"- Prompt/program version: `{metadata['prompt_version']}`",
        f"- Temperature: `{metadata['temperature']}`",
        f"- Max tokens: `{metadata['max_tokens']}`",
        f"- Mode: `{metadata['mode']}`",
    ]
    if "dspy_cache" in metadata:
        lines.append(f"- DSPy cache enabled: `{metadata.get('dspy_cache')}`")
    if model.startswith("ollama_chat/"):
        lines.append("- Ollama Qwen thinking mode: `disabled` (`think=false`)")
    if summary is not None and "reused_raw_outputs" in summary:
        lines.append(f"- Reused raw model outputs: `{summary['reused_raw_outputs']}`")
        lines.append(f"- Reuse source: `{metadata.get('reuse_source') or 'none'}`")
    if "elapsed_seconds" in metadata:
        lines.extend(
            [
                f"- Run started UTC: `{metadata.get('run_started_at_utc')}`",
                f"- Run finished UTC: `{metadata.get('run_finished_at_utc')}`",
                f"- Wall-clock elapsed: `{metadata.get('elapsed_seconds')}` seconds "
                f"(`{metadata.get('elapsed_minutes')}` minutes)",
                f"- Throughput: `{metadata.get('rows_per_second')}` rows/sec "
                f"(`{metadata.get('seconds_per_row')}` sec/row)",
            ]
        )
    lines.extend(
        [
            "- Optimizer: none",
            *extra_before_deterministic,
            f"- Deterministic rule configuration: {deterministic_rule_configuration}",
            *extra_lines,
            f"- Git commit: `{metadata['git_commit']}`",
            f"- Working tree note: `{metadata['working_tree_note']}`",
            f"- JSONL artifact: `{jsonl_path.as_posix()}`",
        ]
    )
    return lines


def write_markdown_report(path: Path, lines: Sequence[str]) -> None:
    """Write a newline-terminated Markdown artifact, creating parents."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
