"""Run no-call component-stress ablations over the H2/H4 validation panel."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_h2_h4_validation_component_stress_ablation_v0"
DEFAULT_PANEL_JSONL_PATH = Path(
    "experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_h2_h4_validation_component_stress_ablation_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_h2_h4_validation_component_stress_ablation_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_h2_h4_validation_component_stress_ablation_v0_2026-06-05.md"
)

CONDITIONS = (
    "deterministic_comparator",
    "staged_final_policy",
    "staged_prediction_bearing_only",
)


def build_component_stress_ablation_rows(
    panel_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Expand panel rows into no-call ablation condition rows."""

    rows: list[dict[str, Any]] = []
    for panel_row in panel_rows:
        rows.append(_condition_row(panel_row, condition="deterministic_comparator"))
        rows.append(_condition_row(panel_row, condition="staged_final_policy"))
        if panel_row.get("final_label"):
            rows.append(_condition_row(panel_row, condition="staged_prediction_bearing_only"))
    rows.sort(
        key=lambda row: (
            row["condition"],
            row["panel_role"],
            row["primary_hidden_family"],
            row["source_row_index"],
        )
    )
    return rows


def summarize_component_stress_ablation_rows(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize no-call ablation behavior by condition and panel stratum."""

    by_condition = {
        condition: _condition_summary(condition, _filter(rows, condition=condition))
        for condition in CONDITIONS
    }
    baseline_rows = _filter(rows, condition="deterministic_comparator")
    comparisons = [
        _comparison_summary(
            "deterministic_comparator",
            condition,
            baseline_rows,
            _filter(rows, condition=condition),
        )
        for condition in CONDITIONS
        if condition != "deterministic_comparator"
    ]
    strata = _stratified_summaries(rows)
    staged_rows = _filter(rows, condition="staged_final_policy")
    return {
        "artifact_kind": "gan2026_h2_h4_validation_component_stress_ablation_summary",
        "policy_name": POLICY_NAME,
        "split_manifest": _first_nonempty(row.get("split_manifest") for row in rows),
        "hypothesis_ids": ["H2", "H4", "H6"],
        "conditions": by_condition,
        "comparisons": comparisons,
        "stratified_staged_final_policy": strata,
        "h6_control_summary": _h6_control_summary(staged_rows),
        "locked_test_row_level_artifacts_used": 0,
        "claim_boundary": (
            "Validation-development no-call component-stress ablation over the "
            "H2/H4 panel. It reuses saved validation panel labels and component "
            "metadata only; locked-test row-level failures remain uninspected."
        ),
        "decision": _decision(comparisons, staged_rows),
        "recommended_next_step": _recommended_next_step(comparisons, staged_rows),
    }


def materialize_component_stress_ablation(
    *,
    panel_jsonl_path: Path = DEFAULT_PANEL_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    panel_rows = load_jsonl_rows(panel_jsonl_path)
    rows = build_component_stress_ablation_rows(panel_rows)
    summary = summarize_component_stress_ablation_rows(rows)
    summary = {
        **summary,
        "source_panel_artifact": str(panel_jsonl_path),
        "jsonl_artifact": str(output_jsonl_path),
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
    }
    write_jsonl_rows(rows, output_jsonl_path)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(summary, output_report_path)
    return summary


def write_report(summary: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 H2/H4 Validation Component-Stress Ablation v0",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Conditions",
        "",
        (
            "| Condition | Rows | Scorable | Correct | Nonprediction | "
            "Exact evidence | Valid source ids |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition, item in summary["conditions"].items():
        lines.append(
            f"| `{condition}` | {item['rows']} | {item['scorable_rows']} | "
            f"{item['correct_rows']} | {item['nonprediction_rows']} | "
            f"{item['exact_evidence_rows']} | {item['valid_source_id_rows']} |"
        )
    lines.extend(
        [
            "",
            "## Comparisons",
            "",
            "| Candidate | Overlap | Changed | W->C | C->W | C->nonprediction | W->nonprediction |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in summary["comparisons"]:
        lines.append(
            f"| `{item['candidate']}` | {item['overlap']} | {item['changed_rows']} | "
            f"{item['wrong_to_correct']} | {item['correct_to_wrong']} | "
            f"{item['correct_to_nonprediction']} | {item['wrong_to_nonprediction']} |"
        )
    h6 = summary["h6_control_summary"]
    lines.extend(
        [
            "",
            "## H6 Control Arm",
            "",
            "| Controls | Preserved | Regressed | Nonprediction regressions |",
            "| ---: | ---: | ---: | ---: |",
            f"| {h6['control_rows']} | {h6['preserved_correct_rows']} | "
            f"{h6['regression_rows']} | {h6['nonprediction_regression_rows']} |",
            "",
            "## Staged Final Policy By Stratum",
            "",
            (
                "| Role | Owner | Family | Rows | Correct | Nonprediction | W->C | "
                "C->W | C->nonprediction |"
            ),
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in summary["stratified_staged_final_policy"]:
        lines.append(
            f"| `{item['panel_role']}` | `{item['component_owner']}` | "
            f"`{item['primary_hidden_family']}` | {item['rows']} | "
            f"{item['correct_rows']} | {item['nonprediction_rows']} | "
            f"{item['wrong_to_correct']} | {item['correct_to_wrong']} | "
            f"{item['correct_to_nonprediction']} |"
        )
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Ablation JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source panel: `{summary['source_panel_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _condition_row(
    panel_row: Mapping[str, Any],
    *,
    condition: str,
) -> dict[str, Any]:
    if condition == "deterministic_comparator":
        label = panel_row.get("baseline_label")
        correct = panel_row.get("baseline_purist_correct")
        action = "predict"
        evidence_exact = panel_row.get("evidence_exact")
        source_ids_valid = panel_row.get("source_ids_valid")
    else:
        label = panel_row.get("final_label") or None
        correct = panel_row.get("final_purist_correct")
        action = "predict" if label else "nonprediction"
        evidence_exact = panel_row.get("evidence_exact") if label else None
        source_ids_valid = panel_row.get("source_ids_valid") if label else None

    return {
        "artifact_kind": "gan2026_h2_h4_validation_component_stress_ablation_row",
        "policy_name": POLICY_NAME,
        "source_row_index": panel_row.get("source_row_index"),
        "split": panel_row.get("split"),
        "split_manifest": panel_row.get("split_manifest"),
        "condition": condition,
        "panel_role": panel_row.get("panel_role"),
        "component_owner": panel_row.get("component_owner"),
        "clinical_subproblem": panel_row.get("clinical_subproblem"),
        "primary_hidden_family": panel_row.get("primary_hidden_family"),
        "hidden_families": panel_row.get("hidden_families", []),
        "baseline_transition": panel_row.get("baseline_transition"),
        "prediction_action": action,
        "prediction_label": label,
        "gold_label": panel_row.get("gold_label"),
        "purist_correct": correct,
        "baseline_purist_correct": panel_row.get("baseline_purist_correct"),
        "final_purist_correct": panel_row.get("final_purist_correct"),
        "evidence_exact": evidence_exact,
        "source_ids_valid": source_ids_valid,
        "parse_valid": panel_row.get("parse_valid"),
        "schema_valid": panel_row.get("schema_valid"),
        "hypothesis_ids": ["H2", "H4"] if panel_row.get("panel_role") == "hard" else ["H6"],
        "claim_boundary": "validation_development_only_no_holdout_row_level_use",
    }


def _condition_summary(
    condition: str,
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "condition": condition,
        "rows": len(rows),
        "scorable_rows": sum(row.get("prediction_action") == "predict" for row in rows),
        "correct_rows": sum(row.get("purist_correct") is True for row in rows),
        "incorrect_rows": sum(row.get("purist_correct") is False for row in rows),
        "nonprediction_rows": sum(row.get("prediction_action") == "nonprediction" for row in rows),
        "exact_evidence_rows": sum(row.get("evidence_exact") is True for row in rows),
        "valid_source_id_rows": sum(row.get("source_ids_valid") is True for row in rows),
    }


def _comparison_summary(
    baseline_name: str,
    candidate_name: str,
    baseline_rows: Sequence[Mapping[str, Any]],
    candidate_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    baseline_by_index = {row["source_row_index"]: row for row in baseline_rows}
    counts: Counter[str] = Counter()
    for row in candidate_rows:
        baseline = baseline_by_index.get(row["source_row_index"])
        if baseline is None:
            continue
        counts["overlap"] += 1
        if baseline.get("prediction_label") != row.get("prediction_label"):
            counts["changed_rows"] += 1
        baseline_correct = baseline.get("purist_correct")
        candidate_correct = row.get("purist_correct")
        candidate_nonprediction = row.get("prediction_action") == "nonprediction"
        if baseline_correct is False and candidate_correct is True:
            counts["wrong_to_correct"] += 1
        if baseline_correct is True and candidate_correct is False:
            counts["correct_to_wrong"] += 1
        if baseline_correct is True and candidate_nonprediction:
            counts["correct_to_nonprediction"] += 1
        if baseline_correct is False and candidate_nonprediction:
            counts["wrong_to_nonprediction"] += 1
    return {
        "baseline": baseline_name,
        "candidate": candidate_name,
        "overlap": counts["overlap"],
        "changed_rows": counts["changed_rows"],
        "wrong_to_correct": counts["wrong_to_correct"],
        "correct_to_wrong": counts["correct_to_wrong"],
        "correct_to_nonprediction": counts["correct_to_nonprediction"],
        "wrong_to_nonprediction": counts["wrong_to_nonprediction"],
    }


def _stratified_summaries(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    staged_rows = _filter(rows, condition="staged_final_policy")
    grouped: dict[tuple[str, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in staged_rows:
        key = (
            str(row.get("panel_role")),
            str(row.get("component_owner")),
            str(row.get("primary_hidden_family")),
        )
        grouped[key].append(row)
    summaries = []
    for (role, owner, family), group_rows in sorted(grouped.items()):
        summaries.append(
            {
                "panel_role": role,
                "component_owner": owner,
                "primary_hidden_family": family,
                **_condition_summary("staged_final_policy", group_rows),
                "wrong_to_correct": sum(
                    row.get("baseline_purist_correct") is False
                    and row.get("purist_correct") is True
                    for row in group_rows
                ),
                "correct_to_wrong": sum(
                    row.get("baseline_purist_correct") is True
                    and row.get("purist_correct") is False
                    for row in group_rows
                ),
                "correct_to_nonprediction": sum(
                    row.get("baseline_purist_correct") is True
                    and row.get("prediction_action") == "nonprediction"
                    for row in group_rows
                ),
            }
        )
    return summaries


def _h6_control_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    controls = [row for row in rows if row.get("panel_role") == "control"]
    return {
        "control_rows": len(controls),
        "preserved_correct_rows": sum(row.get("purist_correct") is True for row in controls),
        "regression_rows": sum(row.get("purist_correct") is not True for row in controls),
        "nonprediction_regression_rows": sum(
            row.get("prediction_action") == "nonprediction" for row in controls
        ),
    }


def _decision(
    comparisons: Sequence[Mapping[str, Any]],
    staged_rows: Sequence[Mapping[str, Any]],
) -> str:
    h6 = _h6_control_summary(staged_rows)
    final_comparison = next(
        item for item in comparisons if item["candidate"] == "staged_final_policy"
    )
    if h6["regression_rows"] == 0 and final_comparison["correct_to_wrong"] == 0:
        return "diagnostic_ablation_passed_h6_controls_but_nonprediction_pressure_remains"
    return "diagnostic_ablation_failed_no_regression_control"


def _recommended_next_step(
    comparisons: Sequence[Mapping[str, Any]],
    staged_rows: Sequence[Mapping[str, Any]],
) -> str:
    final_comparison = next(
        item for item in comparisons if item["candidate"] == "staged_final_policy"
    )
    if final_comparison["correct_to_nonprediction"]:
        return (
            "Investigate action-policy nonpredictions before promoting a new "
            "architecture: the staged policy avoids C->W label regressions but "
            "routes deterministic-correct hard rows to nonprediction. Candidate "
            "changes must recover those rows without damaging H6 controls."
        )
    return (
        "Use the owner/family W->C rows as the next typed candidate-generation "
        "targets and keep the H6 controls fixed as no-regression tests."
    )


def _filter(rows: Sequence[Mapping[str, Any]], *, condition: str) -> list[Mapping[str, Any]]:
    return [row for row in rows if row.get("condition") == condition]


def _first_nonempty(values: Sequence[Any] | Any) -> str:
    for value in values:
        if value:
            return str(value)
    return ""


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    materialize_component_stress_ablation(
        panel_jsonl_path=args.panel_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
