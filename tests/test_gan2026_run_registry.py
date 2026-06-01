from __future__ import annotations

from pathlib import Path

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.run_registry import (
    RunRegistryEntry,
    load_run_registry,
    registry_entry_from_json_record,
    write_run_registry,
)


def test_run_registry_round_trips_jsonl_records(tmp_path: Path) -> None:
    path = tmp_path / "registry.jsonl"
    entry = RunRegistryEntry(
        run_id="gan2026_example_validation25_v1",
        artifact_paths=("experiments/example.jsonl", "experiments/example.md"),
        date="2026-06-01",
        pipeline_family="llm_only_claim_table_selector",
        split="validation",
        row_count=25,
        model="openai/gpt-4.1-mini",
        model_role="prediction-bearing claim selector",
        mode="prompt-only",
        replay_status="cache_first",
        repair_mode="strict_format",
        cache_reuse_source="DSPy cache",
        primary_metrics={"purist_correct": 23, "purist_f1": 0.92},
        evidence_validity="25/25 selected evidence exact",
        decision="revise",
        claim_language_notes="Development diagnostic only.",
    )

    write_run_registry([entry], path)

    assert load_run_registry(path) == [entry]


def test_run_registry_requires_traceable_artifact_path() -> None:
    entry = RunRegistryEntry(
        run_id="missing_artifact",
        artifact_paths=(),
        date="2026-06-01",
        pipeline_family="llm_only",
        split="validation",
        row_count=25,
        model="openai/gpt-4.1-mini",
        model_role="selector",
        mode="prompt-only",
        replay_status="live",
        decision="revise",
    )

    with pytest.raises(ValueError, match="at least one artifact path"):
        entry.to_json_record()


def test_run_registry_rejects_duplicate_run_ids(tmp_path: Path) -> None:
    entry = RunRegistryEntry(
        run_id="duplicate",
        artifact_paths=("experiments/a.md",),
        date="2026-06-01",
        pipeline_family="analysis",
        split="validation",
        row_count=0,
        model="none",
        model_role="analysis only",
        mode="analysis",
        replay_status="analysis_only",
        decision="historical",
    )

    with pytest.raises(ValueError, match="duplicate run_id"):
        write_run_registry([entry, entry], tmp_path / "registry.jsonl")


def test_run_registry_parses_json_record_into_typed_entry() -> None:
    entry = registry_entry_from_json_record(
        {
            "run_id": "gan2026_analysis",
            "artifact_paths": ["experiments/analysis.md"],
            "date": "2026-06-01",
            "pipeline_family": "error_analysis",
            "split": "validation",
            "row_count": 250,
            "model": "none",
            "model_role": "analysis only",
            "mode": "analysis",
            "replay_status": "analysis_only",
            "primary_metrics": {"purist_correct": 243},
            "decision": "historical",
        }
    )

    assert entry.run_id == "gan2026_analysis"
    assert entry.primary_metrics["purist_correct"] == 243


def test_run_registry_rejects_unknown_decision() -> None:
    with pytest.raises(ValueError, match="decision must be one of"):
        registry_entry_from_json_record(
            {
                "run_id": "bad_decision",
                "artifact_paths": ["experiments/analysis.md"],
                "date": "2026-06-01",
                "pipeline_family": "error_analysis",
                "split": "validation",
                "row_count": 250,
                "model": "none",
                "model_role": "analysis only",
                "mode": "analysis",
                "replay_status": "analysis_only",
                "decision": "maybe",
            }
        )
