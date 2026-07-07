"""Seizure-frequency rate builders for ExECTv2 (Stack A).

``PERIOD_UNIT`` is canonical in ``sf_surface_registry.patterns``.
Assembled ``RATE_RULES`` live in ``sf_surface_registry.adapters.extraction``.
"""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    PERIOD_UNIT,
)

__all__ = ["PERIOD_UNIT"]
