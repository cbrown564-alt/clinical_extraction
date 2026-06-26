"""Aggregate telemetry helpers for component-ablation replay."""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)


def aggregate_validity_rates(
    summary: dict[str, Any],
    expected_row_count: int,
) -> dict[str, Any]:
    diagnostics = lane_diagnostic_values(summary)
    raw_mentions = sum(int(row.get("raw_mentions", 0)) for row in diagnostics)
    evidence_invalid = sum(int(row.get("evidence_invalid_dropped", 0)) for row in diagnostics)
    parse_failures = sum(int(row.get("parse_schema_failures", 0)) for row in diagnostics)
    family_cells = max(expected_row_count * len(TARGET_INDICATORS), 1)
    return {
        "schema_validity": round_rate(family_cells - parse_failures, family_cells),
        "schema_validity_basis": "family_lane_parse_schema_failures",
        "evidence_validity": round_rate(raw_mentions - evidence_invalid, raw_mentions),
        "evidence_validity_basis": "raw_mentions_minus_evidence_invalid_dropped",
        "minimum_exact_evidence_rate": min(
            [float(row.get("exact_evidence_rate", 0.0)) for row in diagnostics] or [1.0]
        ),
    }


def aggregate_operational_counts(summary: dict[str, Any]) -> dict[str, Any]:
    diagnostics = lane_diagnostic_values(summary)
    return {
        "call_failures": sum(int(row.get("call_failures", 0)) for row in diagnostics),
        "parse_failures": sum(int(row.get("parse_schema_failures", 0)) for row in diagnostics),
        "evidence_invalid_dropped": sum(
            int(row.get("evidence_invalid_dropped", 0)) for row in diagnostics
        ),
        "raw_mentions": sum(int(row.get("raw_mentions", 0)) for row in diagnostics),
        "scored_mentions": sum(int(row.get("scored_mentions", 0)) for row in diagnostics),
        "exact_evidence_mentions": sum(
            int(row.get("exact_evidence_mentions", 0)) for row in diagnostics
        ),
        "abstentions": "not_recorded_in_source_summary",
        "missing_outputs": "not_recorded_in_source_summary",
    }


def deterministic_action_counts(summary: dict[str, Any]) -> dict[str, Any]:
    fact_origin = summary.get("fact_origin_accounting", {})
    if not isinstance(fact_origin, dict):
        return {}
    by_surface = fact_origin.get("by_surface", {})
    return dict(by_surface) if isinstance(by_surface, dict) else {}


def lane_diagnostic_values(summary: dict[str, Any]) -> list[dict[str, Any]]:
    diagnostics = summary.get("lane_diagnostics", {})
    if not isinstance(diagnostics, dict):
        return []
    return [dict(row) for row in diagnostics.values() if isinstance(row, dict)]


def round_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 1.0
    return round(float(numerator) / float(denominator), 4)

