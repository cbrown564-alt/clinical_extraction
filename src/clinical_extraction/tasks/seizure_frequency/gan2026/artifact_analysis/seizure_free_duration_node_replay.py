"""Replay validation-only seizure-free duration node construction."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
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
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    ClinicalFrequencyStateGraph,
    EvidenceSpan,
    GraphNodeKind,
    StateGraphNode,
    graph_node_labels,
    project_graph_to_gan,
)

DEFAULT_SOURCE_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_"
    "ablation_2026-06-02.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_"
    "2026-06-02.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_"
    "2026-06-02.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_"
    "2026-06-02.md"
)

TARGET_ROW_IDS: frozenset[int] = frozenset(
    {
        3118,
        3137,
        4839,
        4842,
        4951,
        5040,
        5082,
        5092,
        5110,
        5121,
        5136,
        5141,
        5197,
        5210,
        5221,
        5345,
        5379,
        5406,
    }
)


@dataclass(frozen=True)
class DurationNodeCandidate:
    label: str
    evidence: str
    rule_id: str
    rule_taxonomy: str


def run_duration_node_replay(
    records: Sequence[GanFrequencyRecord],
    source_rows: Sequence[Mapping[str, Any]],
    *,
    split: str,
    split_manifest: str,
    source_artifact: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Add validation-only seizure-free duration nodes and replay diagnostics."""

    records_by_source = {record.source_row_index: record for record in records}
    rows: list[dict[str, Any]] = []
    for source_row in _target_source_rows(source_rows):
        source_row_index = int(source_row["source_row_index"])
        rows.append(
            _replay_row(
                records_by_source[source_row_index],
                source_row,
                split=split,
                split_manifest=split_manifest,
            )
        )

    metadata = {
        "artifact_kind": "gan2026_state_graph_seizure_free_duration_node_replay",
        "date": "2026-06-02",
        "pipeline_family": "hybrid_clinical_frequency_state_graph",
        "split": split,
        "split_manifest": split_manifest,
        "row_count": len(rows),
        "source_artifact": source_artifact,
        "graph_builder": (
            "saved_gan2026_state_graph_projection_v0 + seizure_free_duration_node_normalization_v0"
        ),
        "projection_policy": "gan2026_state_graph_projection_v0",
        "claim_language": (
            "Diagnostic validation-cycle graph-node replay only. The node builder "
            "adds exact-evidence seizure-free duration candidates outside frozen "
            "rules_only_v1, scorer normalization, and production projection policy; "
            "unchanged-projection metrics are reported separately."
        ),
        "summary": _summary(rows),
    }
    return rows, metadata


def write_duration_node_replay_json(metadata: Mapping[str, Any], path: Path) -> None:
    """Write replay metadata as JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_duration_node_replay_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    """Write a compact Markdown report for the node replay."""

    summary = metadata["summary"]
    coverage = summary["node_coverage"]
    evidence = summary["evidence"]
    projection = summary["unchanged_projection"]
    lines = [
        "# Gan 2026 State-Graph Seizure-Free Duration Node Replay",
        "",
        "Diagnostic only: this is validation-cycle graph-node construction replay, "
        "not a benchmark result, scorer change, or production projection-policy promotion.",
        "",
        f"- Source artifact: `{metadata['source_artifact']}`",
        f"- Split: `{metadata['split']}`",
        f"- Split manifest: `{metadata['split_manifest']}`",
        f"- Rows: {metadata['row_count']}",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Node Coverage",
        "",
        f"- New duration nodes: {coverage['new_duration_nodes']}",
        f"- Rows with new duration nodes: {coverage['rows_with_new_duration_nodes']}/"
        f"{metadata['row_count']}",
        f"- Baseline exact gold duration nodes: "
        f"{coverage['baseline_exact_gold_duration_rows']}/{metadata['row_count']}",
        f"- Replayed exact gold duration nodes: "
        f"{coverage['replayed_exact_gold_duration_rows']}/{metadata['row_count']}",
        f"- Month-scale representability: "
        f"{coverage['month_scale_representable_rows']}/{metadata['row_count']}",
        f"- Month-scale representability gains: {coverage['month_scale_representability_gains']}",
        f"- Rows still only over-broad year: {coverage['still_only_over_broad_year_rows']}",
        "",
        "## Evidence Validity",
        "",
        f"- Exact-evidence-valid nodes: {evidence['exact_evidence_valid_nodes']}/"
        f"{evidence['new_duration_nodes']}",
        f"- Rows with any evidence error: {evidence['rows_with_evidence_errors']}",
        "",
        "## Unchanged Projection Replay",
        "",
        f"- Exact duration matches after replay with unchanged projection: "
        f"{projection['exact_duration_matches']}/{metadata['row_count']}",
        f"- Projection changed from baseline: {projection['changed_from_baseline']}",
        "",
        "## Rule Families",
        "",
        "| Rule | Nodes | Taxonomy |",
        "| --- | ---: | --- |",
    ]
    for rule, count in sorted(summary["rule_counts"].items()):
        lines.append(f"| `{rule}` | {count} | {summary['rule_taxonomy'].get(rule, '')} |")

    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Source row | Gold | Failure mode | New nodes | Exact gold node | "
            "Month-scale gain | Baseline projection | Replayed projection |",
            "| ---: | --- | --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['source_row_index']} | {row['gold_normalized_label']} | "
            f"{row['source_failure_mode']} | {row['new_duration_node_count']} | "
            f"{row['replayed_exact_gold_duration_node_present']} | "
            f"{row['month_scale_representability_gain']} | "
            f"{row['baseline_projection']['final_label']} | "
            f"{row['replayed_projection']['final_label']} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _target_source_rows(rows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    selected = [
        row
        for row in rows
        if int(row["source_row_index"]) in TARGET_ROW_IDS
        and row.get("gold_label_kind") == FrequencyLabelKind.SEIZURE_FREE.value
    ]
    return sorted(selected, key=lambda row: int(row["source_row_index"]))


def _replay_row(
    record: GanFrequencyRecord,
    source_row: Mapping[str, Any],
    *,
    split: str,
    split_manifest: str,
) -> dict[str, Any]:
    baseline_graph = ClinicalFrequencyStateGraph.model_validate(source_row["graph"])
    new_nodes = _duration_nodes(record, baseline_graph)
    replayed_graph = _append_nodes(baseline_graph, new_nodes)
    baseline_projection = project_graph_to_gan(baseline_graph)
    replayed_projection = project_graph_to_gan(replayed_graph)
    baseline_exact = _exact_gold_duration_node_present(
        baseline_graph,
        record.gold_normalized_label,
    )
    replayed_exact = _exact_gold_duration_node_present(
        replayed_graph,
        record.gold_normalized_label,
    )
    baseline_month = _month_scale_representable(
        baseline_graph,
        record.gold_normalized_label,
    )
    replayed_month = _month_scale_representable(
        replayed_graph,
        record.gold_normalized_label,
    )
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "split_manifest": split_manifest,
        "row_ok": record.row_ok,
        "gold_label": record.gold_label,
        "gold_normalized_label": record.gold_normalized_label,
        "gold_label_kind": record.gold_label_kind.value,
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "source_failure_mode": str(
            source_row.get("failure_mode") or source_row.get("failure_family") or ""
        ),
        "source_artifact": str(source_row.get("source_artifact") or ""),
        "baseline_exact_gold_duration_node_present": baseline_exact,
        "replayed_exact_gold_duration_node_present": replayed_exact,
        "baseline_month_scale_representable": baseline_month,
        "replayed_month_scale_representable": replayed_month,
        "month_scale_representability_gain": (not baseline_month and replayed_month),
        "still_only_over_broad_year": _still_only_over_broad_year(
            replayed_graph,
            record.gold_normalized_label,
        ),
        "new_duration_node_count": len(new_nodes),
        "new_duration_nodes": [node.model_dump(mode="json") for node in new_nodes],
        "baseline_graph": baseline_graph.model_dump(mode="json"),
        "replayed_graph": replayed_graph.model_dump(mode="json"),
        "baseline_graph_labels": _labels(baseline_graph),
        "replayed_graph_labels": _labels(replayed_graph),
        "baseline_projection": baseline_projection.model_dump(mode="json"),
        "replayed_projection": replayed_projection.model_dump(mode="json"),
        "projection_changed_from_baseline": (
            replayed_projection.final_label != baseline_projection.final_label
        ),
        "projection_exact_duration_match": (
            replayed_projection.final_label == record.gold_normalized_label
        ),
    }


def _duration_nodes(
    record: GanFrequencyRecord,
    baseline_graph: ClinicalFrequencyStateGraph,
) -> tuple[StateGraphNode, ...]:
    candidates = _duration_node_candidates(record.note_text)
    seen_existing = {
        (node.normalized_label, node.evidence.text.lower())
        for node in baseline_graph.nodes
        if node.semantic_kind is FrequencyLabelKind.SEIZURE_FREE
    }
    accepted: list[StateGraphNode] = []
    seen_new: set[tuple[str, str]] = set()
    next_index = len(baseline_graph.nodes) + 1
    for candidate in candidates:
        parsed = label_to_frequency_record(candidate.label)
        key = (parsed.normalized_label, candidate.evidence.lower())
        if key in seen_existing or key in seen_new:
            continue
        span = locate_evidence(record.note_text, candidate.evidence)
        start_char, end_char = span if span else (None, None)
        graph_errors = () if span else ("duration_node_evidence_not_exact",)
        accepted.append(
            StateGraphNode(
                node_id=f"duration-sg-{next_index:03d}",
                kind=GraphNodeKind.SEIZURE_FREE,
                normalized_label=parsed.normalized_label,
                semantic_kind=parsed.kind,
                monthly_frequency=parsed.monthly_frequency,
                evidence=EvidenceSpan(
                    text=candidate.evidence,
                    start_char=start_char,
                    end_char=end_char,
                ),
                assertion_status="asserted",
                temporality="current",
                certainty="medium",
                rule_id=candidate.rule_id,
                graph_errors=graph_errors,
            )
        )
        seen_new.add(key)
        next_index += 1
    return tuple(accepted)


def _duration_node_candidates(note_text: str) -> tuple[DurationNodeCandidate, ...]:
    candidates: list[DurationNodeCandidate] = []
    candidates.extend(_explicit_vague_month_candidates(note_text))
    candidates.extend(_explicit_numeric_month_candidates(note_text))
    candidates.extend(_current_control_month_boundary_candidates(note_text))
    candidates.extend(_date_interval_candidates(note_text))
    return tuple(candidates)


def _explicit_vague_month_candidates(note_text: str) -> list[DurationNodeCandidate]:
    patterns = [
        r"\bno events for many months\b",
        r"\bfree of events for several months\b",
        r"\bno auras, warnings, or witnessed events for an extended period\b",
        r"\bno similar episodes reported in recent months\b",
        r"\bonly episodes without epileptic features in the past two months; "
        r"no definite epileptic events documented in this interval\b",
    ]
    return [
        DurationNodeCandidate(
            label="seizure free for multiple month",
            evidence=match.group(0),
            rule_id="seizure_free_duration_node_normalization_v0.month_vague_from_evidence",
            rule_taxonomy="seizure_frequency",
        )
        for pattern in patterns
        for match in re.finditer(pattern, note_text, flags=re.IGNORECASE)
    ]


def _explicit_numeric_month_candidates(note_text: str) -> list[DurationNodeCandidate]:
    candidates: list[DurationNodeCandidate] = []
    patterns = [
        (
            r"\babsence of events for over (?P<amount>four|five|six|\d+) months\b",
            "benchmark_format",
        ),
        (
            r"\blast had a clearly epileptic focal event approximately "
            r"(?P<amount>six|\d+) months ago\b",
            "benchmark_format",
        ),
        (
            r"\bno alerts since the last clinic review (?P<amount>three|\d+) months ago\b",
            "seizure_frequency",
        ),
    ]
    for pattern, taxonomy in patterns:
        for match in re.finditer(pattern, note_text, flags=re.IGNORECASE):
            amount = _number_token(match.group("amount"))
            evidence = match.group(0)
            candidates.append(
                DurationNodeCandidate(
                    label=f"seizure free for {amount} month",
                    evidence=evidence,
                    rule_id=(
                        "seizure_free_duration_node_normalization_v0.numeric_month_from_evidence"
                    ),
                    rule_taxonomy="general",
                )
            )
            candidates.append(
                DurationNodeCandidate(
                    label="seizure free for multiple month",
                    evidence=evidence,
                    rule_id=(
                        "seizure_free_duration_node_normalization_v0."
                        "numeric_to_broad_month_projection_surface"
                    ),
                    rule_taxonomy=taxonomy,
                )
            )
    return candidates


def _current_control_month_boundary_candidates(note_text: str) -> list[DurationNodeCandidate]:
    patterns = [
        r"\bNo seizures since last visit\b",
        r"\bSince the last appointment, the patient reports no definite seizure events\b",
        r"\bSince our last appointment, she has not experienced any seizures\b",
        r"\bNo clinical seizures observed since the initial referral\b",
        r"\bno events suggestive of seizures, warnings, or auras since last review\b",
        r"\bno auras or warnings since\b",
        r"\bSeizure freedom continues\b",
        r"\bSeizure-free since last review\b",
        r"\bremain seizure-free since the last consultation\b",
    ]
    candidates: list[DurationNodeCandidate] = []
    for pattern in patterns:
        for match in re.finditer(pattern, note_text, flags=re.IGNORECASE):
            candidates.append(
                DurationNodeCandidate(
                    label="seizure free for multiple month",
                    evidence=match.group(0),
                    rule_id=(
                        "seizure_free_duration_node_normalization_v0.since_without_date_boundary"
                    ),
                    rule_taxonomy="gan2026_specific",
                )
            )
    return candidates


def _date_interval_candidates(note_text: str) -> list[DurationNodeCandidate]:
    clinic_date = _clinic_date(note_text)
    candidates: list[DurationNodeCandidate] = []
    since_seen_pattern = re.compile(
        r"\bSince I last saw him on (?P<seen>\d{1,2} [A-Z][a-z]+ \d{4}), "
        r"he reports no further episodes suggestive of seizures\b"
    )
    for match in since_seen_pattern.finditer(note_text):
        seen_date = _parse_date(match.group("seen"))
        months = _elapsed_months(seen_date, clinic_date)
        if months is None:
            continue
        candidates.append(
            DurationNodeCandidate(
                label=f"seizure free for {max(1, round(months))} month",
                evidence=match.group(0),
                rule_id=("seizure_free_duration_node_normalization_v0.dated_since_interval"),
                rule_taxonomy="general",
            )
        )
    early_month_pattern = re.compile(
        r"\bthere have been no further events suggestive of seizures; "
        r"she describes the last episode as occurring in early (?P<month>[A-Z][a-z]+)\b"
    )
    for match in early_month_pattern.finditer(note_text):
        if clinic_date is None:
            continue
        seen_date = _parse_date(f"1 {match.group('month')} {clinic_date.year}")
        months = _elapsed_months(seen_date, clinic_date)
        if months is None or months < 1:
            continue
        candidates.append(
            DurationNodeCandidate(
                label="seizure free for multiple month",
                evidence=match.group(0),
                rule_id=("seizure_free_duration_node_normalization_v0.dated_month_boundary"),
                rule_taxonomy="gan2026_specific",
            )
        )
    diary_interval_pattern = re.compile(
        r"\bfrom (?P<start>\d{2} [A-Z][a-z]+ \d{4}) to "
        r"(?P<end>\d{2} [A-Z][a-z]+ \d{4}) shows regular entries without gaps\. "
        r"Across this interval, there have been no witnessed convulsive episodes\b"
    )
    for match in diary_interval_pattern.finditer(note_text):
        start = _parse_date(match.group("start"))
        end = _parse_date(match.group("end"))
        months = _elapsed_months(start, end)
        if months is None or months < 1:
            continue
        evidence = match.group(0)
        candidates.append(
            DurationNodeCandidate(
                label=f"seizure free for {max(1, round(months))} month",
                evidence=evidence,
                rule_id=("seizure_free_duration_node_normalization_v0.dated_diary_interval"),
                rule_taxonomy="general",
            )
        )
        candidates.append(
            DurationNodeCandidate(
                label="seizure free for multiple month",
                evidence=evidence,
                rule_id=(
                    "seizure_free_duration_node_normalization_v0."
                    "numeric_to_broad_month_projection_surface"
                ),
                rule_taxonomy="benchmark_format",
            )
        )
    return candidates


def _clinic_date(note_text: str) -> date | None:
    match = re.search(r"\bClinic Date:\s*(\d{1,2} [A-Z][a-z]+ \d{4})\b", note_text)
    if not match:
        return None
    return _parse_date(match.group(1))


def _parse_date(text: str) -> date | None:
    try:
        return datetime.strptime(text, "%d %B %Y").date()
    except ValueError:
        return None


def _elapsed_months(start: date | None, end: date | None) -> float | None:
    if start is None or end is None or end <= start:
        return None
    return (end - start).days / 30.4375


def _number_token(token: str) -> int:
    return {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
    }.get(token.lower(), int(token) if token.isdigit() else 0)


def _append_nodes(
    graph: ClinicalFrequencyStateGraph,
    nodes: Sequence[StateGraphNode],
) -> ClinicalFrequencyStateGraph:
    all_nodes = (*graph.nodes, *nodes)
    return graph.model_copy(
        update={
            "nodes": all_nodes,
            "graph_builder": (f"{graph.graph_builder}+seizure_free_duration_node_normalization_v0"),
            "competing_hypothesis_node_ids": graph.competing_hypothesis_node_ids,
            "missing_variable_flags": graph.missing_variable_flags,
            "metadata": {
                **graph.metadata,
                "seizure_free_duration_node_normalization_v0_nodes": len(nodes),
            },
        }
    )


def _exact_gold_duration_node_present(
    graph: ClinicalFrequencyStateGraph,
    gold_normalized_label: str,
) -> bool:
    return any(
        node.semantic_kind is FrequencyLabelKind.SEIZURE_FREE
        and not node.graph_errors
        and node.normalized_label == gold_normalized_label
        for node in graph.nodes
    )


def _month_scale_representable(
    graph: ClinicalFrequencyStateGraph,
    gold_normalized_label: str,
) -> bool:
    gold_duration = _duration_record(gold_normalized_label)
    if gold_duration["unit"] != "month":
        return _exact_gold_duration_node_present(graph, gold_normalized_label)
    return any(
        node.semantic_kind is FrequencyLabelKind.SEIZURE_FREE
        and not node.graph_errors
        and _duration_record(node.normalized_label or "")["unit"] == "month"
        for node in graph.nodes
    )


def _still_only_over_broad_year(
    graph: ClinicalFrequencyStateGraph,
    gold_normalized_label: str,
) -> bool:
    gold_duration = _duration_record(gold_normalized_label)
    if gold_duration["unit"] != "month":
        return False
    seizure_free_durations = [
        _duration_record(node.normalized_label or "")
        for node in graph.nodes
        if node.semantic_kind is FrequencyLabelKind.SEIZURE_FREE and not node.graph_errors
    ]
    return bool(seizure_free_durations) and all(
        duration["unit"] == "year" for duration in seizure_free_durations
    )


def _labels(graph: ClinicalFrequencyStateGraph) -> list[dict[str, str | None]]:
    return [{"kind": kind.value, "label": label} for kind, label in graph_node_labels(graph)]


def _summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rule_counts = Counter(
        str(node["rule_id"]) for row in rows for node in row["new_duration_nodes"]
    )
    rule_taxonomy: dict[str, str] = {}
    for row in rows:
        for node in row["new_duration_nodes"]:
            rule_id = str(node["rule_id"])
            rule_taxonomy.setdefault(rule_id, _taxonomy_for_rule(rule_id))
    new_nodes = sum(int(row["new_duration_node_count"]) for row in rows)
    exact_nodes = sum(
        not node["graph_errors"] for row in rows for node in row["new_duration_nodes"]
    )
    return {
        "node_coverage": {
            "new_duration_nodes": new_nodes,
            "rows_with_new_duration_nodes": sum(
                int(row["new_duration_node_count"]) > 0 for row in rows
            ),
            "baseline_exact_gold_duration_rows": sum(
                bool(row["baseline_exact_gold_duration_node_present"]) for row in rows
            ),
            "replayed_exact_gold_duration_rows": sum(
                bool(row["replayed_exact_gold_duration_node_present"]) for row in rows
            ),
            "month_scale_representable_rows": sum(
                bool(row["replayed_month_scale_representable"]) for row in rows
            ),
            "month_scale_representability_gains": sum(
                bool(row["month_scale_representability_gain"]) for row in rows
            ),
            "still_only_over_broad_year_rows": sum(
                bool(row["still_only_over_broad_year"]) for row in rows
            ),
        },
        "evidence": {
            "new_duration_nodes": new_nodes,
            "exact_evidence_valid_nodes": exact_nodes,
            "rows_with_evidence_errors": sum(
                any(node["graph_errors"] for node in row["new_duration_nodes"]) for row in rows
            ),
        },
        "unchanged_projection": {
            "exact_duration_matches": sum(
                bool(row["projection_exact_duration_match"]) for row in rows
            ),
            "changed_from_baseline": sum(
                bool(row["projection_changed_from_baseline"]) for row in rows
            ),
        },
        "source_failure_modes": dict(
            sorted(Counter(str(row["source_failure_mode"]) for row in rows).items())
        ),
        "rule_counts": dict(sorted(rule_counts.items())),
        "rule_taxonomy": rule_taxonomy,
    }


def _taxonomy_for_rule(rule_id: str) -> str:
    if rule_id.endswith(".numeric_month_from_evidence"):
        return "general"
    if rule_id.endswith(".month_vague_from_evidence"):
        return "seizure_frequency"
    if rule_id.endswith(".numeric_to_broad_month_projection_surface"):
        return "benchmark_format"
    if rule_id.endswith(".since_without_date_boundary"):
        return "gan2026_specific"
    if rule_id.endswith(".dated_since_interval"):
        return "general"
    if rule_id.endswith(".dated_month_boundary"):
        return "gan2026_specific"
    if rule_id.endswith(".dated_diary_interval"):
        return "general"
    return "unknown"


def _duration_record(label: str) -> dict[str, Any]:
    match = re.search(
        r"\bseizure free for (?P<amount>\d+|multiple) "
        r"(?P<unit>day|week|month|year)s?\b",
        label,
    )
    if not match:
        return {"known": False, "numeric": False, "amount": None, "unit": None}
    amount_text = match.group("amount")
    return {
        "known": True,
        "numeric": amount_text.isdigit(),
        "amount": int(amount_text) if amount_text.isdigit() else None,
        "unit": match.group("unit"),
    }


def _load_records() -> tuple[list[GanFrequencyRecord], str]:
    records = load_records_for_split("validation")
    manifest = load_split_manifest()
    return records, str(manifest.get("manifest_version", "gan2026_split_v1"))


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Replay Gan 2026 seizure-free duration node construction."
    )
    parser.add_argument("--source-jsonl", type=Path, default=DEFAULT_SOURCE_JSONL_PATH)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    records, split_manifest = _load_records()
    source_rows = _load_graph_source_rows(args.source_jsonl)
    rows, metadata = run_duration_node_replay(
        records,
        source_rows,
        split="validation_hard_slices",
        split_manifest=split_manifest,
        source_artifact=str(args.source_jsonl),
    )
    write_jsonl_rows(rows, args.jsonl)
    write_duration_node_replay_json(metadata, args.json)
    write_duration_node_replay_report(
        rows,
        metadata,
        args.markdown,
        jsonl_path=args.jsonl,
        json_path=args.json,
    )
    print(json.dumps(metadata["summary"], sort_keys=True))


def _load_graph_source_rows(path: Path) -> list[dict[str, Any]]:
    from . import projection_arbitration_ablation

    rows = load_jsonl_rows(path)
    if rows and "graph" in rows[0]:
        return rows
    return projection_arbitration_ablation.load_default_ablation_rows()


if __name__ == "__main__":
    main()
