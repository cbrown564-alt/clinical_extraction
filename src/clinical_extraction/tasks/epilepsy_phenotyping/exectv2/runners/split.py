"""Split runner for the active ExECT methods."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
    Exectv2PipelineConfiguration,
    Exectv2PipelineRunner,
)

from .naming import active_method_name
from .split_policy import DEVELOPMENT_SPLIT_ALIASES, require_development_split

__all__ = ["DEVELOPMENT_SPLIT_ALIASES", "run_split"]


def run_split(
    letters: Sequence[ExectLetter],
    *,
    method: str = "rules",
    split: str,
    model: str = "(model-independent)",
    temperature: float = 0.0,
    max_tokens: int = 0,
    mode: str | None = None,
    prompt_profile: str = "full",
    dspy_cache: bool = True,
    api_base: str | None = None,
    api_key: str | None = None,
    timeout: int | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
    raw_outputs: Mapping[str, str] | None = None,
    program: Any | None = None,
    format_retry_program: Any | None = None,
    model_builder: Callable[..., Any] | None = None,
    program_factory: Callable[[], Any] | None = None,
    format_retry_factory: Callable[[], Any] | None = None,
    config: StructuredMethodConfig | None = None,
    **_: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run one active method over supplied letters after split authorization.

    Split authorization is deliberately before any iteration so locked, mixed,
    and unknown split requests fail closed without consuming input.
    """

    require_development_split(split)

    active_method = active_method_name(method)
    if active_method == "rules":
        del (
            temperature,
            max_tokens,
            raw_outputs,
            program,
            format_retry_program,
            checkpoint_jsonl_path,
            checkpoint_report_path,
            resume,
            progress_every,
        )
        return _run_rules_split(letters, method=method, split=split)
    if active_method not in {"llm", "llm_with_rules"}:
        raise ValueError(f"unsupported ExECT method: {active_method}")
    if mode not in {"live", "prompt-only", "replay"}:
        raise ValueError("ExECT llm mode must be live, prompt-only, or replay")

    return _run_llm_split(
        letters,
        split=split,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        prompt_profile=prompt_profile,
        dspy_cache=dspy_cache,
        api_base=api_base,
        api_key=api_key,
        timeout=timeout,
        raw_outputs=raw_outputs,
        program=program,
        format_retry_program=format_retry_program,
        model_builder=model_builder,
        program_factory=program_factory,
        format_retry_factory=format_retry_factory,
        config=config,
        projection=active_method,
        progress_every=progress_every,
        checkpoint_jsonl_path=checkpoint_jsonl_path,
        checkpoint_report_path=checkpoint_report_path,
        resume=resume,
    )


def _run_rules_split(
    letters: Sequence[ExectLetter], *, method: str, split: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Preserve the completed no-call rules slice."""

    runner = Exectv2PipelineRunner(Exectv2PipelineConfiguration(method=method))
    rows: list[dict[str, Any]] = []
    for letter in letters:
        result = runner.run(letter).result
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "pipeline_family": "rules",
                "method_id": "rules",
                "run_id": "rules",
                "model": "(model-independent)",
                "mode": "no-call",
                "prompt_version": "n/a (deterministic rules)",
                "raw_output": "",
                "call_error": None,
                "parse_errors": [],
                "predicted_mentions": [
                    mention.model_dump(mode="json") for mention in result.prediction.mentions
                ],
                "comparison_projection": [
                    mention.model_dump(mode="json")
                    for mention in result.comparison_projection.mentions
                ],
                "diagnostics": dict(result.prediction.diagnostics),
                "stage_events": [event.to_dict() for event in result.stage_events],
            }
        )

    metadata = {
        "method_id": "rules",
        "pipeline_family": "rules",
        "run_id": "rules",
        "split": split,
        "model": "(model-independent)",
        "mode": "no-call",
        "prompt_version": "n/a (deterministic rules)",
        "row_count": len(rows),
        "call_failures": 0,
        "parse_failures": 0,
    }
    return rows, metadata


def _run_llm_split(
    letters: Sequence[ExectLetter],
    *,
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
    prompt_profile: str,
    dspy_cache: bool,
    api_base: str | None,
    api_key: str | None,
    timeout: int | None,
    raw_outputs: Mapping[str, str] | None,
    program: Any | None,
    format_retry_program: Any | None,
    model_builder: Callable[..., Any] | None,
    program_factory: Callable[[], Any] | None,
    format_retry_factory: Callable[[], Any] | None,
    config: StructuredMethodConfig | None,
    projection: str,
    progress_every: int | None,
    checkpoint_jsonl_path: Path | None,
    checkpoint_report_path: Path | None,
    resume: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the shared producer plus one selected canonical projection."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )
    return structured_one_call.run_split(
        letters,
        split=split,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,  # type: ignore[arg-type]
        dspy_cache=dspy_cache,
        api_base=api_base,
        api_key=api_key,
        timeout=timeout,
        progress_every=progress_every,
        checkpoint_jsonl_path=checkpoint_jsonl_path,
        checkpoint_report_path=checkpoint_report_path,
        resume=resume,
        config=config or StructuredMethodConfig.selected(prompt_profile=prompt_profile),
        model_builder=model_builder,
        program_factory=program_factory,
        format_retry_factory=format_retry_factory,
        program=program,
        format_retry_program=format_retry_program,
        raw_outputs=raw_outputs,
        projection=projection,  # type: ignore[arg-type]
    )
