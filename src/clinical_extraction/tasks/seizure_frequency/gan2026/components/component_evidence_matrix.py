"""Component evidence matrix for Gan 2026 staged hybrid assembly rows."""

from __future__ import annotations

import csv
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

POLICY_NAME = "gan2026_component_evidence_matrix_v0"

FIELDNAMES = [
    "candidate_version",
    "source_row_index",
    "split",
    "split_manifest",
    "gold_label",
    "final_action",
    "prediction_bearing",
    "prediction_label",
    "selected_evidence_exact",
    "selected_source_ids_exist",
    "deterministic_comparator_label",
    "deterministic_comparator_purist_correct",
    "final_purist_correct",
    "comparator_transition",
    "hidden_families",
    "first_failure_owner",
    "first_failure_reason",
    "reasoner_status",
    "router_action",
    "router_reason",
    "safety_floor_changed",
    "safety_floor_label_source",
    "verifier_status",
    "trigger_release_status",
    "trigger_release_label",
    "last_event_duration_auditable",
    "last_event_release_blocker",
    "parse_issue_count",
    "evidence_issue_count",
    "schema_issue_count",
]


def build_matrix_rows(
    assembly_rows: Sequence[Mapping[str, Any]],
    decision_rows: Sequence[Mapping[str, Any]],
    *,
    trigger_release_rows: Sequence[Mapping[str, Any]] = (),
    last_event_rows: Sequence[Mapping[str, Any]] = (),
    candidate_version: str = "hybrid_multi_component_staged_assembly_v0",
) -> list[dict[str, Any]]:
    """Flatten assembled components into one auditable row per source row."""

    assembly_by_source = _by_source(assembly_rows)
    trigger_by_source = _by_source(trigger_release_rows)
    last_event_by_source = _by_source(last_event_rows)
    matrix_rows = []
    for decision in sorted(decision_rows, key=lambda row: int(row["source_row_index"])):
        source_row_index = int(decision["source_row_index"])
        assembly = assembly_by_source.get(source_row_index, {})
        safety = assembly.get("selective_safety_floor_gate_v0") or {}
        reasoner = assembly.get("hybrid_reasoner_replay") or {}
        router = assembly.get("rq9_selective_action_router_v3") or {}
        safety_variant = (safety.get("gate_variants") or {}).get(
            "selective_safety_floor_gate_v0",
            {},
        )
        trigger = trigger_by_source.get(source_row_index)
        last_event = last_event_by_source.get(source_row_index)
        comparator_correct = _bool_or_none(_baseline_purist_correct(safety))
        final_correct = _bool_or_none(
            (decision.get("development_accounting") or {}).get("purist_correct")
        )
        matrix_rows.append(
            {
                "candidate_version": candidate_version,
                "source_row_index": source_row_index,
                "split": decision.get("split", "validation"),
                "split_manifest": decision.get(
                    "split_manifest",
                    "gan2026_split_v1",
                ),
                "gold_label": decision.get("gold_label"),
                "final_action": decision.get("final_action"),
                "prediction_bearing": decision.get("prediction_bearing") is True,
                "prediction_label": decision.get("prediction_label"),
                "selected_evidence_exact": decision.get("selected_evidence_exact"),
                "selected_source_ids_exist": decision.get("selected_source_ids_exist"),
                "deterministic_comparator_label": safety.get("baseline_label"),
                "deterministic_comparator_purist_correct": comparator_correct,
                "final_purist_correct": final_correct,
                "comparator_transition": _transition(
                    comparator_correct,
                    final_correct,
                    str(decision.get("final_action") or ""),
                ),
                "hidden_families": "|".join(str(v) for v in safety.get("hidden_families", [])),
                "first_failure_owner": safety.get("first_failure_owner") or "",
                "first_failure_reason": safety.get("first_failure_reason") or "",
                "reasoner_status": _status_summary(reasoner.get("component_status", {})),
                "router_action": router.get("selective_action"),
                "router_reason": router.get("primary_reason"),
                "safety_floor_changed": safety_variant.get("changed"),
                "safety_floor_label_source": safety_variant.get("label_source"),
                "verifier_status": "used"
                if decision.get("verifier_used") is True
                else "not_run",
                "trigger_release_status": trigger.get("release_decision")
                if trigger
                else "not_applicable",
                "trigger_release_label": trigger.get("prediction_label")
                if trigger
                else None,
                "last_event_duration_auditable": last_event.get("duration_auditable")
                if last_event
                else None,
                "last_event_release_blocker": last_event.get("release_blocker")
                if last_event
                else None,
                "parse_issue_count": _issue_count(reasoner, "parse_errors"),
                "evidence_issue_count": _evidence_issue_count(decision, safety),
                "schema_issue_count": _schema_issue_count(reasoner),
            }
        )
    return matrix_rows


def summarize_matrix_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize matrix rows for validation freeze-gate inspection."""

    action_counts = Counter(str(row.get("final_action")) for row in rows)
    transition_counts = Counter(str(row.get("comparator_transition")) for row in rows)
    first_failure_counts = Counter(
        str(row.get("first_failure_owner") or "none") for row in rows
    )
    return {
        "component_name": "component_evidence_matrix",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "unique_source_rows": len({int(row["source_row_index"]) for row in rows}),
        "action_counts": dict(sorted(action_counts.items())),
        "prediction_bearing_rows": sum(
            row.get("prediction_bearing") is True for row in rows
        ),
        "non_prediction_rows": sum(
            row.get("prediction_bearing") is not True for row in rows
        ),
        "transition_counts": dict(sorted(transition_counts.items())),
        "selected_evidence_exact_false_rows": _false_count(
            rows,
            "selected_evidence_exact",
        ),
        "selected_source_ids_missing_rows": _false_count(
            rows,
            "selected_source_ids_exist",
        ),
        "verifier_status_counts": dict(
            sorted(Counter(str(row.get("verifier_status")) for row in rows).items())
        ),
        "trigger_release_rows": sum(
            row.get("trigger_release_status") == "release_as_prediction"
            for row in rows
        ),
        "last_event_duration_auditable_rows": sum(
            row.get("last_event_duration_auditable") is True for row in rows
        ),
        "first_failure_owner_counts": dict(sorted(first_failure_counts.items())),
        "parse_issue_rows": sum(int(row.get("parse_issue_count") or 0) > 0 for row in rows),
        "evidence_issue_rows": sum(
            int(row.get("evidence_issue_count") or 0) > 0 for row in rows
        ),
        "schema_issue_rows": sum(
            int(row.get("schema_issue_count") or 0) > 0 for row in rows
        ),
        "claim_language": (
            "Validation-development component evidence matrix for the staged "
            "hybrid assembly. It is an audit artifact and does not change "
            "candidate predictions, scorer policy, gold labels, locked-test "
            "behavior, or benchmark-comparable claims."
        ),
    }


def validate_matrix_contract(
    rows: Sequence[Mapping[str, Any]],
    *,
    expected_rows: int = 750,
    split: str = "validation",
    split_manifest: str = "gan2026_split_v1",
) -> list[str]:
    """Return contract issue descriptions for the assembled matrix."""

    issues = []
    source_indices = [int(row["source_row_index"]) for row in rows]
    if len(rows) != expected_rows:
        issues.append(f"expected_{expected_rows}_rows_got_{len(rows)}")
    if len(set(source_indices)) != len(source_indices):
        issues.append("duplicate_source_row_indices")
    if any(row.get("split") != split for row in rows):
        issues.append(f"unexpected_split_not_{split}")
    if any(row.get("split_manifest") != split_manifest for row in rows):
        issues.append(f"unexpected_split_manifest_not_{split_manifest}")
    prediction_rows = [row for row in rows if row.get("prediction_bearing") is True]
    if any(not row.get("prediction_label") for row in prediction_rows):
        issues.append("prediction_bearing_row_missing_prediction_label")
    if any(row.get("verifier_status") == "used" for row in rows):
        issues.append("verifier_used_without_full_validation_protocol")
    return issues


def write_csv_rows(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    """Write matrix rows to CSV with stable columns."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name) for name in FIELDNAMES})


def write_summary_json(summary: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    summary: Mapping[str, Any],
    path: Path,
    *,
    csv_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 Component Evidence Matrix",
        "",
        str(summary["claim_language"]),
        "",
        "## Summary",
        "",
        f"Rows: {summary['row_count']}. Unique source rows: {summary['unique_source_rows']}.",
        f"Prediction-bearing rows: {summary['prediction_bearing_rows']}.",
        f"Non-prediction rows: {summary['non_prediction_rows']}.",
        "",
        "## Contract",
        "",
        "| Gate | Status |",
        "| --- | --- |",
        f"| contract issues | `{', '.join(summary['contract_issues']) or 'none'}` |",
        f"| verifier rows used | {summary['verifier_status_counts'].get('used', 0)} |",
        f"| trigger release proposal rows | {summary['trigger_release_rows']} |",
        (
            "| last-event duration-auditable rows | "
            f"{summary['last_event_duration_auditable_rows']} |"
        ),
        "",
        "## Comparator Transitions",
        "",
        "| Transition | Rows |",
        "| --- | ---: |",
    ]
    for transition, count in summary["transition_counts"].items():
        lines.append(f"| `{transition}` | {count} |")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Matrix CSV: `{csv_path}`",
            f"- Matrix summary JSON: `{json_path}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _by_source(rows: Sequence[Mapping[str, Any]]) -> dict[int, Mapping[str, Any]]:
    return {
        int(row["source_row_index"]): row
        for row in rows
        if row.get("source_row_index") is not None
    }


def _baseline_purist_correct(safety: Mapping[str, Any]) -> Any:
    return (
        (safety.get("gate_variants") or {})
        .get("baseline_safety_floor_v2", {})
        .get("purist_correct")
    )


def _bool_or_none(value: Any) -> bool | None:
    if value is True:
        return True
    if value is False:
        return False
    return None


def _transition(
    comparator_correct: bool | None,
    final_correct: bool | None,
    final_action: str,
) -> str:
    if final_action != "predict":
        prefix = "C" if comparator_correct is True else "W"
        suffix = "review" if final_action == "human_review" else "abstain"
        return f"{prefix}_to_{suffix}"
    if comparator_correct is True and final_correct is True:
        return "C_to_C"
    if comparator_correct is True and final_correct is False:
        return "C_to_W"
    if comparator_correct is False and final_correct is True:
        return "W_to_C"
    if comparator_correct is False and final_correct is False:
        return "W_to_W"
    return "unknown"


def _status_summary(status: Mapping[str, Any]) -> str:
    return "|".join(f"{key}:{status[key]}" for key in sorted(status))


def _issue_count(row: Mapping[str, Any], key: str) -> int:
    value = row.get(key)
    if isinstance(value, Sequence) and not isinstance(value, str):
        return len(value)
    return 0


def _evidence_issue_count(
    decision: Mapping[str, Any],
    safety: Mapping[str, Any],
) -> int:
    if decision.get("prediction_bearing") is not True:
        return 0
    issues = 0
    if decision.get("selected_evidence_exact") is False:
        issues += 1
    if safety.get("selected_source_ids_exist") is False:
        issues += 1
    return issues


def _schema_issue_count(reasoner: Mapping[str, Any]) -> int:
    status = reasoner.get("component_status") or {}
    return sum(
        1
        for key, value in status.items()
        if ("schema" in str(key) or "parse" in str(key))
        and value not in (None, "ok")
    )


def _false_count(rows: Sequence[Mapping[str, Any]], key: str) -> int:
    return sum(row.get(key) is False for row in rows)
