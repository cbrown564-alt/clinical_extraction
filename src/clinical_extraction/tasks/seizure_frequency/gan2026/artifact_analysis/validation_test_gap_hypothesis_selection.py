"""Select controlled hypotheses from the validation-test gap matrix."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

DEFAULT_MATRIX_PATH = Path(
    "experiments/gan2026_validation_test_gap_matrix_v0_validation750_2026-06-05.jsonl"
)
DEFAULT_SURFACE_MAP_PATH = Path(
    "experiments/gan2026_validation_test_surface_map_v0_2026-06-05.json"
)
DEFAULT_VALIDATION_SELECTIVE_PATH = Path(
    "experiments/gan2026_selective_safety_floor_gate_v0_validation750_replay_2026-06-03.json"
)
DEFAULT_TEST_SELECTIVE_PATH = Path(
    "experiments/gan2026_selective_safety_floor_gate_v0_test450_frozen_audit_first_readout_2026-06-03.json"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_validation_test_gap_hypothesis_selection_v0_2026-06-05.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_validation_test_gap_hypothesis_selection_v0_2026-06-05.md"
)


def build_hypothesis_selection(
    matrix_rows: Sequence[Mapping[str, Any]],
    *,
    surface_map: Mapping[str, Any] | None = None,
    validation_selective: Mapping[str, Any] | None = None,
    test_selective: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the next controlled hypothesis queue from saved artifacts."""

    final_rows = [row for row in matrix_rows if row.get("score_layer") == "final_policy"]
    monitor_rows = [
        row for row in matrix_rows if row.get("score_layer") == "abstain_review_monitor"
    ]
    owner_rows = _owner_summary(final_rows)
    family_rows = _family_summary(final_rows)
    evidence_rows = _evidence_summary(final_rows)
    monitor_summary = _monitor_summary(monitor_rows)
    gap_summary = list((surface_map or {}).get("candidate_gap_summary", []))
    selective_summary = _selective_action_summary(
        validation_selective=validation_selective or {},
        test_selective=test_selective or {},
    )

    selected = [
        {
            "hypothesis_id": "H2",
            "name": "component_ownership",
            "priority": 1,
            "status": "selected_for_controlled_validation_experiment",
            "evidence_basis": "validation_test_gap_matrix_v0 validation-only row attribution",
            "why_selected": (
                "Final-policy residual errors separate sharply by owner: "
                "deterministic-adapter prediction rows are mostly correct, while "
                "safety-floor-owned nonpredictions carry the action-policy failures."
            ),
            "next_experiment": (
                "Build a family-indexed component-owner hard/control panel over "
                "validation rows, with deterministic-adapter, safety-floor, and "
                "monitor-policy strata."
            ),
            "promotion_signal": (
                "A proposed component must improve the target owner/family slice "
                "without moving deterministic-correct controls to wrong labels."
            ),
            "inspection_policy": "validation_row_level_allowed_only",
        },
        {
            "hypothesis_id": "H4",
            "name": "evidence_transfers_projection_does_not",
            "priority": 2,
            "status": "selected_for_score_layer_ladder",
            "evidence_basis": "validation_test_gap_matrix_v0 exact-evidence and score-layer rows",
            "why_selected": (
                "All prediction-bearing final-policy rows have exact evidence, but "
                "38 exact-evidence prediction rows remain wrong and 34 additional "
                "rows become abstain/review/monitor nonpredictions."
            ),
            "next_experiment": (
                "Run a score-layer ladder on validation hard slices that separates "
                "selected evidence, source ids, projection choice, adapter rendering, "
                "and final action policy."
            ),
            "promotion_signal": (
                "Keep H4 only if evidence/source-id validity remains high while "
                "projection, rendering, or final action policy explains residual errors."
            ),
            "inspection_policy": "validation_row_level_allowed_only",
        },
        {
            "hypothesis_id": "H6",
            "name": "selective_action_transfers",
            "priority": 3,
            "status": "selected_as_transfer_control",
            "evidence_basis": (
                "validation_test_gap_matrix_v0 plus saved selective-safety-floor "
                "validation and frozen aggregate test readouts"
            ),
            "why_selected": (
                "Broad replacement surfaces show large validation-test gaps, while "
                "the selective safety-floor gate has low-coverage but clean transfer "
                "accounting."
            ),
            "next_experiment": (
                "Use selective-action behavior as a control arm for any H2/H4 "
                "component-stress panel; do not broaden it without matched controls."
            ),
            "promotion_signal": (
                "Changed-label precision stays high, C->W remains near zero, and "
                "coverage expands through typed high-precision candidates."
            ),
            "inspection_policy": "validation_row_level_and_predeclared_aggregate_test_only",
        },
    ]

    return {
        "artifact_kind": "gan2026_validation_test_gap_hypothesis_selection_v0",
        "date": "2026-06-05",
        "split_manifest": _first_nonempty(row.get("split_manifest") for row in matrix_rows),
        "claim_boundary": (
            "Validation-development hypothesis selection only. Locked-test row-level "
            "failure inspection remains unauthorized."
        ),
        "matrix_summary": {
            "final_policy_rows": len(final_rows),
            "monitor_rows": len(monitor_rows),
            "locked_test_row_level_artifacts_used": len(
                {
                    row.get("source_artifact_id")
                    for row in matrix_rows
                    if str(row.get("distribution", "")).startswith("locked_test")
                }
            ),
        },
        "component_owner_summary": owner_rows,
        "hidden_family_summary": family_rows,
        "evidence_summary": evidence_rows,
        "monitor_summary": monitor_summary,
        "surface_gap_summary": gap_summary,
        "selective_action_summary": selective_summary,
        "selected_hypotheses": selected,
        "deferred_hypotheses": [
            {
                "hypothesis_id": "H1",
                "reason": (
                    "Needs predeclared test slice aggregates before accepting "
                    "hidden-family mix."
                ),
            },
            {
                "hypothesis_id": "H3",
                "reason": (
                    "Requires candidate-exposure instrumentation not present in "
                    "gap_matrix_v0."
                ),
            },
            {
                "hypothesis_id": "H5",
                "reason": (
                    "Requires same-raw-output repair ladders with explicit semantic "
                    "repair ownership."
                ),
            },
            {
                "hypothesis_id": "H7",
                "reason": "Requires synthetic or adversarial minimal-pair panels.",
            },
            {
                "hypothesis_id": "H8",
                "reason": (
                    "Benchmark-format rows are visible but not yet isolated as the "
                    "primary gap driver."
                ),
            },
            {
                "hypothesis_id": "H9",
                "reason": (
                    "Monitor-policy rows are available, but H2/H4 should own first "
                    "stress panels."
                ),
            },
            {
                "hypothesis_id": "H10",
                "reason": "No live rerun or same-raw-output variance signal in this artifact.",
            },
        ],
        "recommended_next_step": (
            "Start with H2/H4 combined validation hard/control panel; use H6 selective "
            "action as the no-regression control and do not inspect locked-test rows."
        ),
    }


def write_selection_json(selection: Mapping[str, Any], path: Path) -> None:
    path.write_text(json.dumps(selection, indent=2, sort_keys=True) + "\n")


def write_selection_report(selection: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 Validation-Test Gap Hypothesis Selection v0",
        "",
        f"Split manifest: `{selection.get('split_manifest', '')}`",
        "",
        str(selection.get("claim_boundary", "")),
        "",
        "## Decision",
        "",
        str(selection.get("recommended_next_step", "")),
        "",
        "## Selected Hypotheses",
        "",
        "| Priority | Hypothesis | Status | Next experiment |",
        "| ---: | --- | --- | --- |",
    ]
    for item in selection.get("selected_hypotheses", []):
        lines.append(
            "| {priority} | `{hypothesis_id}` {name} | {status} | {next_experiment} |".format(
                priority=item.get("priority", ""),
                hypothesis_id=_md(item.get("hypothesis_id")),
                name=_md(item.get("name")),
                status=_md(item.get("status")),
                next_experiment=_md(item.get("next_experiment")),
            )
        )

    lines.extend(["", "## Component Owner Summary", ""])
    lines.extend(_summary_table(selection.get("component_owner_summary", []), "Component owner"))
    lines.extend(["", "## Hidden Family Summary", ""])
    lines.extend(_summary_table(selection.get("hidden_family_summary", []), "Hidden family"))
    lines.extend(["", "## Evidence Summary", ""])
    lines.extend(_summary_table(selection.get("evidence_summary", []), "Evidence status"))
    lines.extend(["", "## Monitor Summary", ""])
    lines.extend(["| Action or reason | Rows |", "| --- | ---: |"])
    for item in selection.get("monitor_summary", []):
        lines.append(f"| {_md(item.get('name'))} | {item.get('rows', 0)} |")

    lines.extend(["", "## Surface Gap Context", ""])
    gap_summary = selection.get("surface_gap_summary", [])
    if gap_summary:
        lines.extend(
            [
                "| Candidate | Validation proxy | Test proxy | Gap |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for item in gap_summary:
            lines.append(
                "| {candidate} | {validation} | {test} | {gap} |".format(
                    candidate=_md(item.get("candidate_name")),
                    validation=_metric(item.get("validation_final_purist_proxy")),
                    test=_metric(item.get("test_final_purist_proxy")),
                    gap=_metric(item.get("validation_minus_test_gap")),
                )
            )
    else:
        lines.append("No comparable validation-test surface gaps were available.")

    lines.extend(["", "## Selective Action Context", ""])
    lines.extend(
        [
            "| Split | Rows | Changed | W->C | C->W | Precision |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in selection.get("selective_action_summary", []):
        lines.append(
            "| {split} | {rows} | {changed} | {wtc} | {ctw} | {precision} |".format(
                split=_md(item.get("split")),
                rows=item.get("rows", ""),
                changed=item.get("changed_rows", ""),
                wtc=item.get("wrong_to_correct", ""),
                ctw=item.get("correct_to_wrong", ""),
                precision=_metric(item.get("precision")),
            )
        )

    lines.extend(["", "## Deferred Hypotheses", ""])
    lines.extend(["| Hypothesis | Reason |", "| --- | --- |"])
    for item in selection.get("deferred_hypotheses", []):
        lines.append(
            f"| `{_md(item.get('hypothesis_id'))}` | {_md(item.get('reason'))} |"
        )

    path.write_text("\n".join(lines) + "\n")


def _owner_summary(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped = _group(rows, "component_owner")
    return [_score_summary(name, grouped[name]) for name in sorted(grouped)]


def _family_summary(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        families = row.get("hidden_families") or ["none"]
        for family in families:
            grouped[str(family)].append(row)
    return sorted(
        (_score_summary(name, grouped[name]) for name in grouped),
        key=lambda item: (
            -int(item["incorrect_rows"]) - int(item["nonprediction_rows"]),
            item["name"],
        ),
    )


def _evidence_summary(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("evidence_exact") is True and row.get("source_ids_valid") is True:
            key = "exact_evidence_and_source_ids"
        elif row.get("purist_correct") is None:
            key = "nonprediction_no_selected_evidence"
        else:
            key = "evidence_or_source_id_gap"
        grouped[key].append(row)
    return [_score_summary(name, grouped[name]) for name in sorted(grouped)]


def _score_summary(name: str, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    correct = sum(1 for row in rows if row.get("purist_correct") is True)
    incorrect = sum(1 for row in rows if row.get("purist_correct") is False)
    nonprediction = sum(1 for row in rows if row.get("purist_correct") is None)
    changed = sum(1 for row in rows if row.get("changed_from_baseline") is True)
    return {
        "name": name,
        "rows": len(rows),
        "correct_rows": correct,
        "incorrect_rows": incorrect,
        "nonprediction_rows": nonprediction,
        "changed_rows": changed,
        "wrong_to_correct": sum(1 for row in rows if row.get("wrong_to_correct") is True),
        "correct_to_wrong": sum(1 for row in rows if row.get("correct_to_wrong") is True),
        "exact_evidence_rows": sum(1 for row in rows if row.get("evidence_exact") is True),
        "accuracy_including_nonprediction": correct / len(rows) if rows else None,
    }


def _monitor_summary(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter()
    for row in rows:
        action = str(row.get("abstain_review_monitor_action", ""))
        reason = str(row.get("abstain_review_monitor_reason", ""))
        counts[f"action:{action}"] += 1
        if reason:
            counts[f"reason:{reason}"] += 1
    return [{"name": name, "rows": rows} for name, rows in counts.most_common()]


def _selective_action_summary(
    *,
    validation_selective: Mapping[str, Any],
    test_selective: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        _selective_variant_summary(validation_selective, split="validation750"),
        _selective_variant_summary(test_selective, split="locked_test450"),
    ]


def _selective_variant_summary(payload: Mapping[str, Any], *, split: str) -> dict[str, Any]:
    for item in _iter_selective_variant_rows(payload.get("slice_summary", [])):
        if item.get("variant") == "selective_safety_floor_gate_v0":
            return {
                "split": split,
                "rows": item.get("rows"),
                "changed_rows": item.get("changed_rows"),
                "wrong_to_correct": item.get("wrong_to_correct"),
                "correct_to_wrong": item.get("correct_to_wrong"),
                "precision": item.get("precision") or item.get("changed_label_precision"),
                "inspection_policy": (
                    "validation_row_level_allowed"
                    if split.startswith("validation")
                    else "locked_test_aggregate_only"
                ),
            }
    return {
        "split": split,
        "rows": None,
        "changed_rows": None,
        "wrong_to_correct": None,
        "correct_to_wrong": None,
        "precision": None,
    }


def _iter_selective_variant_rows(slice_summary: Any) -> list[dict[str, Any]]:
    if isinstance(slice_summary, list):
        return [item for item in slice_summary if isinstance(item, dict)]
    if not isinstance(slice_summary, dict):
        return []
    rows: list[dict[str, Any]] = []
    for slice_name, summary in slice_summary.items():
        if not isinstance(summary, dict):
            continue
        variant_summary = summary.get("variant_summary", {})
        if not isinstance(variant_summary, dict):
            continue
        for variant, metrics in variant_summary.items():
            if not isinstance(metrics, dict):
                continue
            rows.append({"slice": slice_name, "variant": variant, **metrics})
    return rows


def _group(rows: Sequence[Mapping[str, Any]], field: str) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(field, ""))].append(row)
    return grouped


def _first_nonempty(values: Sequence[Any] | Any) -> str:
    for value in values:
        if value:
            return str(value)
    return ""


def _summary_table(rows: Sequence[Mapping[str, Any]], label: str) -> list[str]:
    if not rows:
        return ["No rows available."]
    lines = [
        f"| {label} | Rows | Correct | Incorrect | Nonprediction | Changed | Exact evidence |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            (
                "| {name} | {rows} | {correct} | {incorrect} | {nonprediction} | "
                "{changed} | {evidence} |"
            ).format(
                name=_md(row.get("name")),
                rows=row.get("rows", 0),
                correct=row.get("correct_rows", 0),
                incorrect=row.get("incorrect_rows", 0),
                nonprediction=row.get("nonprediction_rows", 0),
                changed=row.get("changed_rows", 0),
                evidence=row.get("exact_evidence_rows", 0),
            )
        )
    return lines


def _metric(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _md(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX_PATH)
    parser.add_argument("--surface-map", type=Path, default=DEFAULT_SURFACE_MAP_PATH)
    parser.add_argument(
        "--validation-selective",
        type=Path,
        default=DEFAULT_VALIDATION_SELECTIVE_PATH,
    )
    parser.add_argument("--test-selective", type=Path, default=DEFAULT_TEST_SELECTIVE_PATH)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    selection = build_hypothesis_selection(
        _read_jsonl(args.matrix),
        surface_map=_read_json(args.surface_map),
        validation_selective=_read_json(args.validation_selective),
        test_selective=_read_json(args.test_selective),
    )
    write_selection_json(selection, args.json_output)
    write_selection_report(selection, args.report_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
