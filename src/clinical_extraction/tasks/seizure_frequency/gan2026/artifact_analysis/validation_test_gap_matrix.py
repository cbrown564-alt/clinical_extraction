"""Build validation-only score-layer rows for the Gan 2026 generalisation-gap matrix."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

DEFAULT_INVENTORY_PATH = Path(
    "experiments/gan2026_validation_test_gap_artifact_inventory_2026-06-05.json"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_validation_test_gap_matrix_v0_validation750_2026-06-05.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_validation_test_gap_matrix_v0_validation750_2026-06-05.md"
)


def build_gap_matrix(
    inventory: Mapping[str, Any],
    *,
    root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build row-level validation matrix rows from saved, row-reviewable artifacts."""

    rows: list[dict[str, Any]] = []
    skipped_artifacts: list[dict[str, str]] = []
    for artifact in inventory.get("artifacts", []):
        distribution = str(artifact.get("distribution", ""))
        if distribution.startswith("locked_test"):
            skipped_artifacts.append(
                {
                    "artifact_id": str(artifact.get("artifact_id", "")),
                    "reason": "locked_test_row_level_blocked",
                }
            )
            continue
        if artifact.get("allowed_inspection") != "validation_row_level_allowed":
            skipped_artifacts.append(
                {
                    "artifact_id": str(artifact.get("artifact_id", "")),
                    "reason": "not_validation_row_level_allowed",
                }
            )
            continue
        if artifact.get("artifact_role") != "component_matrix_seed":
            skipped_artifacts.append(
                {
                    "artifact_id": str(artifact.get("artifact_id", "")),
                    "reason": "unsupported_row_source_role",
                }
            )
            continue
        csv_path = _first_existing_csv_path(artifact.get("paths", []), root=root)
        if csv_path is None:
            skipped_artifacts.append(
                {
                    "artifact_id": str(artifact.get("artifact_id", "")),
                    "reason": "no_csv_row_source",
                }
            )
            continue
        rows.extend(_rows_from_component_csv(csv_path, artifact, inventory=inventory))

    metadata = _metadata(rows, inventory=inventory, skipped_artifacts=skipped_artifacts)
    return rows, metadata


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n")


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
) -> None:
    owner_counts = Counter(str(row.get("component_owner", "")) for row in rows)
    layer_counts = Counter(str(row.get("score_layer", "")) for row in rows)
    transition_counts = Counter(
        str(row.get("baseline_to_layer_transition", ""))
        for row in rows
        if row.get("score_layer") == "final_policy"
    )
    family_counts = Counter(
        family for row in rows for family in row.get("hidden_families", []) if family
    )

    lines = [
        "# Gan 2026 Validation-Test Gap Matrix v0",
        "",
        f"Split manifest: `{metadata.get('split_manifest', '')}`",
        "",
        "This artifact is validation row-level only. Locked-test row-level artifacts are "
        "skipped by construction; locked-test evidence remains aggregate-only unless a "
        "future frozen slice protocol authorizes more.",
        "",
        "## Summary",
        "",
        f"- Matrix rows: {metadata.get('row_count', 0)}",
        f"- Unique validation source rows: {metadata.get('unique_source_rows', 0)}",
        f"- Source artifacts used: {metadata.get('source_artifact_count', 0)}",
        "- Locked-test row-level artifacts used: "
        f"{metadata.get('locked_test_row_level_artifacts_used', 0)}",
        "",
        "## Score Layers",
        "",
    ]
    lines.extend(_counter_table(layer_counts, "Score layer", "Rows"))
    lines.extend(["", "## Component Owners", ""])
    lines.extend(_counter_table(owner_counts, "Component owner", "Rows"))
    lines.extend(["", "## Final-Policy Transitions", ""])
    lines.extend(_counter_table(transition_counts, "Transition", "Rows"))
    lines.extend(["", "## Hidden Families", ""])
    lines.extend(_counter_table(family_counts, "Hidden family", "Layer rows"))
    lines.extend(["", "## Skipped Artifacts", ""])
    if metadata.get("skipped_artifacts"):
        lines.extend(["| Artifact | Reason |", "| --- | --- |"])
        for item in metadata["skipped_artifacts"]:
            lines.append(f"| {_md(item.get('artifact_id'))} | {_md(item.get('reason'))} |")
    else:
        lines.append("No artifacts were skipped.")
    path.write_text("\n".join(lines) + "\n")


def _rows_from_component_csv(
    csv_path: Path,
    artifact: Mapping[str, Any],
    *,
    inventory: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with csv_path.open(newline="") as handle:
        for source in csv.DictReader(handle):
            rows.append(
                _matrix_row(
                    source,
                    artifact,
                    inventory=inventory,
                    score_layer="deterministic_comparator",
                )
            )
            rows.append(
                _matrix_row(
                    source,
                    artifact,
                    inventory=inventory,
                    score_layer="final_policy",
                )
            )
            if source.get("final_action") in {"abstain", "human_review", "monitor"}:
                rows.append(
                    _matrix_row(
                        source,
                        artifact,
                        inventory=inventory,
                        score_layer="abstain_review_monitor",
                    )
                )
    return rows


def _matrix_row(
    source: Mapping[str, str],
    artifact: Mapping[str, Any],
    *,
    inventory: Mapping[str, Any],
    score_layer: str,
) -> dict[str, Any]:
    final_transition = source.get("comparator_transition", "")
    is_final = score_layer == "final_policy"
    is_monitor = score_layer == "abstain_review_monitor"
    baseline_correct = _bool(source.get("deterministic_comparator_purist_correct"))
    final_correct = _bool(source.get("final_purist_correct"))

    layer_label = source.get("deterministic_comparator_label", "")
    layer_correct = baseline_correct
    if is_final:
        layer_label = source.get("prediction_label", "")
        layer_correct = final_correct
    elif is_monitor:
        layer_label = source.get("final_action", "")
        layer_correct = None

    return {
        "artifact_kind": "gan2026_validation_test_gap_matrix_v0",
        "source_artifact_id": artifact.get("artifact_id", ""),
        "candidate_name": artifact.get("candidate_name", ""),
        "candidate_version": source.get("candidate_version") or artifact.get("candidate_name", ""),
        "pipeline_family": artifact.get("pipeline_family", ""),
        "source_row_index": _int(source.get("source_row_index")),
        "split": source.get("split") or "validation",
        "split_manifest": source.get("split_manifest") or inventory.get("split_manifest", ""),
        "distribution": artifact.get("distribution", ""),
        "score_layer": score_layer,
        "clinical_subproblem": _clinical_subproblem(source, score_layer=score_layer),
        "component_owner": _component_owner(source, score_layer=score_layer),
        "inspection_policy": artifact.get("allowed_inspection", ""),
        "hypothesis_ids": artifact.get("hypothesis_ids", []),
        "hidden_families": _split_semicolon(source.get("hidden_families", "")),
        "gold_label": source.get("gold_label", ""),
        "baseline_label": source.get("deterministic_comparator_label", ""),
        "layer_label": layer_label,
        "final_label": source.get("prediction_label", ""),
        "purist_correct": layer_correct,
        "baseline_purist_correct": baseline_correct,
        "final_purist_correct": final_correct,
        "changed_from_baseline": (
            final_transition not in {"", "C_to_C", "W_to_W"} if is_final else False
        ),
        "wrong_to_correct": final_transition == "W_to_C" if is_final else False,
        "correct_to_wrong": final_transition == "C_to_W" if is_final else False,
        "net_gain": _net_gain(final_transition) if is_final else 0,
        "baseline_to_layer_transition": final_transition if is_final else "",
        "evidence_exact": _bool(source.get("selected_evidence_exact")),
        "source_ids_valid": _bool(source.get("selected_source_ids_exist")),
        "parse_valid": _count_is_zero(source.get("parse_issue_count")),
        "schema_valid": _count_is_zero(source.get("schema_issue_count")),
        "evidence_issue_count": _int(source.get("evidence_issue_count")),
        "first_failure_owner": source.get("first_failure_owner", ""),
        "first_failure_reason": source.get("first_failure_reason", ""),
        "abstain_review_monitor_action": source.get("final_action", "") if is_monitor else "",
        "abstain_review_monitor_reason": source.get("router_reason", "") if is_monitor else "",
    }


def _metadata(
    rows: Sequence[Mapping[str, Any]],
    *,
    inventory: Mapping[str, Any],
    skipped_artifacts: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    return {
        "artifact_kind": "gan2026_validation_test_gap_matrix_v0_metadata",
        "split_manifest": inventory.get("split_manifest", ""),
        "protocol": inventory.get("protocol", ""),
        "row_count": len(rows),
        "unique_source_rows": len({row.get("source_row_index") for row in rows}),
        "source_artifact_count": len({row.get("source_artifact_id") for row in rows}),
        "locked_test_row_level_artifacts_used": len(
            {
                row.get("source_artifact_id")
                for row in rows
                if str(row.get("distribution", "")).startswith("locked_test")
            }
        ),
        "skipped_artifacts": list(skipped_artifacts),
    }


def _component_owner(source: Mapping[str, str], *, score_layer: str) -> str:
    if score_layer == "deterministic_comparator":
        return "deterministic_rule"
    if score_layer == "abstain_review_monitor":
        return "safety_floor"
    if _bool(source.get("safety_floor_changed")):
        return "safety_floor"
    if source.get("prediction_bearing") == "True":
        return "deterministic_adapter"
    return "safety_floor"


def _clinical_subproblem(source: Mapping[str, str], *, score_layer: str) -> str:
    if score_layer == "deterministic_comparator":
        return "candidate_generation"
    if score_layer == "abstain_review_monitor":
        return "abstain_review_policy"
    reason = source.get("router_reason", "")
    if "cluster" in reason or "diary" in reason:
        return "cluster_diary_aggregation"
    if "frequency" in reason:
        return "adapter_rendering"
    return "final_policy"


def _first_existing_csv_path(paths: Sequence[str], *, root: Path) -> Path | None:
    for raw_path in paths:
        path = root / raw_path
        if path.suffix == ".csv" and path.exists():
            return path
    return None


def _split_semicolon(value: str) -> list[str]:
    delimiter = ";" if ";" in value else "|"
    return [part for part in value.split(delimiter) if part]


def _bool(value: str | None) -> bool | None:
    if value == "True":
        return True
    if value == "False":
        return False
    return None


def _int(value: str | None) -> int | None:
    if value in {None, ""}:
        return None
    return int(value)


def _count_is_zero(value: str | None) -> bool | None:
    parsed = _int(value)
    if parsed is None:
        return None
    return parsed == 0


def _net_gain(transition: str) -> int:
    if transition == "W_to_C":
        return 1
    if transition == "C_to_W":
        return -1
    return 0


def _counter_table(counter: Counter[str], label: str, value_label: str) -> list[str]:
    if not counter:
        return ["No rows available."]
    lines = [f"| {label} | {value_label} |", "| --- | ---: |"]
    for key, value in counter.most_common():
        lines.append(f"| {_md(key)} | {value} |")
    return lines


def _md(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY_PATH)
    parser.add_argument("--jsonl-output", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    inventory = json.loads(args.inventory.read_text())
    rows, metadata = build_gap_matrix(inventory, root=Path.cwd())
    write_jsonl(rows, args.jsonl_output)
    write_report(rows, metadata, args.report_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
