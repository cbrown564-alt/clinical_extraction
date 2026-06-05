"""Promotion analysis for Gan 2026 trigger-context release proposals."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

POLICY_NAME = "gan2026_trigger_release_promotion_analysis_v0"


def build_promotion_analysis(
    release_rows: Sequence[Mapping[str, Any]],
    proposed_decision_rows: Sequence[Mapping[str, Any]],
    matrix_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Evaluate whether trigger-context release rows pass validation gates."""

    proposed_by_source = _by_source(proposed_decision_rows)
    matrix_by_source = _by_source(matrix_rows)
    row_analyses = []
    issues = []
    for release in release_rows:
        source_row_index = int(release["source_row_index"])
        proposed = proposed_by_source.get(source_row_index)
        matrix = matrix_by_source.get(source_row_index)
        if proposed is None:
            issues.append(f"missing_proposed_decision:{source_row_index}")
            continue
        if matrix is None:
            issues.append(f"missing_matrix_row:{source_row_index}")
            continue
        row_issues = _row_issues(release, proposed, matrix)
        issues.extend(f"{issue}:{source_row_index}" for issue in row_issues)
        row_analyses.append(_row_analysis(release, proposed, matrix, row_issues))

    w_to_c = sum(row["transition"] == "W_to_C" for row in row_analyses)
    c_to_w = sum(row["transition"] == "C_to_W" for row in row_analyses)
    caveat_rows = sum(row["category_correct_not_exact_label"] for row in row_analyses)
    if release_rows and (w_to_c != len(release_rows) or c_to_w != 0):
        issues.append(
            "promotion_gate_expected_all_releases_w_to_c_and_zero_c_to_w"
        )
    decision = _decision(issues, caveat_rows)
    return {
        "component_name": "trigger_release_promotion_analysis",
        "policy_name": POLICY_NAME,
        "release_rows": len(release_rows),
        "analyzed_rows": len(row_analyses),
        "w_to_c_rows": w_to_c,
        "c_to_w_rows": c_to_w,
        "category_correct_not_exact_label_rows": caveat_rows,
        "issues": issues,
        "decision": decision,
        "claim_language": (
            "Validation-development trigger-context release promotion analysis. "
            "It uses validation accounting and component-matrix fields only; it "
            "does not inspect locked-test rows, change scorer policy, change gold "
            "labels, or create a benchmark-comparable claim."
        ),
        "rows": row_analyses,
    }


def write_summary_json(summary: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(summary: Mapping[str, Any], path: Path, *, json_path: Path) -> None:
    lines = [
        "# Gan 2026 Trigger-Context Release Promotion Analysis",
        "",
        str(summary["claim_language"]),
        "",
        "## Decision",
        "",
        f"Decision: `{summary['decision']}`.",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| release rows | {summary['release_rows']} |",
        f"| analyzed rows | {summary['analyzed_rows']} |",
        f"| W->C rows | {summary['w_to_c_rows']} |",
        f"| C->W rows | {summary['c_to_w_rows']} |",
        (
            "| category-correct not exact-label rows | "
            f"{summary['category_correct_not_exact_label_rows']} |"
        ),
        f"| issues | `{', '.join(summary['issues']) or 'none'}` |",
        "",
        "## Rows",
        "",
        "| Row | Label | Matrix action | Transition | Caveat | Issues |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for row in summary["rows"]:
        lines.append(
            f"| {row['source_row_index']} | `{row['prediction_label']}` | "
            f"`{row['matrix_final_action']}` | `{row['transition']}` | "
            f"`{row['caveat']}` | `{', '.join(row['issues']) or 'none'}` |"
        )
    lines.extend(["", "## Artifact", "", f"- Summary JSON: `{json_path}`", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _row_analysis(
    release: Mapping[str, Any],
    proposed: Mapping[str, Any],
    matrix: Mapping[str, Any],
    issues: Sequence[str],
) -> dict[str, Any]:
    purist_correct = (
        proposed.get("development_accounting", {}).get("purist_correct") is True
    )
    matrix_comparator_correct = _as_bool(matrix.get("deterministic_comparator_purist_correct"))
    transition = "W_to_C" if purist_correct and not matrix_comparator_correct else "other"
    if not purist_correct and matrix_comparator_correct:
        transition = "C_to_W"
    elif purist_correct and matrix_comparator_correct:
        transition = "C_to_C"
    category_caveat = (
        purist_correct
        and str(matrix.get("gold_label") or "") != str(release.get("prediction_label") or "")
    )
    return {
        "source_row_index": int(release["source_row_index"]),
        "prediction_label": release.get("prediction_label"),
        "selected_evidence": release.get("selected_evidence"),
        "selected_source_ids": release.get("selected_source_ids", []),
        "matrix_gold_label": matrix.get("gold_label"),
        "matrix_final_action": matrix.get("final_action"),
        "matrix_comparator_transition": matrix.get("comparator_transition"),
        "proposed_purist_correct": purist_correct,
        "transition": transition,
        "category_correct_not_exact_label": category_caveat,
        "caveat": "category_correct_not_exact_label" if category_caveat else "",
        "issues": list(issues),
    }


def _row_issues(
    release: Mapping[str, Any],
    proposed: Mapping[str, Any],
    matrix: Mapping[str, Any],
) -> list[str]:
    issues = []
    if release.get("release_decision") != "release_as_prediction":
        issues.append("not_release_as_prediction")
    if not release.get("prediction_label"):
        issues.append("missing_prediction_label")
    if not release.get("selected_evidence"):
        issues.append("missing_selected_evidence")
    if not release.get("selected_source_ids"):
        issues.append("missing_selected_source_ids")
    if proposed.get("selected_evidence_exact") is not True:
        issues.append("selected_evidence_not_exact")
    if proposed.get("development_accounting", {}).get("purist_correct") is not True:
        issues.append("release_not_purist_correct")
    if matrix.get("final_action") not in {"abstain", "human_review"}:
        issues.append("matrix_row_was_not_nonprediction")
    return issues


def _decision(issues: Sequence[str], caveat_rows: int) -> str:
    if issues:
        return "reject"
    if caveat_rows:
        return "promote_with_category_caveat"
    return "promote"


def _by_source(rows: Sequence[Mapping[str, Any]]) -> dict[int, Mapping[str, Any]]:
    return {
        int(row["source_row_index"]): row
        for row in rows
        if row.get("source_row_index") is not None
    }


def _as_bool(value: Any) -> bool:
    if value is True or value == "True":
        return True
    return False
