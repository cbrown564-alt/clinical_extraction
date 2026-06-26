"""Seizure-frequency rate extraction rules for ExECTv2 (Stack A).

RuleSpec metadata lives in ``sf_surface_registry/catalog/extract.yaml``.
Builders and patterns live in ``rate_builders.py``; ``RATE_RULES`` is assembled
by ``sf_surface_registry/adapters/extraction.py``.
"""
from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    PERIOD_UNIT,
)

__all__ = ["PERIOD_UNIT"]


def __getattr__(name: str) -> Any:
    if name.startswith("__") and name.endswith("__"):
        raise AttributeError(name)
    from .extract_reexports import extract_reexport

    return extract_reexport(name)
