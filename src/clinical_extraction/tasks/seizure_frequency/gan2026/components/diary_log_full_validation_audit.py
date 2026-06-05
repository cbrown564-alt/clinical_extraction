"""Full-validation audit for diary/log candidate ranker behavior."""

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
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist

POLICY_NAME = "gan2026_diary_log_full_validation_audit_v0"
SELECTED_DIARY_RULES = {
    "diary.date_list",
    "diary.monthly_count_log",
    "diary.sleep_awake_month_summary",
}

FIELDNAMES = [
    "source_row_index",
    "candidate_action",
    "candidate_rule_id",
    "candidate_label",
    "candidate_evidence",
    "base_prediction_label",
    "gold_label",
    "base_transition",
    "base_purist_correct",
    "candidate_purist_correct",
    "selected_transition",
]


def build_diary_log_audit_rows(
    matrix_rows: Sequence[Mapping[str, Any]],
    validation_records: Sequence[GanFrequencyRecord],
) -> list[dict[str, Any]]:
    """Materialize diary/log candidate effects over full validation."""

    matrix_by_source = {int(row["source_row_index"]): row for row in matrix_rows}
    rows = []
    for record in validation_records:
        matrix = matrix_by_source[int(record.source_row_index)]
        base_label = str(matrix.get("prediction_label") or "")
        for candidate in candidate_union._deterministic_candidates(  # noqa: SLF001
            record.note_text,
            record.source_row_index,
        ):
            rule_id = _rule_id(candidate)
            if not rule_id.startswith("diary."):
                continue
            candidate_label = str(candidate.get("normalized_label") or "")
            if not candidate_label or candidate_label == base_label:
                continue
            action = "selected" if rule_id in SELECTED_DIARY_RULES else "rejected_rule"
            base_correct = _as_bool(matrix.get("final_purist_correct"))
            candidate_correct = _purist_correct(candidate_label, str(matrix["gold_label"]))
            rows.append(
                {
                    "source_row_index": int(record.source_row_index),
                    "candidate_action": action,
                    "candidate_rule_id": rule_id,
                    "candidate_label": candidate_label,
                    "candidate_evidence": candidate.get("evidence"),
                    "base_prediction_label": base_label,
                    "gold_label": matrix.get("gold_label"),
                    "base_transition": matrix.get("comparator_transition"),
                    "base_purist_correct": base_correct,
                    "candidate_purist_correct": candidate_correct,
                    "selected_transition": _transition(base_correct, candidate_correct)
                    if action == "selected"
                    else "",
                }
            )
    rows.sort(
        key=lambda row: (
            row["candidate_action"],
            int(row["source_row_index"]),
            row["candidate_rule_id"],
        )
    )
    return rows


def summarize_diary_log_audit_rows(
    rows: Sequence[Mapping[str, Any]],
    matrix_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize selected and rejected diary/log candidates."""

    selected = [row for row in rows if row["candidate_action"] == "selected"]
    rejected = [row for row in rows if row["candidate_action"] != "selected"]
    transitions = Counter(str(row["selected_transition"]) for row in selected)
    selected_rules = Counter(str(row["candidate_rule_id"]) for row in selected)
    rejected_rules = Counter(str(row["candidate_rule_id"]) for row in rejected)
    base_correct_rows = sum(_as_bool(row.get("final_purist_correct")) for row in matrix_rows)
    total_rows = len(matrix_rows)
    w_to_c = transitions["W_to_C"]
    c_to_w = transitions["C_to_W"]
    projected_correct_rows = base_correct_rows + w_to_c - c_to_w
    return {
        "component_name": "diary_log_full_validation_audit",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "selected_candidate_rows": len(selected),
        "rejected_candidate_rows": len(rejected),
        "selected_rule_counts": dict(sorted(selected_rules.items())),
        "rejected_rule_counts": dict(sorted(rejected_rules.items())),
        "selected_transition_counts": dict(sorted(transitions.items())),
        "base_correct_rows": base_correct_rows,
        "total_rows": total_rows,
        "base_full_row_purist_proxy": _rate(base_correct_rows, total_rows),
        "projected_correct_rows": projected_correct_rows,
        "projected_full_row_purist_proxy": _rate(projected_correct_rows, total_rows),
        "changed_label_precision": _rate(w_to_c, w_to_c + c_to_w),
        "decision": _decision(w_to_c, c_to_w, len(selected)),
        "claim_language": (
            "Validation-development full-validation diary/log audit. The selected "
            "policy uses fixed diary rule ids from prior hard-panel ablation and "
            "reports rejected diary rules for negative evidence. It does not inspect "
            "locked-test row-level failures, change scorer policy, or make a "
            "benchmark-comparable claim."
        ),
        "recommended_next_step": _recommended_next_step(w_to_c, c_to_w, rejected_rules),
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
        "# Gan 2026 Diary/Log Full-Validation Audit",
        "",
        str(summary["claim_language"]),
        "",
        "## Summary",
        "",
        f"Base full-row Purist proxy: {_format_rate(summary['base_full_row_purist_proxy'])} "
        f"({summary['base_correct_rows']} / {summary['total_rows']}).",
        (
            "Projected full-row Purist proxy with selected diary rules: "
            f"{_format_rate(summary['projected_full_row_purist_proxy'])} "
            f"({summary['projected_correct_rows']} / {summary['total_rows']})."
        ),
        "",
        "| Candidate set | Rows |",
        "| --- | ---: |",
        f"| selected | {summary['selected_candidate_rows']} |",
        f"| rejected | {summary['rejected_candidate_rows']} |",
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
            "| Rule | Selected | Rejected |",
            "| --- | ---: | ---: |",
        ]
    )
    rule_names = sorted(
        set(summary["selected_rule_counts"]) | set(summary["rejected_rule_counts"])
    )
    for rule_name in rule_names:
        lines.append(
            f"| `{rule_name}` | {summary['selected_rule_counts'].get(rule_name, 0)} | "
            f"{summary['rejected_rule_counts'].get(rule_name, 0)} |"
        )
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
        if row["candidate_action"] != "selected":
            continue
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
            f"- Diary/log CSV: `{csv_path}`",
            f"- Diary/log JSON: `{json_path}`",
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


def _recommended_next_step(
    w_to_c: int,
    c_to_w: int,
    rejected_rules: Mapping[str, int],
) -> str:
    if w_to_c > 0 and c_to_w == 0:
        rejected = ", ".join(f"{rule}:{count}" for rule, count in sorted(rejected_rules.items()))
        return (
            "The selected diary/log rule set is clean on full validation. Freeze "
            "the rule ids and run an aggregate-only locked-test audit; keep rejected "
            f"diary rules excluded ({rejected})."
        )
    return (
        "Do not promote the diary/log rule set. Use the rejected/transition rows "
        "to define narrower negative gates before any holdout use."
    )


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() == "true"


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_rate(value: float) -> str:
    return f"{value:.4f}"
