"""Build the Gan 2026 RQ4 projection-decision matrix from saved artifacts."""

from __future__ import annotations

import argparse
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_EVIDENCE_MATRIX_PATH = Path(
    "experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.jsonl"
)
DEFAULT_ARBITRATION_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_"
    "2026-06-02.jsonl"
)
DEFAULT_DURATION_PATH = Path(
    "experiments/"
    "gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_"
    "2026-06-02.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_rq4_projection_decision_matrix_2026-06-03.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_rq4_projection_decision_matrix_2026-06-03.md"
)

PROJECTION_COMPONENTS = {
    "deterministic_top_candidate",
    "state_graph_projection",
    "hybrid_adjudicator_raw",
    "claim_table_final_query",
    "llm_heavy_selected_fact",
}


def build_projection_decision_matrix(
    *,
    evidence_matrix_path: Path = DEFAULT_EVIDENCE_MATRIX_PATH,
    arbitration_path: Path = DEFAULT_ARBITRATION_PATH,
    duration_path: Path = DEFAULT_DURATION_PATH,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(_rows_from_evidence_matrix(evidence_matrix_path))
    rows.extend(_rows_from_arbitration_ablation(arbitration_path))
    rows.extend(_rows_from_duration_ablation(duration_path))
    rows.sort(
        key=lambda row: (
            row["surface"],
            int(row["source_row_index"]),
            row["component_name"],
        )
    )
    return rows, summarize_projection_rows(rows)


def summarize_projection_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_component: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    by_surface: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    by_family: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        by_component[str(row["component_name"])].append(row)
        by_surface[str(row["surface"])].append(row)
        for family in row.get("hidden_families") or [row.get("failure_family") or "unmapped"]:
            by_family[(str(row["component_name"]), str(family))].append(row)

    return {
        "artifact_kind": "gan2026_rq4_projection_decision_matrix",
        "row_count": len(rows),
        "source_row_count": len({int(row["source_row_index"]) for row in rows}),
        "by_component": {
            component: _summary_for_rows(component_rows)
            for component, component_rows in sorted(by_component.items())
        },
        "by_surface": {
            surface: _summary_for_rows(surface_rows)
            for surface, surface_rows in sorted(by_surface.items())
        },
        "hidden_family_summary": {
            f"{component}::{family}": _summary_for_rows(family_rows)
            for (component, family), family_rows in sorted(by_family.items())
        },
    }


def write_matrix_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_matrix_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Gan 2026 RQ4 Projection-Decision Matrix",
        "",
        (
            "Replay-first component matrix for RQ4 projection. This is a "
            "validation-development artifact over saved decisions and diagnostic "
            "ablations, not a benchmark or locked-holdout claim."
        ),
        "",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Matrix rows: {metadata['row_count']}",
        f"- Source rows represented: {metadata['source_row_count']}",
        "",
        "## Component Summary",
        "",
        (
            "| Component | Rows | Projection correct | Changed | W->C | C->W | "
            "Exact evidence | Source-id valid |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for component, summary in metadata["by_component"].items():
        lines.append(
            (
                "| {component} | {rows} | {projection:.3f} | {changed} | {wtc} | "
                "{ctw} | {exact:.3f} | {source_ids:.3f} |"
            ).format(
                component=component,
                rows=summary["rows"],
                projection=summary["projection_correct_rate"],
                changed=summary["changed_from_baseline"],
                wtc=summary["wrong_to_correct"],
                ctw=summary["correct_to_wrong"],
                exact=summary["exact_evidence_rate"],
                source_ids=summary["source_id_valid_rate"],
            )
        )

    lines.extend(
        [
            "",
            "## Surface Summary",
            "",
            "| Surface | Rows | Projection correct | Changed | W->C | C->W |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for surface, summary in metadata["by_surface"].items():
        lines.append(
            (
                "| {surface} | {rows} | {projection:.3f} | {changed} | {wtc} | "
                "{ctw} |"
            ).format(
                surface=surface,
                rows=summary["rows"],
                projection=summary["projection_correct_rate"],
                changed=summary["changed_from_baseline"],
                wtc=summary["wrong_to_correct"],
                ctw=summary["correct_to_wrong"],
            )
        )

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            (
                "Rows from validation750 compare saved scorer-facing labels against the "
                "deterministic top candidate. Rows from projection ablations compare "
                "named graph policies only on preselected diagnostic surfaces where "
                "candidate/state representation already exists. The matrix therefore "
                "answers projection as a development-control question; it does not "
                "promote a production policy or make a holdout-transfer claim."
            ),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _rows_from_evidence_matrix(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in load_jsonl_rows(path):
        component = row.get("candidate_name")
        if component not in PROJECTION_COMPONENTS:
            continue
        candidate_label = _text(row.get("candidate_label"))
        if not candidate_label:
            continue
        rows.append(
            {
                "task": "seizure_frequency",
                "dataset": "gan2026",
                "clinical_subproblem": "projection",
                "surface": row.get("distribution") or row.get("split") or "validation",
                "source_row_index": int(row["source_row_index"]),
                "artifact_path": row.get("artifact_path") or path.as_posix(),
                "component_name": component,
                "component_owner": row.get("component_owner") or "",
                "projection_policy": component,
                "candidate_label": candidate_label,
                "baseline_label": _text(row.get("baseline_label")),
                "gold_label": _text(row.get("gold_label")),
                "projection_correct": row.get("purist_correct"),
                "baseline_correct": row.get("baseline_purist_correct"),
                "changed_from_baseline": bool(row.get("changed_from_deterministic")),
                "wrong_to_correct": bool(row.get("wrong_to_correct")),
                "correct_to_wrong": bool(row.get("correct_to_wrong")),
                "evidence_status": row.get("evidence_status") or "not_instrumented",
                "source_id_status": row.get("source_id_status") or "not_instrumented",
                "hidden_families": row.get("hidden_families") or [],
                "failure_family": row.get("first_failure_owner") or "",
                "claim_boundary": "saved_validation_same_row_projection_replay",
            }
        )
    return rows


def _rows_from_arbitration_ablation(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in load_jsonl_rows(path):
        baseline = row["variant_results"]["baseline_v0"]
        for component, projection in row["variant_results"].items():
            if component == "oracle_gold_node":
                owner = "oracle_upper_bound"
            elif component == "baseline_v0":
                owner = "graph_projection"
            else:
                owner = "diagnostic_graph_policy"
            projection_correct = bool(projection.get("correct"))
            baseline_correct = bool(baseline.get("correct"))
            changed = projection.get("final_label") != baseline.get("final_label")
            rows.append(
                {
                    "task": "seizure_frequency",
                    "dataset": "gan2026",
                    "clinical_subproblem": "projection",
                    "surface": "validation_hard_slice_projection_arbitration",
                    "source_row_index": int(row["source_row_index"]),
                    "artifact_path": path.as_posix(),
                    "component_name": component,
                    "component_owner": owner,
                    "projection_policy": projection.get("projection_policy") or component,
                    "candidate_label": _text(projection.get("final_label")),
                    "baseline_label": _text(baseline.get("final_label")),
                    "gold_label": _text(row.get("gold_normalized_label")),
                    "projection_correct": projection_correct,
                    "baseline_correct": baseline_correct,
                    "changed_from_baseline": changed,
                    "wrong_to_correct": bool(
                        changed and not baseline_correct and projection_correct
                    ),
                    "correct_to_wrong": bool(
                        changed and baseline_correct and not projection_correct
                    ),
                    "evidence_status": "exact" if _text(projection.get("evidence")) else "missing",
                    "source_id_status": (
                        "valid" if projection.get("selected_node_ids") else "not_instrumented"
                    ),
                    "hidden_families": [],
                    "failure_family": row.get("failure_family") or "",
                    "claim_boundary": "diagnostic_representable_graph_projection_replay",
                }
            )
    return rows


def _rows_from_duration_ablation(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in load_jsonl_rows(path):
        baseline = row["baseline_projection"]
        projection = row["month_bucket_projection"]
        baseline_correct = bool(row.get("baseline_correct"))
        projection_correct = bool(row.get("month_bucket_correct"))
        changed = bool(row.get("label_changed"))
        rows.append(
            {
                "task": "seizure_frequency",
                "dataset": "gan2026",
                "clinical_subproblem": "projection",
                "surface": row.get("surface") or "duration_projection_ablation",
                "source_row_index": int(row["source_row_index"]),
                "artifact_path": path.as_posix(),
                "component_name": "graph_gated_month_bucket_duration",
                "component_owner": "diagnostic_graph_policy",
                "projection_policy": projection.get("projection_policy")
                or "graph_gated_month_bucket_duration",
                "candidate_label": _text(projection.get("final_label")),
                "baseline_label": _text(baseline.get("final_label")),
                "gold_label": _text(row.get("gold_normalized_label")),
                "projection_correct": projection_correct,
                "baseline_correct": baseline_correct,
                "changed_from_baseline": changed,
                "wrong_to_correct": bool(changed and not baseline_correct and projection_correct),
                "correct_to_wrong": bool(changed and baseline_correct and not projection_correct),
                "evidence_status": (
                    "exact" if row.get("selected_evidence_valid") is True else "not_judged"
                ),
                "source_id_status": (
                    "valid"
                    if (projection.get("selected_node_ids") or [])
                    else "not_instrumented"
                ),
                "hidden_families": row.get("regression_tags") or [],
                "failure_family": "seizure_free_duration",
                "claim_boundary": "diagnostic_duration_projection_replay",
            }
        )
    return rows


def _summary_for_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    judged = [row for row in rows if row.get("projection_correct") is not None]
    correct = [row for row in judged if row.get("projection_correct") is True]
    exact = [row for row in rows if row.get("evidence_status") == "exact"]
    source_judged = [row for row in rows if row.get("source_id_status") != "not_instrumented"]
    source_valid = [row for row in source_judged if row.get("source_id_status") == "valid"]
    return {
        "rows": len(rows),
        "projection_judged_rows": len(judged),
        "projection_correct_rows": len(correct),
        "projection_correct_rate": _rate(len(correct), len(judged)),
        "changed_from_baseline": sum(1 for row in rows if row.get("changed_from_baseline")),
        "wrong_to_correct": sum(1 for row in rows if row.get("wrong_to_correct")),
        "correct_to_wrong": sum(1 for row in rows if row.get("correct_to_wrong")),
        "exact_evidence_rows": len(exact),
        "exact_evidence_rate": _rate(len(exact), len(rows)),
        "source_id_judged_rows": len(source_judged),
        "source_id_valid_rows": len(source_valid),
        "source_id_valid_rate": _rate(len(source_valid), len(source_judged)),
    }


def _text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-matrix", type=Path, default=DEFAULT_EVIDENCE_MATRIX_PATH)
    parser.add_argument("--arbitration", type=Path, default=DEFAULT_ARBITRATION_PATH)
    parser.add_argument("--duration", type=Path, default=DEFAULT_DURATION_PATH)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    rows, metadata = build_projection_decision_matrix(
        evidence_matrix_path=args.evidence_matrix,
        arbitration_path=args.arbitration,
        duration_path=args.duration,
    )
    write_matrix_jsonl(rows, args.jsonl)
    write_matrix_report(rows, metadata, args.report, jsonl_path=args.jsonl)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
