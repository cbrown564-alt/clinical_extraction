"""Month-bucket duration-selection projection ablation for Gan 2026 state graphs."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    ClinicalFrequencyStateGraph,
    GanGraphProjection,
    project_graph_to_gan,
)

from .seizure_free_duration_projection_ablation import (
    _project_duration_variant,
    _usable_seizure_free_nodes,
)

DEFAULT_TARGET_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_"
    "2026-06-02.jsonl"
)
DEFAULT_REGRESSION_JSONL_PATH = Path(
    "experiments/"
    "gan2026_clinical_frequency_state_graph_validation_hard_slices_diagnostics_"
    "2026-06-02.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_"
    "2026-06-02.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/"
    "gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_"
    "2026-06-02.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/"
    "gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_"
    "2026-06-02.md"
)
DEFAULT_V1_JSONL_PATH = Path(
    "experiments/"
    "gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_"
    "2026-06-02.jsonl"
)
DEFAULT_V1_JSON_PATH = Path(
    "experiments/"
    "gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_"
    "2026-06-02.json"
)
DEFAULT_V1_REPORT_PATH = Path(
    "experiments/"
    "gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_"
    "2026-06-02.md"
)
DEFAULT_GRAPH_GATED_JSONL_PATH = Path(
    "experiments/"
    "gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_"
    "2026-06-02.jsonl"
)
DEFAULT_GRAPH_GATED_JSON_PATH = Path(
    "experiments/"
    "gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_"
    "2026-06-02.json"
)
DEFAULT_GRAPH_GATED_REPORT_PATH = Path(
    "experiments/"
    "gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_"
    "2026-06-02.md"
)


def run_month_bucket_duration_selection_ablation(
    target_rows: Sequence[Mapping[str, Any]],
    regression_rows: Sequence[Mapping[str, Any]],
    *,
    split: str,
    split_manifest: str,
    policy_variant: str = "v0",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Replay month-bucket duration selection on target and regression surfaces."""

    target_ids = {int(row["source_row_index"]) for row in target_rows}
    rows = [
        _ablation_row(
            row,
            surface="target_duration_enriched",
            graph_key="replayed_graph",
            policy_variant=policy_variant,
        )
        for row in target_rows
    ]
    rows.extend(
        _ablation_row(
            row,
            surface="regression_validation_hard_slice",
            graph_key="graph",
            policy_variant=policy_variant,
        )
        for row in regression_rows
        if int(row["source_row_index"]) not in target_ids
    )
    rows = sorted(
        rows,
        key=lambda row: (
            0 if row["surface"] == "target_duration_enriched" else 1,
            int(row["source_row_index"]),
        ),
    )
    metadata = {
        "artifact_kind": (
            "gan2026_state_graph_projection_ablation_month_bucket_duration_selection_"
            f"{policy_variant}"
        ),
        "date": "2026-06-02",
        "pipeline_family": "hybrid_clinical_frequency_state_graph",
        "split": split,
        "split_manifest": split_manifest,
        "row_count": len(rows),
        "projection_policy": (_projection_policy_name(policy_variant)),
        "policy_variant": policy_variant,
        "claim_language": (
            "Diagnostic validation-cycle projection ablation only. The policy "
            "is evaluated separately from scorer normalization, graph-node "
            "construction, production projection policy, and holdout testing."
        ),
        "summary": _summary(rows),
    }
    return rows, metadata


def write_month_bucket_ablation_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_month_bucket_ablation_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 Month-Bucket Duration Selection Projection Ablation "
        f"{metadata.get('policy_variant', 'v0')}",
        "",
        "Diagnostic only: this is validation-cycle projection replay over saved "
        "state-graph artifacts, not a benchmark result, scorer-normalization "
        "change, or production projection-policy promotion.",
        "",
        f"- Split: `{metadata['split']}`",
        f"- Split manifest: `{metadata['split_manifest']}`",
        f"- Rows: {metadata['row_count']}",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Surface Mix",
        "",
        "| Surface | Rows | Changed labels | Changed-label rate |",
        "| --- | ---: | ---: | ---: |",
    ]
    for surface, stats in sorted(summary["surfaces"].items()):
        lines.append(
            f"| `{surface}` | {stats['rows']} | {stats['changed_labels']} | "
            f"{stats['changed_label_rate']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Target Duration Surface",
            "",
            f"- Exact duration corrections: {summary['target']['exact_duration_corrections']}",
            f"- Exact duration regressions: {summary['target']['exact_duration_regressions']}",
            f"- Selected-node evidence valid: "
            f"{summary['target']['selected_evidence_valid_rows']}/"
            f"{summary['target']['rows']}",
            "",
            "## Regression Panel",
            "",
            f"- Already-correct regressions: "
            f"{summary['regression']['already_correct_regressions']}",
            f"- Non-duration seizure-free regressions: "
            f"{summary['regression']['non_duration_seizure_free_regressions']}",
            f"- Unknown/no-reference/boundary changes: "
            f"{summary['regression']['unknown_no_reference_boundary_changes']}",
            f"- Frequency-with-seizure-free-node changes: "
            f"{summary['regression']['frequency_with_seizure_free_node_changes']}",
            f"- Selected-node evidence valid: "
            f"{summary['regression']['selected_evidence_valid_rows']}/"
            f"{summary['regression']['rows']}",
            "",
            "## Regression Family Tags",
            "",
            "| Family | Rows | Changed labels |",
            "| --- | ---: | ---: |",
        ]
    )
    for tag, stats in sorted(summary["regression_family_tags"].items()):
        lines.append(f"| `{tag}` | {stats['rows']} | {stats['changed_labels']} |")
    if summary.get("graph_gate"):
        lines.extend(
            [
                "",
                "## Graph Metadata Gate",
                "",
                f"- Blocked month-bucket replacements: {summary['graph_gate']['blocked_rows']}",
                "",
                "| Graph flag | Rows |",
                "| --- | ---: |",
            ]
        )
        for flag, stats in sorted(summary["graph_gate"].items()):
            if flag == "blocked_rows":
                continue
            lines.append(f"| `{flag}` | {stats['rows']} |")
    lines.extend(
        [
            "",
            "## Regression Tags",
            "",
            "| Tag | Rows | Changed labels |",
            "| --- | ---: | ---: |",
        ]
    )
    for tag, stats in sorted(summary["regression_tags"].items()):
        lines.append(f"| `{tag}` | {stats['rows']} | {stats['changed_labels']} |")
    lines.extend(
        [
            "",
            "## Changed Rows",
            "",
            "| Source row | Surface | Gold | Baseline | Month-bucket | Tags |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if not row["label_changed"]:
            continue
        lines.append(
            f"| {row['source_row_index']} | `{row['surface']}` | "
            f"{row['gold_normalized_label']} | "
            f"{row['baseline_projection']['final_label']} | "
            f"{row['month_bucket_projection']['final_label']} | "
            f"{', '.join(row['regression_tags'])} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_default_surfaces(
    *,
    target_jsonl: Path = DEFAULT_TARGET_JSONL_PATH,
    regression_jsonl: Path = DEFAULT_REGRESSION_JSONL_PATH,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Load the predeclared target and validation regression surfaces."""

    return load_jsonl_rows(target_jsonl), load_jsonl_rows(regression_jsonl)


def _ablation_row(
    row: Mapping[str, Any],
    *,
    surface: str,
    graph_key: str,
    policy_variant: str,
) -> dict[str, Any]:
    graph = ClinicalFrequencyStateGraph.model_validate(row[graph_key])
    baseline = _baseline_projection(row, graph)
    month_bucket, graph_gate = _month_bucket_projection(
        graph,
        baseline=baseline,
        policy_variant=policy_variant,
    )
    gold = str(row["gold_normalized_label"])
    label_changed = baseline.final_label != month_bucket.final_label
    selected_evidence_valid = _selected_evidence_valid(graph, month_bucket)
    return {
        "source_row_index": int(row["source_row_index"]),
        "surface": surface,
        "graph_key": graph_key,
        "gold_normalized_label": gold,
        "gold_label_kind": str(row["gold_label_kind"]),
        "gold_monthly_frequency": float(row["gold_monthly_frequency"]),
        "baseline_projection": baseline.model_dump(mode="json"),
        "month_bucket_projection": month_bucket.model_dump(mode="json"),
        "policy_variant": policy_variant,
        "baseline_correct": baseline.final_label == gold,
        "month_bucket_correct": month_bucket.final_label == gold,
        "label_changed": label_changed,
        "selected_evidence_valid": selected_evidence_valid,
        "seizure_free_node_count": len(_usable_seizure_free_nodes(graph)),
        "regression_tags": _regression_tags(row, graph, baseline),
        "graph_gate": graph_gate,
    }


def _baseline_projection(
    row: Mapping[str, Any],
    graph: ClinicalFrequencyStateGraph,
) -> GanGraphProjection:
    projection = (
        row.get("replayed_projection") or row.get("projection") or row.get("baseline_projection")
    )
    if isinstance(projection, Mapping) and projection.get("final_label"):
        parsed = label_to_frequency_record(str(projection["final_label"]))
        live = project_graph_to_gan(graph)
        return live.model_copy(
            update={
                "final_label": parsed.normalized_label,
                "final_kind": parsed.kind,
                "monthly_frequency": parsed.monthly_frequency,
            }
        )
    return project_graph_to_gan(graph)


def _month_bucket_projection(
    graph: ClinicalFrequencyStateGraph,
    *,
    baseline: GanGraphProjection,
    policy_variant: str,
) -> tuple[GanGraphProjection, dict[str, Any]]:
    empty_gate = {"blocked": False, "flags": [], "selected_node_ids": []}
    if not _usable_seizure_free_nodes(graph):
        return _projection_with_policy_name(baseline, policy_variant), empty_gate
    candidate = _project_duration_variant(
        "month_bucket_duration_selection",
        graph,
        gold_normalized_label="",
    )
    if policy_variant == "gated_v1":
        return _gated_month_bucket_projection(baseline, candidate), empty_gate
    if policy_variant == "graph_gated_v2":
        graph_gate = _graph_metadata_gate(graph, candidate)
        if graph_gate["blocked"]:
            return _projection_with_policy_name(baseline, policy_variant), graph_gate
        return (
            candidate.model_copy(
                update={
                    "projection_policy": _projection_policy_name(policy_variant),
                    "rationale": (
                        "Projected with diagnostic month-bucket duration policy graph_gated_v2."
                    ),
                }
            ),
            graph_gate,
        )
    return candidate, empty_gate


def _gated_month_bucket_projection(
    baseline: GanGraphProjection,
    candidate: GanGraphProjection,
) -> GanGraphProjection:
    if baseline.final_kind is not FrequencyLabelKind.SEIZURE_FREE:
        return _projection_with_policy_name(baseline, "gated_v1")
    if _numeric_month_equivalent(baseline.final_label, candidate.final_label):
        return _projection_with_policy_name(baseline, "gated_v1")
    return candidate.model_copy(
        update={
            "projection_policy": (
                "gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1"
            ),
            "rationale": ("Projected with gated diagnostic month-bucket duration policy v1."),
        }
    )


def _projection_with_policy_name(
    projection: GanGraphProjection,
    policy_variant: str,
) -> GanGraphProjection:
    return projection.model_copy(
        update={"projection_policy": _projection_policy_name(policy_variant)}
    )


def _projection_policy_name(policy_variant: str) -> str:
    if policy_variant == "v0":
        return "gan2026_state_graph_projection_ablation_month_bucket_duration_selection"
    return (
        f"gan2026_state_graph_projection_ablation_month_bucket_duration_selection_{policy_variant}"
    )


def _graph_metadata_gate(
    graph: ClinicalFrequencyStateGraph,
    candidate: GanGraphProjection,
) -> dict[str, Any]:
    selected = _selected_nodes(graph, candidate)
    flags: list[str] = []
    if _has_active_boundary_state_node(graph):
        flags.append("active_boundary_state_node")
    if not selected or not all(
        node.rule_id.startswith("seizure_free_duration_node_normalization_v0.") for node in selected
    ):
        flags.append("selected_rule_not_duration_normalization_v0")
    return {
        "blocked": bool(flags),
        "flags": sorted(flags),
        "selected_node_ids": [node.node_id for node in selected],
    }


def _selected_nodes(
    graph: ClinicalFrequencyStateGraph,
    projection: GanGraphProjection,
) -> list[Any]:
    nodes = {node.node_id: node for node in graph.nodes}
    return [nodes[node_id] for node_id in projection.selected_node_ids if node_id in nodes]


def _has_active_boundary_state_node(graph: ClinicalFrequencyStateGraph) -> bool:
    return any(
        node.semantic_kind
        in {
            FrequencyLabelKind.UNKNOWN,
            FrequencyLabelKind.NO_REFERENCE,
            FrequencyLabelKind.UNRESOLVED_MULTIPLE,
        }
        and node.assertion_status == "asserted"
        and node.temporality == "current"
        and not node.graph_errors
        for node in graph.nodes
    )


def _selected_evidence_valid(
    graph: ClinicalFrequencyStateGraph,
    projection: GanGraphProjection,
) -> bool:
    nodes = {node.node_id: node for node in graph.nodes}
    selected = [nodes[node_id] for node_id in projection.selected_node_ids if node_id in nodes]
    if not selected:
        return True
    return all(
        node.evidence.start_char is not None and node.evidence.end_char is not None
        for node in selected
    )


def _regression_tags(
    row: Mapping[str, Any],
    graph: ClinicalFrequencyStateGraph,
    baseline: GanGraphProjection,
) -> list[str]:
    tags: list[str] = []
    gold_kind = str(row["gold_label_kind"])
    gold_label = str(row["gold_normalized_label"])
    if bool(row.get("projection_exact_label_match")) or baseline.final_label == gold_label:
        tags.append("already_projection_correct")
    if gold_kind == FrequencyLabelKind.SEIZURE_FREE.value and not _is_duration_label(gold_label):
        tags.append("non_duration_seizure_free")
    if gold_kind == FrequencyLabelKind.SEIZURE_FREE.value and _is_numeric_duration_label(
        gold_label
    ):
        tags.append("numeric_seizure_free_duration")
    if gold_kind == FrequencyLabelKind.FREQUENCY.value and _usable_seizure_free_nodes(graph):
        tags.append("frequency_with_seizure_free_node")
    if gold_kind in {
        FrequencyLabelKind.UNKNOWN.value,
        FrequencyLabelKind.NO_REFERENCE.value,
        FrequencyLabelKind.UNRESOLVED_MULTIPLE.value,
    }:
        tags.append("unknown_no_reference_boundary")
    tags.extend(str(tag) for tag in row.get("validation_hard_slice_memberships", []))
    return sorted(tags)


def _summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    target_rows = [row for row in rows if row["surface"] == "target_duration_enriched"]
    regression_rows = [row for row in rows if row["surface"] == "regression_validation_hard_slice"]
    return {
        "all_rows": _surface_summary(rows),
        "surfaces": {
            surface: _surface_summary([row for row in rows if row["surface"] == surface])
            for surface in sorted({str(row["surface"]) for row in rows})
        },
        "target": {
            **_surface_summary(target_rows),
            "exact_duration_corrections": sum(
                not bool(row["baseline_correct"]) and bool(row["month_bucket_correct"])
                for row in target_rows
            ),
            "exact_duration_regressions": sum(
                bool(row["baseline_correct"]) and not bool(row["month_bucket_correct"])
                for row in target_rows
            ),
            "selected_evidence_valid_rows": sum(
                bool(row["selected_evidence_valid"]) for row in target_rows
            ),
        },
        "regression": {
            **_surface_summary(regression_rows),
            "already_correct_regressions": _changed_tag_count(
                regression_rows,
                "already_projection_correct",
                require_baseline_correct=True,
            ),
            "non_duration_seizure_free_regressions": _changed_tag_count(
                regression_rows,
                "non_duration_seizure_free",
                require_baseline_correct=True,
            ),
            "unknown_no_reference_boundary_changes": _changed_tag_count(
                regression_rows,
                "unknown_no_reference_boundary",
            ),
            "frequency_with_seizure_free_node_changes": _changed_tag_count(
                regression_rows,
                "frequency_with_seizure_free_node",
            ),
            "selected_evidence_valid_rows": sum(
                bool(row["selected_evidence_valid"]) for row in regression_rows
            ),
        },
        "regression_tags": _tag_summary(regression_rows),
        "regression_family_tags": _tag_summary(
            regression_rows,
            tag_filter=_is_validation_family_tag,
        ),
        "graph_gate": _graph_gate_summary(rows),
    }


def _surface_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    changed = sum(bool(row["label_changed"]) for row in rows)
    return {
        "rows": len(rows),
        "changed_labels": changed,
        "changed_label_rate": round(changed / len(rows), 4) if rows else 0.0,
        "baseline_correct": sum(bool(row["baseline_correct"]) for row in rows),
        "month_bucket_correct": sum(bool(row["month_bucket_correct"]) for row in rows),
    }


def _tag_summary(
    rows: Sequence[Mapping[str, Any]],
    *,
    tag_filter: Callable[[str], bool] | None = None,
) -> dict[str, dict[str, int]]:
    tags = Counter(
        tag
        for row in rows
        for tag in row["regression_tags"]
        if tag_filter is None or tag_filter(tag)
    )
    changed = Counter(
        tag
        for row in rows
        if row["label_changed"]
        for tag in row["regression_tags"]
        if tag_filter is None or tag_filter(tag)
    )
    return {tag: {"rows": tags[tag], "changed_labels": changed[tag]} for tag in sorted(tags)}


def _graph_gate_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    gate_rows = [row for row in rows if row.get("graph_gate")]
    blocked = [row for row in gate_rows if bool(row.get("graph_gate", {}).get("blocked"))]
    flags = Counter(flag for row in blocked for flag in row.get("graph_gate", {}).get("flags", []))
    return {
        "blocked_rows": len(blocked),
        **{flag: {"rows": flags[flag]} for flag in sorted(flags)},
    }


def _is_validation_family_tag(tag: str) -> bool:
    return tag in {
        "candidate_absent_or_weak",
        "cluster_or_diary",
        "deterministic_miss",
        "seizure_free_overreach",
        "shorthand_interval_range",
        "temporal_conflict",
        "unknown_no_reference_boundary",
    }


def _changed_tag_count(
    rows: Sequence[Mapping[str, Any]],
    tag: str,
    *,
    require_baseline_correct: bool = False,
) -> int:
    return sum(
        bool(row["label_changed"])
        and tag in row["regression_tags"]
        and (not require_baseline_correct or bool(row["baseline_correct"]))
        for row in rows
    )


def _is_duration_label(label: str) -> bool:
    return "seizure free for " in label


def _is_numeric_duration_label(label: str) -> bool:
    return any(f"seizure free for {digit}" in label for digit in "123456789")


def _numeric_month_equivalent(left: str, right: str) -> bool:
    left_parts = _numeric_month_parts(left)
    right_parts = _numeric_month_parts(right)
    return left_parts is not None and left_parts == right_parts


def _numeric_month_parts(label: str) -> tuple[str, str] | None:
    match = re.fullmatch(r"seizure free for (?P<amount>\d+) months?", label)
    if not match:
        return None
    return match.group("amount"), "month"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run month-bucket duration-selection projection ablation v0."
    )
    parser.add_argument("--target-jsonl", type=Path, default=DEFAULT_TARGET_JSONL_PATH)
    parser.add_argument("--regression-jsonl", type=Path, default=DEFAULT_REGRESSION_JSONL_PATH)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--policy-variant",
        choices=("v0", "gated_v1", "graph_gated_v2"),
        default="v0",
    )
    args = parser.parse_args(argv)
    if args.policy_variant == "gated_v1":
        args.jsonl = DEFAULT_V1_JSONL_PATH if args.jsonl == DEFAULT_JSONL_PATH else args.jsonl
        args.json = DEFAULT_V1_JSON_PATH if args.json == DEFAULT_JSON_PATH else args.json
        args.markdown = (
            DEFAULT_V1_REPORT_PATH if args.markdown == DEFAULT_REPORT_PATH else args.markdown
        )
    elif args.policy_variant == "graph_gated_v2":
        args.jsonl = (
            DEFAULT_GRAPH_GATED_JSONL_PATH if args.jsonl == DEFAULT_JSONL_PATH else args.jsonl
        )
        args.json = DEFAULT_GRAPH_GATED_JSON_PATH if args.json == DEFAULT_JSON_PATH else args.json
        args.markdown = (
            DEFAULT_GRAPH_GATED_REPORT_PATH
            if args.markdown == DEFAULT_REPORT_PATH
            else args.markdown
        )

    target_rows, regression_rows = load_default_surfaces(
        target_jsonl=args.target_jsonl,
        regression_jsonl=args.regression_jsonl,
    )
    rows, metadata = run_month_bucket_duration_selection_ablation(
        target_rows,
        regression_rows,
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
        policy_variant=args.policy_variant,
    )
    write_jsonl_rows(rows, args.jsonl)
    write_month_bucket_ablation_json(metadata, args.json)
    write_month_bucket_ablation_report(
        rows,
        metadata,
        args.markdown,
        jsonl_path=args.jsonl,
        json_path=args.json,
    )
    print(json.dumps(metadata["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
