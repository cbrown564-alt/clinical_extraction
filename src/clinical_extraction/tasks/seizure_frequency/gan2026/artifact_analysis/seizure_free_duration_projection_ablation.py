"""Seizure-free duration projection ablation over saved Gan 2026 graph artifacts."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    ClinicalFrequencyStateGraph,
    GanGraphProjection,
    StateGraphNode,
    project_graph_to_gan,
)

DEFAULT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_"
    "ablation_2026-06-02.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_"
    "ablation_2026-06-02.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_"
    "ablation_2026-06-02.md"
)


@dataclass(frozen=True)
class DurationProjectionVariant:
    name: str
    description: str


DURATION_PROJECTION_VARIANTS: tuple[DurationProjectionVariant, ...] = (
    DurationProjectionVariant(
        name="baseline_v0",
        description="Existing gan2026_state_graph_projection_v0 policy.",
    ),
    DurationProjectionVariant(
        name="seizure_free_priority",
        description="Select a seizure-free node before non-seizure-free nodes.",
    ),
    DurationProjectionVariant(
        name="longest_seizure_free_duration",
        description="Select the seizure-free node with the longest parsed duration.",
    ),
    DurationProjectionVariant(
        name="shortest_seizure_free_duration",
        description="Select the seizure-free node with the shortest parsed duration.",
    ),
    DurationProjectionVariant(
        name="numeric_duration_priority",
        description=(
            "Prefer explicit numeric seizure-free durations over broad multiple-unit labels."
        ),
    ),
    DurationProjectionVariant(
        name="month_bucket_duration_selection",
        description=(
            "Prefer broad month-bucket seizure-free nodes over competing numeric-month "
            "or broad-year nodes, preserving plural numeric-month labels for diagnostics."
        ),
    ),
    DurationProjectionVariant(
        name="oracle_exact_seizure_free_node",
        description="Gold-aware upper bound: select an exact seizure-free gold node when present.",
    ),
)


def run_seizure_free_duration_ablation(
    ablation_rows: Sequence[Mapping[str, Any]],
    *,
    split: str,
    split_manifest: str,
    graph_key: str = "graph",
    artifact_kind: str = "gan2026_state_graph_seizure_free_duration_projection_ablation",
    report_title: str = "Gan 2026 State-Graph Seizure-Free Duration Projection Ablation",
    claim_language: str | None = None,
    source_artifact_override: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run duration-focused variants over seizure-free graph projection misses."""

    rows = [
        _duration_row(
            row,
            graph_key=graph_key,
            source_artifact_override=source_artifact_override,
        )
        for row in ablation_rows
        if _is_duration_surface(row, graph_key=graph_key)
    ]
    metadata = {
        "artifact_kind": artifact_kind,
        "date": "2026-06-02",
        "pipeline_family": "hybrid_clinical_frequency_state_graph",
        "split": split,
        "split_manifest": split_manifest,
        "row_count": len(rows),
        "graph_key": graph_key,
        "report_title": report_title,
        "projection_variants": {
            variant.name: variant.description for variant in DURATION_PROJECTION_VARIANTS
        },
        "claim_language": claim_language
        or (
            "Diagnostic only. This replays duration-selection policies over saved "
            "validation graph artifacts where the gold label is seizure-free and "
            "at least one usable seizure-free graph node exists. It does not change "
            "the scorer, graph construction, production projection policy, or "
            "holdout status."
        ),
        "summary": _summary(rows),
    }
    return rows, metadata


def write_duration_ablation_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_duration_ablation_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    summary = metadata["summary"]
    title = metadata.get(
        "report_title",
        "Gan 2026 State-Graph Seizure-Free Duration Projection Ablation",
    )
    lines = [
        f"# {title}",
        "",
        "Diagnostic only: this is validation-cycle replay over saved graph artifacts, "
        "not a benchmark result and not a projection-policy promotion.",
        "",
        "All seizure-free labels have monthly frequency `0.0` under the Gan scorer, "
        "so this report focuses on exact duration-label behavior rather than Purist "
        "or Pragmatic F1.",
        "",
        f"- Split: `{metadata['split']}`",
        f"- Split manifest: `{metadata['split_manifest']}`",
        f"- Rows: {metadata['row_count']}",
        f"- Graph field: `{metadata.get('graph_key', 'graph')}`",
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
                "| Variant | Exact duration matches | Corrections vs baseline | "
                "Regressions vs baseline | Selected seizure-free rows |"
            ),
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for variant in DURATION_PROJECTION_VARIANTS:
        stats = summary["variants"][variant.name]
        lines.append(
            f"| `{variant.name}` | {stats['exact_matches']}/{metadata['row_count']} | "
            f"{stats['baseline_wrong_to_variant_correct']} | "
            f"{stats['baseline_correct_to_variant_wrong']} | "
            f"{stats['selected_seizure_free_rows']} |"
        )
    if "month_bucket_duration_selection" in summary["variants"]:
        lines.extend(
            [
                "",
                "`month_bucket_duration_selection` is a diagnostic output-surface "
                "variant. It prefers broad month-bucket nodes over numeric-month "
                "or broad-year conflicts and preserves plural numeric-month labels; "
                "it does not change scorer normalization or production projection.",
            ]
        )

    lines.extend(
        [
            "",
            "## Failure Modes",
            "",
            "| Mode | Rows |",
            "| --- | ---: |",
        ]
    )
    for mode, count in sorted(summary["failure_modes"].items()):
        lines.append(f"| {mode} | {count} |")

    lines.extend(
        [
            "",
            "## Scorer-Equivalent Duration Labels",
            "",
            "| Source row | Gold | Baseline | Exact node present | Best non-oracle labels |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        best_names = summary["row_best_non_oracle"].get(str(row["source_row_index"]), [])
        best_labels = ", ".join(
            f"{name}: {row['variant_results'][name]['final_label']}" for name in best_names
        )
        lines.append(
            f"| {row['source_row_index']} | {row['gold_normalized_label']} | "
            f"{row['variant_results']['baseline_v0']['final_label']} | "
            f"{row['exact_gold_seizure_free_node_present']} | {best_labels} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _is_duration_surface(row: Mapping[str, Any], *, graph_key: str) -> bool:
    if row.get("gold_label_kind") != FrequencyLabelKind.SEIZURE_FREE.value:
        return False
    graph = ClinicalFrequencyStateGraph.model_validate(row[graph_key])
    return bool(_usable_seizure_free_nodes(graph))


def _duration_row(
    row: Mapping[str, Any],
    *,
    graph_key: str,
    source_artifact_override: str | None,
) -> dict[str, Any]:
    graph = ClinicalFrequencyStateGraph.model_validate(row[graph_key])
    gold_label = str(row["gold_normalized_label"])
    seizure_free_nodes = _usable_seizure_free_nodes(graph)
    variant_results = {
        variant.name: _variant_result(
            _project_duration_variant(variant.name, graph, gold_normalized_label=gold_label),
            gold_label=gold_label,
        )
        for variant in DURATION_PROJECTION_VARIANTS
    }
    exact_gold_nodes = [node for node in seizure_free_nodes if node.normalized_label == gold_label]
    return {
        "source_row_index": int(row["source_row_index"]),
        "source": str(row.get("source") or row.get("split") or "unknown"),
        "source_artifact": source_artifact_override or str(row.get("source_artifact") or ""),
        "graph_key": graph_key,
        "gold_normalized_label": gold_label,
        "gold_duration": _duration_record(gold_label),
        "baseline_projection_label": _baseline_projection_label(row),
        "failure_mode": _failure_mode(
            baseline=variant_results["baseline_v0"],
            exact_gold_nodes=exact_gold_nodes,
            seizure_free_nodes=seizure_free_nodes,
        ),
        "graph_node_count": len(graph.nodes),
        "seizure_free_node_count": len(seizure_free_nodes),
        "seizure_free_nodes": [
            _node_summary(node, gold_normalized_label=gold_label) for node in seizure_free_nodes
        ],
        "exact_gold_seizure_free_node_present": bool(exact_gold_nodes),
        "variant_results": variant_results,
    }


def _project_duration_variant(
    variant_name: str,
    graph: ClinicalFrequencyStateGraph,
    *,
    gold_normalized_label: str,
) -> GanGraphProjection:
    if variant_name == "baseline_v0":
        return project_graph_to_gan(graph)

    seizure_free_nodes = _usable_seizure_free_nodes(graph)
    if not seizure_free_nodes:
        return project_graph_to_gan(graph).model_copy(
            update={"projection_policy": f"gan2026_state_graph_{variant_name}"}
        )

    if variant_name == "seizure_free_priority":
        selected = max(seizure_free_nodes, key=lambda node: (node.monthly_frequency, node.node_id))
    elif variant_name == "longest_seizure_free_duration":
        selected = max(
            seizure_free_nodes,
            key=lambda node: (_duration_sort_key(node), node.node_id),
        )
    elif variant_name == "shortest_seizure_free_duration":
        selected = min(
            seizure_free_nodes,
            key=lambda node: (_duration_sort_key(node), node.node_id),
        )
    elif variant_name == "numeric_duration_priority":
        selected = max(
            seizure_free_nodes,
            key=lambda node: (_numeric_duration_sort_key(node), node.node_id),
        )
    elif variant_name == "month_bucket_duration_selection":
        selected = max(
            seizure_free_nodes,
            key=lambda node: (_month_bucket_duration_sort_key(node), node.node_id),
        )
        return _projection_from_node(
            selected,
            rationale=(
                "Projected with diagnostic seizure-free duration policy "
                "month_bucket_duration_selection."
            ),
            policy_name="gan2026_state_graph_projection_ablation_month_bucket_duration_selection",
            final_label_override=_month_bucket_diagnostic_label(selected),
        )
    elif variant_name == "oracle_exact_seizure_free_node":
        exact_nodes = [
            node for node in seizure_free_nodes if node.normalized_label == gold_normalized_label
        ]
        selected = max(
            exact_nodes or seizure_free_nodes,
            key=lambda node: (_duration_sort_key(node), node.node_id),
        )
    else:
        raise ValueError(f"unknown duration projection variant: {variant_name}")

    return _projection_from_node(
        selected,
        rationale=f"Projected with diagnostic seizure-free duration policy {variant_name}.",
        policy_name=f"gan2026_state_graph_projection_ablation_{variant_name}",
    )


def _projection_from_node(
    node: StateGraphNode,
    *,
    rationale: str,
    policy_name: str,
    final_label_override: str | None = None,
) -> GanGraphProjection:
    record = label_to_frequency_record(final_label_override or node.normalized_label or "unknown")
    return GanGraphProjection(
        final_label=record.normalized_label,
        final_kind=record.kind,
        monthly_frequency=record.monthly_frequency,
        selected_node_ids=(node.node_id,),
        rationale=rationale,
        evidence=node.evidence.text,
        projection_policy=policy_name,
    )


def _usable_seizure_free_nodes(graph: ClinicalFrequencyStateGraph) -> list[StateGraphNode]:
    return [
        node
        for node in graph.nodes
        if node.semantic_kind is FrequencyLabelKind.SEIZURE_FREE
        and node.assertion_status == "asserted"
        and not node.graph_errors
    ]


def _variant_result(projection: GanGraphProjection, *, gold_label: str) -> dict[str, Any]:
    return {
        **projection.model_dump(mode="json"),
        "correct": projection.final_label == gold_label,
        "selected_seizure_free": projection.final_kind is FrequencyLabelKind.SEIZURE_FREE,
    }


def _summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    row_sources = Counter(str(row["source"]) for row in rows)
    failure_modes = Counter(str(row["failure_mode"]) for row in rows)
    variants = {
        variant.name: _variant_summary(rows, variant.name)
        for variant in DURATION_PROJECTION_VARIANTS
    }
    row_best = {str(row["source_row_index"]): _best_non_oracle_variants(row) for row in rows}
    return {
        "row_sources": dict(sorted(row_sources.items())),
        "failure_modes": dict(sorted(failure_modes.items())),
        "variants": variants,
        "row_best_non_oracle": row_best,
    }


def _variant_summary(rows: Sequence[Mapping[str, Any]], variant_name: str) -> dict[str, Any]:
    return {
        "exact_matches": sum(bool(row["variant_results"][variant_name]["correct"]) for row in rows),
        "selected_seizure_free_rows": sum(
            bool(row["variant_results"][variant_name]["selected_seizure_free"]) for row in rows
        ),
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
        for variant in DURATION_PROJECTION_VARIANTS
        if variant.name != "oracle_exact_seizure_free_node"
        and bool(row["variant_results"][variant.name]["correct"])
    ]
    if correct:
        return correct
    return [
        variant.name
        for variant in DURATION_PROJECTION_VARIANTS
        if variant.name != "oracle_exact_seizure_free_node"
        and row["variant_results"][variant.name]["final_label"]
        != row["variant_results"]["baseline_v0"]["final_label"]
    ]


def _failure_mode(
    *,
    baseline: Mapping[str, Any],
    exact_gold_nodes: Sequence[StateGraphNode],
    seizure_free_nodes: Sequence[StateGraphNode],
) -> str:
    if baseline["final_kind"] != FrequencyLabelKind.SEIZURE_FREE.value:
        return "non_seizure_free_selected"
    if exact_gold_nodes:
        return "exact_seizure_free_node_not_selected"
    if any(_duration_record(node.normalized_label or "")["numeric"] for node in seizure_free_nodes):
        return "numeric_duration_present_but_gold_absent"
    return "only_broad_duration_nodes"


def _node_summary(
    node: StateGraphNode,
    *,
    gold_normalized_label: str,
) -> dict[str, Any]:
    return {
        "node_id": node.node_id,
        "normalized_label": node.normalized_label,
        "duration": _duration_record(node.normalized_label or ""),
        "exact_gold_match": node.normalized_label == gold_normalized_label,
        "evidence": node.evidence.text,
        "rule_id": node.rule_id,
    }


def _duration_sort_key(node: StateGraphNode) -> tuple[int, float]:
    duration = _duration_record(node.normalized_label or "")
    return int(duration["known"]), float(duration["months"])


def _numeric_duration_sort_key(node: StateGraphNode) -> tuple[int, float]:
    duration = _duration_record(node.normalized_label or "")
    return int(duration["numeric"]), float(duration["months"])


def _month_bucket_duration_sort_key(node: StateGraphNode) -> tuple[int, int, float]:
    duration = _duration_record(node.normalized_label or "")
    is_broad_month = duration["known"] and not duration["numeric"] and duration["unit"] == "month"
    is_numeric_month = duration["known"] and duration["numeric"] and duration["unit"] == "month"
    return int(is_broad_month), int(is_numeric_month), -float(duration["months"])


def _month_bucket_diagnostic_label(node: StateGraphNode) -> str | None:
    duration = _duration_record(node.normalized_label or "")
    if (
        duration["numeric"]
        and duration["unit"] == "month"
        and duration["amount"] is not None
        and int(duration["amount"]) != 1
    ):
        return f"seizure free for {duration['amount']} months"
    return None


def _duration_record(label: str) -> dict[str, Any]:
    match = re.search(
        r"\bseizure free for (?P<amount>\d+|multiple) "
        r"(?P<unit>day|week|month|year)s?\b",
        label,
    )
    if not match:
        return {"known": False, "numeric": False, "amount": None, "unit": None, "months": -1.0}
    amount_text = match.group("amount")
    unit = match.group("unit")
    numeric = amount_text.isdigit()
    if numeric:
        amount = int(amount_text)
        months = _duration_months(amount, unit)
    else:
        amount = None
        months = {
            "day": 0.5,
            "week": 1.0,
            "month": 6.0,
            "year": 24.0,
        }[unit]
    return {
        "known": True,
        "numeric": numeric,
        "amount": amount,
        "unit": unit,
        "months": months,
    }


def _duration_months(amount: int, unit: str) -> float:
    if unit == "day":
        return amount / 30.0
    if unit == "week":
        return amount / 4.345
    if unit == "month":
        return float(amount)
    if unit == "year":
        return float(amount * 12)
    raise ValueError(f"unknown duration unit: {unit}")


def main(argv: Sequence[str] | None = None) -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
        load_jsonl_rows,
    )

    from . import projection_arbitration_ablation

    parser = argparse.ArgumentParser(
        description="Replay Gan 2026 seizure-free duration projection ablations."
    )
    parser.add_argument("--source-jsonl", type=Path)
    parser.add_argument("--graph-key", default="graph")
    parser.add_argument("--artifact-kind")
    parser.add_argument("--report-title")
    parser.add_argument("--source-artifact-override")
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    if args.source_jsonl:
        source_rows = load_jsonl_rows(args.source_jsonl)
    else:
        source_rows = projection_arbitration_ablation.load_default_ablation_rows()
    rows, metadata = run_seizure_free_duration_ablation(
        source_rows,
        split="validation_hard_slices",
        split_manifest="gan2026_split_v1",
        graph_key=args.graph_key,
        artifact_kind=args.artifact_kind
        or "gan2026_state_graph_seizure_free_duration_projection_ablation",
        report_title=args.report_title
        or "Gan 2026 State-Graph Seizure-Free Duration Projection Ablation",
        source_artifact_override=args.source_artifact_override,
    )
    write_jsonl_rows(rows, args.jsonl)
    write_duration_ablation_json(metadata, args.json)
    write_duration_ablation_report(
        rows,
        metadata,
        args.markdown,
        jsonl_path=args.jsonl,
        json_path=args.json,
    )
    print(json.dumps(metadata["summary"], sort_keys=True))


def _baseline_projection_label(row: Mapping[str, Any]) -> str:
    value = row.get("baseline_projection_label")
    if value is not None:
        return str(value)
    projection = row.get("baseline_projection")
    if isinstance(projection, Mapping):
        return str(projection.get("final_label") or "")
    projection = row.get("replayed_projection")
    if isinstance(projection, Mapping):
        return str(projection.get("final_label") or "")
    variant_results = row.get("variant_results")
    if isinstance(variant_results, Mapping):
        baseline = variant_results.get("baseline_v0")
        if isinstance(baseline, Mapping):
            return str(baseline.get("final_label") or "")
    return ""


if __name__ == "__main__":
    main()
