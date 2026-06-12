from __future__ import annotations

from pathlib import Path

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
    RunRegistryEntry,
    load_run_registry,
    registry_entry_from_json_record,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    render_run_registry_markdown,
    write_run_registry_markdown,
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
            "primary_metrics": {"purist_correct": 243, "purist_ci": [0.8, 0.9]},
            "decision": "historical",
        }
    )

    assert entry.run_id == "gan2026_analysis"
    assert entry.primary_metrics["purist_correct"] == 243
    assert entry.primary_metrics["purist_ci"] == [0.8, 0.9]


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


def test_run_registry_validates_artifact_paths_relative_to_repo(tmp_path: Path) -> None:
    artifact = tmp_path / "experiments" / "example.md"
    artifact.parent.mkdir()
    artifact.write_text("# Example\n", encoding="utf-8")
    entry = RunRegistryEntry(
        run_id="traceable",
        artifact_paths=("experiments/example.md",),
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

    validate_run_registry_artifacts([entry], repo_root=tmp_path)

    missing = RunRegistryEntry(
        run_id="missing",
        artifact_paths=("experiments/missing.md",),
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
    with pytest.raises(ValueError, match="missing artifact path"):
        validate_run_registry_artifacts([missing], repo_root=tmp_path)


def test_run_registry_renders_decision_grouped_markdown_index(tmp_path: Path) -> None:
    revise = RunRegistryEntry(
        run_id="revise_run",
        artifact_paths=("experiments/revise.jsonl", "experiments/revise.md"),
        date="2026-06-01",
        pipeline_family="llm_only_claim_table_selector",
        split="validation",
        row_count=250,
        model="openai/gpt-4.1-mini",
        model_role="LLM-only selector",
        mode="prompt-only",
        replay_status="schema_replay",
        repair_mode="strict_format",
        primary_metrics={"clean_purist_correct": 231, "clean_pragmatic_correct": 238},
        evidence_validity="247/250 selected evidence exact",
        decision="revise",
        claim_language_notes="Development diagnostic only.",
    )
    reject = RunRegistryEntry(
        run_id="reject_run",
        artifact_paths=("experiments/reject.md",),
        date="2026-06-01",
        pipeline_family="llm_only_claim_table_selector",
        split="validation",
        row_count=750,
        model="openai/gpt-4.1-mini",
        model_role="LLM-only selector",
        mode="prompt-only",
        replay_status="cache_first",
        repair_mode="clean_scorer_facing",
        primary_metrics={"clean_purist_correct": 528},
        evidence_validity="See interpretation report.",
        decision="reject",
        claim_language_notes="Rejected for holdout.",
    )

    markdown = render_run_registry_markdown([reject, revise])

    assert markdown.startswith("# Gan 2026 Run Registry\n")
    assert "## Revise" in markdown
    assert "## Reject" in markdown
    assert "`revise_run`" in markdown
    assert "clean_purist_correct=231" in markdown
    assert "`experiments/revise.jsonl`" in markdown
    assert markdown.index("## Revise") < markdown.index("## Reject")

    path = tmp_path / "RUN_INDEX.md"
    write_run_registry_markdown([revise], path)
    assert path.read_text(encoding="utf-8").endswith("\n")
