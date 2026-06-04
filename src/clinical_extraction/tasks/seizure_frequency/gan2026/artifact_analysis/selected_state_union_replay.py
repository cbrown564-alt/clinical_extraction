"""Replay selected-state projection over the gated v3 boundary-candidate union."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    candidate_union,
)
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
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_rich_selected_state_reasoner import (  # noqa: E501
    RichSelectedStateExtractionRecord,
    deterministic_project_selected_state,
)

DEFAULT_RICH_STATE_REPLAY_PATH = candidate_union.DEFAULT_RICH_STATE_REPLAY_PATH
DEFAULT_BOUNDARY_V3_JSONL_PATH = Path(
    "experiments/gan2026_selective_boundary_candidate_experiment_v3_2026-06-04.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_selected_state_union_replay_v3_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_selected_state_union_replay_v3_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_selected_state_union_replay_v3_2026-06-04.md"
)
KNOWN_REAL_MODEL_ERROR_ROWS = (15593,)


def build_selected_state_union_replay_rows(
    saved_rows: Sequence[Mapping[str, Any]],
    boundary_rows: Sequence[Mapping[str, Any]],
    *,
    panel_rows: Sequence[Mapping[str, Any]] = (),
    max_union_candidates: int = candidate_union.MAX_UNION_CANDIDATES_PER_ROW,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Join saved selected states with v3 boundary candidates and replay projection."""

    boundary_by_source = {int(row["source_row_index"]): row for row in boundary_rows}
    panels_by_source = {int(row["source_row_index"]): row for row in panel_rows}
    rows = [
        _selected_state_union_replay_row(
            saved_row,
            boundary_row=boundary_by_source.get(int(saved_row["source_row_index"])),
            panel_row=panels_by_source.get(int(saved_row["source_row_index"])),
            max_union_candidates=max_union_candidates,
        )
        for saved_row in saved_rows
    ]
    rows.sort(key=lambda row: int(row["source_row_index"]))
    return rows, summarize_selected_state_union_replay_rows(rows)


def summarize_selected_state_union_replay_rows(
    rows: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    comparator_correct = sum(row["comparison"]["comparator_correct"] for row in rows)
    primary_rows = [row for row in rows if row["primary_v3_selected_state_replay"]["scorable"]]
    primary_correct = sum(
        row["comparison"]["primary_v3_projection_correct"] for row in primary_rows
    )
    safety_correct = sum(row["comparison"]["safety_floor_correct"] for row in rows)
    w_to_c = [
        int(row["source_row_index"])
        for row in rows
        if row["comparison"]["safety_w_to_c_against_comparator"]
    ]
    c_to_w = [
        int(row["source_row_index"])
        for row in rows
        if row["comparison"]["safety_c_to_w_against_comparator"]
    ]
    primary_c_to_w = [
        int(row["source_row_index"])
        for row in primary_rows
        if row["comparison"]["primary_v3_c_to_w_against_comparator"]
    ]
    known_model_errors = [
        int(row["source_row_index"])
        for row in rows
        if row["source_row_index"] in KNOWN_REAL_MODEL_ERROR_ROWS
        and row["primary_v3_selected_state_replay"]["label"] != row["gold_label"]
    ]
    return {
        "artifact_kind": "gan2026_selected_state_union_replay_v3",
        "date": "2026-06-04",
        "split_manifest": "gan2026_split_v1",
        "split": "validation",
        "source_artifact": str(DEFAULT_RICH_STATE_REPLAY_PATH),
        "boundary_candidate_artifact": str(DEFAULT_BOUNDARY_V3_JSONL_PATH),
        "row_count": len(rows),
        "claim_language": (
            "Validation-development no-call selected-state replay over saved rich "
            "selected states plus the controlled v3 boundary-candidate artifact. "
            "No locked-test inspection, live model call, scorer-policy change, "
            "whole-pipeline promotion, or benchmark-comparable claim is authorized."
        ),
        "metrics": {
            "rows_with_v3_boundary_candidates": sum(
                bool(row["v3_boundary_candidate_summary"]["retained_count"]) for row in rows
            ),
            "rows_with_union_verified_candidates": sum(
                bool(row["candidate_burden_summary"]["union_verified_count"]) for row in rows
            ),
            "comparator_correct_rows": comparator_correct,
            "primary_v3_projection_scorable_rows": len(primary_rows),
            "primary_v3_projection_correct_rows": primary_correct,
            "safety_floor_correct_rows": safety_correct,
            "safety_w_to_c_against_comparator_rows": len(w_to_c),
            "safety_c_to_w_against_comparator_rows": len(c_to_w),
            "primary_v3_c_to_w_against_comparator_rows": len(primary_c_to_w),
            "known_real_model_error_rows_carried": len(known_model_errors),
        },
        "safety_w_to_c_source_row_indices": w_to_c,
        "safety_c_to_w_source_row_indices": c_to_w,
        "primary_v3_c_to_w_source_row_indices": primary_c_to_w,
        "known_real_model_error_source_row_indices": known_model_errors,
        "candidate_kind_counts": _candidate_kind_counts(rows),
        "by_hidden_family": _by_hidden_family(rows),
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Selected-State Union Replay V3",
        "",
        "This is a no-call validation-development replay over the saved 75-row rich "
        "selected-state hard panel and the controlled v3 boundary-candidate output.",
        "",
        "## Outcome",
        "",
        (
            "The gated v3 union is coherent as a downstream selected-state input "
            "artifact, but the primary v3 candidate-state projection is not a final "
            "label policy. It is scorable on "
            f"{metrics['primary_v3_projection_scorable_rows']} rows and correct on "
            f"{metrics['primary_v3_projection_correct_rows']} of them; a deterministic "
            "safety-floor replay preserves the prior comparator score with "
            f"{metrics['safety_w_to_c_against_comparator_rows']} W->C and "
            f"{metrics['safety_c_to_w_against_comparator_rows']} C->W changes."
        ),
        "",
        "## Claim Boundary",
        "",
        str(metadata["claim_language"]),
        "",
        "## Artifacts",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Saved selected-state replay: `{metadata['source_artifact']}`",
        f"- V3 boundary candidates: `{metadata['boundary_candidate_artifact']}`",
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
            "## V3 Boundary Rows",
            "",
            "| Row | Gold | Comparator | Primary v3 projection | "
            "Safety-floor label | Delta | Notes |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if not row["v3_boundary_candidate_summary"]["retained_count"]:
            continue
        notes = []
        if row["source_row_index"] in metadata["known_real_model_error_source_row_indices"]:
            notes.append("known real model cluster-cadence error")
        lines.append(
            f"| {row['source_row_index']} | `{row['gold_label']}` | "
            f"`{row['comparator_selected_state_replay']['label']}` | "
            f"`{row['primary_v3_selected_state_replay']['label'] or 'unscorable'}` | "
            f"`{row['safety_floor_selected_state_replay']['label']}` | "
            f"`{row['comparison']['safety_delta']}` | {'; '.join(notes)} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Keep v3 boundary candidates as a useful selected-state input surface, "
            "not as final labels.",
            "- Keep row 15593 visible as a real v3 model error before any broader replay.",
            "- The safety-floor result is diagnostic because it preserves "
            "deterministic-correct rows by policy.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _selected_state_union_replay_row(
    saved_row: Mapping[str, Any],
    *,
    boundary_row: Mapping[str, Any] | None,
    panel_row: Mapping[str, Any] | None,
    max_union_candidates: int,
) -> dict[str, Any]:
    source_row_index = int(saved_row["source_row_index"])
    note_text = str(saved_row.get("typed_input", {}).get("note_text") or "")
    deterministic_candidates = candidate_union._deterministic_candidates(  # noqa: SLF001
        note_text, source_row_index
    )
    v3_candidates = [_materialize_v3_candidate(candidate) for candidate in _retained(boundary_row)]
    union, rejected = candidate_union._gated_union(  # noqa: SLF001
        [*deterministic_candidates, *v3_candidates],
        max_union_candidates=max_union_candidates,
    )
    gold_label = _normalize_label(saved_row.get("reference", {}).get("gold_normalized_label"))
    comparator_label = _normalize_label(_comparator_label(saved_row))
    primary = _primary_v3_candidate(union)
    primary_replay = _project_candidate(primary)
    safety_label = _safety_floor_label(comparator_label, primary_replay.get("label"))
    comparator_correct = comparator_label == gold_label
    primary_correct = (
        primary_replay.get("label") == gold_label if primary_replay["scorable"] else None
    )
    safety_correct = safety_label == gold_label
    return {
        "artifact_kind": "gan2026_selected_state_union_replay_v3_row",
        "claim_boundary": "validation_development_no_call_selected_state_union_replay",
        "source_row_index": source_row_index,
        "split": saved_row.get("split", "validation"),
        "split_manifest": saved_row.get("split_manifest", "gan2026_split_v1"),
        "gold_label": gold_label,
        "hidden_families": list(panel_row.get("hidden_families") or []) if panel_row else [],
        "candidate_burden_summary": {
            "deterministic_count": len(deterministic_candidates),
            "v3_boundary_candidate_count": len(v3_candidates),
            "union_verified_count": len(union),
            "rejected_count": len(rejected),
        },
        "v3_boundary_candidate_summary": {
            "retained_count": len(_retained(boundary_row)),
            "parse_errors": list(boundary_row.get("parse_errors") or []) if boundary_row else [],
            "call_status": boundary_row.get("call_status") if boundary_row else "not_in_slice",
        },
        "union_verified_candidates": union,
        "rejected_candidates": rejected,
        "comparator_selected_state_replay": {
            "label": comparator_label,
            "source": "saved_rich_selected_state_policy_replay",
            "correct": comparator_correct,
        },
        "primary_v3_selected_state_replay": primary_replay,
        "safety_floor_selected_state_replay": {
            "label": safety_label,
            "source": "comparator_when_known_else_primary_v3_candidate_state",
            "correct": safety_correct,
        },
        "comparison": {
            "comparator_correct": comparator_correct,
            "primary_v3_projection_correct": primary_correct,
            "primary_v3_c_to_w_against_comparator": bool(
                comparator_correct and primary_correct is False
            ),
            "safety_floor_correct": safety_correct,
            "safety_w_to_c_against_comparator": bool(
                not comparator_correct and safety_correct
            ),
            "safety_c_to_w_against_comparator": bool(
                comparator_correct and not safety_correct
            ),
            "safety_delta": _delta(comparator_correct, safety_correct),
        },
    }


def _materialize_v3_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    materialized = dict(candidate)
    materialized["metadata"] = dict(candidate.get("metadata") or {})
    materialized["provenance"] = ["live_llm_boundary_proposal_v3"]
    materialized["gate_failures"] = list(candidate.get("gate_failures") or [])
    return materialized


def _retained(boundary_row: Mapping[str, Any] | None) -> list[Mapping[str, Any]]:
    if not boundary_row:
        return []
    return list(boundary_row.get("retained_candidates") or [])


def _primary_v3_candidate(candidates: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    for candidate in candidates:
        if "live_llm_boundary_proposal_v3" in set(candidate.get("provenance") or []):
            return candidate
    return None


def _project_candidate(candidate: Mapping[str, Any] | None) -> dict[str, Any]:
    if candidate is None:
        return {
            "label": None,
            "scorable": False,
            "candidate_id": None,
            "candidate_kind": None,
            "projection_errors": ["no_v3_candidate"],
        }
    selected_state = _candidate_to_selected_state(candidate)
    try:
        extraction = RichSelectedStateExtractionRecord.model_validate(
            {"selected_state": selected_state}
        )
        projected = deterministic_project_selected_state(extraction)
    except ValueError as exc:
        return {
            "label": None,
            "scorable": False,
            "candidate_id": candidate.get("candidate_id"),
            "candidate_kind": candidate.get("candidate_kind"),
            "selected_state": selected_state,
            "projection_errors": [str(exc)],
        }
    return {
        "label": _normalize_label(projected),
        "scorable": bool(projected),
        "candidate_id": candidate.get("candidate_id"),
        "candidate_kind": candidate.get("candidate_kind"),
        "selected_state": selected_state,
        "projection_errors": [],
    }


def _candidate_to_selected_state(candidate: Mapping[str, Any]) -> dict[str, Any]:
    metadata = candidate.get("metadata") or {}
    rate = metadata.get("rate") or {}
    cluster = metadata.get("cluster") or {}
    seizure_free = metadata.get("seizure_free") or {}
    candidate_kind = str(candidate.get("candidate_kind") or "")
    assertion_status = str(candidate.get("assertion_status") or "uncertain")
    currentness = str(candidate.get("currentness") or "unclear")
    if candidate_kind == "conditional_frequency":
        currentness = "conditional"
        assertion_status = "hypothetical"
    return {
        "state_kind": _state_kind(candidate_kind),
        "selected_evidence": str(candidate.get("evidence") or ""),
        "raw_source_phrase": str(metadata.get("evidence_quote") or candidate.get("evidence") or ""),
        "currentness": _currentness(currentness),
        "assertion_status": _assertion_status(assertion_status),
        "applies_to": str(metadata.get("seizure_type") or candidate.get("semiology") or ""),
        "rate": {
            "count_low": rate.get("count_low"),
            "count_high": rate.get("count_high"),
            "count_is_upper_bound": False,
            "count_is_multiple": bool(rate.get("count_is_multiple")),
            "time_count_low": rate.get("time_count_low"),
            "time_count_high": rate.get("time_count_high"),
            "time_unit": rate.get("time_unit"),
            "rate_time_basis_known": bool(rate.get("time_unit")),
            "rate_text": str(rate.get("rate_text") or ""),
        },
        "cluster": {
            "has_cluster_pattern": bool(cluster.get("has_cluster_pattern")),
            "cluster_cadence_known": bool(cluster.get("cluster_cadence_text")),
            "cluster_cadence_text": str(cluster.get("cluster_cadence_text") or ""),
            "seizures_per_cluster_low": cluster.get("seizures_per_cluster_low"),
            "seizures_per_cluster_high": cluster.get("seizures_per_cluster_high"),
            "cluster_uncertainty": str(cluster.get("cluster_uncertainty") or ""),
        },
        "seizure_free_boundary": {
            "has_no_event_claim": bool(seizure_free.get("has_no_event_claim")),
            "duration_count": seizure_free.get("duration_count"),
            "duration_unit": seizure_free.get("duration_unit"),
            "applies_to_all_seizure_types": bool(
                seizure_free.get("applies_to_all_seizure_types")
            ),
            "has_recent_events_or_conditions": bool(
                seizure_free.get("has_recent_events_or_conditions")
            ),
            "boundary_note": str(seizure_free.get("boundary_note") or ""),
        },
        "conditionality_note": str(metadata.get("conditionality_note") or ""),
        "ambiguity_flags": list(metadata.get("ambiguity_flags") or []),
        "competing_state_summary": str(metadata.get("competing_state_summary") or ""),
        "selection_reason": str(metadata.get("reason") or ""),
        "raw_model_label_hint": str(candidate.get("normalized_label") or ""),
    }


def _state_kind(candidate_kind: str) -> str:
    if candidate_kind == "seizure_free":
        return "seizure_free"
    if candidate_kind == "unknown_frequency":
        return "unknown"
    if candidate_kind == "no_reference":
        return "no_reference"
    return "frequency"


def _currentness(value: str) -> str:
    allowed = {"current", "recent", "historical", "future", "conditional", "unclear"}
    return value if value in allowed else "unclear"


def _assertion_status(value: str) -> str:
    return value if value in {"asserted", "negated", "hypothetical", "uncertain"} else "uncertain"


def _safety_floor_label(comparator_label: str, primary_label: Any) -> str:
    primary = _normalize_label(primary_label)
    if comparator_label not in {"", "unknown", "no seizure frequency reference"}:
        return comparator_label
    return primary or comparator_label


def _comparator_label(row: Mapping[str, Any]) -> str:
    return str(
        row.get("policy_replay", {}).get("revised_deterministic_projected_label")
        or row.get("deterministic_projected_label")
        or ""
    )


def _normalize_label(label: Any) -> str:
    if not label:
        return ""
    try:
        return label_to_frequency_record(str(label)).normalized_label
    except ValueError:
        return str(label).strip().lower()


def _delta(before_correct: bool, after_correct: bool) -> str:
    if before_correct and after_correct:
        return "C->C"
    if before_correct and not after_correct:
        return "C->W"
    if not before_correct and after_correct:
        return "W->C"
    return "W->W"


def _candidate_kind_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = Counter(
        candidate["candidate_kind"]
        for row in rows
        for candidate in row["union_verified_candidates"]
        if "live_llm_boundary_proposal_v3" in set(candidate.get("provenance") or [])
    )
    return dict(sorted(counts.items()))


def _by_hidden_family(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        for family in row.get("hidden_families") or ["unclassified"]:
            summary[str(family)]["rows"] += 1
            if row["v3_boundary_candidate_summary"]["retained_count"]:
                summary[str(family)]["v3_boundary_rows"] += 1
            if row["comparison"]["safety_w_to_c_against_comparator"]:
                summary[str(family)]["safety_w_to_c_rows"] += 1
            if row["comparison"]["safety_c_to_w_against_comparator"]:
                summary[str(family)]["safety_c_to_w_rows"] += 1
    return {family: dict(counts) for family, counts in sorted(summary.items())}


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rich-state-replay-path", type=Path, default=DEFAULT_RICH_STATE_REPLAY_PATH
    )
    parser.add_argument(
        "--boundary-v3-jsonl-path", type=Path, default=DEFAULT_BOUNDARY_V3_JSONL_PATH
    )
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    saved_rows = load_jsonl_rows(args.rich_state_replay_path)
    boundary_rows = load_jsonl_rows(args.boundary_v3_jsonl_path)
    panel_rows = load_jsonl_rows(args.panel_jsonl_path) if args.panel_jsonl_path.exists() else []
    rows, metadata = build_selected_state_union_replay_rows(
        saved_rows, boundary_rows, panel_rows=panel_rows
    )
    metadata = {
        **metadata,
        "source_artifact": str(args.rich_state_replay_path),
        "boundary_candidate_artifact": str(args.boundary_v3_jsonl_path),
    }
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
