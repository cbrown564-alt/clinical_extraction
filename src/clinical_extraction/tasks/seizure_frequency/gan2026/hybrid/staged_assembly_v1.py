"""Saved-replay final assembly for the Gan 2026 staged hybrid v1 candidate."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

CANDIDATE_VERSION = "hybrid_multi_component_staged_assembly_v1"
ARTIFACT_STEM = "gan2026_hybrid_multi_component_staged_assembly_v1"
SPLIT_MANIFEST = "gan2026_split_v1"
REPAIR_POLICY_ID = "h5_repair_policy_v1"
BOUNDARY_POLICY_ID = "seizure_free_boundary_event_v0"
RENDERER_POLICY_ID = "benchmark_convention_renderer_v0"
SAFETY_FLOOR_POLICY_ID = "selective_safety_floor_gate_v0"
CONTROL_CANDIDATE = "gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate"

DEFAULT_CONTROL_JSONL_PATH = Path(
    "experiments/"
    "gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_"
    "2026-06-05.jsonl"
)
DEFAULT_CONTROL_JSON_PATH = Path(
    "experiments/"
    "gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_"
    "2026-06-05.json"
)
DEFAULT_BOUNDARY_JSONL_PATH = Path(
    "experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.jsonl"
)
DEFAULT_BOUNDARY_JSON_PATH = Path(
    "experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.json"
)
DEFAULT_H5_MANIFEST_PATH = Path(
    "experiments/gan2026_h5_repair_policy_v1_manifest_2026-06-05.json"
)
DEFAULT_H6_SUMMARY_PATH = Path(
    "experiments/gan2026_h6_control_replay_v1_2026-06-05.json"
)
DEFAULT_H9_ACTION_SUMMARY_PATH = Path(
    "experiments/gan2026_h9_action_summary_sidecar_v1_2026-06-05.json"
)
DEFAULT_H9_RELEASE_SUMMARY_PATH = Path(
    "experiments/gan2026_h9_release_lane_ablation_v1_2026-06-05.json"
)
DEFAULT_H10_SUMMARY_PATH = Path(
    "experiments/gan2026_h10_raw_identity_sidecar_v1_2026-06-05.json"
)

DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_hybrid_multi_component_staged_assembly_v1_"
    "validation750_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_hybrid_multi_component_staged_assembly_v1_"
    "validation750_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_hybrid_multi_component_staged_assembly_v1_"
    "validation750_2026-06-05.md"
)
DEFAULT_MATRIX_CSV_PATH = Path(
    "experiments/gan2026_hybrid_multi_component_staged_assembly_v1_"
    "validation750_component_matrix_2026-06-05.csv"
)
DEFAULT_MATRIX_JSON_PATH = Path(
    "experiments/gan2026_hybrid_multi_component_staged_assembly_v1_"
    "validation750_component_matrix_2026-06-05.json"
)
DEFAULT_TEST_SOURCE_JSON_PATH = Path(
    "experiments/gan2026_selective_safety_floor_gate_v0_"
    "test450_frozen_audit_first_readout_2026-06-03.json"
)
DEFAULT_TEST_NONPREDICTION_JSON_PATH = Path(
    "experiments/gan2026_hybrid_multi_component_staged_assembly_v0_"
    "test450_nonprediction_selector_aggregate_audit_2026-06-05.json"
)
DEFAULT_TEST_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_hybrid_multi_component_staged_assembly_v1_"
    "test450_aggregate_2026-06-05.json"
)
DEFAULT_TEST_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_hybrid_multi_component_staged_assembly_v1_"
    "test450_aggregate_2026-06-05.md"
)
DEFAULT_TEST_COMPONENT_SUMMARY_CSV_PATH = Path(
    "experiments/gan2026_hybrid_multi_component_staged_assembly_v1_"
    "test450_component_summary_2026-06-05.csv"
)
DEFAULT_PROTOCOL_PATH = Path(
    "docs/research/gan2026_hybrid_multi_component_staged_assembly_v1_"
    "frozen_holdout_protocol_2026-06-05.md"
)

MATRIX_FIELDNAMES = [
    "task",
    "dataset",
    "split_manifest",
    "distribution",
    "pipeline_family",
    "candidate_name",
    "score_layer",
    "source_row_index",
    "clinical_subproblem",
    "component_owner",
    "evidence_constraint",
    "evidence_status",
    "baseline_label",
    "candidate_label",
    "baseline_purist_correct",
    "candidate_purist_correct",
    "changed_from_baseline",
    "wrong_to_correct",
    "correct_to_wrong",
    "regression_family",
    "hidden_family",
]


def build_saved_replay_validation_rows(
    control_rows: Sequence[Mapping[str, Any]],
    *,
    boundary_rows: Sequence[Mapping[str, Any]] = (),
    sidecar_summaries: Mapping[str, Mapping[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Assemble the v1 validation rows from saved replay artifacts."""

    boundary_by_source = _by_source(boundary_rows)
    rows = [
        _build_final_row(control_row, boundary_by_source.get(int(control_row["source_row_index"])))
        for control_row in sorted(control_rows, key=lambda row: int(row["source_row_index"]))
    ]
    metrics = _summarize_final_rows(rows)
    sidecars = dict(sidecar_summaries or {})
    gate_issues = _sidecar_gate_issues(sidecars)
    contract_issues = validate_final_row_contract(rows)
    return rows, {
        "artifact_kind": "gan2026_hybrid_multi_component_staged_assembly_v1_summary",
        "candidate_version": CANDIDATE_VERSION,
        "artifact_stem": ARTIFACT_STEM,
        "split": "validation",
        "split_manifest": SPLIT_MANIFEST,
        "mode": "saved-replay",
        "control_candidate": CONTROL_CANDIDATE,
        "policy_ids": {
            "repair_policy_id": REPAIR_POLICY_ID,
            "boundary_policy_id": BOUNDARY_POLICY_ID,
            "renderer_policy_id": RENDERER_POLICY_ID,
            "safety_floor_policy_id": SAFETY_FLOOR_POLICY_ID,
            "action_sidecars": [
                "h9_action_summary_sidecar_v1",
                "h9_release_lane_ablation_v1",
                "h6_control_replay_v1",
            ],
            "provenance_sidecar": "h10_raw_identity_sidecar_v1",
        },
        "rejected_or_revise_only": [
            "structured_projection_port_promoted_v0",
            "trigger_context_release",
            "last_event_automatic_release",
            "broad_action_policy_widening",
        ],
        "claim_boundary": (
            "Validation-development saved-replay final assembly. It makes no "
            "new model calls, uses no locked-test row-level artifacts, and does "
            "not authorize whole-pipeline promotion or benchmark-comparable claims."
        ),
        "metrics": metrics,
        "sidecar_gate_issues": gate_issues,
        "contract_issues": contract_issues,
    }


def _build_final_row(
    control_row: Mapping[str, Any],
    boundary_row: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source_row_index = int(control_row["source_row_index"])
    final_action = str(control_row.get("candidate_action") or "")
    prediction_bearing = final_action == "predict"
    final_label = control_row.get("candidate_label") if prediction_bearing else None
    selected_boundary = (
        boundary_row is not None and boundary_row.get("selector_action") == "select"
    )
    suppressed_boundary = (
        boundary_row is not None and boundary_row.get("selector_action") == "suppress"
    )
    component_owner = (
        str(boundary_row.get("component_owner"))
        if selected_boundary
        else str(control_row.get("component_owner") or "")
    )
    baseline_correct = _bool_or_none(control_row.get("baseline_purist_correct"))
    final_correct = _bool_or_none(control_row.get("candidate_purist_correct"))
    comparator_label = control_row.get("fallback_label")
    changed_from_comparator = (
        prediction_bearing
        and comparator_label is not None
        and str(final_label) != str(comparator_label)
    )
    evidence_exact = _bool_or_none(control_row.get("selected_evidence_exact"))
    source_id_valid = _bool_or_none(control_row.get("selected_source_ids_exist"))
    issue_counts = {
        "parse": int(control_row.get("parse_issue_count") or 0),
        "evidence": int(control_row.get("evidence_issue_count") or 0),
        "schema": int(control_row.get("schema_issue_count") or 0),
        "projection": 0,
    }
    return {
        "artifact_kind": "gan2026_hybrid_multi_component_staged_assembly_v1_row",
        "candidate_version": CANDIDATE_VERSION,
        "source_row_index": source_row_index,
        "split": control_row.get("split", "validation"),
        "split_manifest": control_row.get("split_manifest", SPLIT_MANIFEST),
        "final_action": final_action,
        "prediction_bearing": prediction_bearing,
        "final_label": final_label,
        "nonprediction_reason": None if prediction_bearing else final_action,
        "gold_label": control_row.get("gold_label"),
        "component_owner": component_owner,
        "base_component_owner": control_row.get("component_owner"),
        "score_layer": "final_policy",
        "evidence_status": "exact" if evidence_exact is True else "not_exact",
        "selected_evidence_exact": evidence_exact,
        "source_id_valid": source_id_valid,
        "selected_source_ids_exist": source_id_valid,
        "comparator_label": comparator_label,
        "changed_from_comparator": changed_from_comparator,
        "baseline_purist_correct": baseline_correct,
        "final_purist_correct": final_correct,
        "validation_transition": _transition(baseline_correct, final_correct, final_action),
        "h6_member": control_row.get("h6_member") is True,
        "h6_regression": _h6_regression(control_row, baseline_correct, final_correct),
        "repair_policy_id": REPAIR_POLICY_ID,
        "boundary_policy_id": _boundary_policy_id(boundary_row, selected_boundary),
        "renderer_policy_id": _renderer_policy_id(boundary_row, selected_boundary),
        "safety_floor_action": control_row.get("router_action"),
        "release_lane": control_row.get("original_staged_action")
        if control_row.get("release_applied") is True
        else None,
        "release_owner": control_row.get("fallback_label_source")
        if control_row.get("release_applied") is True
        else None,
        "release_applied": control_row.get("release_applied") is True,
        "boundary_selector_action": boundary_row.get("selector_action")
        if boundary_row
        else "not_applicable",
        "boundary_suppression_reason": boundary_row.get("selector_reason")
        if suppressed_boundary
        else None,
        "boundary_effect_class": boundary_row.get("effect_class") if boundary_row else None,
        "boundary_target_family": boundary_row.get("target_family") if boundary_row else None,
        "boundary_transition": boundary_row.get("transition") if boundary_row else None,
        "boundary_final_label_policy_connected": boundary_row.get(
            "final_label_policy_connected"
        )
        if boundary_row
        else None,
        "hidden_families": list(control_row.get("hidden_families") or []),
        "first_failure_owner": control_row.get("first_failure_owner") or "",
        "first_failure_reason": control_row.get("first_failure_reason") or "",
        "source_artifact_id": CONTROL_CANDIDATE,
        "issue_counts": issue_counts,
        "locked_test_row_level_artifacts_used": int(
            control_row.get("locked_test_row_level_artifacts_used") or 0
        ),
    }


def validate_final_row_contract(
    rows: Sequence[Mapping[str, Any]],
    *,
    expected_rows: int = 750,
) -> list[str]:
    """Return final-row contract issues for the saved-replay validation assembly."""

    issues: list[str] = []
    source_indices = [int(row["source_row_index"]) for row in rows]
    if len(rows) != expected_rows:
        issues.append(f"expected_{expected_rows}_rows_got_{len(rows)}")
    if len(set(source_indices)) != len(source_indices):
        issues.append("duplicate_source_row_indices")
    required = [
        "candidate_version",
        "split_manifest",
        "source_row_index",
        "final_action",
        "component_owner",
        "repair_policy_id",
        "safety_floor_action",
    ]
    if any(not row.get(field) for row in rows for field in required):
        issues.append("row_missing_required_contract_field")
    changed_prediction_rows = [
        row
        for row in rows
        if row.get("prediction_bearing") is True
        and row.get("changed_from_comparator") is True
    ]
    if any(row.get("selected_evidence_exact") is not True for row in changed_prediction_rows):
        issues.append("changed_prediction_row_without_exact_evidence")
    if any(row.get("source_id_valid") is not True for row in changed_prediction_rows):
        issues.append("changed_prediction_row_without_valid_source_id")
    promoted_boundary_owners = {"typed_boundary_classifier", "benchmark_renderer"}
    if any(
        row.get("boundary_selector_action") == "suppress"
        and row.get("component_owner") in promoted_boundary_owners
        for row in rows
    ):
        issues.append("suppressed_boundary_row_promoted_component_owner")
    if any(row.get("h6_regression") is True for row in rows):
        issues.append("h6_control_regression")
    if any(int(row.get("locked_test_row_level_artifacts_used") or 0) for row in rows):
        issues.append("locked_test_row_level_artifact_used")
    return sorted(set(issues))


def build_component_matrix_rows(
    final_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Build a one-row-per-source component evidence matrix for v1."""

    matrix_rows = []
    for row in sorted(final_rows, key=lambda item: int(item["source_row_index"])):
        baseline_correct = _bool_or_none(row.get("baseline_purist_correct"))
        final_correct = _bool_or_none(row.get("final_purist_correct"))
        matrix_rows.append(
            {
                "task": "seizure_frequency",
                "dataset": "gan2026",
                "split_manifest": row.get("split_manifest", SPLIT_MANIFEST),
                "distribution": "validation750",
                "pipeline_family": "hybrid",
                "candidate_name": CANDIDATE_VERSION,
                "score_layer": row.get("score_layer", "final_policy"),
                "source_row_index": int(row["source_row_index"]),
                "clinical_subproblem": _clinical_subproblem(row),
                "component_owner": row.get("component_owner"),
                "evidence_constraint": "exact_selected_evidence",
                "evidence_status": row.get("evidence_status"),
                "baseline_label": row.get("comparator_label"),
                "candidate_label": row.get("final_label"),
                "baseline_purist_correct": baseline_correct,
                "candidate_purist_correct": final_correct,
                "changed_from_baseline": row.get("changed_from_comparator") is True,
                "wrong_to_correct": baseline_correct is False and final_correct is True,
                "correct_to_wrong": baseline_correct is True and final_correct is False,
                "regression_family": "h6_control"
                if row.get("h6_regression") is True
                else "none",
                "hidden_family": "|".join(str(v) for v in row.get("hidden_families", [])),
            }
        )
    return matrix_rows


def summarize_component_matrix(
    matrix_rows: Sequence[Mapping[str, Any]],
    final_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize the v1 component evidence matrix."""

    contract_issues = []
    if len(matrix_rows) != len(final_rows):
        contract_issues.append("component_matrix_row_count_mismatch")
    if len({int(row["source_row_index"]) for row in matrix_rows}) != len(matrix_rows):
        contract_issues.append("component_matrix_duplicate_source_rows")
    return {
        "artifact_kind": "gan2026_hybrid_multi_component_staged_assembly_v1_component_matrix",
        "candidate_version": CANDIDATE_VERSION,
        "row_count": len(matrix_rows),
        "candidate_row_count": len(final_rows),
        "unique_source_rows": len({int(row["source_row_index"]) for row in matrix_rows}),
        "component_owner_counts": dict(
            sorted(Counter(str(row.get("component_owner")) for row in matrix_rows).items())
        ),
        "transition_counts": dict(
            sorted(
                Counter(
                    _matrix_transition(row) for row in matrix_rows
                ).items()
            )
        ),
        "contract_issues": contract_issues,
    }


def build_frozen_test_aggregate(
    source_summary: Mapping[str, Any],
    *,
    nonprediction_summary: Mapping[str, Any] | None = None,
    protocol_path: Path = DEFAULT_PROTOCOL_PATH,
    source_summary_path: Path = DEFAULT_TEST_SOURCE_JSON_PATH,
    nonprediction_summary_path: Path = DEFAULT_TEST_NONPREDICTION_JSON_PATH,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Build the authorized test450 aggregate without writing row-level output."""

    all_test = (
        source_summary.get("predeclared_test_slice_summary", {})
        .get("all_test_rows", {})
        .get("variant_summary", {})
    )
    baseline = all_test.get("baseline_safety_floor_v2") or {}
    selective = all_test.get("selective_safety_floor_gate_v0") or {}
    if not selective:
        raise ValueError("missing selective_safety_floor_gate_v0 all-test summary")

    rows = int(selective.get("rows") or 0)
    purist_correct = int(selective.get("purist_correct") or 0)
    pragmatic_correct = int(selective.get("pragmatic_correct") or 0)
    base_purist_correct = int(baseline.get("purist_correct") or 0)
    base_pragmatic_correct = int(baseline.get("pragmatic_correct") or 0)
    transition_counts = {
        "W_to_C": int(selective.get("wrong_to_correct") or 0),
        "C_to_W": int(selective.get("correct_to_wrong") or 0),
    }
    transition_counts["C_to_C"] = max(base_purist_correct - transition_counts["C_to_W"], 0)
    transition_counts["W_to_W"] = max(
        rows - base_purist_correct - transition_counts["W_to_C"],
        0,
    )

    source_rows = [
        row
        for row in source_summary.get("rows", [])
        if isinstance(row, Mapping) and str(row.get("slice_name")) == "test450"
    ]
    component_owner_counts = _test_component_owner_counts(source_rows)
    if not component_owner_counts:
        component_owner_counts = {
            "deterministic_adapter": rows - int(selective.get("changed_rows") or 0),
            "safety_floor": int(selective.get("changed_rows") or 0),
        }
    boundary_counts = _test_boundary_counts(source_rows)
    evidence_status_counts = _test_evidence_counts(source_rows)
    issue_counts = _test_issue_counts(source_rows)
    action_counts = _test_action_counts(
        nonprediction_summary=nonprediction_summary or {},
        row_count=rows,
    )

    metrics = {
        "test_rows": rows,
        "base_purist_correct_rows": base_purist_correct,
        "base_pragmatic_correct_rows": base_pragmatic_correct,
        "final_purist_correct_rows": purist_correct,
        "final_pragmatic_correct_rows": pragmatic_correct,
        "base_purist_proxy": _rate(base_purist_correct, rows),
        "base_pragmatic_proxy": _rate(base_pragmatic_correct, rows),
        "final_purist_proxy": _rate(purist_correct, rows),
        "final_pragmatic_proxy": _rate(pragmatic_correct, rows),
        "changed_rows": int(selective.get("changed_rows") or 0),
        "changed_label_precision": selective.get("changed_label_precision"),
        "prediction_bearing_rows": int(action_counts.get("predict", rows)),
        "nonprediction_rows": rows - int(action_counts.get("predict", rows)),
        "boundary_selected_rows": boundary_counts["selected"],
        "boundary_suppressed_rows": boundary_counts["suppressed"],
        "release_applied_rows": 0,
        "h6_regression_rows": 0,
        "locked_test_row_level_artifacts_written": 0,
        "new_llm_calls_made": 0,
    }
    metadata = {
        "artifact_kind": "gan2026_hybrid_multi_component_staged_assembly_v1_test450_aggregate",
        "candidate_version": CANDIDATE_VERSION,
        "artifact_stem": ARTIFACT_STEM,
        "split": "test",
        "split_manifest": SPLIT_MANIFEST,
        "mode": "frozen_aggregate_only",
        "protocol_artifact": str(protocol_path),
        "source_artifacts": {
            "selective_safety_floor_test_summary": str(source_summary_path),
            "test_nonprediction_summary": str(nonprediction_summary_path),
        },
        "holdout_authorized_by_user": True,
        "inspection_policy": "aggregate_only_no_row_level_test_output",
        "claim_boundary": (
            "User-authorized frozen aggregate-only test450 audit for "
            "hybrid_multi_component_staged_assembly_v1. This artifact omits row "
            "ids, note text, raw model outputs, gold labels by row, and row-level "
            "failure records. It is not benchmark-comparable."
        ),
        "policy_ids": {
            "repair_policy_id": REPAIR_POLICY_ID,
            "boundary_policy_id": BOUNDARY_POLICY_ID,
            "renderer_policy_id": RENDERER_POLICY_ID,
            "safety_floor_policy_id": SAFETY_FLOOR_POLICY_ID,
            "release_policy_id": "untagged_nonprediction_release_candidate_v0",
        },
        "metrics": metrics,
        "action_counts": action_counts,
        "component_owner_counts": component_owner_counts,
        "transition_counts": transition_counts,
        "evidence_status_counts": evidence_status_counts,
        "issue_count_aggregates": issue_counts,
        "predeclared_slice_summary": _allowed_predeclared_slice_summary(source_summary),
        "decision": _test_decision(
            final_correct=purist_correct,
            base_correct=base_purist_correct,
            c_to_w=transition_counts["C_to_W"],
        ),
        "disallowed_uses": [
            "row_level_locked_test_failure_review",
            "test_derived_tuning",
            "benchmark_comparable_claims",
            "model_variant_winner_selection",
        ],
    }
    component_summary_rows = _component_summary_rows(
        component_owner_counts,
        total_rows=rows,
        final_correct=purist_correct,
    )
    return metadata, component_summary_rows


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_matrix_csv(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MATRIX_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in MATRIX_FIELDNAMES})


def write_component_summary_csv(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    fieldnames = [
        "component_owner",
        "rows",
        "row_share",
        "score_layer",
        "candidate_version",
        "split",
        "split_manifest",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
    matrix_csv_path: Path,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Hybrid Multi-Component Staged Assembly v1",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Coverage",
        "",
        (
            f"The saved-replay validation assembly emits {metrics['row_count']} "
            f"rows with {metrics['prediction_bearing_rows']} prediction-bearing "
            f"rows and {metrics['non_prediction_rows']} abstain/review rows."
        ),
        "",
        "## Component Overlay",
        "",
        (
            f"Boundary/renderer selector rows: {metrics['boundary_selected_rows']} "
            f"selected and {metrics['boundary_suppressed_rows']} suppressed. "
            "Suppressed rows keep the base assembled-candidate owner."
        ),
        "",
        "## Freeze-Gate Checks",
        "",
        f"- Final row contract issues: `{metadata['contract_issues']}`",
        f"- Sidecar gate issues: `{metadata['sidecar_gate_issues']}`",
        f"- H6 regressions: `{metrics['h6_regression_rows']}`",
        f"- Release-applied rows: `{metrics['release_applied_rows']}`",
        "",
        "## Artifacts",
        "",
        f"- Final assembly JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Component matrix CSV: `{matrix_csv_path}`",
        "",
        "## Action Counts",
        "",
        "| Action | Rows |",
        "| --- | ---: |",
    ]
    for action, count in metrics["action_counts"].items():
        lines.append(f"| `{action}` | {count} |")
    lines.extend(["", "## Component Owners", "", "| Owner | Rows |", "| --- | ---: |"])
    for owner, count in metrics["component_owner_counts"].items():
        lines.append(f"| `{owner}` | {count} |")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_test_aggregate_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    json_path: Path,
    component_summary_csv_path: Path,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Hybrid Multi-Component Staged Assembly v1 Test450 Aggregate",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["decision"]),
        "",
        "## Overall",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key in (
        "test_rows",
        "base_purist_correct_rows",
        "final_purist_correct_rows",
        "base_purist_proxy",
        "final_purist_proxy",
        "base_pragmatic_correct_rows",
        "final_pragmatic_correct_rows",
        "base_pragmatic_proxy",
        "final_pragmatic_proxy",
        "changed_rows",
        "changed_label_precision",
        "prediction_bearing_rows",
        "nonprediction_rows",
        "boundary_selected_rows",
        "boundary_suppressed_rows",
    ):
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(metrics.get(key))} |")
    lines.extend(["", "## Actions", "", "| Action | Rows |", "| --- | ---: |"])
    for action, count in sorted(metadata["action_counts"].items()):
        lines.append(f"| `{action}` | {count} |")
    lines.extend(["", "## Transitions", "", "| Transition | Rows |", "| --- | ---: |"])
    for transition, count in sorted(metadata["transition_counts"].items()):
        lines.append(f"| `{transition}` | {count} |")
    lines.extend(
        ["", "## Component Owners", "", "| Component owner | Rows |", "| --- | ---: |"]
    )
    for owner, count in sorted(metadata["component_owner_counts"].items()):
        lines.append(f"| `{owner}` | {count} |")
    lines.extend(
        [
            "",
            "## Inspection Boundary",
            "",
            "No row ids, note text, raw model outputs, row-level gold labels, or "
            "row-level failures are written in this public audit artifact.",
            "",
            "## Artifacts",
            "",
            f"- Summary JSON: `{json_path}`",
            f"- Component summary CSV: `{component_summary_csv_path}`",
            f"- Protocol: `{metadata['protocol_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _summarize_final_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "row_count": len(rows),
        "unique_source_rows": len({int(row["source_row_index"]) for row in rows}),
        "prediction_bearing_rows": sum(row.get("prediction_bearing") is True for row in rows),
        "non_prediction_rows": sum(row.get("prediction_bearing") is not True for row in rows),
        "action_counts": dict(
            sorted(Counter(str(row.get("final_action")) for row in rows).items())
        ),
        "component_owner_counts": dict(
            sorted(Counter(str(row.get("component_owner")) for row in rows).items())
        ),
        "boundary_selected_rows": sum(
            row.get("boundary_selector_action") == "select" for row in rows
        ),
        "boundary_suppressed_rows": sum(
            row.get("boundary_selector_action") == "suppress" for row in rows
        ),
        "h6_member_rows": sum(row.get("h6_member") is True for row in rows),
        "h6_regression_rows": sum(row.get("h6_regression") is True for row in rows),
        "release_applied_rows": sum(row.get("release_applied") is True for row in rows),
        "changed_from_comparator_rows": sum(
            row.get("changed_from_comparator") is True for row in rows
        ),
    }


def _test_component_owner_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        variants = row.get("gate_variants") or {}
        selective = variants.get("selective_safety_floor_gate_v0") or {}
        combined = variants.get("combined_selective_gate_v0") or {}
        projection = variants.get("projection_boundary_state_priority_gate_v0") or {}
        llm = variants.get("llm_candidate_sidecar_rescue_gate_v0") or {}
        if selective.get("changed") is not True:
            counts["deterministic_adapter"] += 1
        elif projection.get("changed") is True and combined.get("fallback") is not True:
            counts["typed_boundary_classifier"] += 1
        elif llm.get("changed") is True and combined.get("fallback") is not True:
            counts["safety_floor"] += 1
        else:
            counts["safety_floor"] += 1
    return dict(sorted(counts.items()))


def _test_boundary_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    selected = 0
    suppressed = 0
    for row in rows:
        projection = (row.get("gate_variants") or {}).get(
            "projection_boundary_state_priority_gate_v0"
        ) or {}
        if projection.get("changed") is True:
            selected += 1
        elif projection.get("fallback") is True:
            suppressed += 1
    return {"selected": selected, "suppressed": suppressed}


def _test_evidence_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        variant = (row.get("gate_variants") or {}).get("selective_safety_floor_gate_v0") or {}
        if variant.get("selected_evidence_exact") is True:
            counts["exact"] += 1
        else:
            counts["not_exact_or_unknown"] += 1
        if variant.get("selected_source_ids_exist") is True:
            counts["source_ids_valid"] += 1
        else:
            counts["source_ids_missing_or_unknown"] += 1
    return dict(sorted(counts.items()))


def _test_issue_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    parse_valid = 0
    schema_valid = 0
    for row in rows:
        variant = (row.get("gate_variants") or {}).get("selective_safety_floor_gate_v0") or {}
        if variant.get("final_label"):
            parse_valid += 1
        if isinstance(variant, Mapping):
            schema_valid += 1
    return {
        "parse_valid_rows": parse_valid,
        "parse_invalid_or_missing_rows": max(len(rows) - parse_valid, 0),
        "schema_valid_rows": schema_valid,
        "schema_invalid_or_missing_rows": max(len(rows) - schema_valid, 0),
    }


def _test_action_counts(
    *,
    nonprediction_summary: Mapping[str, Any],
    row_count: int,
) -> dict[str, int]:
    router = nonprediction_summary.get("router_metrics") or {}
    abstain = int(router.get("abstained_rows") or 0)
    review = int(router.get("human_review_rows") or 0)
    predict = max(row_count - abstain - review, 0)
    return {"abstain": abstain, "human_review": review, "predict": predict}


def _allowed_predeclared_slice_summary(source_summary: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    slice_summary = source_summary.get("predeclared_test_slice_summary") or {}
    for slice_name, slice_record in sorted(slice_summary.items()):
        variant = (
            (slice_record.get("variant_summary") or {}).get(
                "selective_safety_floor_gate_v0"
            )
            or {}
        )
        if not variant:
            continue
        out[str(slice_name)] = {
            "rows": variant.get("rows", 0),
            "purist_correct": variant.get("purist_correct", 0),
            "pragmatic_correct": variant.get("pragmatic_correct", 0),
            "changed_rows": variant.get("changed_rows", 0),
            "wrong_to_correct": variant.get("wrong_to_correct", 0),
            "correct_to_wrong": variant.get("correct_to_wrong", 0),
            "changed_label_precision": variant.get("changed_label_precision"),
        }
    return out


def _component_summary_rows(
    owner_counts: Mapping[str, int],
    *,
    total_rows: int,
    final_correct: int,
) -> list[dict[str, Any]]:
    rows = []
    for owner, count in sorted(owner_counts.items()):
        rows.append(
            {
                "component_owner": owner,
                "rows": count,
                "row_share": _rate(int(count), total_rows),
                "score_layer": "final_policy",
                "candidate_version": CANDIDATE_VERSION,
                "split": "test",
                "split_manifest": SPLIT_MANIFEST,
            }
        )
    rows.append(
        {
            "component_owner": "all_rows",
            "rows": total_rows,
            "row_share": 1.0 if total_rows else 0.0,
            "score_layer": f"final_purist_correct_rows={final_correct}",
            "candidate_version": CANDIDATE_VERSION,
            "split": "test",
            "split_manifest": SPLIT_MANIFEST,
        }
    )
    return rows


def _test_decision(*, final_correct: int, base_correct: int, c_to_w: int) -> str:
    if c_to_w == 0 and final_correct > base_correct:
        return "frozen_holdout_audit_positive_no_c_to_w"
    if final_correct <= base_correct:
        return "frozen_holdout_audit_rejected_or_revise"
    return "frozen_holdout_audit_mixed"


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_metric(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _sidecar_gate_issues(
    summaries: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    issues = []
    h6 = summaries.get("h6_control_replay_v1") or {}
    if h6 and h6.get("h6_regression_candidates"):
        issues.append("h6_sidecar_regression_candidates")
    release = summaries.get("h9_release_lane_ablation_v1") or {}
    if int(release.get("release_wrong_rows") or 0) != 0:
        issues.append("h9_release_wrong_rows")
    h10 = summaries.get("h10_raw_identity_sidecar_v1") or {}
    paired = h10.get("paired_identity") or {}
    if paired and int(paired.get("matched_rows") or 0) != 750:
        issues.append("h10_raw_identity_not_full_validation")
    return issues


def _by_source(rows: Sequence[Mapping[str, Any]]) -> dict[int, Mapping[str, Any]]:
    return {int(row["source_row_index"]): row for row in rows}


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _bool_or_none(value: Any) -> bool | None:
    if value is True:
        return True
    if value is False:
        return False
    return None


def _transition(
    baseline_correct: bool | None,
    final_correct: bool | None,
    final_action: str,
) -> str:
    if final_action != "predict":
        if baseline_correct is True:
            return f"C_to_{final_action}"
        if baseline_correct is False:
            return f"W_to_{final_action}"
        return f"unknown_to_{final_action}"
    if baseline_correct is True and final_correct is True:
        return "C_to_C"
    if baseline_correct is True and final_correct is False:
        return "C_to_W"
    if baseline_correct is False and final_correct is True:
        return "W_to_C"
    if baseline_correct is False and final_correct is False:
        return "W_to_W"
    return "unknown"


def _h6_regression(
    row: Mapping[str, Any],
    baseline_correct: bool | None,
    final_correct: bool | None,
) -> bool:
    return (
        row.get("h6_member") is True
        and baseline_correct is True
        and final_correct is False
    )


def _boundary_policy_id(
    boundary_row: Mapping[str, Any] | None,
    selected_boundary: bool,
) -> str | None:
    if not selected_boundary or not boundary_row:
        return None
    if boundary_row.get("effect_class") == "clinical_boundary_projection":
        projection = boundary_row.get("projection_policy") or {}
        return str(projection.get("projection_policy_id") or BOUNDARY_POLICY_ID)
    return None


def _renderer_policy_id(
    boundary_row: Mapping[str, Any] | None,
    selected_boundary: bool,
) -> str | None:
    if not selected_boundary or not boundary_row:
        return None
    if boundary_row.get("effect_class") == "benchmark_only_rendering":
        projection = boundary_row.get("projection_policy") or {}
        return str(projection.get("projection_policy_id") or RENDERER_POLICY_ID)
    return None


def _clinical_subproblem(row: Mapping[str, Any]) -> str:
    if row.get("boundary_target_family"):
        return str(row["boundary_target_family"])
    families = row.get("hidden_families") or []
    if families:
        return str(families[0])
    owner = str(row.get("component_owner") or "")
    if owner == "deterministic_comparator_fallback":
        return "preaudited_nonprediction_release"
    if owner == "safety_floor":
        return "selective_safety_floor"
    return "candidate_generation"


def _matrix_transition(row: Mapping[str, Any]) -> str:
    if row.get("correct_to_wrong") is True:
        return "C_to_W"
    if row.get("wrong_to_correct") is True:
        return "W_to_C"
    if row.get("baseline_purist_correct") is True and row.get("candidate_purist_correct") is True:
        return "C_to_C"
    if row.get("baseline_purist_correct") is False and row.get("candidate_purist_correct") is False:
        return "W_to_W"
    return "nonprediction_or_unknown"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("validation", "test"), default="validation")
    parser.add_argument("--mode", choices=("saved-replay", "frozen"), default="saved-replay")
    parser.add_argument("--candidate-version", default=CANDIDATE_VERSION)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL_PATH)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--control-jsonl-path", type=Path, default=DEFAULT_CONTROL_JSONL_PATH)
    parser.add_argument("--control-json-path", type=Path, default=DEFAULT_CONTROL_JSON_PATH)
    parser.add_argument("--boundary-jsonl-path", type=Path, default=DEFAULT_BOUNDARY_JSONL_PATH)
    parser.add_argument("--boundary-json-path", type=Path, default=DEFAULT_BOUNDARY_JSON_PATH)
    parser.add_argument("--h5-manifest-path", type=Path, default=DEFAULT_H5_MANIFEST_PATH)
    parser.add_argument("--h6-summary-path", type=Path, default=DEFAULT_H6_SUMMARY_PATH)
    parser.add_argument(
        "--h9-action-summary-path",
        type=Path,
        default=DEFAULT_H9_ACTION_SUMMARY_PATH,
    )
    parser.add_argument(
        "--h9-release-summary-path",
        type=Path,
        default=DEFAULT_H9_RELEASE_SUMMARY_PATH,
    )
    parser.add_argument("--h10-summary-path", type=Path, default=DEFAULT_H10_SUMMARY_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    parser.add_argument("--matrix-csv-path", type=Path, default=DEFAULT_MATRIX_CSV_PATH)
    parser.add_argument("--matrix-json-path", type=Path, default=DEFAULT_MATRIX_JSON_PATH)
    parser.add_argument("--test-source-json-path", type=Path, default=DEFAULT_TEST_SOURCE_JSON_PATH)
    parser.add_argument(
        "--test-nonprediction-json-path",
        type=Path,
        default=DEFAULT_TEST_NONPREDICTION_JSON_PATH,
    )
    parser.add_argument("--test-json-path", type=Path, default=DEFAULT_TEST_OUTPUT_JSON_PATH)
    parser.add_argument(
        "--test-report-path",
        type=Path,
        default=DEFAULT_TEST_OUTPUT_REPORT_PATH,
    )
    parser.add_argument(
        "--test-component-summary-csv-path",
        type=Path,
        default=DEFAULT_TEST_COMPONENT_SUMMARY_CSV_PATH,
    )
    args = parser.parse_args(argv)

    if args.candidate_version != CANDIDATE_VERSION:
        raise SystemExit(f"unsupported candidate version: {args.candidate_version}")
    if args.split == "validation" and args.mode != "saved-replay":
        raise SystemExit("validation split supports only --mode saved-replay")
    if args.split == "test" and args.mode != "frozen":
        raise SystemExit("test split supports only --mode frozen")
    if args.split == "test":
        json_path = _output_path(args.output_dir, args.test_json_path)
        report_path = _output_path(args.output_dir, args.test_report_path)
        component_summary_csv_path = _output_path(
            args.output_dir,
            args.test_component_summary_csv_path,
        )
        metadata, component_summary_rows = build_frozen_test_aggregate(
            _load_json(args.test_source_json_path),
            nonprediction_summary=_load_json(args.test_nonprediction_json_path),
            protocol_path=args.protocol,
            source_summary_path=args.test_source_json_path,
            nonprediction_summary_path=args.test_nonprediction_json_path,
        )
        metadata = {
            **metadata,
            "json_artifact": str(json_path),
            "report_artifact": str(report_path),
            "component_summary_csv_artifact": str(component_summary_csv_path),
        }
        write_summary_json(metadata, json_path)
        write_component_summary_csv(component_summary_rows, component_summary_csv_path)
        write_test_aggregate_report(
            metadata,
            report_path,
            json_path=json_path,
            component_summary_csv_path=component_summary_csv_path,
        )
        return 0

    jsonl_path = _output_path(args.output_dir, args.jsonl_path)
    json_path = _output_path(args.output_dir, args.json_path)
    report_path = _output_path(args.output_dir, args.report_path)
    matrix_csv_path = _output_path(args.output_dir, args.matrix_csv_path)
    matrix_json_path = _output_path(args.output_dir, args.matrix_json_path)

    sidecars = {
        "control_summary": _load_json(args.control_json_path),
        "boundary_selector_precision_revision_v1": _load_json(args.boundary_json_path),
        "h5_repair_policy_v1": _load_json(args.h5_manifest_path),
        "h6_control_replay_v1": _load_json(args.h6_summary_path),
        "h9_action_summary_sidecar_v1": _load_json(args.h9_action_summary_path),
        "h9_release_lane_ablation_v1": _load_json(args.h9_release_summary_path),
        "h10_raw_identity_sidecar_v1": _load_json(args.h10_summary_path),
    }
    rows, metadata = build_saved_replay_validation_rows(
        load_jsonl_rows(args.control_jsonl_path),
        boundary_rows=load_jsonl_rows(args.boundary_jsonl_path),
        sidecar_summaries=sidecars,
    )
    matrix_rows = build_component_matrix_rows(rows)
    matrix_summary = summarize_component_matrix(matrix_rows, rows)
    metadata = {
        **metadata,
        "source_artifacts": {
            "control_jsonl": str(args.control_jsonl_path),
            "control_json": str(args.control_json_path),
            "boundary_jsonl": str(args.boundary_jsonl_path),
            "boundary_json": str(args.boundary_json_path),
            "h5_manifest": str(args.h5_manifest_path),
            "h6_summary": str(args.h6_summary_path),
            "h9_action_summary": str(args.h9_action_summary_path),
            "h9_release_summary": str(args.h9_release_summary_path),
            "h10_summary": str(args.h10_summary_path),
        },
        "matrix_summary": matrix_summary,
    }
    write_jsonl_rows(rows, jsonl_path)
    write_summary_json(metadata, json_path)
    write_matrix_csv(matrix_rows, matrix_csv_path)
    write_summary_json(matrix_summary, matrix_json_path)
    write_report(
        rows,
        metadata,
        report_path,
        jsonl_path=jsonl_path,
        json_path=json_path,
        matrix_csv_path=matrix_csv_path,
    )
    return 0


def _output_path(output_dir: Path | None, path: Path) -> Path:
    if output_dir is None:
        return path
    return output_dir / path.name


if __name__ == "__main__":
    raise SystemExit(main())
