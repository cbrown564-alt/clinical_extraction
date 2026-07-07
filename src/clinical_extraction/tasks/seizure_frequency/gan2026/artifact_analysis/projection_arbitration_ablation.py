"""Projection/arbitration ablations over saved Gan 2026 state-graph artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
    evaluate_predictions,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    ClinicalFrequencyStateGraph,
    GanGraphProjection,
    ProjectionPolicy,
    StateGraphNode,
    project_graph_to_gan,
)

DEFAULT_HARD_SLICE_JSONL_PATH = Path(
    "experiments/"
    "gan2026_clinical_frequency_state_graph_validation_hard_slices_diagnostics_"
    "2026-06-02.jsonl"
)
DEFAULT_ACCEPTED_REPLAY_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_"
    "2026-06-02.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_"
    "2026-06-02.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_"
    "2026-06-02.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_"
    "2026-06-02.md"
)


@dataclass(frozen=True)
class ProjectionVariant:
    name: str
    description: str


PROJECTION_VARIANTS: tuple[ProjectionVariant, ...] = (
    ProjectionVariant(
        name="baseline_v0",
        description="Existing gan2026_state_graph_projection_v0 policy.",
    ),
    ProjectionVariant(
        name="competing_frequency_uncertainty",
        description="Emit unknown when multiple current frequency hypotheses compete.",
    ),
    ProjectionVariant(
        name="boundary_state_priority",
        description="Prioritize unknown/unresolved-multiple boundary-state nodes.",
    ),
    ProjectionVariant(
        name="seizure_free_priority",
        description="Prioritize seizure-free state nodes before concrete frequency nodes.",
    ),
    ProjectionVariant(
        name="lowest_current_frequency",
        description="Select the lowest current concrete frequency node instead of the highest.",
    ),
    ProjectionVariant(
        name="oracle_gold_node",
        description="Gold-aware upper bound: select an exact gold node when present.",
    ),
)


def run_projection_arbitration_ablation(
    ablation_rows: Sequence[Mapping[str, Any]],
    *,
    split: str,
    split_manifest: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run named projection variants over already-representable graph rows."""

    rows = [_ablation_row(row) for row in ablation_rows]
    metadata = {
        "artifact_kind": "gan2026_state_graph_projection_arbitration_ablation",
        "date": "2026-06-02",
        "pipeline_family": "hybrid_clinical_frequency_state_graph",
        "split": split,
        "split_manifest": split_manifest,
        "row_count": len(rows),
        "projection_variants": {
            variant.name: variant.description for variant in PROJECTION_VARIANTS
        },
        "claim_language": (
            "Diagnostic only. This replays named projection/arbitration variants "
            "over saved validation graph artifacts; it does not change scorer, "
            "graph construction, production projection policy, or holdout status."
        ),
        "summary": _summary(rows),
    }
    return rows, metadata


def write_ablation_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_ablation_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 State-Graph Projection/Arbitration Ablation",
        "",
        "Diagnostic only: this is validation-cycle replay over saved graph artifacts, "
        "not a benchmark result and not a projection-policy promotion.",
        "",
        f"- Split: `{metadata['split']}`",
        f"- Split manifest: `{metadata['split_manifest']}`",
        f"- Rows: {metadata['row_count']}",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Row Sources",
        "",
        "| Source | Rows |",
        "| --- | ---: |",
    ]
    for source, count in sorted(summary["row_sources"].items()):
        lines.append(f"| {source} | {count} |")

    lines.extend(
        [
            "",
            "## Projection Variants",
            "",
            (
                "| Variant | Exact matches | Purist F1 | Pragmatic F1 | "
                "Corrections vs baseline | Regressions vs baseline |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for variant in PROJECTION_VARIANTS:
        stats = summary["variants"][variant.name]
        lines.append(
            f"| `{variant.name}` | {stats['exact_matches']}/{metadata['row_count']} | "
            f"{stats['purist_f1']:.4f} | {stats['pragmatic_f1']:.4f} | "
            f"{stats['baseline_wrong_to_variant_correct']} | "
            f"{stats['baseline_correct_to_variant_wrong']} |"
        )

    lines.extend(
        [
            "",
            "## Failure Families",
            "",
            (
                "| Family | Rows | Baseline exact | Best non-oracle variant | "
                "Best exact | Oracle exact |"
            ),
            "| --- | ---: | ---: | --- | ---: | ---: |",
        ]
    )
    for family, stats in sorted(summary["failure_families"].items()):
        lines.append(
            f"| {family} | {stats['rows']} | {stats['baseline_exact']} | "
            f"`{stats['best_non_oracle_variant']}` | "
            f"{stats['best_non_oracle_exact']} | {stats['oracle_exact']} |"
        )

    lines.extend(
        [
            "",
            "## Remaining Baseline Misses",
            "",
            "| Source row | Source | Gold | Baseline | Best non-oracle labels | Oracle |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        best_names = summary["row_best_non_oracle"].get(str(row["source_row_index"]), [])
        best_labels = ", ".join(
            f"{name}: {row['variant_results'][name]['final_label']}" for name in best_names
        )
        lines.append(
            f"| {row['source_row_index']} | {row['source']} | "
            f"{row['gold_normalized_label']} | "
            f"{row['variant_results']['baseline_v0']['final_label']} | "
            f"{best_labels} | "
            f"{row['variant_results']['oracle_gold_node']['final_label']} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_default_ablation_rows(
    *,
    hard_slice_jsonl: Path = DEFAULT_HARD_SLICE_JSONL_PATH,
    accepted_replay_jsonl: Path = DEFAULT_ACCEPTED_REPLAY_JSONL_PATH,
) -> list[dict[str, Any]]:
    """Load the predeclared saved-artifact surfaces for projection replay."""

    rows: list[dict[str, Any]] = []
    for row in load_jsonl_rows(hard_slice_jsonl):
        if bool(row.get("oracle_representable")) and (
            row["projection"]["final_label"] != row["gold_normalized_label"]
        ):
            rows.append(
                {
                    "source_row_index": row["source_row_index"],
                    "source": "validation_hard_slice_representable_projection_miss",
                    "source_artifact": str(hard_slice_jsonl),
                    "gold_normalized_label": row["gold_normalized_label"],
                    "gold_label_kind": row["gold_label_kind"],
                    "gold_monthly_frequency": row["gold_monthly_frequency"],
                    "graph": row["graph"],
                    "baseline_projection_label": row["projection"]["final_label"],
                    "failure_family": _failure_family(row["gold_label_kind"]),
                }
            )
    for row in load_jsonl_rows(accepted_replay_jsonl):
        if bool(row.get("replayed_oracle_representable")) and not bool(
            row.get("projection_exact_label_match")
        ):
            rows.append(
                {
                    "source_row_index": row["source_row_index"],
                    "source": "accepted_boundary_node_replay_projection_miss",
                    "source_artifact": str(accepted_replay_jsonl),
                    "gold_normalized_label": row["gold_normalized_label"],
                    "gold_label_kind": row["gold_label_kind"],
                    "gold_monthly_frequency": row["gold_monthly_frequency"],
                    "graph": row["replayed_graph"],
                    "baseline_projection_label": row["replayed_projection"]["final_label"],
                    "failure_family": _failure_family(row["gold_label_kind"]),
                }
            )
    return sorted(rows, key=lambda row: (str(row["source"]), int(row["source_row_index"])))


def _ablation_row(row: Mapping[str, Any]) -> dict[str, Any]:
    graph = ClinicalFrequencyStateGraph.model_validate(row["graph"])
    gold_label = str(row["gold_normalized_label"])
    variant_results = {
        variant.name: _variant_result(
            _project_variant(
                variant.name,
                graph,
                gold_normalized_label=gold_label,
                gold_label_kind=str(row["gold_label_kind"]),
            ),
            gold_label=gold_label,
        )
        for variant in PROJECTION_VARIANTS
    }
    return {
        "source_row_index": int(row["source_row_index"]),
        "source": str(row["source"]),
        "source_artifact": str(row["source_artifact"]),
        "gold_normalized_label": gold_label,
        "gold_label_kind": str(row["gold_label_kind"]),
        "gold_monthly_frequency": float(row["gold_monthly_frequency"]),
        "failure_family": str(row["failure_family"]),
        "graph_node_count": len(graph.nodes),
        "variant_results": variant_results,
    }


def _project_variant(
    variant_name: str,
    graph: ClinicalFrequencyStateGraph,
    *,
    gold_normalized_label: str,
    gold_label_kind: str,
) -> GanGraphProjection:
    if variant_name == "baseline_v0":
        return project_graph_to_gan(graph)
    if variant_name == "competing_frequency_uncertainty":
        return project_graph_to_gan(graph, policy=ProjectionPolicy(force_single_label=False))
    if variant_name == "boundary_state_priority":
        return _project_by_priority(
            graph,
            (
                FrequencyLabelKind.UNRESOLVED_MULTIPLE,
                FrequencyLabelKind.UNKNOWN,
                FrequencyLabelKind.SEIZURE_FREE,
                FrequencyLabelKind.FREQUENCY,
                FrequencyLabelKind.NO_REFERENCE,
            ),
            policy_name="gan2026_state_graph_projection_ablation_boundary_state_priority",
        )
    if variant_name == "seizure_free_priority":
        return _project_by_priority(
            graph,
            (
                FrequencyLabelKind.SEIZURE_FREE,
                FrequencyLabelKind.FREQUENCY,
                FrequencyLabelKind.UNKNOWN,
                FrequencyLabelKind.UNRESOLVED_MULTIPLE,
                FrequencyLabelKind.NO_REFERENCE,
            ),
            policy_name="gan2026_state_graph_projection_ablation_seizure_free_priority",
        )
    if variant_name == "lowest_current_frequency":
        return _project_lowest_current_frequency(graph)
    if variant_name == "oracle_gold_node":
        return _project_oracle_gold_node(
            graph,
            gold_normalized_label=gold_normalized_label,
            gold_label_kind=gold_label_kind,
        )
    raise ValueError(f"unknown projection variant: {variant_name}")


def _project_by_priority(
    graph: ClinicalFrequencyStateGraph,
    kind_priority: Sequence[FrequencyLabelKind],
    *,
    policy_name: str,
) -> GanGraphProjection:
    for kind in kind_priority:
        nodes = [node for node in graph.nodes if _usable_node(node) and node.semantic_kind is kind]
        if nodes:
            selected = max(nodes, key=lambda node: (node.monthly_frequency, node.node_id))
            return _projection_from_node(
                selected,
                rationale=f"Projected with diagnostic kind priority; selected {kind.value}.",
                policy_name=policy_name,
            )
    return project_graph_to_gan(graph).model_copy(update={"projection_policy": policy_name})


def _project_lowest_current_frequency(graph: ClinicalFrequencyStateGraph) -> GanGraphProjection:
    current_frequency_nodes = [
        node
        for node in graph.nodes
        if _usable_node(node)
        and node.semantic_kind is FrequencyLabelKind.FREQUENCY
        and node.temporality == "current"
    ]
    if not current_frequency_nodes:
        return project_graph_to_gan(graph).model_copy(
            update={
                "projection_policy": (
                    "gan2026_state_graph_projection_ablation_lowest_current_frequency"
                )
            }
        )
    selected = min(current_frequency_nodes, key=lambda node: (node.monthly_frequency, node.node_id))
    return _projection_from_node(
        selected,
        rationale="Projected with diagnostic lowest-current-frequency arbitration.",
        policy_name="gan2026_state_graph_projection_ablation_lowest_current_frequency",
    )


def _project_oracle_gold_node(
    graph: ClinicalFrequencyStateGraph,
    *,
    gold_normalized_label: str,
    gold_label_kind: str,
) -> GanGraphProjection:
    gold_kind = FrequencyLabelKind(gold_label_kind)
    exact_nodes = [
        node
        for node in graph.nodes
        if _usable_node(node) and node.normalized_label == gold_normalized_label
    ]
    if exact_nodes:
        selected = max(exact_nodes, key=lambda node: (node.monthly_frequency, node.node_id))
        return _projection_from_node(
            selected,
            rationale="Gold-aware diagnostic upper bound selected exact gold node.",
            policy_name="gan2026_state_graph_projection_ablation_oracle_gold_node",
        )
    kind_nodes = [
        node for node in graph.nodes if _usable_node(node) and node.semantic_kind is gold_kind
    ]
    if kind_nodes:
        selected = max(kind_nodes, key=lambda node: (node.monthly_frequency, node.node_id))
        return _projection_from_node(
            selected,
            rationale="Gold-aware diagnostic upper bound selected gold-kind node.",
            policy_name="gan2026_state_graph_projection_ablation_oracle_gold_node",
        )
    return project_graph_to_gan(graph).model_copy(
        update={"projection_policy": "gan2026_state_graph_projection_ablation_oracle_gold_node"}
    )


def _projection_from_node(
    node: StateGraphNode,
    *,
    rationale: str,
    policy_name: str,
) -> GanGraphProjection:
    record = label_to_frequency_record(node.normalized_label or "unknown")
    return GanGraphProjection(
        final_label=record.normalized_label,
        final_kind=record.kind,
        monthly_frequency=record.monthly_frequency,
        selected_node_ids=(node.node_id,),
        rationale=rationale,
        evidence=node.evidence.text,
        projection_policy=policy_name,
    )


def _usable_node(node: StateGraphNode) -> bool:
    return node.assertion_status == "asserted" and not node.graph_errors


def _variant_result(
    projection: GanGraphProjection,
    *,
    gold_label: str,
) -> dict[str, Any]:
    return {
        **projection.model_dump(mode="json"),
        "correct": projection.final_label == gold_label,
    }


def _summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    row_sources = Counter(str(row["source"]) for row in rows)
    variants = {
        variant.name: _variant_summary(rows, variant.name) for variant in PROJECTION_VARIANTS
    }
    family_stats: dict[str, dict[str, Any]] = {}
    for family in sorted({str(row["failure_family"]) for row in rows}):
        family_rows = [row for row in rows if row["failure_family"] == family]
        non_oracle = {
            variant.name: sum(
                bool(row["variant_results"][variant.name]["correct"]) for row in family_rows
            )
            for variant in PROJECTION_VARIANTS
            if variant.name != "oracle_gold_node"
        }
        best_variant, best_exact = max(non_oracle.items(), key=lambda item: (item[1], item[0]))
        family_stats[family] = {
            "rows": len(family_rows),
            "baseline_exact": non_oracle["baseline_v0"],
            "best_non_oracle_variant": best_variant,
            "best_non_oracle_exact": best_exact,
            "oracle_exact": sum(
                bool(row["variant_results"]["oracle_gold_node"]["correct"]) for row in family_rows
            ),
        }
    row_best = {str(row["source_row_index"]): _best_non_oracle_variants(row) for row in rows}
    return {
        "row_sources": dict(sorted(row_sources.items())),
        "variants": variants,
        "failure_families": family_stats,
        "row_best_non_oracle": row_best,
    }


def _variant_summary(rows: Sequence[Mapping[str, Any]], variant_name: str) -> dict[str, Any]:
    y_true = [float(row["gold_monthly_frequency"]) for row in rows]
    y_pred = [float(row["variant_results"][variant_name]["monthly_frequency"]) for row in rows]
    purist = evaluate_predictions(y_true, y_pred, method="purist")
    pragmatic = evaluate_predictions(y_true, y_pred, method="pragmatic")
    return {
        "exact_matches": sum(bool(row["variant_results"][variant_name]["correct"]) for row in rows),
        "purist_accuracy": purist["micro"]["accuracy"],
        "purist_f1": purist["micro"]["f1"],
        "pragmatic_accuracy": pragmatic["micro"]["accuracy"],
        "pragmatic_f1": pragmatic["micro"]["f1"],
        "baseline_wrong_to_variant_correct": sum(
            not bool(row["variant_results"]["baseline_v0"]["correct"])
            and bool(row["variant_results"][variant_name]["correct"])
            for row in rows
        ),
        "baseline_correct_to_variant_wrong": sum(
            bool(row["variant_results"]["baseline_v0"]["correct"])
            and not bool(row["variant_results"][variant_name]["correct"])
            for row in rows
        ),
    }


def _best_non_oracle_variants(row: Mapping[str, Any]) -> list[str]:
    correct = [
        variant.name
        for variant in PROJECTION_VARIANTS
        if variant.name != "oracle_gold_node"
        and bool(row["variant_results"][variant.name]["correct"])
    ]
    if correct:
        return correct
    return [
        variant.name
        for variant in PROJECTION_VARIANTS
        if variant.name != "oracle_gold_node"
        and row["variant_results"][variant.name]["final_label"]
        != row["variant_results"]["baseline_v0"]["final_label"]
    ]


def _failure_family(gold_label_kind: str) -> str:
    return {
        "frequency": "frequency_arbitration",
        "seizure_free": "seizure_free_arbitration",
        "unknown": "unknown_arbitration",
        "unresolved_multiple": "unresolved_multiple_arbitration",
    }.get(gold_label_kind, "other_arbitration")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Replay Gan 2026 state-graph projection/arbitration ablations."
    )
    parser.add_argument("--hard-slice-jsonl", type=Path, default=DEFAULT_HARD_SLICE_JSONL_PATH)
    parser.add_argument(
        "--accepted-replay-jsonl",
        type=Path,
        default=DEFAULT_ACCEPTED_REPLAY_JSONL_PATH,
    )
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    ablation_rows = load_default_ablation_rows(
        hard_slice_jsonl=args.hard_slice_jsonl,
        accepted_replay_jsonl=args.accepted_replay_jsonl,
    )
    rows, metadata = run_projection_arbitration_ablation(
        ablation_rows,
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
    )
    write_jsonl_rows(rows, args.jsonl)
    write_ablation_json(metadata, args.json)
    write_ablation_report(
        rows,
        metadata,
        args.markdown,
        jsonl_path=args.jsonl,
        json_path=args.json,
    )
    print(json.dumps(metadata["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
