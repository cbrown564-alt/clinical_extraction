"""Run change-only verifier audits for deterministic/state exact alternatives."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selective_verifier_experiment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    change_only_candidate_verifier,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DATE = "2026-06-05"
MODEL = "openai/gpt-4.1"
PROMPT_VERSION = "gan2026_change_only_candidate_verifier_v0"
DEFAULT_CANDIDATE_DISCOVERY_PATH = Path(
    "experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.jsonl"
)
DEFAULT_RAW_REUSE_PATHS = [
    Path("experiments/gan2026_change_only_verifier_calibration_gpt41_2026-06-05.jsonl"),
    Path(
        "experiments/gan2026_change_only_verifier_expanded_calibration_gpt41_2026-06-05.jsonl"
    ),
    Path(
        "experiments/gan2026_change_only_verifier_det_state_alt_calibration_gpt41_2026-06-05.jsonl"
    ),
    Path(
        "experiments/gan2026_change_only_verifier_sf_unknown_family_gpt41_2026-06-05.jsonl"
    ),
]
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_change_only_verifier_det_state_alt_full_family_gpt41_2026-06-05.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_change_only_verifier_det_state_alt_full_family_gpt41_2026-06-05.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_change_only_verifier_det_state_alt_full_family_gpt41_2026-06-05.md"
)
DEFAULT_TEST_INPUT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_"
    "deterministic_safety_floor_live_2026-06-03.jsonl"
)
DEFAULT_TEST_JSON_PATH = Path(
    "experiments/"
    "gan2026_change_only_verifier_det_state_alt_test450_aggregate_audit_2026-06-05.json"
)
DEFAULT_TEST_REPORT_PATH = Path(
    "experiments/"
    "gan2026_change_only_verifier_det_state_alt_test450_aggregate_audit_2026-06-05.md"
)
DEFAULT_CURRENT_VALIDATION_PATH = Path(
    "experiments/gan2026_staged_hybrid_assembly_validation750_no_call_2026-06-04.jsonl"
)

GENERATOR_NAMES = {"deterministic_candidates_all", "state_graph_nodes"}
CANDIDATE_KINDS = {"frequency_rate", "cluster_frequency"}
_CURRENT_PREDICTION_CACHE: dict[int, str] | None = None


def build_validation_family(
    candidate_rows: Sequence[Mapping[str, Any]],
    current_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Select one deterministic/state exact alternative per validation row."""

    current_by_source = {int(row["source_row_index"]): row for row in current_rows}
    candidates_by_source: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for candidate in candidate_rows:
        if not _candidate_eligible(candidate):
            continue
        source_row_index = int(candidate["source_row_index"])
        current = current_by_source.get(source_row_index)
        if current is None:
            continue
        current_label = str(current["prediction_label"])
        candidate_label = _normalized_label(candidate.get("candidate_label"))
        if not candidate_label or candidate_label == _normalized_label(current_label):
            continue
        candidates_by_source[source_row_index].append(candidate)

    rows = []
    for source_row_index, candidates in sorted(candidates_by_source.items()):
        current = current_by_source[source_row_index]
        selected = sorted(candidates, key=_candidate_rank_key)[0]
        rows.append(
            {
                "source_row_index": source_row_index,
                "split": "validation",
                "split_manifest": "gan2026_split_v1",
                "clinical_text": str(current["clinical_text"]),
                "gold_label": str(current["gold_label"]),
                "current_label": _normalized_label(current["prediction_label"]),
                "proposed_label": _normalized_label(selected["candidate_label"]),
                "proposed_evidence": str(selected.get("candidate_evidence") or ""),
                "candidate_source": str(selected.get("generator_name") or ""),
                "candidate_kind": str(selected.get("candidate_kind") or ""),
                "candidate_id": str(selected.get("candidate_id") or ""),
                "candidate_evidence_status": str(selected.get("evidence_status") or ""),
                "candidate_rank_policy": (
                    "deterministic_candidates_all before state_graph_nodes; "
                    "frequency_rate before cluster_frequency; then normalized label, "
                    "candidate_id, evidence"
                ),
            }
        )
    return rows


def run_family_experiment(
    family_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
    raw_reuse_paths: Sequence[Path],
    progress_every: int = 10,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw_reuse = load_reusable_raw_outputs(raw_reuse_paths)
    output_rows = []
    sorted_rows = sorted(family_rows, key=lambda item: int(item["source_row_index"]))
    for index, row in enumerate(sorted_rows, 1):
        output_rows.append(
            _run_row(
                row,
                model=model,
                max_tokens=max_tokens,
                raw_reuse=raw_reuse,
            )
        )
        if progress_every and index % progress_every == 0:
            summary = change_only_candidate_verifier.summarize_rows(output_rows)
            print(
                f"processed={index}/{len(family_rows)} "
                f"transitions={summary['transition_counts']}"
            )
    metadata = summarize_family_rows(
        output_rows,
        model=model,
        source_artifact=DEFAULT_CANDIDATE_DISCOVERY_PATH,
        raw_reuse_paths=raw_reuse_paths,
    )
    return output_rows, metadata


def summarize_family_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    source_artifact: Path,
    raw_reuse_paths: Sequence[Path],
) -> dict[str, Any]:
    summary = change_only_candidate_verifier.summarize_rows(rows)
    transitions = Counter(str(row["transition"]) for row in rows)
    whole_base_correct = int(rows[0]["whole_validation_base_correct_rows"]) if rows else 0
    projected_whole = whole_base_correct + transitions["W_to_C"] - transitions["C_to_W"]
    parse_ok = sum(not row["parse_errors"] for row in rows)
    exact = sum(bool(row["verifier_decision"]["all_evidence_quotes_exact"]) for row in rows)
    return {
        "artifact_kind": "gan2026_change_only_verifier_det_state_alt_full_family_summary",
        "date": DATE,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "policy_name": change_only_candidate_verifier.POLICY_NAME,
        "source_artifact": str(source_artifact),
        "raw_reuse_paths": [str(path) for path in raw_reuse_paths],
        "claim_boundary": (
            "Validation-development row-level full-family audit over deterministic/state "
            "exact frequency or cluster alternatives. The proposal ranker does not use gold "
            "labels; gold labels are used only for validation accounting. This artifact does "
            "not authorize locked-test row-level inspection or benchmark claims."
        ),
        "proposal_policy": (
            "Select one non-gold deterministic/state exact alternative per validation row: "
            "deterministic_candidates_all before state_graph_nodes; frequency_rate before "
            "cluster_frequency; then normalized label, candidate_id, evidence."
        ),
        "summary": summary,
        "metrics": {
            "row_count": len(rows),
            "call_ok_rows": sum(row["call_status"] == "ok" for row in rows),
            "model_call_rows": sum(not row["raw_output_reused"] for row in rows),
            "raw_output_reused_rows": sum(row["raw_output_reused"] for row in rows),
            "parse_ok_rows": parse_ok,
            "parse_error_rows": len(rows) - parse_ok,
            "all_evidence_quotes_exact_rows": exact,
            "base_correct_rows": summary["base_correct_rows"],
            "projected_correct_rows": summary["projected_correct_rows"],
            "base_purist_proxy": summary["base_purist_proxy"],
            "projected_purist_proxy": summary["projected_purist_proxy"],
            "whole_validation_base_correct_rows": whole_base_correct,
            "whole_validation_projected_correct_rows": projected_whole,
            "whole_validation_base_purist_proxy": _rate(whole_base_correct, 750),
            "whole_validation_projected_purist_proxy": _rate(projected_whole, 750),
            "changed_label_precision": summary["changed_label_precision"],
        },
        "transition_counts": summary["transition_counts"],
        "recommendation_counts": summary["recommendation_counts"],
        "candidate_source_counts": dict(
            sorted(Counter(str(row["candidate_source"]) for row in rows).items())
        ),
        "candidate_kind_counts": dict(
            sorted(Counter(str(row["candidate_kind"]) for row in rows).items())
        ),
        "regression_source_row_indices": [
            int(row["source_row_index"]) for row in rows if row["transition"] == "C_to_W"
        ],
        "improved_source_row_indices": [
            int(row["source_row_index"]) for row in rows if row["transition"] == "W_to_C"
        ],
        "interpretation": _interpretation(summary),
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
        "# Gan 2026 Change-Only Verifier Deterministic/State Full Family",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["interpretation"]),
        "",
        "## Artifacts",
        "",
        f"- Row JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Source matrix: `{metadata['source_artifact']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Transitions", "", "| Transition | Rows |", "| --- | ---: |"])
    for key, value in metadata["transition_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## Recommendations", "", "| Recommendation | Rows |", "| --- | ---: |"])
    for key, value in metadata["recommendation_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Changed Validation Rows",
            "",
            "| Row | Current | Proposed | Source | Kind | Transition | Quotes exact |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if row["transition"] in {"C_to_C", "W_to_W"}:
            continue
        lines.append(
            f"| {row['source_row_index']} | `{row['current_label']}` | "
            f"`{row['proposed_label']}` | `{row['candidate_source']}` | "
            f"`{row['candidate_kind']}` | `{row['transition']}` | "
            f"{row['verifier_decision']['all_evidence_quotes_exact']} |"
        )
    lines.extend(
        [
            "",
            "## Promotion Boundary",
            "",
            "Promotion requires zero C->W regressions on this validation family and a "
            "positive W->C count. Any follow-up locked-test use must be frozen and "
            "aggregate-only.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_test_family(test_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Build the frozen holdout family without using gold labels for proposal selection."""

    family = []
    for row in test_rows:
        score_layer = row["score_layers"]["hybrid_adjudicator_raw"]
        current_label = _normalized_label(score_layer["final_label"])
        if not current_label:
            continue
        candidates = []
        component_inputs = row["component_inputs"]
        for candidate in component_inputs.get("deterministic_candidates") or []:
            normalized = _normalized_label(candidate.get("normalized_label"))
            if (
                normalized
                and normalized != current_label
                and candidate.get("kind") in CANDIDATE_KINDS
            ):
                candidate_id = candidate.get("source_id") or candidate.get("event_id") or ""
                candidates.append(
                    {
                        "candidate_source": "deterministic_candidates_all",
                        "candidate_kind": str(candidate.get("kind") or ""),
                        "candidate_id": str(candidate_id),
                        "proposed_label": normalized,
                        "proposed_evidence": str(candidate.get("evidence") or ""),
                    }
                )
        for candidate in component_inputs.get("state_graph_nodes") or []:
            normalized = _normalized_label(candidate.get("normalized_label"))
            if (
                normalized
                and normalized != current_label
                and candidate.get("kind") in CANDIDATE_KINDS
            ):
                candidate_id = candidate.get("source_id") or candidate.get("node_id") or ""
                candidates.append(
                    {
                        "candidate_source": "state_graph_nodes",
                        "candidate_kind": str(candidate.get("kind") or ""),
                        "candidate_id": str(candidate_id),
                        "proposed_label": normalized,
                        "proposed_evidence": str(candidate.get("evidence") or ""),
                    }
                )
        if not candidates:
            continue
        selected = sorted(candidates, key=_test_candidate_rank_key)[0]
        family.append(
            {
                "source_row_index": int(row["source_row_index"]),
                "split": "test",
                "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
                "clinical_text": str(component_inputs["note_text"]),
                "gold_label": str(row["reference"]["gold_normalized_label"]),
                "current_label": current_label,
                "proposed_label": selected["proposed_label"],
                "proposed_evidence": selected["proposed_evidence"],
                "candidate_source": selected["candidate_source"],
                "candidate_kind": selected["candidate_kind"],
                "candidate_id": selected["candidate_id"],
            }
        )
    return family


def run_test_aggregate_audit(
    test_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
    progress_every: int = 10,
) -> dict[str, Any]:
    family_rows = build_test_family(test_rows)
    output_rows = []
    for index, row in enumerate(family_rows, 1):
        output_rows.append(_run_row(row, model=model, max_tokens=max_tokens, raw_reuse={}))
        if progress_every and index % progress_every == 0:
            summary = change_only_candidate_verifier.summarize_rows(output_rows)
            print(
                f"processed={index}/{len(family_rows)} "
                f"transitions={summary['transition_counts']}"
            )
    return summarize_test_aggregate(output_rows, test_rows, model=model)


def summarize_test_aggregate(
    rows: Sequence[Mapping[str, Any]],
    test_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
) -> dict[str, Any]:
    summary = change_only_candidate_verifier.summarize_rows(rows)
    transitions = Counter(str(row["transition"]) for row in rows)
    base_correct = sum(
        bool(row["score_layers"]["hybrid_adjudicator_raw"]["purist_correct"])
        for row in test_rows
    )
    projected_correct = base_correct + transitions["W_to_C"] - transitions["C_to_W"]
    return {
        "artifact_kind": "gan2026_change_only_verifier_det_state_alt_test450_aggregate_audit",
        "date": DATE,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "policy_name": change_only_candidate_verifier.POLICY_NAME,
        "source_artifact": str(DEFAULT_TEST_INPUT_PATH),
        "claim_boundary": (
            "Frozen locked-test aggregate-only audit over deterministic/state exact "
            "frequency or cluster alternatives. This summary intentionally omits row ids, "
            "clinical text, raw model outputs, and row-level errors."
        ),
        "proposal_policy": (
            "Select one non-gold deterministic/state exact alternative per eligible test row: "
            "deterministic candidates before state graph nodes; frequency_rate before "
            "cluster_frequency; then normalized label, candidate_id, evidence."
        ),
        "metrics": {
            "test_rows": len(test_rows),
            "eligible_rows": len(rows),
            "call_ok_rows": sum(row["call_status"] == "ok" for row in rows),
            "parse_ok_rows": sum(not row["parse_errors"] for row in rows),
            "parse_error_rows": sum(bool(row["parse_errors"]) for row in rows),
            "all_evidence_quotes_exact_rows": sum(
                bool(row["verifier_decision"]["all_evidence_quotes_exact"])
                for row in rows
            ),
            "base_correct_rows": base_correct,
            "projected_correct_rows": projected_correct,
            "base_purist_proxy": _rate(base_correct, len(test_rows)),
            "projected_purist_proxy": _rate(projected_correct, len(test_rows)),
            "changed_label_precision": summary["changed_label_precision"],
        },
        "transition_counts": summary["transition_counts"],
        "recommendation_counts": summary["recommendation_counts"],
        "candidate_source_counts": dict(
            sorted(Counter(str(row["candidate_source"]) for row in rows).items())
        ),
        "candidate_kind_counts": dict(
            sorted(Counter(str(row["candidate_kind"]) for row in rows).items())
        ),
        "decision": (
            "does_not_meet_goal"
            if _rate(projected_correct, len(test_rows)) < 0.9
            else "meets_requested_test_threshold"
        ),
        "interpretation": (
            "Aggregate-only holdout result does not approach the requested Purist F1 >= 0.9 "
            "threshold."
            if _rate(projected_correct, len(test_rows)) < 0.9
            else "Aggregate-only holdout result reaches the requested threshold."
        ),
    }


def write_test_aggregate_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    json_path: Path,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Change-Only Verifier Test450 Aggregate Audit",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["interpretation"]),
        "",
        "## Artifacts",
        "",
        f"- Summary JSON: `{json_path}`",
        f"- Source artifact: `{metadata['source_artifact']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Transitions", "", "| Transition | Rows |", "| --- | ---: |"])
    for key, value in metadata["transition_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## Recommendations", "", "| Recommendation | Rows |", "| --- | ---: |"])
    for key, value in metadata["recommendation_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Inspection Boundary",
            "",
            "No test row ids, clinical text, raw model outputs, or row-level failures are "
            "stored in this report.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def load_reusable_raw_outputs(paths: Sequence[Path]) -> dict[tuple[int, str, str], str]:
    raw_by_key: dict[tuple[int, str, str], str] = {}
    for path in paths:
        if not path.exists():
            continue
        for row in load_jsonl_rows(path):
            raw_output = row.get("raw_model_output")
            if not raw_output:
                continue
            key = _raw_reuse_key(row)
            if key:
                raw_by_key[key] = str(raw_output)
    return raw_by_key


def _run_row(
    row: Mapping[str, Any],
    *,
    model: str,
    max_tokens: int,
    raw_reuse: Mapping[tuple[int, str, str], str],
) -> dict[str, Any]:
    model_input = change_only_candidate_verifier.build_model_input(row)
    system_prompt = str(model_input.pop("system_prompt"))
    raw_key = _raw_reuse_key(row)
    raw_output = raw_reuse.get(raw_key, "")
    raw_output_reused = bool(raw_output)
    call_errors: list[str] = []
    usage: dict[str, Any] = {}
    latency_seconds: float | None = None
    call_status = "ok"
    if not raw_output:
        try:
            raw_output, usage, latency_seconds = (
                selective_verifier_experiment._call_openai_responses(
                    system_prompt,
                    model_input,
                    model=model,
                    max_tokens=max_tokens,
                )
            )
        except Exception as exc:  # pragma: no cover - live failure path
            call_status = "error"
            call_errors.append(f"{type(exc).__name__}: {exc}")
    parsed, parse_errors = (
        change_only_candidate_verifier.parse_output(raw_output) if raw_output else (None, [])
    )
    if parsed is None and not call_errors and not parse_errors:
        parse_errors = ["empty_output"]
    decision = change_only_candidate_verifier.verifier_decision(
        parsed,
        row,
        parse_errors=parse_errors,
    )
    current_correct = _purist_correct(row["current_label"], row["gold_label"])
    transition = change_only_candidate_verifier.transition(
        current_correct,
        bool(decision["purist_correct"]),
    )
    return {
        "artifact_kind": "gan2026_change_only_verifier_det_state_alt_full_family_row",
        "source_row_index": int(row["source_row_index"]),
        "split": row.get("split", "validation"),
        "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "call_status": call_status,
        "call_errors": call_errors,
        "latency_seconds": latency_seconds,
        "usage": usage,
        "raw_output_reused": raw_output_reused,
        "raw_model_output": raw_output,
        "parse_errors": parse_errors,
        "parsed_output": parsed.model_dump(mode="json") if parsed else None,
        "recommendation": parsed.recommendation if parsed else "parse_error",
        "current_label": row["current_label"],
        "proposed_label": row["proposed_label"],
        "gold_label": row["gold_label"],
        "candidate_source": row["candidate_source"],
        "candidate_kind": row["candidate_kind"],
        "candidate_id": row["candidate_id"],
        "proposed_evidence": row["proposed_evidence"],
        "current_purist_correct": current_correct,
        "verifier_decision": decision,
        "transition": transition,
        "whole_validation_base_correct_rows": (
            int(row["whole_validation_base_correct_rows"])
            if "whole_validation_base_correct_rows" in row
            else None
        ),
        "claim_boundary": "validation_development_change_only_verifier_det_state_full_family",
    }


def load_current_validation_rows() -> list[dict[str, Any]]:
    rows = []
    records = load_records_for_split("validation")
    for record in records:
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "clinical_text": record.note_text,
                "gold_label": record.gold_label,
                "prediction_label": _current_prediction_label(record.source_row_index),
            }
        )
    whole_base_correct = sum(
        _purist_correct(row["prediction_label"], row["gold_label"]) for row in rows
    )
    for row in rows:
        row["whole_validation_base_correct_rows"] = whole_base_correct
    return rows


def _current_prediction_label(source_row_index: int) -> str:
    global _CURRENT_PREDICTION_CACHE
    # The staged assembly validation artifact is the comparator current label for this branch.
    if _CURRENT_PREDICTION_CACHE is None:
        rows = load_jsonl_rows(DEFAULT_CURRENT_VALIDATION_PATH)
        _CURRENT_PREDICTION_CACHE = {
            int(row["source_row_index"]): str(
                row["hybrid_reasoner_replay"]["score_layer"]["final_label"]
            )
            for row in rows
        }
    return _CURRENT_PREDICTION_CACHE[int(source_row_index)]


def _candidate_eligible(candidate: Mapping[str, Any]) -> bool:
    if candidate.get("split") != "validation":
        return False
    if candidate.get("generator_name") not in GENERATOR_NAMES:
        return False
    if candidate.get("candidate_kind") not in CANDIDATE_KINDS:
        return False
    if candidate.get("evidence_status") != "exact":
        return False
    return _normalized_label(candidate.get("candidate_label")) is not None


def _candidate_rank_key(candidate: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        candidate.get("generator_name") != "deterministic_candidates_all",
        candidate.get("candidate_kind") != "frequency_rate",
        str(_normalized_label(candidate.get("candidate_label")) or ""),
        str(candidate.get("candidate_id") or ""),
        str(candidate.get("candidate_evidence") or ""),
    )


def _test_candidate_rank_key(candidate: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        candidate.get("candidate_source") != "deterministic_candidates_all",
        candidate.get("candidate_kind") != "frequency_rate",
        str(candidate.get("proposed_label") or ""),
        str(candidate.get("candidate_id") or ""),
        str(candidate.get("proposed_evidence") or ""),
    )


def _raw_reuse_key(row: Mapping[str, Any]) -> tuple[int, str, str] | None:
    try:
        return (
            int(row["source_row_index"]),
            str(_normalized_label(row["current_label"]) or ""),
            str(_normalized_label(row["proposed_label"]) or ""),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _normalized_label(label: Any) -> str | None:
    if not label:
        return None
    try:
        return label_to_frequency_record(str(label)).normalized_label
    except ValueError:
        return None


def _purist_correct(label: Any, gold_label: Any) -> bool:
    try:
        prediction = label_to_frequency_record(str(label))
        gold = label_to_frequency_record(str(gold_label))
    except ValueError:
        return False
    from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist

    return map_purist(prediction.monthly_frequency) == map_purist(gold.monthly_frequency)


def _interpretation(summary: Mapping[str, Any]) -> str:
    if summary["decision"] == "promote_candidate":
        return (
            "Promote to a frozen aggregate-only holdout audit: validation full-family "
            "accounting has positive W->C movement and zero C->W regressions."
        )
    if summary["transition_counts"].get("C_to_W", 0):
        return "Reject or revise on validation: at least one validation C->W regression remains."
    return "Diagnostic only: no validation regressions, but no corrected rows either."


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["validation-family", "test-aggregate"],
        default="validation-family",
    )
    parser.add_argument(
        "--candidate-discovery-path",
        type=Path,
        default=DEFAULT_CANDIDATE_DISCOVERY_PATH,
    )
    parser.add_argument("--test-input-path", type=Path, default=DEFAULT_TEST_INPUT_PATH)
    parser.add_argument("--test-json-path", type=Path, default=DEFAULT_TEST_JSON_PATH)
    parser.add_argument("--test-report-path", type=Path, default=DEFAULT_TEST_REPORT_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--max-tokens", type=int, default=500)
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument(
        "--raw-reuse-path",
        type=Path,
        action="append",
        default=list(DEFAULT_RAW_REUSE_PATHS),
    )
    args = parser.parse_args(argv)

    if args.mode == "test-aggregate":
        metadata = run_test_aggregate_audit(
            load_jsonl_rows(args.test_input_path),
            model=args.model,
            max_tokens=args.max_tokens,
            progress_every=args.progress_every,
        )
        write_summary_json(metadata, args.test_json_path)
        write_test_aggregate_report(
            metadata,
            args.test_report_path,
            json_path=args.test_json_path,
        )
        print(json.dumps(metadata["metrics"], indent=2, sort_keys=True))
        print(metadata["interpretation"])
        return

    current_rows = load_current_validation_rows()
    family_rows = build_validation_family(
        load_jsonl_rows(args.candidate_discovery_path),
        current_rows,
    )
    whole_base = current_rows[0]["whole_validation_base_correct_rows"] if current_rows else 0
    for row in family_rows:
        row["whole_validation_base_correct_rows"] = whole_base
    rows, metadata = run_family_experiment(
        family_rows,
        model=args.model,
        max_tokens=args.max_tokens,
        raw_reuse_paths=args.raw_reuse_path,
        progress_every=args.progress_every,
    )
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    print(json.dumps(metadata["metrics"], indent=2, sort_keys=True))
    print(metadata["interpretation"])


if __name__ == "__main__":
    main()
