"""Canonical claim-boundary and restricted-surface policy for splits and registry rows."""

from __future__ import annotations

from typing import Any


def claim_boundary_for_split(split: str) -> str:
    """Return the registry/MLflow claim-boundary tag for a split name."""

    lower = split.lower()
    if "full200" in lower:
        return "full200_aggregate_only"
    if "test" in lower or "holdout" in lower:
        return "locked_holdout_aggregate"
    if "validation" in lower:
        return "validation_development"
    if "dev" in lower:
        return "dev_only"
    return "analysis_only"


def fresh_evidence_claim_boundary_for_split(split: str) -> str:
    """Return the human-readable claim boundary for V12 fresh-evidence artifacts."""

    if split == "test":
        return (
            "frozen aggregate-only V12 test450 audit; first readout is aggregate "
            "Purist/Pragmatic and health metrics only; no row-level test inspection, "
            "post-test tuning, or benchmark-comparable claim without separate review"
        )
    return (
        "validation-development V12 fresh-evidence reasoner; no holdout use, "
        "no row-level test inspection, and no benchmark claim"
    )


def restricted_surface_for_split(split: str) -> bool:
    """Return whether a split name denotes a restricted aggregate-only surface."""

    lower = split.lower()
    return "full200" in lower or "test" in lower or "holdout" in lower


def restricted_surface_for_registry_entry(entry: Any) -> bool:
    """Return whether a registry entry's split denotes a restricted surface."""

    return restricted_surface_for_split(str(getattr(entry, "split", "")))
