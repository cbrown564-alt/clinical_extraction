"""Shared constants for cross-model reliability analysis."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.loader import (
    load_rich_schema_runs,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.types import (
    ReliabilityRun,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)

FAMILIES: tuple[str, ...] = tuple(TARGET_INDICATORS)

RICH_SCHEMA_RUNS: tuple[ReliabilityRun, ...] = load_rich_schema_runs()

_FAMILY_BASE_RISK = {
    "Diagnosis": 0.22,
    "SeizureFrequency": 0.25,
    "Prescription": 0.16,
    "Investigations": 0.14,
}
_CALIBRATION_FEATURES: tuple[str, ...] = (
    "family:Diagnosis",
    "family:SeizureFrequency",
    "family:Prescription",
    "family:Investigations",
    "evidence_invalid",
    "low_confidence",
    "source_final_delta",
    "active_rate",
    "plan_language",
    "result_state",
    "deterministic_action_count",
    "prediction_count",
)
_PLAN_LANGUAGE = re.compile(
    r"\b(?:plan|planned|future|increase|reduce|switch|commence|start|"
    r"consider|option|suggest|if\s+.*then)\b",
    re.IGNORECASE,
)
