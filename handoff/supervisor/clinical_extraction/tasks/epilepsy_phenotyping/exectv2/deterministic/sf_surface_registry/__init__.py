"""Canonical SF surface registry (P1-1 Phase 0–5).

One typed catalog of SeizureFrequency clinical surfaces. Phase adapters live
under ``adapters/``; see ``README.md`` for migration status and public API.
"""

from __future__ import annotations

from .catalog import load_all_catalog_rules, rules_for_phase, validate_unique_rule_ids
from .types import SurfacePhase, SurfaceRule

__all__ = [
    "SurfacePhase",
    "SurfaceRule",
    "load_all_catalog_rules",
    "rules_for_phase",
    "validate_unique_rule_ids",
]
