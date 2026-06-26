"""Quarantine switches for target-indicator projection families."""

from __future__ import annotations

from collections.abc import Mapping

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.catalog import (
    quarantined_projection_families,
)

ProjectionFamilySwitches = Mapping[str, bool]

QUARANTINED_TARGET_PROJECTION_FAMILIES = quarantined_projection_families()
TARGET_PROJECTION_AUDIT_REPLAY_SWITCHES = {
    family: True for family in sorted(QUARANTINED_TARGET_PROJECTION_FAMILIES)
}


def audit_only_projection_replay_switches() -> dict[str, bool]:
    """Enable quarantined projection families for same-raw replay audits only."""

    return dict(TARGET_PROJECTION_AUDIT_REPLAY_SWITCHES)


def effective_target_projection_family_switches(
    switches: ProjectionFamilySwitches | None = None,
) -> dict[str, bool]:
    """Return the effective enabled/disabled state for quarantined families."""

    return {
        family: is_projection_family_enabled(family, switches)
        for family in sorted(QUARANTINED_TARGET_PROJECTION_FAMILIES)
    }


def is_projection_family_enabled(
    family: str,
    switches: ProjectionFamilySwitches | None,
) -> bool:
    if switches is not None and family in switches:
        return switches[family]
    return family not in QUARANTINED_TARGET_PROJECTION_FAMILIES


def quarantined_projection_family_warning(family: str) -> str:
    return f"quarantined_projection_family: {family}"
