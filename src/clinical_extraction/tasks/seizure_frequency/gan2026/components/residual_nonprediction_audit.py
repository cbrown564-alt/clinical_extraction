"""Audit non-prediction rows from the Gan 2026 staged decision layer."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


def build_residual_nonprediction_rows(
    decision_rows: Sequence[Mapping[str, Any]],
    assembly_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Join non-prediction decision rows to their blocked source candidates."""

    assembly_by_source = {
        int(row["source_row_index"]): row
        for row in assembly_rows
        if row.get("source_row_index") is not None
    }
    audit_rows = []
    for decision in decision_rows:
        if decision.get("prediction_bearing") is True:
            continue
        source_row_index = int(decision["source_row_index"])
        assembly = assembly_by_source.get(source_row_index, {})
        router = assembly.get("rq9_selective_action_router_v3") or {}
        source_candidate = router.get("source_candidate") or {}
        audit_rows.append(
            {
                "artifact_kind": "gan2026_residual_nonprediction_audit_row",
                "source_row_index": source_row_index,
                "final_action": decision.get("final_action"),
                "decision_reason": decision.get("decision_reason"),
                "secondary_reasons": decision.get("secondary_reasons", []),
                "gold_label": decision.get("gold_label"),
                "blocked_candidate_label": source_candidate.get("final_label"),
                "blocked_candidate_purist_correct": source_candidate.get(
                    "purist_correct"
                ),
                "blocked_candidate_pragmatic_correct": source_candidate.get(
                    "pragmatic_correct"
                ),
                "blocked_candidate_evidence": source_candidate.get(
                    "selected_evidence"
                ),
                "blocked_candidate_source_ids": source_candidate.get(
                    "selected_source_ids", []
                ),
            }
        )
    return audit_rows


def summarize_residual_nonpredictions(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize residual abstain and review pressure."""

    action_counts = Counter(str(row.get("final_action")) for row in rows)
    reason_counts = Counter(str(row.get("decision_reason")) for row in rows)
    gold_counts = Counter(str(row.get("gold_label")) for row in rows)
    blocked_correct_rows = sum(
        row.get("blocked_candidate_purist_correct") is True for row in rows
    )
    blocked_wrong_rows = sum(
        row.get("blocked_candidate_purist_correct") is False for row in rows
    )
    return {
        "component_name": "residual_nonprediction_audit",
        "row_count": len(rows),
        "action_counts": dict(sorted(action_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "gold_label_counts": dict(sorted(gold_counts.items())),
        "blocked_correct_rows": blocked_correct_rows,
        "blocked_wrong_rows": blocked_wrong_rows,
        "blocked_unknown_correctness_rows": len(rows)
        - blocked_correct_rows
        - blocked_wrong_rows,
        "non_unknown_gold_rows": sum(
            row.get("gold_label") not in {None, "unknown"} for row in rows
        ),
        "recommended_next_step": (
            "Run a selective abstention-pressure review before full-validation "
            "verifier use or promotion."
        ),
        "claim_language": (
            "Validation-development audit of non-prediction rows from the staged "
            "decision layer. Gold and blocked-candidate correctness are development "
            "accounting only; this does not authorize locked-test inspection, "
            "benchmark-comparable claims, or full-validation verifier use."
        ),
    }


def write_summary_json(summary: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 Residual Non-Prediction Audit",
        "",
        str(summary["claim_language"]),
        "",
        "## Summary",
        "",
        (
            f"The staged decision layer has {summary['row_count']} "
            "non-prediction rows. Development accounting says the blocked source "
            f"candidate was Purist-correct on {summary['blocked_correct_rows']} rows "
            f"and Purist-wrong on {summary['blocked_wrong_rows']} rows."
        ),
        "",
        "## Actions",
        "",
        "| Action | Rows |",
        "| --- | ---: |",
    ]
    for action, count in summary["action_counts"].items():
        lines.append(f"| `{action}` | {count} |")
    lines.extend(["", "## Reasons", "", "| Reason | Rows |", "| --- | ---: |"])
    for reason, count in summary["reason_counts"].items():
        lines.append(f"| `{reason}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Audit JSONL: `{jsonl_path}`",
            f"- Audit summary JSON: `{json_path}`",
            "",
            "## Rows",
            "",
            "| Row | Action | Reason | Gold | Blocked label | Blocked Purist-correct |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['source_row_index']} | `{row['final_action']}` | "
            f"`{row['decision_reason']}` | `{row['gold_label']}` | "
            f"`{row['blocked_candidate_label']}` | "
            f"{row['blocked_candidate_purist_correct']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
