"""Registry-driven surfacing for Gan Explorer and Component Impact.

The curated run list is the source of truth for which validation-750 comparators
appear in the Example Explorer dropdown and the Component Impact stage ladders.
Registry rows carry the same fields via ``surface_as_architecture`` so the
Observatory API and reconcile script stay aligned.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.core.registry import RunRegistryEntry, load_run_registry

ComparisonRole = Literal["control", "diagnostic"]
ArchitectureKind = Literal["rules_only", "hybrid", "llm_only"]


@dataclass(frozen=True)
class SurfacedRunCuration:
    """One Explorer / Component Impact comparator row."""

    run_id: str
    display_label: str
    architecture_family: ArchitectureKind
    pipeline_family: str
    comparison_role: ComparisonRole
    model_display: str
    source_jsonl: str | None = None
    executable: bool = False
    sort_order: int = 0


LIVE_DETERMINISTIC = SurfacedRunCuration(
    run_id="rules_only",
    display_label="Deterministic canonical",
    architecture_family="rules_only",
    pipeline_family="rules_only",
    comparison_role="control",
    model_display="rules",
    executable=True,
    sort_order=0,
)

SURFACED_REPLAY_RUNS: tuple[SurfacedRunCuration, ...] = (
    SurfacedRunCuration(
        run_id="gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07",
        display_label="Hybrid (LLM extract) · GPT-4.1-mini",
        architecture_family="hybrid",
        pipeline_family="hybrid_structured_events",
        comparison_role="diagnostic",
        model_display="GPT-4.1-mini",
        source_jsonl="experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl",
        sort_order=10,
    ),
    SurfacedRunCuration(
        run_id="gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08",
        display_label="Hybrid (LLM extract) · DeepSeek",
        architecture_family="hybrid",
        pipeline_family="hybrid_structured_events",
        comparison_role="diagnostic",
        model_display="DeepSeek",
        source_jsonl="experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08.jsonl",
        sort_order=11,
    ),
    SurfacedRunCuration(
        run_id="gan2026_three_way_comparison_validation750_hybrid_structured_events_qwen3635b_2026-06-08",
        display_label="Hybrid (LLM extract) · Qwen",
        architecture_family="hybrid",
        pipeline_family="hybrid_structured_events",
        comparison_role="diagnostic",
        model_display="Qwen",
        source_jsonl="experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_qwen3635b_2026-06-08.jsonl",
        sort_order=12,
    ),
    SurfacedRunCuration(
        run_id="gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07",
        display_label="LLM-only (rules in prompt) · GPT-4.1-mini",
        architecture_family="llm_only",
        pipeline_family="llm_only_canonical_pipeline",
        comparison_role="diagnostic",
        model_display="GPT-4.1-mini",
        source_jsonl="experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07.jsonl",
        sort_order=20,
    ),
    SurfacedRunCuration(
        run_id="gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08",
        display_label="LLM-only (rules in prompt) · DeepSeek",
        architecture_family="llm_only",
        pipeline_family="llm_only_canonical_pipeline",
        comparison_role="diagnostic",
        model_display="DeepSeek",
        source_jsonl="experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08.jsonl",
        sort_order=21,
    ),
    SurfacedRunCuration(
        run_id="gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_qwen3635b_2026-06-08",
        display_label="LLM-only (rules in prompt) · Qwen",
        architecture_family="llm_only",
        pipeline_family="llm_only_canonical_pipeline",
        comparison_role="diagnostic",
        model_display="Qwen",
        source_jsonl="experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_qwen3635b_2026-06-08.jsonl",
        sort_order=22,
    ),
)

DETERMINISTIC_COMPONENT_RUN_ID = "deterministic_canonical_pipeline"

CURATED_RUNS: tuple[SurfacedRunCuration, ...] = (LIVE_DETERMINISTIC, *SURFACED_REPLAY_RUNS)
CURATED_BY_RUN_ID: dict[str, SurfacedRunCuration] = {
    curation.run_id: curation for curation in CURATED_RUNS
}

# Legacy Explorer dropdown values map to the default surfaced run per family.
LEGACY_FAMILY_DEFAULT_RUN: dict[str, str] = {
    "rules_only": LIVE_DETERMINISTIC.run_id,
    "hybrid_structured_events": SURFACED_REPLAY_RUNS[0].run_id,
    "llm_only_canonical_pipeline": SURFACED_REPLAY_RUNS[3].run_id,
}


def resolve_run_id(value: str | None) -> str:
    """Map a URL/store value to a curated run id."""

    if not value:
        return LIVE_DETERMINISTIC.run_id
    if value in CURATED_BY_RUN_ID:
        return value
    return LEGACY_FAMILY_DEFAULT_RUN.get(value, LIVE_DETERMINISTIC.run_id)


def curation_for_run(run_id: str) -> SurfacedRunCuration | None:
    return CURATED_BY_RUN_ID.get(run_id)


def build_surfaced_run_payload(
    curation: SurfacedRunCuration,
    *,
    registry_entry: RunRegistryEntry | None = None,
) -> dict[str, Any]:
    """Build one Observatory dropdown entry."""

    has_jsonl = (
        curation.executable
        or (
            registry_entry is not None
            and any(path.endswith(".jsonl") for path in registry_entry.artifact_paths)
        )
        or (curation.source_jsonl is not None)
    )
    return {
        "value": curation.run_id,
        "run_id": curation.run_id,
        "label": curation.display_label,
        "display_label": curation.display_label,
        "executable": curation.executable,
        "kind": curation.architecture_family,
        "architecture_family": curation.architecture_family,
        "pipeline_family": curation.pipeline_family,
        "model": curation.model_display,
        "comparison_role": curation.comparison_role,
        "has_replay_artifact": has_jsonl,
        "run_count": 1 if registry_entry else (1 if curation.executable else 0),
    }


def build_surfaced_runs(
    entries: list[RunRegistryEntry] | None = None,
) -> list[dict[str, Any]]:
    """Return curated Explorer / Component Impact comparators in display order."""

    by_run_id = {entry.run_id: entry for entry in entries or []}
    surfaced: list[dict[str, Any]] = []
    for curation in sorted(CURATED_RUNS, key=lambda item: item.sort_order):
        entry = by_run_id.get(curation.run_id)
        if curation.executable or entry is not None or curation.source_jsonl:
            surfaced.append(build_surfaced_run_payload(curation, registry_entry=entry))
    return surfaced


def apply_curation_to_entry(
    entry: RunRegistryEntry,
    curation: SurfacedRunCuration,
) -> RunRegistryEntry:
    """Return a copy of ``entry`` with surfacing fields set."""

    from dataclasses import replace

    registry_roles = tuple(dict.fromkeys((*entry.registry_roles, "architecture_comparator")))
    return replace(
        entry,
        surface_as_architecture=True,
        display_label=curation.display_label,
        architecture_family=curation.architecture_family,
        comparison_role=curation.comparison_role,
        registry_roles=registry_roles,
    )


def missing_registry_seed(curation: SurfacedRunCuration) -> RunRegistryEntry:
    """Minimal registry row for a curated replay run not yet indexed."""

    assert curation.source_jsonl is not None
    model = {
        "GPT-4.1-mini": "openai/gpt-4.1-mini",
        "DeepSeek": "deepseek/deepseek-chat",
        "Qwen": "ollama_chat/qwen3.6:35b",
    }[curation.model_display]
    return RunRegistryEntry(
        run_id=curation.run_id,
        artifact_paths=(curation.source_jsonl,),
        date="2026-06-08",
        pipeline_family=curation.pipeline_family,
        split="validation",
        row_count=750,
        model=model,
        model_role=f"{curation.architecture_family} architecture comparator",
        mode="validation750 replay",
        replay_status="saved_output_replay",
        decision="revise",
        surface_as_architecture=True,
        display_label=curation.display_label,
        architecture_family=curation.architecture_family,
        comparison_role=curation.comparison_role,
        registry_roles=("architecture_comparator",),
        claim_language_notes=(
            "Registry row seeded by run surfacing reconcile for Explorer/Component Impact."
        ),
    )


def reconcile_registry_entries(entries: list[RunRegistryEntry]) -> list[RunRegistryEntry]:
    """Apply surfacing curation and seed missing replay rows."""

    by_run_id = {entry.run_id: entry for entry in entries}
    updated = dict(by_run_id)
    for curation in SURFACED_REPLAY_RUNS:
        existing = by_run_id.get(curation.run_id)
        if existing is not None:
            updated[curation.run_id] = apply_curation_to_entry(existing, curation)
        else:
            updated[curation.run_id] = missing_registry_seed(curation)
    return sorted(updated.values(), key=lambda entry: entry.run_id)


def load_surfaced_runs_from_registry(registry_path: Path) -> list[dict[str, Any]]:
    return build_surfaced_runs(load_run_registry(registry_path))
