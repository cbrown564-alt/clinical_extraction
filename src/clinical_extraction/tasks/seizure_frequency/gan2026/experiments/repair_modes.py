"""Named repair-mode metadata for Gan 2026 attribution artifacts."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from clinical_extraction.paper.rungs import normalize_repair_mode

REPAIR_MODE_METADATA: Mapping[str, Mapping[str, Any]] = {
    "strict_json_raw_model": {
        "repair_mode": "strict_json_raw_model",
        "attribution_source": "strict_json_raw_llm_output",
        "repair_family": "none",
        "semantic_selection_owner": "llm",
        "deterministic_semantic_repair": False,
        "scorer_facing": False,
    },
    "json_dialect_only": {
        "repair_mode": "json_dialect_only",
        "attribution_source": "raw_llm_output_plus_json_dialect_repair",
        "repair_family": "python_literal_json_dialect_repair",
        "semantic_selection_owner": "llm",
        "deterministic_semantic_repair": False,
        "scorer_facing": False,
    },
    "raw_model": {
        "repair_mode": "raw_model",
        "attribution_source": "raw_llm_output_plus_json_dialect_repair",
        "repair_family": "python_literal_json_dialect_repair",
        "semantic_selection_owner": "llm",
        "deterministic_semantic_repair": False,
        "scorer_facing": False,
    },
    "llm_encode": {
        "repair_mode": "llm_encode",
        "attribution_source": "llm_selected_evidence_plus_deterministic_derivation",
        "repair_family": "selected_evidence_label_derivation",
        "semantic_selection_owner": "llm_evidence_selection_then_deterministic_label",
        "deterministic_semantic_repair": True,
        "scorer_facing": True,
    },
    "llm_select": {
        "repair_mode": "llm_select",
        "attribution_source": "raw_llm_output_plus_all_deterministic_repair_families",
        "repair_family": "full_structured_events_repair_stack",
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
    """Return stable attribution metadata for a named repair mode.

    Legacy names ``selected_evidence_derivation``, ``hybrid_full_stack``,
    and ``llm_revise`` resolve to ``llm_encode`` and ``llm_select``.
    """

    if mode is None:
        return {}
    resolved = normalize_repair_mode(mode)
    metadata = REPAIR_MODE_METADATA.get(resolved, REPAIR_MODE_METADATA["custom"])
    payload = dict(metadata)
    payload["repair_mode"] = resolved
    return payload


def repair_mode_layers(modes: Iterable[str]) -> dict[str, dict[str, Any]]:
    """Build a per-layer repair-mode metadata map."""

    return {normalize_repair_mode(mode): repair_mode_metadata(mode) for mode in modes}
