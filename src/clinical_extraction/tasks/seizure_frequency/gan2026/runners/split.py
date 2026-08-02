"""Run a Gan 2026 pipeline on one data split."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineArchitecture,
    PipelineConfiguration,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.naming import active_pipeline_name


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
    """Run the selected retained pipeline on one data split."""
    del candidate_set_jsonl_path
    if active_pipeline_name(architecture) == "rules":
        return _run_deterministic_split(
            records,
            architecture="rules",
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
            dspy_cache=dspy_cache,
            api_base=api_base,
        )

    if architecture == "hybrid_structured_events":
        from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
            llm_with_rules,
        )

        return llm_with_rules.run_split(
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

    if active_pipeline_name(architecture) == "llm":
        from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
            llm,
        )

        return llm.run_split(
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

    raise ValueError(f"Unknown retained pipeline ID: {architecture}")


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
    from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import rules

    config = PipelineConfiguration(
        architecture=architecture,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        dspy_cache=dspy_cache,
        api_base=api_base,
    )
    rows = []
    for record in records:
        result = rules.run_record(record, config).to_pipeline_result()
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

    def comparison_flag(row: Mapping[str, object], key: str) -> bool:
        comparison = row.get("comparison")
        return bool(comparison.get(key)) if isinstance(comparison, Mapping) else False

    purist_correct = sum(comparison_flag(row, "purist_correct") for row in rows)
    pragmatic_correct = sum(comparison_flag(row, "pragmatic_correct") for row in rows)
    metadata["summary"] = {
        "examples": len(rows),
        "purist_correct": purist_correct,
        "purist_accuracy": round(purist_correct / len(rows), 4) if rows else 0.0,
        "pragmatic_correct": pragmatic_correct,
        "pragmatic_accuracy": round(pragmatic_correct / len(rows), 4) if rows else 0.0,
    }
    return rows, metadata
