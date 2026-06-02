"""Named repair-mode metadata for Gan 2026 attribution artifacts."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

REPAIR_MODE_METADATA: Mapping[str, Mapping[str, Any]] = {
    "raw_model": {
        "repair_mode": "raw_model",
        "attribution_source": "raw_llm_output",
        "repair_family": "none",
        "semantic_selection_owner": "llm",
        "deterministic_semantic_repair": False,
        "scorer_facing": False,
    },
    "strict_format": {
        "repair_mode": "strict_format",
        "attribution_source": "raw_llm_output_plus_format_repair",
        "repair_family": "format_preserving_label_repair",
        "semantic_selection_owner": "llm",
        "deterministic_semantic_repair": False,
        "scorer_facing": True,
    },
    "clean_scorer_facing": {
        "repair_mode": "clean_scorer_facing",
        "attribution_source": "raw_llm_output_plus_clean_scorer_policy",
        "repair_family": "clean_scorer_facing_gold_policy",
        "semantic_selection_owner": "llm",
        "deterministic_semantic_repair": False,
        "scorer_facing": True,
    },
    "selected_evidence_derivation": {
        "repair_mode": "selected_evidence_derivation",
        "attribution_source": "llm_selected_evidence_plus_deterministic_derivation",
        "repair_family": "selected_evidence_label_derivation",
        "semantic_selection_owner": "llm_evidence_selection_then_deterministic_label",
        "deterministic_semantic_repair": True,
        "scorer_facing": True,
    },
    "hybrid_full_stack": {
        "repair_mode": "hybrid_full_stack",
        "attribution_source": "raw_llm_output_plus_all_deterministic_repair_families",
        "repair_family": "full_structured_events_repair_stack",
        "semantic_selection_owner": "hybrid",
        "deterministic_semantic_repair": True,
        "scorer_facing": True,
    },
    "deterministic_candidate_top": {
        "repair_mode": "deterministic_candidate_top",
        "attribution_source": "deterministic_candidate_generator",
        "repair_family": "rules_only_candidate_selection",
        "semantic_selection_owner": "deterministic",
        "deterministic_semantic_repair": True,
        "scorer_facing": True,
    },
    "raw_hybrid_adjudicator": {
        "repair_mode": "raw_hybrid_adjudicator",
        "attribution_source": "llm_adjudicator_over_deterministic_candidates",
        "repair_family": "hybrid_adjudicator_label_repair",
        "semantic_selection_owner": "hybrid",
        "deterministic_semantic_repair": True,
        "scorer_facing": True,
    },
    "conservative_hybrid_adjudicator": {
        "repair_mode": "conservative_hybrid_adjudicator",
        "attribution_source": "llm_adjudicator_plus_conservative_deterministic_gates",
        "repair_family": "hybrid_overreach_gates_and_deterministic_fallback",
        "semantic_selection_owner": "hybrid",
        "deterministic_semantic_repair": True,
        "scorer_facing": True,
    },
    "custom": {
        "repair_mode": "custom",
        "attribution_source": "custom_repair_configuration",
        "repair_family": "custom",
        "semantic_selection_owner": "mixed_or_unspecified",
        "deterministic_semantic_repair": None,
        "scorer_facing": None,
    },
}


def repair_mode_metadata(mode: str | None) -> dict[str, Any]:
    """Return stable attribution metadata for a named repair mode."""

    if mode is None:
        return {}
    metadata = REPAIR_MODE_METADATA.get(mode, REPAIR_MODE_METADATA["custom"])
    payload = dict(metadata)
    payload["repair_mode"] = mode
    return payload


def repair_mode_layers(modes: Iterable[str]) -> dict[str, dict[str, Any]]:
    """Build a per-layer repair-mode metadata map."""

    return {mode: repair_mode_metadata(mode) for mode in modes}
