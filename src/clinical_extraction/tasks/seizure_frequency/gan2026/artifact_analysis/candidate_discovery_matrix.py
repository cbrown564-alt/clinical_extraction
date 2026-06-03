"""Build the Gan 2026 RQ1 candidate-discovery matrix from saved artifacts."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from statistics import median
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist

DEFAULT_ARTIFACT_PATHS = (
    Path(
        "experiments/"
        "gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_"
        "deterministic_safety_floor_v2_replay_2026-06-03.jsonl"
    ),
    Path(
        "experiments/"
        "gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_"
        "gpt41mini_v1_live_2026-06-03.jsonl"
    ),
)
DEFAULT_ATLAS_CSV_PATH = Path(
    "experiments/gan2026_hidden_family_first_failure_atlas_2026-06-03.csv"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.md"
)
RECALL_MATCH_STATUSES = {"exact_label", "purist_category", "semantic_state"}


def build_candidate_discovery_matrix(
    artifact_paths: Sequence[Path] = DEFAULT_ARTIFACT_PATHS,
    *,
    atlas_csv_path: Path | None = DEFAULT_ATLAS_CSV_PATH,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    atlas = load_atlas_lookup(atlas_csv_path) if atlas_csv_path else {}
    rows: list[dict[str, Any]] = []
    for artifact_path in artifact_paths:
        artifact_name = artifact_path.name
        for artifact_row in load_jsonl_rows(artifact_path):
            rows.extend(
                _candidate_rows_for_artifact_row(
                    artifact_row,
                    artifact_path,
                    artifact_name,
                    atlas,
                )
            )
    rows.sort(key=lambda row: (row["source_row_index"], row["generator_name"], row["candidate_id"]))
    return rows, summarize_candidate_rows(rows)


def load_atlas_lookup(path: Path) -> dict[tuple[str, int], dict[str, Any]]:
    if not path.exists():
        return {}
    lookup: dict[tuple[str, int], dict[str, Any]] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                source_row_index = int(row["source_row_index"])
            except (KeyError, TypeError, ValueError):
                continue
            families = [item for item in (row.get("hidden_families") or "").split(";") if item]
            lookup[(row.get("artifact_name") or "", source_row_index)] = {
                "hidden_families": families,
                "first_failure_owner": row.get("first_failure_owner") or "",
            }
    return lookup


def summarize_candidate_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_generator: dict[str, dict[str, Any]] = {}
    rows_by_generator: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    source_rows_by_generator: dict[str, set[int]] = defaultdict(set)
    candidate_counts: dict[tuple[str, int], int] = defaultdict(int)

    for row in rows:
        generator = str(row["generator_name"])
        source_row_index = int(row["source_row_index"])
        rows_by_generator[generator].append(row)
        source_rows_by_generator[generator].add(source_row_index)
        candidate_counts[(generator, source_row_index)] += 1

    for generator, generator_rows in sorted(rows_by_generator.items()):
        counts = [
            count
            for (row_generator, _source_row), count in candidate_counts.items()
            if row_generator == generator
        ]
        recalled_source_rows = {
            int(row["source_row_index"])
            for row in generator_rows
            if row.get("gold_match_status") in RECALL_MATCH_STATUSES
        }
        recall_rows = [
            row for row in generator_rows if row.get("gold_match_status") in RECALL_MATCH_STATUSES
        ]
        false_positive_rows = [
            row
            for row in generator_rows
            if row.get("gold_match_status") not in RECALL_MATCH_STATUSES
        ]
        exact_rows = [row for row in generator_rows if row.get("evidence_status") == "exact"]
        source_row_count = len(source_rows_by_generator[generator])
        by_generator[generator] = {
            "source_rows": source_row_count,
            "candidate_rows": len(generator_rows),
            "gold_state_recall_rows": len(recall_rows),
            "gold_state_recalled_source_rows": len(recalled_source_rows),
            "gold_state_recall_rate": _rate(len(recalled_source_rows), source_row_count),
            "false_positive_candidate_rows": len(false_positive_rows),
            "false_positive_candidates_per_note": round(
                len(false_positive_rows) / source_row_count,
                4,
            )
            if source_row_count
            else 0.0,
            "exact_evidence_rows": len(exact_rows),
            "exact_evidence_rate": _rate(len(exact_rows), len(generator_rows)),
            "candidates_per_note_median": median(counts) if counts else 0,
            "candidates_per_note_p90": _p90(counts),
        }

    return {
        "artifact_kind": "gan2026_rq1_candidate_discovery_matrix",
        "row_count": len(rows),
        "source_row_count": len({int(row["source_row_index"]) for row in rows}),
        "by_generator": by_generator,
    }


def write_matrix_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_matrix_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Gan 2026 RQ1 Candidate-Discovery Matrix",
        "",
        (
            "Replay-first component matrix for RQ1 candidate discovery. This is a "
            "validation-development artifact, not a benchmark or locked-holdout claim."
        ),
        "",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Matrix rows: {metadata['row_count']}",
        f"- Source rows represented: {metadata['source_row_count']}",
        "",
        "## Generator Summary",
        "",
        (
            "| Generator | Source rows | Candidates | Recalled source rows | Recall rate | "
            "False positives/note | Exact evidence | Exact rate | Median candidates/note | "
            "p90 candidates/note |"
        ),
        (
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
        ),
    ]
    for generator, summary in metadata["by_generator"].items():
        lines.append(
            (
                "| {generator} | {source_rows} | {candidate_rows} | "
                "{recalled_source_rows} | {recall_rate:.3f} | "
                "{false_positives_per_note:.3f} | {exact_rows} | "
                "{exact_rate:.3f} | {median_count} | {p90_count} |"
            ).format(
                generator=generator,
                source_rows=summary["source_rows"],
                candidate_rows=summary["candidate_rows"],
                recalled_source_rows=summary["gold_state_recalled_source_rows"],
                recall_rate=summary["gold_state_recall_rate"],
                false_positives_per_note=summary["false_positive_candidates_per_note"],
                exact_rows=summary["exact_evidence_rows"],
                exact_rate=summary["exact_evidence_rate"],
                median_count=summary["candidates_per_note_median"],
                p90_count=summary["candidates_per_note_p90"],
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            (
                "This matrix measures candidate recall, exact evidence, candidate burden, "
                "and metadata availability from saved artifacts. It does not measure final "
                "Purist/Pragmatic F1 and does not authorize locked-holdout use."
            ),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _candidate_rows_for_artifact_row(
    artifact_row: Mapping[str, Any],
    artifact_path: Path,
    artifact_name: str,
    atlas: Mapping[tuple[str, int], Mapping[str, Any]],
) -> list[dict[str, Any]]:
    source_row_index = int(artifact_row["source_row_index"])
    context = _row_context(artifact_row, artifact_name, source_row_index, atlas)
    candidates: list[tuple[str, Mapping[str, Any]]] = []
    component_inputs = artifact_row.get("component_inputs") or {}

    for candidate in _as_list(component_inputs.get("deterministic_candidates")):
        candidates.append(("deterministic_candidates_all", candidate))
    deterministic_top = component_inputs.get("deterministic_top")
    if isinstance(deterministic_top, Mapping):
        candidates.append(
            ("deterministic_top_candidate", _deterministic_top_candidate(deterministic_top))
        )
    state_graph_nodes = component_inputs.get("state_graph_nodes") or artifact_row.get(
        "state_graph_nodes"
    )
    for node in _as_list(state_graph_nodes):
        candidates.append(("state_graph_nodes", node))
    for candidate in _as_list(
        component_inputs.get("llm_candidates")
        or (artifact_row.get("structured_llm_candidate_record") or {}).get("candidates")
    ):
        candidates.append(("llm_candidate_selector_raw", candidate))

    selected_state = _llm_selected_state_candidate(artifact_row)
    if selected_state is not None:
        candidates.append(("llm_selected_state_or_evidence", selected_state))

    return [
        _matrix_row(generator, candidate, artifact_path, context)
        for generator, candidate in candidates
    ]


def _row_context(
    artifact_row: Mapping[str, Any],
    artifact_name: str,
    source_row_index: int,
    atlas: Mapping[tuple[str, int], Mapping[str, Any]],
) -> dict[str, Any]:
    reference = artifact_row.get("reference") or {}
    note_text = (
        (artifact_row.get("component_inputs") or {}).get("note_text")
        or (artifact_row.get("typed_input") or {}).get("note_text")
        or ""
    )
    atlas_row = (
        atlas.get((artifact_name, source_row_index))
        or atlas.get(("", source_row_index))
        or {}
    )
    return {
        "source_row_index": source_row_index,
        "split": artifact_row.get("split") or "",
        "split_manifest": artifact_row.get("split_manifest") or "gan2026_split_v1",
        "distribution": _distribution_for_row(artifact_row),
        "note_text": note_text,
        "hidden_families": list(atlas_row.get("hidden_families") or []),
        "first_failure_owner": atlas_row.get("first_failure_owner") or "",
        "gold_label": reference.get("gold_label") or reference.get("gold_normalized_label") or "",
        "gold_label_kind": reference.get("gold_label_kind") or "",
        "gold_monthly_frequency": reference.get("gold_monthly_frequency"),
    }


def _matrix_row(
    generator: str,
    candidate: Mapping[str, Any],
    artifact_path: Path,
    context: Mapping[str, Any],
) -> dict[str, Any]:
    label = _candidate_label(candidate)
    evidence = _text(candidate.get("evidence") or candidate.get("selected_evidence"))
    kind = _candidate_kind(candidate)
    denominator_or_window = _denominator_or_window(candidate)
    cluster_burden = _cluster_burden(candidate)
    seizure_free_duration = _seizure_free_duration(candidate)
    evidence_status = _evidence_status(evidence, str(context.get("note_text") or ""))
    match_status, match_basis = _gold_match_status(
        label=label,
        candidate_kind=kind,
        evidence_status=evidence_status,
        gold_label=str(context.get("gold_label") or ""),
        gold_label_kind=str(context.get("gold_label_kind") or ""),
        gold_monthly_frequency=context.get("gold_monthly_frequency"),
    )
    return {
        "source_row_index": context["source_row_index"],
        "split": context["split"],
        "split_manifest": context["split_manifest"],
        "distribution": context["distribution"],
        "artifact_path": artifact_path.as_posix(),
        "generator_name": generator,
        "candidate_id": _candidate_id(candidate, generator),
        "candidate_kind": kind,
        "candidate_label": label,
        "candidate_evidence": evidence,
        "evidence_status": evidence_status,
        "source_id_valid": _source_id_valid(candidate),
        "temporality": candidate.get("temporality") or "",
        "assertion_status": candidate.get("assertion_status") or "",
        "certainty": candidate.get("certainty") or candidate.get("confidence") or "",
        "applies_to": candidate.get("applies_to"),
        "denominator_or_window": denominator_or_window,
        "cluster_burden": cluster_burden,
        "seizure_free_duration": seizure_free_duration,
        "hidden_families": context["hidden_families"],
        "first_failure_owner": context["first_failure_owner"],
        "gold_label": context["gold_label"],
        "gold_match_status": match_status,
        "gold_match_basis": match_basis,
        "metadata_missing_fields": _metadata_missing_fields(
            kind=kind,
            evidence=evidence,
            temporality=_text(candidate.get("temporality")),
            assertion_status=_text(candidate.get("assertion_status")),
            denominator_or_window=denominator_or_window,
            cluster_burden=cluster_burden,
            seizure_free_duration=seizure_free_duration,
        ),
    }


def _deterministic_top_candidate(top: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": ",".join(str(item) for item in top.get("selected_event_ids") or [])
        or "deterministic_top",
        "kind": top.get("final_kind") or top.get("selected_decision", {}).get("final_kind"),
        "normalized_label": top.get("final_label"),
        "evidence": top.get("evidence") or top.get("selected_decision", {}).get("evidence"),
        "source_id": ",".join(str(item) for item in top.get("selected_event_ids") or []),
    }


def _llm_selected_state_candidate(artifact_row: Mapping[str, Any]) -> dict[str, Any] | None:
    structured = artifact_row.get("structured_record") or {}
    selected_fact = structured.get("selected_fact") or {}
    if not selected_fact:
        return None
    raw_answer = structured.get("raw_model_answer") or {}
    return {
        "candidate_id": selected_fact.get("fact_id") or "selected_fact",
        "kind": selected_fact.get("clinical_kind"),
        "normalized_label": raw_answer.get("raw_model_parser_label")
        or selected_fact.get("raw_value"),
        "evidence": selected_fact.get("evidence") or raw_answer.get("selected_evidence"),
        "raw_value": selected_fact.get("raw_value"),
        "temporality": selected_fact.get("temporality"),
        "assertion_status": selected_fact.get("assertion_status"),
        "applies_to": selected_fact.get("applies_to"),
    }


def _gold_match_status(
    *,
    label: str,
    candidate_kind: str,
    evidence_status: str,
    gold_label: str,
    gold_label_kind: str,
    gold_monthly_frequency: Any,
) -> tuple[str, str]:
    if not gold_label:
        return "not_judged", "missing_gold_label"
    try:
        gold_record = label_to_frequency_record(gold_label)
    except ValueError:
        gold_record = None
    try:
        candidate_record = label_to_frequency_record(label)
    except ValueError:
        candidate_record = None
    if gold_record is not None and candidate_record is not None:
        if candidate_record.normalized_label == gold_record.normalized_label:
            return "exact_label", "candidate_label"
        candidate_purist = map_purist(candidate_record.monthly_frequency)
        gold_purist = map_purist(gold_record.monthly_frequency)
        if candidate_purist == gold_purist:
            return "purist_category", "candidate_label"
    if evidence_status == "exact" and _kind_matches_gold(
        candidate_kind,
        gold_label_kind,
        gold_record,
    ):
        return "semantic_state", "candidate_kind_and_exact_evidence"
    if gold_monthly_frequency is None:
        return "not_judged", "missing_gold_frequency"
    return "no_match", "candidate_label_or_kind"


def _kind_matches_gold(
    candidate_kind: str,
    gold_label_kind: str,
    gold_record: Any,
) -> bool:
    candidate_label_kind = _candidate_kind_to_label_kind(candidate_kind)
    if gold_label_kind:
        return candidate_label_kind == gold_label_kind
    if gold_record is None:
        return False
    return candidate_label_kind == str(gold_record.kind)


def _candidate_kind_to_label_kind(candidate_kind: str) -> str:
    if candidate_kind in {"frequency", "frequency_rate", "cluster_frequency"}:
        return str(FrequencyLabelKind.FREQUENCY)
    if candidate_kind == "seizure_free":
        return str(FrequencyLabelKind.SEIZURE_FREE)
    if candidate_kind in {"unknown", "unknown_frequency", "last_event_only"}:
        return str(FrequencyLabelKind.UNKNOWN)
    if candidate_kind == "no_reference":
        return str(FrequencyLabelKind.NO_REFERENCE)
    if candidate_kind == "unresolved_multiple":
        return str(FrequencyLabelKind.UNRESOLVED_MULTIPLE)
    return candidate_kind


def _candidate_label(candidate: Mapping[str, Any]) -> str:
    return _text(
        candidate.get("normalized_label")
        or candidate.get("final_label")
        or candidate.get("raw_model_parser_label")
        or candidate.get("raw_value")
    )


def _candidate_kind(candidate: Mapping[str, Any]) -> str:
    return _text(
        candidate.get("kind") or candidate.get("clinical_kind") or candidate.get("final_kind")
    )


def _candidate_id(candidate: Mapping[str, Any], generator: str) -> str:
    return _text(
        candidate.get("candidate_id")
        or candidate.get("event_id")
        or candidate.get("node_id")
        or candidate.get("fact_id")
        or candidate.get("source_id")
        or generator
    )


def _source_id_valid(candidate: Mapping[str, Any]) -> bool:
    return bool(candidate.get("source_id") or candidate.get("event_id") or candidate.get("node_id"))


def _evidence_status(evidence: str, note_text: str) -> str:
    if not evidence:
        return "missing"
    if note_text and evidence in note_text:
        return "exact"
    return "source_near"


def _denominator_or_window(candidate: Mapping[str, Any]) -> dict[str, Any]:
    match_groups = candidate.get("match_groups")
    if isinstance(match_groups, Mapping):
        return {key: value for key, value in match_groups.items() if value not in (None, "")}
    operands = candidate.get("operands")
    if isinstance(operands, Mapping):
        frequency = operands.get("frequency")
        if isinstance(frequency, Mapping):
            return {key: value for key, value in frequency.items() if value not in (None, "")}
    return {}


def _cluster_burden(candidate: Mapping[str, Any]) -> dict[str, Any]:
    cluster = candidate.get("cluster") or candidate.get("cluster_burden")
    if isinstance(cluster, Mapping):
        return dict(cluster)
    if "cluster" in _candidate_kind(candidate):
        return _denominator_or_window(candidate)
    return {}


def _seizure_free_duration(candidate: Mapping[str, Any]) -> dict[str, Any]:
    if _candidate_kind(candidate) != "seizure_free":
        return {}
    fields = {}
    for key in ("duration", "duration_value", "duration_unit", "raw_value", "normalized_label"):
        if candidate.get(key):
            fields[key] = candidate[key]
    return fields


def _metadata_missing_fields(
    *,
    kind: str,
    evidence: str,
    temporality: str,
    assertion_status: str,
    denominator_or_window: Mapping[str, Any],
    cluster_burden: Mapping[str, Any],
    seizure_free_duration: Mapping[str, Any],
) -> list[str]:
    missing = []
    for field, value in (
        ("evidence", evidence),
        ("temporality", temporality),
        ("assertion_status", assertion_status),
    ):
        if not value:
            missing.append(field)
    if kind in {"frequency", "frequency_rate"} and not denominator_or_window:
        missing.append("denominator_or_window")
    if kind == "cluster_frequency" and not cluster_burden:
        missing.append("cluster_burden")
    if kind == "seizure_free" and not seizure_free_duration:
        missing.append("seizure_free_duration")
    return missing


def _distribution_for_row(row: Mapping[str, Any]) -> str:
    split = row.get("split") or ""
    if split == "validation":
        return "validation750"
    if split == "test":
        return "locked_holdout_audit"
    return str(split or "unknown")


def _as_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def _p90(values: Sequence[int]) -> int:
    if not values:
        return 0
    sorted_values = sorted(values)
    index = min(len(sorted_values) - 1, int(0.9 * (len(sorted_values) - 1)))
    return sorted_values[index]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", nargs="*", type=Path, default=list(DEFAULT_ARTIFACT_PATHS))
    parser.add_argument("--atlas-csv", type=Path, default=DEFAULT_ATLAS_CSV_PATH)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    artifact_paths = args.artifacts or list(DEFAULT_ARTIFACT_PATHS)
    rows, metadata = build_candidate_discovery_matrix(
        artifact_paths,
        atlas_csv_path=args.atlas_csv,
    )
    write_matrix_jsonl(rows, args.jsonl)
    write_matrix_report(rows, metadata, args.report, jsonl_path=args.jsonl)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
