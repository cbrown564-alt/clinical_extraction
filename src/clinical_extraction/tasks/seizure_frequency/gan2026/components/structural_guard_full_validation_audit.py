"""Full-validation audit for structurally guarded candidate-union selection."""

from __future__ import annotations

import csv
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    candidate_union,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    candidate_union_ranker_ablation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist

POLICY_NAME = "gan2026_structural_guard_full_validation_audit_v0"
RANKER_NAME = "comparator_absent_structural_guard_rank_v0"

FIELDNAMES = [
    "source_row_index",
    "candidate_label",
    "candidate_kind",
    "candidate_rule_id",
    "candidate_evidence",
    "base_prediction_label",
    "gold_label",
    "base_purist_correct",
    "candidate_purist_correct",
    "selected_transition",
]


def build_structural_guard_audit_rows(
    matrix_rows: Sequence[Mapping[str, Any]],
    validation_records: Sequence[GanFrequencyRecord],
) -> list[dict[str, Any]]:
    """Materialize the hard-panel structural guard over full validation."""

    matrix_by_source = {int(row["source_row_index"]): row for row in matrix_rows}
    rows = []
    for record in validation_records:
        matrix = matrix_by_source[int(record.source_row_index)]
        base_label = str(matrix.get("prediction_label") or "")
        candidates = list(
            candidate_union._deterministic_candidates(  # noqa: SLF001
                record.note_text,
                record.source_row_index,
            )
        )
        candidate = candidate_union_ranker_ablation._comparator_absent_structural_guard_rank(  # noqa: SLF001
            {
                "comparator_selected_state_replay": {"label": base_label},
                "union_verified_candidates": candidates,
            }
        )
        if not candidate:
            continue
        candidate_label = str(candidate.get("normalized_label") or "")
        base_correct = _as_bool(matrix.get("final_purist_correct"))
        candidate_correct = _purist_correct(candidate_label, str(matrix["gold_label"]))
        rows.append(
            {
                "source_row_index": int(record.source_row_index),
                "candidate_label": candidate_label,
                "candidate_kind": candidate.get("candidate_kind"),
                "candidate_rule_id": _rule_id(candidate),
                "candidate_evidence": candidate.get("evidence"),
                "base_prediction_label": base_label,
                "gold_label": matrix.get("gold_label"),
                "base_purist_correct": base_correct,
                "candidate_purist_correct": candidate_correct,
                "selected_transition": _transition(base_correct, candidate_correct),
            }
        )
    rows.sort(key=lambda row: int(row["source_row_index"]))
    return rows


def summarize_structural_guard_audit_rows(
    rows: Sequence[Mapping[str, Any]],
    matrix_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize full-validation structural-guard candidate effects."""

    transitions = Counter(str(row["selected_transition"]) for row in rows)
    rules = Counter(str(row["candidate_rule_id"]) for row in rows)
    kinds = Counter(str(row["candidate_kind"]) for row in rows)
    base_correct_rows = sum(_as_bool(row.get("final_purist_correct")) for row in matrix_rows)
    total_rows = len(matrix_rows)
    w_to_c = transitions["W_to_C"]
    c_to_w = transitions["C_to_W"]
    projected_correct_rows = base_correct_rows + w_to_c - c_to_w
    return {
        "component_name": "structural_guard_full_validation_audit",
        "policy_name": POLICY_NAME,
        "ranker_name": RANKER_NAME,
        "selected_candidate_rows": len(rows),
        "selected_transition_counts": dict(sorted(transitions.items())),
        "selected_candidate_kind_counts": dict(sorted(kinds.items())),
        "selected_candidate_rule_counts": dict(sorted(rules.items())),
        "base_correct_rows": base_correct_rows,
        "total_rows": total_rows,
        "base_full_row_purist_proxy": _rate(base_correct_rows, total_rows),
        "projected_correct_rows": projected_correct_rows,
        "projected_full_row_purist_proxy": _rate(projected_correct_rows, total_rows),
        "changed_label_precision": _rate(w_to_c, w_to_c + c_to_w),
        "decision": _decision(w_to_c, c_to_w, len(rows)),
        "claim_language": (
            "Validation-development full-validation audit for the frozen "
            "comparator-absent structural guard ranker. Selection uses only "
            "non-gold candidate features and the existing validation component "
            "matrix as the base assembly surface; gold labels are used only for "
            "post-selection W->C/C->W accounting. This does not change scorer "
            "policy, split policy, or locked-test behavior."
        ),
        "recommended_next_step": _recommended_next_step(w_to_c, c_to_w),
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
        "# Gan 2026 Structural-Guard Full-Validation Audit",
        "",
        str(summary["claim_language"]),
        "",
        "## Summary",
        "",
        f"Base full-row Purist proxy: {_format_rate(summary['base_full_row_purist_proxy'])} "
        f"({summary['base_correct_rows']} / {summary['total_rows']}).",
        (
            "Projected full-row Purist proxy with structural guard: "
            f"{_format_rate(summary['projected_full_row_purist_proxy'])} "
            f"({summary['projected_correct_rows']} / {summary['total_rows']})."
        ),
        "",
        "## Selected Transitions",
        "",
        "| Transition | Rows |",
        "| --- | ---: |",
    ]
    for transition, count in summary["selected_transition_counts"].items():
        lines.append(f"| `{transition}` | {count} |")
    lines.extend(
        [
            "",
            "## Rule Counts",
            "",
            "| Rule | Rows |",
            "| --- | ---: |",
        ]
    )
    for rule_name, count in summary["selected_candidate_rule_counts"].items():
        lines.append(f"| `{rule_name}` | {count} |")
    lines.extend(
        [
            "",
            "## Selected Rows",
            "",
            "| Row | Base | Candidate | Gold | Transition | Rule |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['source_row_index']} | `{row['base_prediction_label']}` | "
            f"`{row['candidate_label']}` | `{row['gold_label']}` | "
            f"`{row['selected_transition']}` | `{row['candidate_rule_id']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Structural-guard CSV: `{csv_path}`",
            f"- Structural-guard JSON: `{json_path}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _rule_id(candidate: Mapping[str, Any]) -> str:
    return str((candidate.get("metadata") or {}).get("rule_id") or "")


def _purist_correct(label: str, gold_label: str) -> bool:
    if label == gold_label:
        return True
    predicted = _purist_category(label)
    gold = _purist_category(gold_label)
    return bool(predicted and gold and predicted == gold)


def _purist_category(label: str) -> str | None:
    try:
        record = label_to_frequency_record(label)
    except ValueError:
        return None
    return str(map_purist(record.monthly_frequency))


def _transition(base_correct: bool, candidate_correct: bool) -> str:
    if base_correct and candidate_correct:
        return "C_to_C"
    if base_correct and not candidate_correct:
        return "C_to_W"
    if not base_correct and candidate_correct:
        return "W_to_C"
    return "W_to_W"


def _decision(w_to_c: int, c_to_w: int, selected_rows: int) -> str:
    if selected_rows and w_to_c > 0 and c_to_w == 0:
        return "freeze_candidate_for_aggregate_audit"
    if w_to_c > c_to_w:
        return "diagnostic_positive_but_not_promotable"
    return "reject"


def _recommended_next_step(w_to_c: int, c_to_w: int) -> str:
    if w_to_c > 0 and c_to_w == 0:
        return (
            "The structural guard is clean on full validation. Freeze this exact "
            "candidate policy and run an aggregate-only locked-test audit without "
            "test row-level inspection."
        )
    return (
        "Do not promote the structural guard. Use validation selected-row "
        "transitions to design narrower non-gold gates before any holdout use."
    )


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() == "true"


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_rate(value: float) -> str:
    return f"{value:.4f}"
