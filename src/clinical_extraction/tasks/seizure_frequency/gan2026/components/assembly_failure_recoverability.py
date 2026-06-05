"""Recoverability analysis for Gan 2026 staged assembly validation failures."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

RECALL_STATUSES = {"exact_label", "purist_category", "semantic_state"}
ACTIONABLE_STATUSES = {"exact_label", "purist_category"}
POLICY_NAME = "gan2026_assembly_failure_recoverability_v0"

FIELDNAMES = [
    "source_row_index",
    "failure_transition",
    "final_action",
    "prediction_label",
    "gold_label",
    "best_recall_status",
    "best_generator",
    "best_candidate_label",
    "best_candidate_kind",
    "best_evidence_status",
    "best_source_id_valid",
    "recoverability_class",
    "candidate_generator_counts",
]


def build_recoverability_rows(
    matrix_rows: Sequence[Mapping[str, Any]],
    candidate_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Join assembly failure rows to candidate-discovery alternatives."""

    candidates_by_source: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for candidate in candidate_rows:
        candidates_by_source[int(candidate["source_row_index"])].append(candidate)

    rows = []
    for matrix in matrix_rows:
        transition = str(matrix.get("comparator_transition") or "")
        if not transition.startswith("W_to_"):
            continue
        source_row_index = int(matrix["source_row_index"])
        candidates = candidates_by_source.get(source_row_index, [])
        best = _best_candidate(candidates)
        rows.append(
            {
                "source_row_index": source_row_index,
                "failure_transition": transition,
                "final_action": matrix.get("final_action"),
                "prediction_label": matrix.get("prediction_label"),
                "gold_label": matrix.get("gold_label"),
                "best_recall_status": best.get("gold_match_status") if best else "",
                "best_generator": best.get("generator_name") if best else "",
                "best_candidate_label": best.get("candidate_label") if best else "",
                "best_candidate_kind": best.get("candidate_kind") if best else "",
                "best_evidence_status": best.get("evidence_status") if best else "",
                "best_source_id_valid": best.get("source_id_valid") if best else None,
                "recoverability_class": _recoverability_class(best),
                "candidate_generator_counts": _generator_counts(candidates),
            }
        )
    rows.sort(key=lambda row: (row["failure_transition"], int(row["source_row_index"])))
    return rows


def summarize_recoverability_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    base_correct_rows: int = 0,
    total_rows: int = 0,
) -> dict[str, Any]:
    """Summarize recoverability by failure transition and candidate generator."""

    by_transition = Counter(str(row["failure_transition"]) for row in rows)
    by_recoverability = Counter(str(row["recoverability_class"]) for row in rows)
    by_best_generator = Counter(str(row["best_generator"] or "none") for row in rows)
    actionable = [
        row for row in rows if row["recoverability_class"] == "actionable_candidate"
    ]
    return {
        "component_name": "assembly_failure_recoverability",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "by_failure_transition": dict(sorted(by_transition.items())),
        "by_recoverability_class": dict(sorted(by_recoverability.items())),
        "by_best_generator": dict(sorted(by_best_generator.items())),
        "actionable_candidate_rows": len(actionable),
        "exact_label_actionable_rows": sum(
            row.get("best_recall_status") == "exact_label" for row in actionable
        ),
        "purist_category_actionable_rows": sum(
            row.get("best_recall_status") == "purist_category" for row in actionable
        ),
        "actionable_candidate_rate": _rate(len(actionable), len(rows)),
        "base_correct_rows": base_correct_rows,
        "total_rows": total_rows,
        "oracle_exact_label_upper_bound_correct_rows": base_correct_rows
        + sum(row.get("best_recall_status") == "exact_label" for row in actionable),
        "oracle_actionable_upper_bound_correct_rows": base_correct_rows
        + len(actionable),
        "oracle_exact_label_upper_bound_score": _rate(
            base_correct_rows
            + sum(row.get("best_recall_status") == "exact_label" for row in actionable),
            total_rows,
        ),
        "oracle_actionable_upper_bound_score": _rate(
            base_correct_rows + len(actionable),
            total_rows,
        ),
        "claim_language": (
            "Validation-development recoverability analysis over assembly failure "
            "rows and saved candidate-discovery artifacts. It does not inspect "
            "locked-test row-level failures, change predictions, change scorer "
            "policy, or make a benchmark-comparable claim."
        ),
        "recommended_next_step": _recommended_next_step(rows),
    }


def write_csv_rows(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in FIELDNAMES})


def write_summary_json(summary: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    path: Path,
    *,
    csv_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 Assembly Failure Recoverability",
        "",
        str(summary["claim_language"]),
        "",
        "## Summary",
        "",
        f"Failure rows analyzed: {summary['row_count']}.",
        f"Actionable candidate rows: {summary['actionable_candidate_rows']} "
        f"({_format_rate(summary['actionable_candidate_rate'])}).",
        (
            "Exact-label actionable rows: "
            f"{summary['exact_label_actionable_rows']}; Purist-category-only "
            f"actionable rows: {summary['purist_category_actionable_rows']}."
        ),
        (
            "Oracle upper-bound full-row Purist scores: exact-label only "
            f"{_format_rate(summary['oracle_exact_label_upper_bound_score'])}; "
            "all actionable "
            f"{_format_rate(summary['oracle_actionable_upper_bound_score'])}."
        ),
        "",
        "## Recoverability",
        "",
        "| Class | Rows |",
        "| --- | ---: |",
    ]
    for cls, count in summary["by_recoverability_class"].items():
        lines.append(f"| `{cls}` | {count} |")
    lines.extend(["", "## Failure Transitions", "", "| Transition | Rows |", "| --- | ---: |"])
    for transition, count in summary["by_failure_transition"].items():
        lines.append(f"| `{transition}` | {count} |")
    lines.extend(["", "## Best Generator", "", "| Generator | Rows |", "| --- | ---: |"])
    for generator, count in summary["by_best_generator"].items():
        lines.append(f"| `{generator}` | {count} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Recoverability CSV: `{csv_path}`",
            f"- Recoverability JSON: `{json_path}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _best_candidate(candidates: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    ranked = sorted(candidates, key=_candidate_rank)
    if not ranked:
        return None
    best = ranked[0]
    if best.get("gold_match_status") not in RECALL_STATUSES:
        return None
    return best


def _candidate_rank(candidate: Mapping[str, Any]) -> tuple[int, int, str]:
    status_rank = {"exact_label": 0, "purist_category": 1, "semantic_state": 2}
    status = str(candidate.get("gold_match_status") or "")
    source_valid = 0 if candidate.get("source_id_valid") is True else 1
    return (status_rank.get(status, 99), source_valid, str(candidate.get("generator_name") or ""))


def _recoverability_class(candidate: Mapping[str, Any] | None) -> str:
    if candidate is None:
        return "no_recalled_candidate"
    if candidate.get("gold_match_status") in ACTIONABLE_STATUSES:
        if candidate.get("source_id_valid") is True and candidate.get("evidence_status") == "exact":
            return "actionable_candidate"
        return "candidate_with_evidence_or_source_issue"
    return "semantic_state_only"


def _generator_counts(candidates: Sequence[Mapping[str, Any]]) -> str:
    counts = Counter(str(candidate.get("generator_name") or "") for candidate in candidates)
    return "|".join(f"{name}:{counts[name]}" for name in sorted(counts))


def _recommended_next_step(rows: Sequence[Mapping[str, Any]]) -> str:
    actionable = [
        row for row in rows if row["recoverability_class"] == "actionable_candidate"
    ]
    if actionable:
        generators = Counter(str(row["best_generator"]) for row in actionable)
        best_generator, count = generators.most_common(1)[0]
        return (
            f"Run a validation ablation that lets `{best_generator}` override "
            f"only the {count} actionable failure rows it already recalls with "
            "exact evidence and valid source ids; compare W->C and C->W before "
            "any holdout use."
        )
    return (
        "Existing saved candidates do not expose enough exact/source-valid "
        "recoverable alternatives for these assembly failures; build new "
        "candidate-generation mechanisms on validation/synthetic hard panels."
    )


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_rate(value: float) -> str:
    return f"{value:.3f}"
