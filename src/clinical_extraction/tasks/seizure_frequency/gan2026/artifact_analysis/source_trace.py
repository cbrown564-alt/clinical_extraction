"""Source-id and selected-evidence trace checks for Gan 2026 components."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def build_selected_source_id_trace(
    structured_record: Mapping[str, Any], *, exact_trace: bool
) -> dict[str, Any]:
    """Materialize source-id status for an already selected evidence trace."""

    selected_source_ids = [
        str(value) for value in structured_record.get("selected_source_ids") or []
    ]
    declared_status = str(structured_record.get("source_id_status") or "").strip()
    expected_source_ids = ["note"] if exact_trace else []
    missing_expected_source_ids = [
        source_id for source_id in expected_source_ids if source_id not in selected_source_ids
    ]
    unexpected_source_ids = [
        source_id for source_id in selected_source_ids if source_id not in expected_source_ids
    ]
    if declared_status:
        status = declared_status
    elif not exact_trace:
        status = "invalid"
    elif selected_source_ids:
        status = (
            "valid" if not missing_expected_source_ids and not unexpected_source_ids else "invalid"
        )
    else:
        status = "not_instrumented"
    return {
        "source_id_status": status,
        "declared_source_id_status": declared_status or None,
        "selected_source_ids": selected_source_ids,
        "expected_source_ids": expected_source_ids,
        "missing_expected_source_ids": missing_expected_source_ids,
        "unexpected_source_ids": unexpected_source_ids,
        "trace_basis": (
            "exact_selected_evidence" if exact_trace else "non_exact_or_missing_evidence"
        ),
    }


def projection_source_id_consistency(
    candidate: Mapping[str, Any] | None,
    projected: Mapping[str, Any],
) -> dict[str, Any]:
    """Check whether a projected selected-state candidate is source traceable."""

    if candidate is None:
        return {
            "consistent": True,
            "status": "not_applicable",
            "selected_source_ids": [],
            "required_source_id_status": "valid",
            "failures": [],
        }
    failures: list[str] = []
    source_id_status = str(candidate.get("source_id_status") or "")
    selected_source_ids = [str(candidate.get("source_id") or "")]
    if projected.get("scorable") and source_id_status != "valid":
        failures.append("scorable_projection_without_valid_source_id")
    if projected.get("scorable") and not candidate.get("exact_evidence"):
        failures.append("scorable_projection_without_exact_evidence")
    if projected.get("scorable") and not str(candidate.get("evidence") or "").strip():
        failures.append("scorable_projection_without_evidence")
    return {
        "consistent": not failures,
        "status": "valid" if not failures else "invalid",
        "selected_source_ids": selected_source_ids,
        "source_id_status": source_id_status,
        "exact_evidence": bool(candidate.get("exact_evidence")),
        "failures": failures,
    }


def summarize_projection_source_id_consistency(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    inconsistent = [
        int(row["source_row_index"])
        for row in rows
        if not row["projection_source_id_consistency"]["consistent"]
    ]
    return {
        "projection_source_id_consistent_rows": len(rows) - len(inconsistent),
        "projection_source_id_inconsistent_rows": len(inconsistent),
        "projection_source_id_inconsistent_source_row_indices": inconsistent,
    }
