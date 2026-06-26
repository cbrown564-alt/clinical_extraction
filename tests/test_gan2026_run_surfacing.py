"""Tests for Gan registry-driven run surfacing."""

from __future__ import annotations

from pathlib import Path

from clinical_extraction.core.registry import (
    RunRegistryEntry,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_surfacing import (
    CURATED_BY_RUN_ID,
    LIVE_DETERMINISTIC,
    build_surfaced_runs,
    reconcile_registry_entries,
    resolve_run_id,
)


def test_build_surfaced_runs_includes_live_and_replay_comparators() -> None:
    surfaced = build_surfaced_runs([])

    run_ids = [item["run_id"] for item in surfaced]
    assert run_ids[0] == LIVE_DETERMINISTIC.run_id
    assert len(run_ids) == len(CURATED_BY_RUN_ID)
    assert "Hybrid (LLM extract) · DeepSeek" in {item["label"] for item in surfaced}
    assert all(item["value"] == item["run_id"] for item in surfaced)


def test_resolve_run_id_maps_legacy_family_values() -> None:
    assert resolve_run_id("hybrid_structured_events") == CURATED_BY_RUN_ID[
        "gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07"
    ].run_id
    assert resolve_run_id("rules_only") == "rules_only"


def test_reconcile_registry_seeds_missing_qwen_rows(tmp_path: Path) -> None:
    existing = RunRegistryEntry(
        run_id="gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07",
        artifact_paths=(
            "experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl",
        ),
        date="2026-06-07",
        pipeline_family="hybrid_structured_events",
        split="validation",
        row_count=750,
        model="openai/gpt-4.1-mini",
        model_role="hybrid comparator",
        mode="live",
        replay_status="saved_output_replay",
        decision="revise",
    )
    reconciled = reconcile_registry_entries([existing])
    by_id = {entry.run_id: entry for entry in reconciled}

    assert by_id[existing.run_id].surface_as_architecture is True
    assert by_id[existing.run_id].display_label == "Hybrid (LLM extract) · GPT-4.1-mini"
    assert by_id[existing.run_id].registry_roles == ("architecture_comparator",)
    qwen_id = (
        "gan2026_three_way_comparison_validation750_"
        "hybrid_structured_events_qwen3635b_2026-06-08"
    )
    assert qwen_id in by_id
    assert by_id[qwen_id].surface_as_architecture is True
    assert by_id[qwen_id].registry_roles == ("architecture_comparator",)

    registry_path = tmp_path / "registry.jsonl"
    write_run_registry(reconciled, registry_path)
    assert registry_path.exists()
