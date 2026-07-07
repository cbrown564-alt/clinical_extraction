"""Audit gold-blinded lanes for recovering staged-policy nonpredictions."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_nonprediction_recovery_audit_v0"
DEFAULT_COMPONENT_CSV_PATH = Path(
    "experiments/"
    "gan2026_hybrid_multi_component_staged_assembly_v0_validation750_component_matrix_"
    "2026-06-04.csv"
)
DEFAULT_PANEL_JSONL_PATH = Path(
    "experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_nonprediction_recovery_audit_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_nonprediction_recovery_audit_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_nonprediction_recovery_audit_v0_2026-06-05.md"
)

NONPREDICTION_ACTIONS = {"abstain", "human_review"}
SENTINEL_LABELS = {"unknown", "no seizure frequency reference"}


def build_recovery_audit_rows(
    component_rows: Sequence[Mapping[str, Any]],
    panel_rows: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, Any]]:
    """Build candidate release rows for staged nonpredictions."""

    panel_indices = {int(row["source_row_index"]) for row in panel_rows}
    rows = []
    for row in component_rows:
        if row.get("final_action") not in NONPREDICTION_ACTIONS:
            continue
        hidden_families = _split_hidden_families(row.get("hidden_families", ""))
        release_lanes = _release_lanes(row, hidden_families)
        rows.append(
            {
                "artifact_kind": "gan2026_nonprediction_recovery_audit_row",
                "policy_name": POLICY_NAME,
                "source_row_index": _int(row["source_row_index"]),
                "split": row.get("split", "validation"),
                "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
                "surface_membership": (
                    "h2_h4_component_stress_panel"
                    if _int(row["source_row_index"]) in panel_indices
                    else "validation750_nonpanel"
                ),
                "final_action": row.get("final_action"),
                "router_reason": row.get("router_reason"),
                "hidden_families": hidden_families,
                "untagged_nonprediction": not hidden_families,
                "baseline_label": row.get("deterministic_comparator_label"),
                "baseline_label_family": _label_family(row.get("deterministic_comparator_label")),
                "gold_label": row.get("gold_label"),
                "release_lanes": release_lanes,
                "release_candidate_label": (
                    row.get("deterministic_comparator_label") if release_lanes else None
                ),
                "release_action": "release_baseline" if release_lanes else "keep_nonprediction",
                "development_accounting": {
                    "baseline_purist_correct": _bool(
                        row.get("deterministic_comparator_purist_correct")
                    ),
                    "comparator_transition": row.get("comparator_transition"),
                    "would_recover_c_to_nonprediction": str(
                        row.get("comparator_transition", "")
                    ).startswith("C_to"),
                    "would_release_wrong_baseline": str(
                        row.get("comparator_transition", "")
                    ).startswith("W_to"),
                },
                "claim_boundary": "validation_development_only_no_holdout_row_level_use",
            }
        )
    rows.sort(key=lambda item: item["source_row_index"])
    return rows


def summarize_recovery_audit_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize release-lane candidates and no-regression accounting."""

    variants = {
        "untagged_nonprediction": lambda row: bool(row["untagged_nonprediction"]),
        "sentinel_untagged_nonprediction": lambda row: bool(
            row["untagged_nonprediction"]
            and row["baseline_label_family"] in {"unknown", "no_reference"}
        ),
        "trigger_untagged_nonprediction": lambda row: bool(
            row["untagged_nonprediction"]
            and row["router_reason"] == "trigger_conditioned_frequency"
        ),
        "all_nonpredictions": lambda row: True,
    }
    variant_summaries = [
        _variant_summary(name, rows, predicate) for name, predicate in variants.items()
    ]
    selected = next(
        item for item in variant_summaries if item["variant"] == "untagged_nonprediction"
    )
    return {
        "artifact_kind": "gan2026_nonprediction_recovery_audit_summary",
        "policy_name": POLICY_NAME,
        "split_manifest": _first_nonempty(row.get("split_manifest") for row in rows),
        "row_count": len(rows),
        "action_counts": dict(Counter(str(row["final_action"]) for row in rows)),
        "reason_counts": dict(Counter(str(row["router_reason"]) for row in rows)),
        "variant_summaries": variant_summaries,
        "selected_candidate_lane": selected,
        "locked_test_row_level_artifacts_used": 0,
        "claim_boundary": (
            "Validation-development nonprediction recovery audit. Release lanes "
            "use observable validation artifact fields such as hidden-family tags, "
            "router reason, and baseline label family; correctness is development "
            "accounting only and does not authorize holdout use."
        ),
        "decision": _decision(selected),
        "recommended_next_step": _recommended_next_step(selected),
    }


def materialize_recovery_audit(
    *,
    component_csv_path: Path = DEFAULT_COMPONENT_CSV_PATH,
    panel_jsonl_path: Path = DEFAULT_PANEL_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    component_rows = _read_csv_rows(component_csv_path)
    panel_rows = load_jsonl_rows(panel_jsonl_path) if panel_jsonl_path.exists() else []
    rows = build_recovery_audit_rows(component_rows, panel_rows)
    summary = summarize_recovery_audit_rows(rows)
    summary = {
        **summary,
        "source_component_matrix": str(component_csv_path),
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
    selected = summary["selected_candidate_lane"]
    lines = [
        "# Gan 2026 Nonprediction Recovery Audit v0",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Selected Lane",
        "",
        (
            f"`{selected['variant']}` releases {selected['release_rows']} rows with "
            f"{selected['would_recover_c_to_nonprediction']} C->nonprediction "
            f"recoveries and {selected['would_release_wrong_baseline']} wrong-baseline "
            "releases by validation development accounting."
        ),
        "",
        "## Variant Summary",
        "",
        (
            "| Variant | Release rows | C->nonprediction recovered | "
            "Wrong baseline released | Panel rows |"
        ),
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for item in summary["variant_summaries"]:
        lines.append(
            f"| `{item['variant']}` | {item['release_rows']} | "
            f"{item['would_recover_c_to_nonprediction']} | "
            f"{item['would_release_wrong_baseline']} | {item['panel_release_rows']} |"
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
            f"- Audit JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Component matrix: `{summary['source_component_matrix']}`",
            f"- H2/H4 panel: `{summary['source_panel_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _variant_summary(
    name: str,
    rows: Sequence[Mapping[str, Any]],
    predicate: Callable[[Mapping[str, Any]], bool],
) -> dict[str, Any]:
    selected = [row for row in rows if predicate(row)]
    accounting = [row["development_accounting"] for row in selected]
    return {
        "variant": name,
        "release_rows": len(selected),
        "would_recover_c_to_nonprediction": sum(
            item["would_recover_c_to_nonprediction"] is True for item in accounting
        ),
        "would_release_wrong_baseline": sum(
            item["would_release_wrong_baseline"] is True for item in accounting
        ),
        "baseline_correct_rows": sum(
            item["baseline_purist_correct"] is True for item in accounting
        ),
        "panel_release_rows": sum(
            row["surface_membership"] == "h2_h4_component_stress_panel" for row in selected
        ),
        "release_lane_counts": dict(
            Counter(lane for row in selected for lane in row["release_lanes"])
        ),
    }


def _release_lanes(row: Mapping[str, Any], hidden_families: Sequence[str]) -> list[str]:
    lanes = []
    if not hidden_families:
        lanes.append("untagged_nonprediction")
    if not hidden_families and _label_family(row.get("deterministic_comparator_label")) in {
        "unknown",
        "no_reference",
    }:
        lanes.append("sentinel_untagged_nonprediction")
    if not hidden_families and row.get("router_reason") == "trigger_conditioned_frequency":
        lanes.append("trigger_untagged_nonprediction")
    return lanes


def _decision(selected: Mapping[str, Any]) -> str:
    if selected["release_rows"] and selected["would_release_wrong_baseline"] == 0:
        return "candidate_lane_passes_validation_no_regression_audit"
    return "candidate_lane_rejected_or_needs_narrowing"


def _recommended_next_step(selected: Mapping[str, Any]) -> str:
    if selected["would_release_wrong_baseline"] == 0:
        return (
            "Predeclare `untagged_nonprediction` as a validation-cycle release "
            "candidate over staged-policy nonpredictions, then test it as a "
            "candidate patch with H6 controls fixed before any holdout protocol."
        )
    return (
        "Do not release this lane. Narrow the observable criteria and rerun the "
        "validation-only recovery audit."
    )


def _read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _split_hidden_families(value: Any) -> list[str]:
    text = str(value or "")
    delimiter = "|" if "|" in text else ";"
    return [part for part in text.split(delimiter) if part]


def _label_family(label: Any) -> str:
    text = str(label or "").strip().lower()
    if text == "unknown":
        return "unknown"
    if text == "no seizure frequency reference":
        return "no_reference"
    if text.startswith("seizure free"):
        return "seizure_free"
    if "cluster" in text:
        return "cluster"
    if text:
        return "frequency"
    return "missing"


def _bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value == "True":
        return True
    if value == "False":
        return False
    return None


def _int(value: Any) -> int:
    return int(value)


def _first_nonempty(values: Sequence[Any] | Any) -> str:
    for value in values:
        if value:
            return str(value)
    return ""


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component-csv-path", type=Path, default=DEFAULT_COMPONENT_CSV_PATH)
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    materialize_recovery_audit(
        component_csv_path=args.component_csv_path,
        panel_jsonl_path=args.panel_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
