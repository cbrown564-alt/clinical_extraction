"""Scoring-layer reporting helpers for ExECTv2 architecture evaluation.

``assembly`` and other non-report pipelines import from here so they do not
depend on the ``reports`` package directly.
"""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.recovery import (
    error_taxonomy_summary,
    evidence_validation_summary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.render import (
    architecture_report,
)

__all__ = [
    "architecture_report",
    "error_taxonomy_summary",
    "evidence_validation_summary",
]
