"""First deterministic all-entity baseline for ExECTv2.

This package composes the mature SeizureFrequency deterministic extractor with
high-precision rules for the first structured entities named in the GPT-first
strategy: Prescription, Investigations, and Diagnosis. It is intentionally a
transparent floor and candidate source, not a benchmark-complete solution.
"""

from __future__ import annotations

from .orchestrator import (
    ACTIVE_DETERMINISTIC_ENTITIES,
    extract_deterministic_all9,
    run_all9_on_letters,
)
from .prescription import _canonical_dose_unit
from .text import _frequency_from_text

__all__ = [
    "ACTIVE_DETERMINISTIC_ENTITIES",
    "extract_deterministic_all9",
    "run_all9_on_letters",
    "_canonical_dose_unit",
    "_frequency_from_text",
]
