"""SeizureFrequency benchmark rewrite dictionary (registry facade)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.adapters.convention import (
    apply_rewrite_adapter,
    is_noise_adapter,
    residual_candidates_adapter,
)


def sf_convention_rewrite(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> tuple[str, dict[str, Any], str] | None:
    """Apply SF benchmark rewrites via the canonical surface registry."""

    return apply_rewrite_adapter(text, evidence=evidence, attributes=attributes)


def is_sf_convention_noise(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> bool:
    """True for SF renderings that are prompt-selection residue, not frequency facts."""

    return is_noise_adapter(text, evidence=evidence, attributes=attributes)


def sf_residual_additions(note_text: str) -> list[tuple[str, str, dict[str, str]]]:
    """Return bounded dev residual SF additions from explicit source patterns."""

    return residual_candidates_adapter(note_text)
