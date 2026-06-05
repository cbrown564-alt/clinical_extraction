"""Build the H2/H4 validation component-stress hard/control panel."""

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

POLICY_NAME = "gan2026_h2_h4_validation_component_stress_panel_v0"
DEFAULT_MATRIX_PATH = Path(
    "experiments/gan2026_validation_test_gap_matrix_v0_validation750_2026-06-05.jsonl"
)
DEFAULT_SELECTION_PATH = Path(
    "experiments/gan2026_validation_test_gap_hypothesis_selection_v0_2026-06-05.json"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.md"
)

HARD_ROW_LIMIT_PER_STRATUM = 12
CONTROL_RATIO = 1


def build_component_stress_panel_rows(
    matrix_rows: Sequence[Mapping[str, Any]],
    *,
    hard_limit_per_stratum: int = HARD_ROW_LIMIT_PER_STRATUM,
    control_ratio: int = CONTROL_RATIO,
) -> list[dict[str, Any]]:
    """Select validation hard rows and deterministic-correct controls."""

    final_rows = [
        row
        for row in matrix_rows
        if row.get("score_layer") == "final_policy"
        and row.get("split") == "validation"
        and row.get("distribution") == "validation750"
    ]
    hard_rows = _limit_by_stratum(
        [row for row in final_rows if row.get("purist_correct") is not True],
        limit=hard_limit_per_stratum,
    )
    control_pool = [
        row
        for row in final_rows
        if row.get("purist_correct") is True
        and row.get("baseline_purist_correct") is True
        and row.get("baseline_to_layer_transition") == "C_to_C"
    ]
    controls = _matched_controls(
        hard_rows,
        control_pool,
        ratio=control_ratio,
    )

    panel_rows = [
        _panel_row(row, panel_role="hard", match_quality="target_failure")
        for row in hard_rows
    ]
    panel_rows.extend(
        _panel_row(row, panel_role="control", match_quality=quality)
        for row, quality in controls
    )
    panel_rows.sort(
        key=lambda row: (
            row["panel_role"],
            row["primary_hidden_family"],
            row["component_owner"],
            row["clinical_subproblem"],
            row["source_row_index"],
        )
    )
    return panel_rows


def summarize_component_stress_panel_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    selection: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Summarize the selected H2/H4 panel and H6 transfer-control context."""

    hard_rows = [row for row in rows if row.get("panel_role") == "hard"]
    control_rows = [row for row in rows if row.get("panel_role") == "control"]
    by_role = Counter(str(row.get("panel_role")) for row in rows)
    by_family = Counter(str(row.get("primary_hidden_family")) for row in rows)
    by_owner = Counter(str(row.get("component_owner")) for row in rows)
    by_subproblem = Counter(str(row.get("clinical_subproblem")) for row in rows)
    by_transition = Counter(str(row.get("baseline_transition")) for row in rows)
    by_match_quality = Counter(str(row.get("match_quality")) for row in control_rows)

    selected_hypotheses = list((selection or {}).get("selected_hypotheses", []))
    selected_ids = [
        item.get("hypothesis_id")
        for item in selected_hypotheses
        if item.get("hypothesis_id") in {"H2", "H4", "H6"}
    ]
    if not selected_ids:
        selected_ids = ["H2", "H4", "H6"]

    return {
        "artifact_kind": "gan2026_h2_h4_validation_component_stress_panel_summary",
        "policy_name": POLICY_NAME,
        "split_manifest": _first_nonempty(row.get("split_manifest") for row in rows),
        "hypothesis_ids": selected_ids,
        "source_matrix_artifact": str(DEFAULT_MATRIX_PATH),
        "source_hypothesis_selection_artifact": str(DEFAULT_SELECTION_PATH),
        "row_count": len(rows),
        "hard_rows": len(hard_rows),
        "control_rows": len(control_rows),
        "role_counts": dict(sorted(by_role.items())),
        "family_counts": dict(sorted(by_family.items())),
        "component_owner_counts": dict(sorted(by_owner.items())),
        "clinical_subproblem_counts": dict(sorted(by_subproblem.items())),
        "baseline_transition_counts": dict(sorted(by_transition.items())),
        "control_match_quality_counts": dict(sorted(by_match_quality.items())),
        "hard_exact_evidence_rows": sum(
            row.get("evidence_exact") is True for row in hard_rows
        ),
        "hard_valid_source_id_rows": sum(
            row.get("source_ids_valid") is True for row in hard_rows
        ),
        "hard_nonprediction_rows": sum(
            row.get("baseline_transition", "").endswith(("abstain", "review"))
            for row in hard_rows
        ),
        "locked_test_row_level_artifacts_used": 0,
        "claim_boundary": (
            "Validation-development H2/H4 component-stress design panel. It uses "
            "validation row-level gap-matrix rows only, uses H6 selective-action "
            "as a no-regression transfer-control context, and does not inspect "
            "locked-test row-level failures."
        ),
        "decision": (
            "ready_for_component_stress_ablation"
            if hard_rows and control_rows
            else "panel_contract_failed"
        ),
        "recommended_next_step": (
            "Run component-stress ablations on this panel before designing another "
            "prediction-bearing architecture: preserve exact evidence/source-id "
            "rates, report W->C and C->W within owner/family strata, and treat "
            "deterministic-correct controls as the H6 no-regression arm."
        ),
    }


def materialize_component_stress_panel(
    *,
    matrix_path: Path = DEFAULT_MATRIX_PATH,
    selection_path: Path = DEFAULT_SELECTION_PATH,
    output_jsonl_path: Path = DEFAULT_JSONL_PATH,
    output_json_path: Path = DEFAULT_JSON_PATH,
    output_report_path: Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    matrix_rows = load_jsonl_rows(matrix_path)
    selection = _read_json(selection_path)
    rows = build_component_stress_panel_rows(matrix_rows)
    summary = summarize_component_stress_panel_rows(rows, selection=selection)
    summary = {
        **summary,
        "source_matrix_artifact": str(matrix_path),
        "source_hypothesis_selection_artifact": str(selection_path),
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
        "# Gan 2026 H2/H4 Validation Component-Stress Panel v0",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| rows | {summary['row_count']} |",
        f"| hard rows | {summary['hard_rows']} |",
        f"| control rows | {summary['control_rows']} |",
        f"| hard exact-evidence rows | {summary['hard_exact_evidence_rows']} |",
        f"| hard valid-source-id rows | {summary['hard_valid_source_id_rows']} |",
        f"| hard nonprediction rows | {summary['hard_nonprediction_rows']} |",
        "| locked-test row-level artifacts used | "
        f"{summary['locked_test_row_level_artifacts_used']} |",
        "",
        "## Component Owners",
        "",
    ]
    lines.extend(_counter_table(summary["component_owner_counts"], "Owner"))
    lines.extend(["", "## Clinical Subproblems", ""])
    lines.extend(_counter_table(summary["clinical_subproblem_counts"], "Subproblem"))
    lines.extend(["", "## Hidden Families", ""])
    lines.extend(_counter_table(summary["family_counts"], "Family"))
    lines.extend(["", "## Control Match Quality", ""])
    lines.extend(_counter_table(summary["control_match_quality_counts"], "Match quality"))
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Panel JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source matrix: `{summary['source_matrix_artifact']}`",
            f"- Hypothesis selection: `{summary['source_hypothesis_selection_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _limit_by_stratum(
    rows: Sequence[Mapping[str, Any]],
    *,
    limit: int,
) -> list[Mapping[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_stratum_key(row)].append(row)
    selected: list[Mapping[str, Any]] = []
    for key in sorted(grouped):
        selected.extend(
            sorted(grouped[key], key=lambda row: int(row["source_row_index"]))[:limit]
        )
    return selected


def _matched_controls(
    hard_rows: Sequence[Mapping[str, Any]],
    control_pool: Sequence[Mapping[str, Any]],
    *,
    ratio: int,
) -> list[tuple[Mapping[str, Any], str]]:
    selected: list[tuple[Mapping[str, Any], str]] = []
    used: set[int] = set()
    by_stratum = Counter(_stratum_key(row) for row in hard_rows)
    for stratum, hard_count in sorted(by_stratum.items()):
        wanted = hard_count * ratio
        matches = _candidate_controls(control_pool, stratum, used=used)
        for row, quality in matches[:wanted]:
            used.add(int(row["source_row_index"]))
            selected.append((row, quality))
    return selected


def _candidate_controls(
    control_pool: Sequence[Mapping[str, Any]],
    stratum: tuple[str, str, str, str],
    *,
    used: set[int],
) -> list[tuple[Mapping[str, Any], str]]:
    owner, subproblem, family, transition = stratum
    candidates: list[tuple[tuple[int, int], Mapping[str, Any], str]] = []
    for row in control_pool:
        source_row_index = int(row["source_row_index"])
        if source_row_index in used:
            continue
        row_owner, row_subproblem, row_family, _ = _stratum_key(row)
        if row_owner != owner:
            continue
        quality = "owner_only"
        rank = 3
        if row_subproblem == subproblem and row_family == family:
            quality = "owner_subproblem_family"
            rank = 0
        elif row_subproblem == subproblem and row_family == "none":
            quality = "owner_subproblem_untagged"
            rank = 1
        elif row_subproblem == subproblem:
            quality = "owner_subproblem_other_family"
            rank = 2
        candidates.append(((rank, source_row_index), row, quality))
    candidates.sort(key=lambda item: item[0])
    return [(row, quality) for _, row, quality in candidates]


def _panel_row(
    row: Mapping[str, Any],
    *,
    panel_role: str,
    match_quality: str,
) -> dict[str, Any]:
    family = _primary_family(row)
    transition = str(row.get("baseline_to_layer_transition") or "")
    return {
        "artifact_kind": "gan2026_h2_h4_validation_component_stress_panel_row",
        "policy_name": POLICY_NAME,
        "source_row_index": int(row["source_row_index"]),
        "split": row.get("split"),
        "split_manifest": row.get("split_manifest"),
        "distribution": row.get("distribution"),
        "panel_role": panel_role,
        "match_quality": match_quality,
        "hypothesis_ids": ["H2", "H4"] if panel_role == "hard" else ["H2", "H4", "H6"],
        "component_owner": row.get("component_owner"),
        "clinical_subproblem": row.get("clinical_subproblem"),
        "primary_hidden_family": family,
        "hidden_families": row.get("hidden_families", []),
        "baseline_transition": transition,
        "stress_target": _stress_target(row, panel_role=panel_role),
        "expected_panel_use": _expected_panel_use(panel_role, transition),
        "gold_label": row.get("gold_label"),
        "baseline_label": row.get("baseline_label"),
        "final_label": row.get("final_label"),
        "purist_correct": row.get("purist_correct"),
        "baseline_purist_correct": row.get("baseline_purist_correct"),
        "final_purist_correct": row.get("final_purist_correct"),
        "evidence_exact": row.get("evidence_exact"),
        "source_ids_valid": row.get("source_ids_valid"),
        "parse_valid": row.get("parse_valid"),
        "schema_valid": row.get("schema_valid"),
        "first_failure_owner": row.get("first_failure_owner"),
        "first_failure_reason": row.get("first_failure_reason"),
        "claim_boundary": "validation_development_only_no_holdout_row_level_use",
        "source_note_text": None,
    }


def _stress_target(row: Mapping[str, Any], *, panel_role: str) -> str:
    if panel_role == "control":
        return "deterministic_correct_no_regression_control"
    transition = str(row.get("baseline_to_layer_transition") or "")
    if transition.endswith("abstain") or transition.endswith("review"):
        return "action_policy_nonprediction"
    if row.get("evidence_exact") is True and row.get("source_ids_valid") is True:
        return "exact_evidence_projection_or_rendering_failure"
    return "component_owner_residual_failure"


def _expected_panel_use(panel_role: str, transition: str) -> str:
    if panel_role == "control":
        return "candidate_must_preserve_correct_label"
    if transition.endswith("abstain") or transition.endswith("review"):
        return "candidate_must_choose_predict_or_preserve_review_with_reason"
    return "candidate_must_repair_label_without_losing_exact_evidence"


def _stratum_key(row: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("component_owner") or ""),
        str(row.get("clinical_subproblem") or ""),
        _primary_family(row),
        str(row.get("baseline_to_layer_transition") or ""),
    )


def _primary_family(row: Mapping[str, Any]) -> str:
    families = [str(item) for item in row.get("hidden_families", []) if item]
    return families[0] if families else "none"


def _counter_table(counts: Mapping[str, int], label: str) -> list[str]:
    if not counts:
        return ["No rows available."]
    lines = [f"| {label} | Rows |", "| --- | ---: |"]
    for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{_md(name)}` | {count} |")
    return lines


def _first_nonempty(values: Sequence[Any] | Any) -> str:
    for value in values:
        if value:
            return str(value)
    return ""


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX_PATH)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION_PATH)
    parser.add_argument("--jsonl-output", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)
    materialize_component_stress_panel(
        matrix_path=args.matrix,
        selection_path=args.selection,
        output_jsonl_path=args.jsonl_output,
        output_json_path=args.json_output,
        output_report_path=args.report_output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
