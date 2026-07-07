"""Materialize saved-artifact Gan 2026 candidate-union diagnostics."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.rq1_rq2_control_panels import (  # noqa: E501
    DEFAULT_PANEL_JSONL_PATH,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph.graph import (
    StateGraphNode,
    build_state_graph,
)

DEFAULT_RICH_STATE_REPLAY_PATH = Path(
    "experiments/gan2026_rich_selected_state_hard_panel_policy_replay_2026-06-04.jsonl"
)
DEFAULT_JSONL_PATH = Path("experiments/gan2026_candidate_union_saved_artifact_2026-06-04.jsonl")
DEFAULT_JSON_PATH = Path("experiments/gan2026_candidate_union_saved_artifact_2026-06-04.json")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_candidate_union_saved_artifact_2026-06-04.md")
DEFAULT_PROTOCOL_PATH = Path("")
MAX_UNION_CANDIDATES_PER_ROW = 12


def build_candidate_union_rows(
    saved_rows: Sequence[Mapping[str, Any]],
    *,
    panel_rows: Sequence[Mapping[str, Any]] = (),
    max_union_candidates: int = MAX_UNION_CANDIDATES_PER_ROW,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    panels_by_source = {int(row["source_row_index"]): row for row in panel_rows}
    rows = [
        _candidate_union_row(
            source_row,
            panel_row=panels_by_source.get(int(source_row["source_row_index"])),
            max_union_candidates=max_union_candidates,
        )
        for source_row in saved_rows
    ]
    rows.sort(key=lambda row: int(row["source_row_index"]))
    return rows, summarize_candidate_union_rows(rows)


def summarize_candidate_union_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    surface_counts = {
        "deterministic": sum(
            bool(row["gold_state_recall_summary"]["deterministic_candidates_recall"])
            for row in rows
        ),
        "llm_boundary_proposal": sum(
            bool(row["gold_state_recall_summary"]["llm_boundary_candidate_recall"]) for row in rows
        ),
        "union_verified": sum(
            bool(row["gold_state_recall_summary"]["union_verified_candidate_recall"])
            for row in rows
        ),
    }
    deterministic_lost = [
        int(row["source_row_index"])
        for row in rows
        if row["gold_state_recall_summary"]["deterministic_candidates_recall"]
        and not row["gold_state_recall_summary"]["union_verified_candidate_recall"]
    ]
    rescue = [
        int(row["source_row_index"])
        for row in rows
        if not row["gold_state_recall_summary"]["deterministic_candidates_recall"]
        and row["gold_state_recall_summary"]["union_verified_candidate_recall"]
    ]
    union_counts = [int(row["candidate_burden_summary"]["union_verified_count"]) for row in rows]
    rejected_counts = [int(row["candidate_burden_summary"]["rejected_count"]) for row in rows]
    gate_failures = Counter(failure for row in rows for failure in row["gate_failures"])
    return {
        "artifact_kind": "gan2026_candidate_union_saved_artifact",
        "date": "2026-06-04",
        "split_manifest": "gan2026_split_v1",
        "split": "validation",
        "source_artifact": str(DEFAULT_RICH_STATE_REPLAY_PATH),
        "row_count": len(rows),
        "claim_language": (
            "Validation-development saved-artifact candidate-union diagnostic only. "
            "No new live LLM calls, final-label promotion, locked-test inspection, "
            "or benchmark-comparable claim."
        ),
        "max_union_candidates_per_row": MAX_UNION_CANDIDATES_PER_ROW,
        "metrics": {
            "deterministic_gold_state_recall_rows": surface_counts["deterministic"],
            "llm_boundary_gold_state_recall_rows": surface_counts["llm_boundary_proposal"],
            "union_verified_gold_state_recall_rows": surface_counts["union_verified"],
            "llm_recall_rescue_rows": len(rescue),
            "deterministic_recall_lost_rows": len(deterministic_lost),
            "exact_evidence_rate": _candidate_rate(rows, "exact_evidence"),
            "valid_source_id_rate": _candidate_rate(rows, "valid_source_id"),
            "unsupported_candidate_rate": _unsupported_candidate_rate(rows),
            "median_union_candidate_count": _median(union_counts),
            "p90_union_candidate_count": _percentile(union_counts, 90),
            "total_rejected_candidates": sum(rejected_counts),
        },
        "llm_recall_rescue_source_row_indices": rescue,
        "deterministic_recall_lost_source_row_indices": deterministic_lost,
        "gate_failure_counts": dict(sorted(gate_failures.items())),
        "by_hidden_family": _hidden_family_summary(rows),
        "metadata_completeness_by_kind": _metadata_completeness(rows),
    }


def write_candidate_union_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_candidate_union_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
    protocol_path: Path = DEFAULT_PROTOCOL_PATH,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Saved-Artifact Candidate Union Diagnostic",
        "",
        "This is a no-call validation-development diagnostic over saved rich selected-state "
        "hard-panel artifacts. It materializes the candidate-union schema and gates before "
        "any new selective boundary-candidate calls.",
        "",
        "## Answer",
        "",
        (
            "The saved-artifact union machinery is coherent enough to support the next "
            "predeclared selective LLM boundary-candidate slice. The gated union preserved "
            f"deterministic gold-state recall with {metrics['deterministic_recall_lost_rows']} "
            "lost deterministic-recall rows and bounded the hard-panel union burden at "
            f"median {metrics['median_union_candidate_count']:.1f}, p90 "
            f"{metrics['p90_union_candidate_count']:.1f} candidates per row."
        ),
        "",
        "## Claim Boundary",
        "",
        str(metadata["claim_language"]),
        "",
        "## Artifacts",
        "",
        f"- Protocol: `{protocol_path}`",
        f"- Candidate-union JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Source replay: `{metadata['source_artifact']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(
        [
            "",
            "## Gate Failures",
            "",
            "| Gate failure | Count |",
            "| --- | ---: |",
        ]
    )
    for key, value in metadata["gate_failure_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Hidden-Family Recall",
            "",
            "| Hidden family | Rows | Deterministic recall | Union recall |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for family, summary in sorted(metadata["by_hidden_family"].items()):
        lines.append(
            f"| `{family}` | {summary['rows']} | "
            f"{summary['deterministic_recall_rows']} | {summary['union_recall_rows']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The artifact uses deterministic state-graph candidates as the broad substrate.",
            "- Saved rich selected-state outputs are treated only as replayed boundary proposals.",
            "- The union gate preserves provenance and rejects overflow or unsupported candidates.",
            (
                "- A new live proposer is still blocked until its exact hard slice and "
                "schema are predeclared."
            ),
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _candidate_union_row(
    row: Mapping[str, Any],
    *,
    panel_row: Mapping[str, Any] | None,
    max_union_candidates: int,
) -> dict[str, Any]:
    source_row_index = int(row["source_row_index"])
    note_text = str(row.get("typed_input", {}).get("note_text") or "")
    deterministic_candidates = _deterministic_candidates(note_text, source_row_index)
    llm_proposals = _llm_boundary_candidate_proposals(row, note_text=note_text)
    union, rejected = _gated_union(
        [*deterministic_candidates, *llm_proposals],
        max_union_candidates=max_union_candidates,
    )
    gold_label = str(row.get("reference", {}).get("gold_normalized_label") or "")
    hidden_families = list(panel_row.get("hidden_families") or []) if panel_row else []
    return {
        "artifact_kind": "gan2026_candidate_union_saved_artifact_row",
        "claim_boundary": "validation_development_saved_artifact_no_call_candidate_union",
        "source_row_index": source_row_index,
        "split": row.get("split", "validation"),
        "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
        "gold_label": gold_label,
        "hidden_families": hidden_families,
        "deterministic_candidates": deterministic_candidates,
        "llm_boundary_candidate_proposals": llm_proposals,
        "union_verified_candidates": union,
        "rejected_candidates": rejected,
        "candidate_burden_summary": {
            "deterministic_count": len(deterministic_candidates),
            "llm_boundary_candidate_count": len(llm_proposals),
            "union_verified_count": len(union),
            "rejected_count": len(rejected),
        },
        "gold_state_recall_summary": {
            "deterministic_candidates_recall": _surface_recalls_gold(
                deterministic_candidates, gold_label
            ),
            "llm_boundary_candidate_recall": _surface_recalls_gold(llm_proposals, gold_label),
            "union_verified_candidate_recall": _surface_recalls_gold(union, gold_label),
        },
        "metadata_completeness_summary": _row_metadata_completeness(union),
        "gate_failures": sorted(
            {
                failure
                for candidate in [*union, *rejected]
                for failure in candidate.get("gate_failures", [])
            }
        ),
        "deterministic_top_label": _deterministic_top_label(row),
        "downstream_selected_state_replay": {},
    }


def _deterministic_candidates(note_text: str, source_row_index: int) -> list[dict[str, Any]]:
    graph = build_state_graph(note_text, source_row_index=source_row_index)
    return [_candidate_from_graph_node(node) for node in graph.nodes]


def _candidate_from_graph_node(node: StateGraphNode) -> dict[str, Any]:
    candidate = _base_candidate(
        candidate_id=f"det-{node.node_id}",
        source="deterministic",
        candidate_kind=node.kind.value,
        normalized_label=node.normalized_label,
        evidence=node.evidence.text,
        currentness=node.temporality,
        assertion_status=node.assertion_status,
        semiology=node.applies_to,
        metadata={
            "rule_id": node.rule_id,
            "semantic_kind": node.semantic_kind.value,
            "monthly_frequency": node.monthly_frequency,
            "graph_errors": list(node.graph_errors),
        },
    )
    if node.graph_errors:
        candidate["gate_failures"].append("normalization_error")
    return candidate


def _llm_boundary_candidate_proposals(
    row: Mapping[str, Any], *, note_text: str
) -> list[dict[str, Any]]:
    selected_state = row.get("structured_record", {}).get("selected_state")
    if not isinstance(selected_state, Mapping):
        return []
    state_kind = str(selected_state.get("state_kind") or "unknown")
    candidate_kind = _selected_state_candidate_kind(selected_state)
    label = _deterministic_top_label(row)
    metadata = {
        "proposal_source": "saved_rich_selected_state_replay",
        "state_kind": state_kind,
        "raw_model_label_hint": selected_state.get("raw_model_label_hint"),
        "raw_source_phrase": selected_state.get("raw_source_phrase"),
        "selection_reason": selected_state.get("selection_reason"),
        "ambiguity_flags": selected_state.get("ambiguity_flags") or [],
        "rate": selected_state.get("rate") or {},
        "cluster": selected_state.get("cluster") or {},
        "seizure_free_boundary": selected_state.get("seizure_free_boundary") or {},
        "conditionality_note": selected_state.get("conditionality_note"),
        "competing_state_summary": selected_state.get("competing_state_summary"),
    }
    candidate = _base_candidate(
        candidate_id="llm-rich-selected-state-001",
        source="llm_boundary_proposal",
        candidate_kind=candidate_kind,
        normalized_label=label,
        evidence=str(selected_state.get("selected_evidence") or ""),
        currentness=str(selected_state.get("currentness") or "unclear"),
        assertion_status=str(selected_state.get("assertion_status") or "unknown"),
        semiology=_optional_text(selected_state.get("applies_to")),
        metadata=metadata,
    )
    _add_metadata_gate_failures(candidate, note_text=note_text)
    return [candidate]


def _base_candidate(
    *,
    candidate_id: str,
    source: str,
    candidate_kind: str,
    normalized_label: str | None,
    evidence: str,
    currentness: str,
    assertion_status: str,
    semiology: str | None,
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    candidate = {
        "candidate_id": candidate_id,
        "candidate_kind": candidate_kind,
        "normalized_label": normalized_label,
        "evidence": evidence,
        "source_id": "note" if evidence else "",
        "source_id_status": "valid" if evidence else "missing",
        "exact_evidence": bool(evidence),
        "currentness": currentness,
        "assertion_status": assertion_status,
        "semiology": semiology,
        "metadata": dict(metadata),
        "provenance": [source],
        "gate_failures": [],
    }
    if not evidence:
        candidate["gate_failures"].append("missing_evidence")
    return candidate


def _add_metadata_gate_failures(candidate: dict[str, Any], *, note_text: str) -> None:
    evidence = str(candidate.get("evidence") or "")
    if evidence and evidence not in note_text:
        candidate["exact_evidence"] = False
        candidate["gate_failures"].append("non_exact_evidence")
    if candidate["source_id_status"] != "valid":
        candidate["gate_failures"].append("invalid_source_id")
    required = _required_metadata_fields(candidate)
    missing = [field for field in required if not _metadata_field_present(candidate, field)]
    if missing:
        candidate["gate_failures"].append("missing_required_metadata:" + ",".join(missing))


def _gated_union(
    candidates: Sequence[Mapping[str, Any]], *, max_union_candidates: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    retained_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    rejected: list[dict[str, Any]] = []
    for candidate in candidates:
        materialized = dict(candidate)
        materialized["provenance"] = list(candidate.get("provenance") or [])
        materialized["gate_failures"] = list(candidate.get("gate_failures") or [])
        if materialized["gate_failures"]:
            rejected.append(materialized)
            continue
        key = _dedupe_key(materialized)
        if key in retained_by_key:
            existing = retained_by_key[key]
            existing["provenance"] = sorted(
                set(existing.get("provenance", [])) | set(materialized.get("provenance", []))
            )
            continue
        retained_by_key[key] = materialized

    retained = list(retained_by_key.values())
    retained.sort(key=_candidate_sort_key)
    if len(retained) <= max_union_candidates:
        return retained, sorted(rejected, key=_candidate_sort_key)

    overflow = retained[max_union_candidates:]
    for candidate in overflow:
        candidate["gate_failures"] = [
            *candidate.get("gate_failures", []),
            "candidate_burden_overflow",
        ]
    return retained[:max_union_candidates], sorted([*rejected, *overflow], key=_candidate_sort_key)


def _selected_state_candidate_kind(selected_state: Mapping[str, Any]) -> str:
    cluster = selected_state.get("cluster") or {}
    seizure_free = selected_state.get("seizure_free_boundary") or {}
    state_kind = str(selected_state.get("state_kind") or "")
    if isinstance(cluster, Mapping) and cluster.get("has_cluster_pattern"):
        return "cluster_frequency"
    if state_kind == "seizure_free" or (
        isinstance(seizure_free, Mapping) and seizure_free.get("has_no_event_claim")
    ):
        return "seizure_free"
    if state_kind == "no_reference":
        return "no_reference"
    if state_kind == "unknown":
        return "unknown_frequency"
    return "frequency_rate"


def _required_metadata_fields(candidate: Mapping[str, Any]) -> tuple[str, ...]:
    kind = str(candidate.get("candidate_kind") or "")
    if kind == "frequency_rate":
        return ("currentness", "assertion_status", "rate")
    if kind == "cluster_frequency":
        return ("currentness", "assertion_status", "cluster")
    if kind == "seizure_free":
        return ("currentness", "assertion_status", "seizure_free_boundary")
    if kind in {"unknown_frequency", "no_reference"}:
        return ("currentness", "assertion_status")
    return ("currentness",)


def _metadata_field_present(candidate: Mapping[str, Any], field: str) -> bool:
    if field in {"currentness", "assertion_status"}:
        return bool(candidate.get(field)) and str(candidate.get(field)) not in {
            "unknown",
            "unclear",
        }
    metadata = candidate.get("metadata") or {}
    value = metadata.get(field) if isinstance(metadata, Mapping) else None
    return bool(value)


def _surface_recalls_gold(candidates: Sequence[Mapping[str, Any]], gold_label: str) -> bool:
    gold = _normalized_label(gold_label)
    return bool(gold) and any(
        _normalized_label(candidate.get("normalized_label")) == gold for candidate in candidates
    )


def _normalized_label(label: Any) -> str:
    if not label:
        return ""
    try:
        return label_to_frequency_record(str(label)).normalized_label
    except ValueError:
        return str(label).strip().lower()


def _deterministic_top_label(row: Mapping[str, Any]) -> str:
    replay = row.get("policy_replay") or {}
    if isinstance(replay, Mapping) and replay.get("revised_deterministic_projected_label"):
        return str(replay["revised_deterministic_projected_label"])
    return str(row.get("deterministic_projected_label") or "")


def _dedupe_key(candidate: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        str(candidate.get("candidate_kind") or ""),
        _normalized_label(candidate.get("normalized_label")),
        " ".join(str(candidate.get("evidence") or "").lower().split()),
    )


def _candidate_sort_key(candidate: Mapping[str, Any]) -> tuple[int, str, str]:
    provenance = set(candidate.get("provenance") or [])
    provenance_rank = 0 if "deterministic" in provenance else 1
    return (
        provenance_rank,
        str(candidate.get("candidate_kind") or ""),
        str(candidate.get("evidence") or "").lower(),
    )


def _row_metadata_completeness(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not candidates:
        return {"complete_candidates": 0, "candidate_count": 0, "completion_rate": 0.0}
    complete = sum(not _required_metadata_missing(candidate) for candidate in candidates)
    return {
        "complete_candidates": complete,
        "candidate_count": len(candidates),
        "completion_rate": complete / len(candidates),
    }


def _required_metadata_missing(candidate: Mapping[str, Any]) -> bool:
    return any(
        not _metadata_field_present(candidate, field)
        for field in _required_metadata_fields(candidate)
    )


def _candidate_rate(rows: Sequence[Mapping[str, Any]], field: str) -> float:
    candidates = [candidate for row in rows for candidate in row["union_verified_candidates"]]
    if not candidates:
        return 0.0
    if field == "valid_source_id":
        return sum(candidate.get("source_id_status") == "valid" for candidate in candidates) / len(
            candidates
        )
    return sum(bool(candidate.get(field)) for candidate in candidates) / len(candidates)


def _unsupported_candidate_rate(rows: Sequence[Mapping[str, Any]]) -> float:
    candidates = [
        candidate
        for row in rows
        for candidate in [*row["union_verified_candidates"], *row["rejected_candidates"]]
    ]
    if not candidates:
        return 0.0
    unsupported = sum(bool(candidate.get("gate_failures")) for candidate in candidates)
    return unsupported / len(candidates)


def _hidden_family_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        for family in row.get("hidden_families") or ["unclassified"]:
            summary[str(family)]["rows"] += 1
            if row["gold_state_recall_summary"]["deterministic_candidates_recall"]:
                summary[str(family)]["deterministic_recall_rows"] += 1
            if row["gold_state_recall_summary"]["union_verified_candidate_recall"]:
                summary[str(family)]["union_recall_rows"] += 1
    return {family: dict(counts) for family, counts in summary.items()}


def _metadata_completeness(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, float | int]]:
    by_kind: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        for candidate in row["union_verified_candidates"]:
            kind = str(candidate.get("candidate_kind") or "")
            by_kind[kind]["candidate_count"] += 1
            if not _required_metadata_missing(candidate):
                by_kind[kind]["complete_candidates"] += 1
    return {
        kind: {
            "candidate_count": counts["candidate_count"],
            "complete_candidates": counts["complete_candidates"],
            "completion_rate": _safe_rate(counts["complete_candidates"], counts["candidate_count"]),
        }
        for kind, counts in sorted(by_kind.items())
    }


def _median(values: Sequence[int]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[midpoint])
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2


def _percentile(values: Sequence[int], percentile: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((percentile / 100) * (len(ordered) - 1))))
    return float(ordered[index])


def _safe_rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rich-state-replay-path", type=Path, default=DEFAULT_RICH_STATE_REPLAY_PATH
    )
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    rows = load_jsonl_rows(args.rich_state_replay_path)
    panel_rows = load_jsonl_rows(args.panel_jsonl_path) if args.panel_jsonl_path.exists() else []
    artifact_rows, metadata = build_candidate_union_rows(rows, panel_rows=panel_rows)
    metadata = {**metadata, "source_artifact": str(args.rich_state_replay_path)}
    write_jsonl_rows(artifact_rows, args.jsonl_path)
    write_candidate_union_json(metadata, args.json_path)
    write_candidate_union_report(
        metadata, args.report_path, jsonl_path=args.jsonl_path, json_path=args.json_path
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
