"""Replay accepted boundary-state builder nodes into diagnostic state graphs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import locate_evidence
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
    load_split_manifest,
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
    EvidenceSpan,
    GraphNodeKind,
    StateGraphNode,
    build_state_graph,
    graph_node_labels,
    project_graph_to_gan,
)

DEFAULT_BOUNDARY_BUILDER_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_"
    "gpt41mini_live_2026-06-02.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_"
    "2026-06-02.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_"
    "2026-06-02.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_accepted_boundary_nodes_replay_"
    "2026-06-02.md"
)


def run_accepted_boundary_node_replay(
    records: Sequence[GanFrequencyRecord],
    boundary_rows: Sequence[Mapping[str, Any]],
    *,
    split: str,
    split_manifest: str,
    source_artifact: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Merge accepted validation boundary-builder nodes and replay graph diagnostics."""

    records_by_source = {record.source_row_index: record for record in records}
    accepted_rows = _accepted_boundary_rows(boundary_rows)
    replay_rows: list[dict[str, Any]] = []
    for boundary_row in accepted_rows:
        source_row_index = int(boundary_row["source_row_index"])
        record = records_by_source[source_row_index]
        replay_rows.append(
            _replay_row(
                record,
                boundary_row,
                split=split,
                split_manifest=split_manifest,
            )
        )

    metadata = {
        "artifact_kind": "gan2026_accepted_boundary_nodes_graph_replay",
        "date": "2026-06-02",
        "pipeline_family": "hybrid_clinical_frequency_state_graph",
        "split": split,
        "split_manifest": split_manifest,
        "row_count": len(replay_rows),
        "source_artifact": source_artifact,
        "graph_builder": (
            "deterministic_oracle_span_harvester_v0 + accepted_boundary_state_nodes_v0"
        ),
        "projection_policy": "gan2026_state_graph_projection_v0",
        "claim_language": (
            "Diagnostic graph replay only. Accepted hosted nodes are merged for "
            "coverage analysis; projection and arbitration policy are unchanged and "
            "remain separate ablation targets."
        ),
        "summary": _summary(replay_rows),
    }
    return replay_rows, metadata


def write_replay_json(metadata: Mapping[str, Any], path: Path) -> None:
    """Write replay metadata as JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_replay_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    """Write a compact report for accepted-node graph replay."""

    summary = metadata["summary"]
    coverage = summary["coverage"]
    projection = summary["projection"]
    lines = [
        "# Gan 2026 Accepted Boundary Nodes Graph Replay",
        "",
        "This is diagnostic graph replay only, not a benchmark result.",
        "",
        f"- Source artifact: `{metadata['source_artifact']}`",
        f"- Split: `{metadata['split']}`",
        f"- Split manifest: `{metadata['split_manifest']}`",
        f"- Rows: {metadata['row_count']}",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Coverage Replay",
        "",
        f"- Accepted boundary-builder rows: {coverage['accepted_boundary_rows']}",
        f"- Accepted hosted nodes: {coverage['accepted_hosted_nodes']}",
        f"- Baseline representable rows: {coverage['baseline_representable_rows']}/"
        f"{metadata['row_count']}",
        f"- Replayed representable rows: {coverage['replayed_representable_rows']}/"
        f"{metadata['row_count']}",
        f"- Representability gains: {coverage['representability_gains']}",
        "",
        "## Projection Replay",
        "",
        f"- Exact normalized label matches: {projection['exact_label_matches']}/"
        f"{metadata['row_count']}",
        f"- Purist accuracy/F1: {projection['purist_accuracy']:.4f} / "
        f"{projection['purist_f1']:.4f}",
        f"- Pragmatic accuracy/F1: {projection['pragmatic_accuracy']:.4f} / "
        f"{projection['pragmatic_f1']:.4f}",
        f"- Projection changed after accepted-node merge: "
        f"{projection['changed_from_baseline']}",
        "",
        "## Rows",
        "",
        "| Source row | Gold | Baseline representable | Replayed representable | "
        "Baseline projection | Replayed projection | Hosted nodes |",
        "| ---: | --- | --- | --- | --- | --- | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['source_row_index']} | {row['gold_normalized_label']} | "
            f"{row['baseline_oracle_representable']} | "
            f"{row['replayed_oracle_representable']} | "
            f"{row['baseline_projection']['final_label']} | "
            f"{row['replayed_projection']['final_label']} | "
            f"{row['accepted_hosted_node_count']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _accepted_boundary_rows(
    rows: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    accepted = [
        row
        for row in rows
        if bool(row.get("representability_gain_candidate"))
        and not row.get("parse_errors")
        and str(row.get("surface_role") or "") == "validation_boundary_missing"
    ]
    return sorted(accepted, key=lambda row: int(row["source_row_index"]))


def _replay_row(
    record: GanFrequencyRecord,
    boundary_row: Mapping[str, Any],
    *,
    split: str,
    split_manifest: str,
) -> dict[str, Any]:
    baseline_graph = build_state_graph(
        record.note_text,
        source_row_index=record.source_row_index,
        include_no_reference_fallback=True,
    )
    accepted_nodes = _accepted_nodes_from_boundary_row(record, boundary_row, baseline_graph)
    replayed_graph = _append_nodes(
        baseline_graph,
        accepted_nodes,
        accepted_boundary_row_id=str(boundary_row["source_row_index"]),
    )
    baseline_projection = project_graph_to_gan(baseline_graph)
    replayed_projection = project_graph_to_gan(replayed_graph)
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "split_manifest": split_manifest,
        "row_ok": record.row_ok,
        "gold_label": record.gold_label,
        "gold_normalized_label": record.gold_normalized_label,
        "gold_label_kind": record.gold_label_kind.value,
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "baseline_oracle_representable": _gold_is_representable(
            record,
            graph_node_labels(baseline_graph),
        ),
        "replayed_oracle_representable": _gold_is_representable(
            record,
            graph_node_labels(replayed_graph),
        ),
        "accepted_hosted_node_count": len(accepted_nodes),
        "accepted_hosted_nodes": [node.model_dump(mode="json") for node in accepted_nodes],
        "baseline_graph": baseline_graph.model_dump(mode="json"),
        "replayed_graph": replayed_graph.model_dump(mode="json"),
        "baseline_projection": baseline_projection.model_dump(mode="json"),
        "replayed_projection": replayed_projection.model_dump(mode="json"),
        "projection_changed_from_baseline": (
            replayed_projection.final_label != baseline_projection.final_label
        ),
        "projection_exact_label_match": (
            replayed_projection.final_label == record.gold_normalized_label
        ),
    }


def _accepted_nodes_from_boundary_row(
    record: GanFrequencyRecord,
    boundary_row: Mapping[str, Any],
    baseline_graph: ClinicalFrequencyStateGraph,
) -> tuple[StateGraphNode, ...]:
    structured_record = boundary_row.get("structured_record") or {}
    nodes = structured_record.get("nodes") or []
    accepted: list[StateGraphNode] = []
    next_index = len(baseline_graph.nodes) + 1
    for node in nodes:
        graph_node = _hosted_node(
            record,
            node,
            index=next_index,
        )
        if _node_represents_gold(record, graph_node):
            accepted.append(graph_node)
            next_index += 1
    return tuple(accepted)


def _hosted_node(
    record: GanFrequencyRecord,
    node: Mapping[str, Any],
    *,
    index: int,
) -> StateGraphNode:
    normalized_label = _hosted_node_label(node)
    label_record = label_to_frequency_record(normalized_label)
    evidence_text = str(node.get("evidence") or "")
    span = locate_evidence(record.note_text, evidence_text)
    start_char, end_char = span if span else (None, None)
    graph_errors = () if span else ("hosted_boundary_evidence_not_exact",)
    return StateGraphNode(
        node_id=f"hosted-boundary-sg-{index:03d}",
        kind=GraphNodeKind.UNKNOWN_FREQUENCY,
        normalized_label=label_record.normalized_label,
        semantic_kind=label_record.kind,
        monthly_frequency=label_record.monthly_frequency,
        evidence=EvidenceSpan(text=evidence_text, start_char=start_char, end_char=end_char),
        assertion_status=str(node.get("assertion_status") or "unknown"),
        temporality=str(node.get("temporality") or "unclear"),
        certainty=str(node.get("certainty") or "unknown"),
        rule_id="hosted_boundary_state_graph_builder_v0.accepted_node",
        graph_errors=graph_errors,
    )


def _hosted_node_label(node: Mapping[str, Any]) -> str:
    raw_label = node.get("node_normalized_label")
    if raw_label:
        return str(raw_label)
    if str(node.get("semantic_kind") or "") == "unknown":
        return "unknown"
    return "unknown"


def _append_nodes(
    graph: ClinicalFrequencyStateGraph,
    nodes: Sequence[StateGraphNode],
    *,
    accepted_boundary_row_id: str,
) -> ClinicalFrequencyStateGraph:
    all_nodes = (*graph.nodes, *nodes)
    return graph.model_copy(
        update={
            "nodes": all_nodes,
            "graph_builder": (
                "deterministic_oracle_span_harvester_v0+"
                "accepted_boundary_state_nodes_v0"
            ),
            "missing_variable_flags": _missing_variable_flags(all_nodes),
            "metadata": {
                **graph.metadata,
                "accepted_boundary_row_id": accepted_boundary_row_id,
                "accepted_boundary_node_count": len(nodes),
            },
        }
    )


def _missing_variable_flags(nodes: Sequence[StateGraphNode]) -> tuple[str, ...]:
    flags: list[str] = []
    if any(node.semantic_kind is FrequencyLabelKind.UNKNOWN for node in nodes):
        flags.append("frequency_unquantified")
    if any(node.graph_errors for node in nodes):
        flags.append("normalization_error")
    return tuple(flags)


def _summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    y_true = [float(row["gold_monthly_frequency"]) for row in rows]
    y_pred = [
        float(row["replayed_projection"]["monthly_frequency"]) for row in rows
    ]
    purist = evaluate_predictions(y_true, y_pred, method="purist")
    pragmatic = evaluate_predictions(y_true, y_pred, method="pragmatic")
    gained_rows = [
        row
        for row in rows
        if not row["baseline_oracle_representable"]
        and row["replayed_oracle_representable"]
    ]
    return {
        "coverage": {
            "accepted_boundary_rows": len(rows),
            "accepted_hosted_nodes": sum(
                int(row["accepted_hosted_node_count"]) for row in rows
            ),
            "baseline_representable_rows": sum(
                bool(row["baseline_oracle_representable"]) for row in rows
            ),
            "replayed_representable_rows": sum(
                bool(row["replayed_oracle_representable"]) for row in rows
            ),
            "representability_gains": len(gained_rows),
            "representability_gain_source_row_indices": [
                int(row["source_row_index"]) for row in gained_rows
            ],
            "accepted_rows_by_gold_kind": dict(
                sorted(Counter(str(row["gold_label_kind"]) for row in rows).items())
            ),
        },
        "projection": {
            "purist_accuracy": purist["micro"]["accuracy"],
            "purist_f1": purist["micro"]["f1"],
            "pragmatic_accuracy": pragmatic["micro"]["accuracy"],
            "pragmatic_f1": pragmatic["micro"]["f1"],
            "exact_label_matches": sum(
                bool(row["projection_exact_label_match"]) for row in rows
            ),
            "changed_from_baseline": sum(
                bool(row["projection_changed_from_baseline"]) for row in rows
            ),
        },
    }


def _gold_is_representable(
    record: GanFrequencyRecord,
    node_labels: Sequence[tuple[FrequencyLabelKind, str | None]],
) -> bool:
    if record.gold_label_kind in {
        FrequencyLabelKind.UNKNOWN,
        FrequencyLabelKind.NO_REFERENCE,
        FrequencyLabelKind.SEIZURE_FREE,
    }:
        return any(kind is record.gold_label_kind for kind, _label in node_labels)
    return any(label == record.gold_normalized_label for _kind, label in node_labels)


def _node_represents_gold(record: GanFrequencyRecord, node: StateGraphNode) -> bool:
    if node.graph_errors:
        return False
    if record.gold_label_kind in {
        FrequencyLabelKind.UNKNOWN,
        FrequencyLabelKind.NO_REFERENCE,
        FrequencyLabelKind.SEIZURE_FREE,
    }:
        return node.semantic_kind is record.gold_label_kind
    return node.normalized_label == record.gold_normalized_label


def _load_records() -> tuple[list[GanFrequencyRecord], str]:
    records = load_records_for_split("validation")
    manifest = load_split_manifest()
    return records, str(manifest.get("manifest_version", "gan2026_split_v1"))


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Replay accepted Gan 2026 boundary-state nodes into diagnostic graphs."
    )
    parser.add_argument(
        "--boundary-builder-jsonl",
        type=Path,
        default=DEFAULT_BOUNDARY_BUILDER_JSONL_PATH,
    )
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    records, split_manifest = _load_records()
    boundary_rows = load_jsonl_rows(args.boundary_builder_jsonl)
    rows, metadata = run_accepted_boundary_node_replay(
        records,
        boundary_rows,
        split="validation_hard_slices",
        split_manifest=split_manifest,
        source_artifact=str(args.boundary_builder_jsonl),
    )
    write_jsonl_rows(rows, args.jsonl)
    write_replay_json(metadata, args.json)
    write_replay_report(
        rows,
        metadata,
        args.markdown,
        jsonl_path=args.jsonl,
        json_path=args.json,
    )
    print(json.dumps(metadata["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
