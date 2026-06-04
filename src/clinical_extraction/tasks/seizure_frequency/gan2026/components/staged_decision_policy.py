"""Prediction-bearing decision policy for assembled Gan 2026 component rows."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

PREDICT = "predict"
ABSTAIN = "abstain"
HUMAN_REVIEW = "human_review"
POLICY_NAME = "gan2026_staged_decision_policy_v0"


def build_decision_rows(
    assembly_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Build compact decision rows from assembled component rows."""

    return [build_decision_row(row) for row in assembly_rows]


def build_decision_row(assembly_row: Mapping[str, Any]) -> dict[str, Any]:
    """Apply the conservative staged decision policy to one assembled row."""

    router = assembly_row.get("rq9_selective_action_router_v3") or {}
    safety = assembly_row.get("selective_safety_floor_gate_v0") or {}
    reasoner = assembly_row.get("hybrid_reasoner_replay") or {}
    source_candidate = router.get("source_candidate") or {}
    action = str(router.get("selective_action") or HUMAN_REVIEW)
    prediction_bearing = action == PREDICT

    return {
        "artifact_kind": "gan2026_staged_decision_policy_row",
        "policy_name": POLICY_NAME,
        "source_row_index": assembly_row["source_row_index"],
        "split": assembly_row.get("split", "validation"),
        "split_manifest": assembly_row.get("split_manifest", "gan2026_split_v1"),
        "gold_label": assembly_row.get("gold_label"),
        "final_action": action,
        "prediction_bearing": prediction_bearing,
        "prediction_label": source_candidate.get("final_label")
        if prediction_bearing
        else None,
        "selected_evidence": source_candidate.get("selected_evidence")
        if prediction_bearing
        else None,
        "selected_source_ids": source_candidate.get("selected_source_ids", [])
        if prediction_bearing
        else [],
        "selected_evidence_exact": source_candidate.get("selected_evidence_exact")
        if prediction_bearing
        else None,
        "selected_source_ids_exist": safety.get("selected_source_ids_exist")
        if prediction_bearing
        else None,
        "decision_reason": router.get("primary_reason"),
        "secondary_reasons": router.get("secondary_reasons", []),
        "source_layer": router.get("source_layer"),
        "component_presence": dict(assembly_row.get("component_presence", {})),
        "component_status": {
            "reasoner": reasoner.get("component_status", {}),
            "safety_floor_selected_evidence_exact": safety.get(
                "selected_evidence_exact"
            ),
            "safety_floor_selected_source_ids_exist": safety.get(
                "selected_source_ids_exist"
            ),
            "router_action": action,
        },
        "development_accounting": {
            "purist_correct": source_candidate.get("purist_correct")
            if prediction_bearing
            else None,
            "pragmatic_correct": source_candidate.get("pragmatic_correct")
            if prediction_bearing
            else None,
        },
        "verifier_used": False,
    }


def summarize_decision_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize prediction and non-prediction decisions."""

    action_counts = Counter(str(row.get("final_action")) for row in rows)
    prediction_rows = [row for row in rows if row.get("prediction_bearing") is True]
    return {
        "component_name": "staged_decision_policy_v0",
        "row_count": len(rows),
        "prediction_bearing_rows": len(prediction_rows),
        "non_prediction_rows": len(rows) - len(prediction_rows),
        "action_counts": dict(sorted(action_counts.items())),
        "selective_purist_accuracy": _safe_rate(
            sum(
                row.get("development_accounting", {}).get("purist_correct") is True
                for row in prediction_rows
            ),
            len(prediction_rows),
        ),
        "selective_pragmatic_accuracy": _safe_rate(
            sum(
                row.get("development_accounting", {}).get("pragmatic_correct") is True
                for row in prediction_rows
            ),
            len(prediction_rows),
        ),
        "verifier_rows_used": sum(row.get("verifier_used") is True for row in rows),
        "claim_language": (
            "Conservative no-call decision layer over assembled validation rows. "
            "Only router predict rows are prediction-bearing; abstain and "
            "human_review rows remain non-predictions. The promoted verifier "
            "slice is not used for full-validation decisions."
        ),
    }


def _safe_rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0
