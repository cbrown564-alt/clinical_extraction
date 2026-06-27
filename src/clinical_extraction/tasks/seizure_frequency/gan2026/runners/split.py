"""Split-run dispatch for Gan 2026 pipeline architectures."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineArchitecture,
    PipelineConfiguration,
)


def run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    architecture: PipelineArchitecture,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool,
    api_base: str | None,
    escalation_reason: str | None,
    progress_every: int | None,
    checkpoint_jsonl_path: Path | None,
    checkpoint_report_path: Path | None,
    candidate_set_jsonl_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Execute a run split using the specified unified runner architecture."""
    if architecture in ("deterministic", "deterministic_canonical_pipeline"):
        return _run_deterministic_split(
            records,
            architecture=architecture,
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
            dspy_cache=dspy_cache,
            api_base=api_base,
        )

    if architecture == "hybrid":
        from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
            llm_candidate_set_clinical_assessment_probe,
        )
        return llm_candidate_set_clinical_assessment_probe.run_split(
            records,
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
            dspy_cache=dspy_cache,
            api_base=api_base,
            escalation_reason=escalation_reason,
            progress_every=progress_every,
            checkpoint_jsonl_path=checkpoint_jsonl_path,
            checkpoint_report_path=checkpoint_report_path,
            candidate_set_jsonl_path=candidate_set_jsonl_path,
        )

    if architecture == "llm_only_direct_labeler":
        from clinical_extraction.tasks.seizure_frequency.gan2026.llm import llm_only_direct_labeler
        return llm_only_direct_labeler.run_split(
            records,
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
            dspy_cache=dspy_cache,
            api_base=api_base,
            escalation_reason=escalation_reason,
            progress_every=progress_every,
            checkpoint_jsonl_path=checkpoint_jsonl_path,
            checkpoint_report_path=checkpoint_report_path,
        )

    if architecture == "hybrid_structured_events":
        from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
            hybrid_structured_events,
        )
        return hybrid_structured_events.run_split(
            records,
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
            dspy_cache=dspy_cache,
            api_base=api_base,
            escalation_reason=escalation_reason,
            progress_every=progress_every,
            checkpoint_jsonl_path=checkpoint_jsonl_path,
            checkpoint_report_path=checkpoint_report_path,
        )

    if architecture == "llm_only_canonical_pipeline":
        from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
            llm_only_canonical_pipeline,
        )
        return llm_only_canonical_pipeline.run_split(
            records,
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
            dspy_cache=dspy_cache,
            api_base=api_base,
            escalation_reason=escalation_reason,
            progress_every=progress_every,
            checkpoint_jsonl_path=checkpoint_jsonl_path,
            checkpoint_report_path=checkpoint_report_path,
        )

    raise ValueError(f"Unknown architecture: {architecture}")


def _run_deterministic_split(
    records: Sequence[GanFrequencyRecord],
    *,
    architecture: PipelineArchitecture,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool,
    api_base: str | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
        label_to_frequency_record,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
        build_run_metadata,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
        map_pragmatic,
        map_purist,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners import (
        deterministic,
        deterministic_canonical,
    )

    config = PipelineConfiguration(
        architecture=architecture,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        dspy_cache=dspy_cache,
    )
    run_item = (
        deterministic.run_item
        if architecture == "deterministic"
        else deterministic_canonical.run_item
    )
    rows = []
    for record in records:
        result = run_item(record, config)
        final_label = result.output.final_value
        predicted_frequency = label_to_frequency_record(final_label).monthly_frequency
        comparison = {
            "predicted_monthly_frequency": predicted_frequency,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "purist_correct": map_purist(predicted_frequency)
            == map_purist(record.gold_monthly_frequency),
            "pragmatic_correct": map_pragmatic(predicted_frequency)
            == map_pragmatic(record.gold_monthly_frequency),
        }
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "final_label": final_label,
                "evidence_valid": bool(result.diagnostics.get("evidence_valid")),
                "diagnostics": result.diagnostics,
                "comparison": comparison,
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_monthly_frequency": record.gold_monthly_frequency,
                    "row_ok": record.row_ok,
                },
            }
        )

    metadata = build_run_metadata(
        mode=mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_version=f"{architecture}_v1",
        dspy_version="none",
        split=split,
        split_manifest=split_manifest,
        api_base=api_base,
        row_count=len(records),
    )
    purist_correct = sum(1 for r in rows if r["comparison"]["purist_correct"])
    pragmatic_correct = sum(1 for r in rows if r["comparison"]["pragmatic_correct"])
    metadata["summary"] = {
        "examples": len(rows),
        "purist_correct": purist_correct,
        "purist_accuracy": round(purist_correct / len(rows), 4) if rows else 0.0,
        "pragmatic_correct": pragmatic_correct,
        "pragmatic_accuracy": round(pragmatic_correct / len(rows), 4) if rows else 0.0,
    }
    return rows, metadata
