"""Split runner for the active ExECT rules and LLM-only methods."""

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

from ..llm.pipelines.key_entities_structured.constants import PromptProfile
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
    mode: str = "no-call",
    prompt_profile: PromptProfile = "full",
    dspy_cache: bool = True,
    api_base: str | None = None,
    api_key: str | None = None,
    timeout: int | None = None,
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

    del checkpoint_jsonl_path, checkpoint_report_path, resume
    active_method = active_method_name(method)
    if active_method == "rules":
        del temperature, max_tokens, raw_outputs, program, format_retry_program
        return _run_rules_split(letters, method=method, split=split)
    if active_method != "llm":
        raise ValueError("the ExECT llm_with_rules split runner remains a separate phase")

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
    prompt_profile: PromptProfile,
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
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run only the shared producer plus the selected raw-candidate projection."""

    if mode not in {"live", "prompt-only", "replay"}:
        raise ValueError("ExECT llm mode must be live, prompt-only, or replay")
    if mode == "replay" and raw_outputs is None:
        raise ValueError("replay mode requires raw_outputs")

    if mode == "live":
        import dspy

        from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

        from ..llm.pipelines.key_entities_structured.signatures import (
            DspyKeyEntitiesStructuredExtractor,
        )

        builder = model_builder or build_dspy_lm
        if program is None:
            dspy.configure(
                lm=builder(
                    model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    cache=dspy_cache,
                    api_base=api_base,
                    api_key=api_key,
                    timeout=timeout,
                )
            )
        program = program or (
            program_factory() if program_factory else DspyKeyEntitiesStructuredExtractor()
        )
        format_retry_program = format_retry_program or (
            format_retry_factory() if format_retry_factory else None
        )

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )

    rows: list[dict[str, Any]] = []
    for letter in letters:
        producer = structured_one_call.produce_structured_letter(
            letter,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,  # type: ignore[arg-type]
            raw_output=(raw_outputs or {}).get(letter.letter_id),
            program=program,
            format_retry_program=format_retry_program,
            split=split,
            api_base=api_base,
            config=config or StructuredMethodConfig.selected(prompt_profile=prompt_profile),
        )
        result = structured_one_call.run_llm_only_letter(letter, producer)
        rows.append(dict(result.row))

    metadata = {
        "method_id": "llm",
        "pipeline_family": "llm",
        "run_id": "llm",
        "split": split,
        "model": model,
        "mode": mode,
        "prompt_version": rows[0].get("prompt_version", "") if rows else "",
        "prompt_profile": rows[0].get("prompt_profile", "full") if rows else "full",
        "row_count": len(rows),
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "parse_failures": sum(bool(row.get("parse_errors")) for row in rows),
    }
    return rows, metadata
