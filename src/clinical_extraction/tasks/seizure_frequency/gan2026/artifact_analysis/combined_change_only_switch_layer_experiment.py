"""Compose validation-clean change-only switch families into one switch layer."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    change_only_det_state_family_experiment as det_state_experiment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    change_only_candidate_verifier,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist

DATE = "2026-06-05"
MODEL = "openai/gpt-4.1"
POLICY_NAME = "gan2026_combined_change_only_switch_layer_v0"
DEFAULT_DET_STATE_VALIDATION_JSONL_PATH = Path(
    "experiments/gan2026_change_only_verifier_det_state_alt_full_family_gpt41_2026-06-05.jsonl"
)
DEFAULT_LLM_VALIDATION_JSONL_PATH = Path(
    "experiments/gan2026_change_only_verifier_llm_selector_exact_full_family_gpt41_reparse2_2026-06-05.jsonl"
)
DEFAULT_VALIDATION_JSONL_PATH = Path(
    "experiments/gan2026_combined_change_only_switch_layer_validation750_2026-06-05.jsonl"
)
DEFAULT_VALIDATION_JSON_PATH = Path(
    "experiments/gan2026_combined_change_only_switch_layer_validation750_2026-06-05.json"
)
DEFAULT_VALIDATION_REPORT_PATH = Path(
    "experiments/gan2026_combined_change_only_switch_layer_validation750_2026-06-05.md"
)
DEFAULT_TEST_INPUT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_"
    "deterministic_safety_floor_live_2026-06-03.jsonl"
)
DEFAULT_TEST_JSON_PATH = Path(
    "experiments/gan2026_combined_change_only_switch_layer_test450_aggregate_audit_2026-06-05.json"
)
DEFAULT_TEST_REPORT_PATH = Path(
    "experiments/gan2026_combined_change_only_switch_layer_test450_aggregate_audit_2026-06-05.md"
)


def validation_rows_from_saved_outputs(
    det_state_rows: Sequence[Mapping[str, Any]],
    llm_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    current_rows = det_state_experiment.load_current_validation_rows()
    proposals = {
        "det_state_exact": _proposal_by_source(det_state_rows, "det_state_exact"),
        "llm_selector_exact": _proposal_by_source(llm_rows, "llm_selector_exact"),
    }
    rows = []
    for current in current_rows:
        idx = int(current["source_row_index"])
        current_label = _normalized_label(current["prediction_label"])
        final_label = current_label
        selected = None
        for family_name in ["det_state_exact", "llm_selector_exact"]:
            proposal = proposals[family_name].get(idx)
            if not proposal:
                continue
            if proposal["label"] and proposal["label"] != current_label:
                final_label = proposal["label"]
                selected = proposal
                break
        current_correct = _purist_correct(current_label, current["gold_label"])
        final_correct = _purist_correct(final_label, current["gold_label"])
        rows.append(
            {
                "artifact_kind": "gan2026_combined_change_only_switch_layer_validation_row",
                "source_row_index": idx,
                "split": "validation",
                "split_manifest": "gan2026_split_v1",
                "policy_name": POLICY_NAME,
                "current_label": current_label,
                "final_label": final_label,
                "gold_label": _normalized_label(current["gold_label"]),
                "current_purist_correct": current_correct,
                "final_purist_correct": final_correct,
                "transition": change_only_candidate_verifier.transition(
                    current_correct,
                    final_correct,
                ),
                "selected_family": selected["family_name"] if selected else "keep_current",
                "selected_candidate_kind": selected.get("candidate_kind") if selected else None,
                "selected_candidate_source": selected.get("candidate_source") if selected else None,
            }
        )
    metadata = summarize_validation_rows(rows)
    return rows, metadata


def summarize_validation_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    transitions = Counter(str(row["transition"]) for row in rows)
    family_counts = Counter(str(row["selected_family"]) for row in rows)
    base_correct = sum(bool(row["current_purist_correct"]) for row in rows)
    final_correct = sum(bool(row["final_purist_correct"]) for row in rows)
    return {
        "artifact_kind": "gan2026_combined_change_only_switch_layer_validation_summary",
        "date": DATE,
        "policy_name": POLICY_NAME,
        "claim_boundary": (
            "Validation-development composition of already validation-clean change-only "
            "switch families over the staged reasoner scorer-facing label. This does not "
            "authorize benchmark-comparable claims."
        ),
        "family_priority": ["det_state_exact", "llm_selector_exact", "keep_current"],
        "metrics": {
            "row_count": len(rows),
            "base_correct_rows": base_correct,
            "projected_correct_rows": final_correct,
            "base_purist_proxy": _rate(base_correct, len(rows)),
            "projected_purist_proxy": _rate(final_correct, len(rows)),
            "changed_rows": sum(row["selected_family"] != "keep_current" for row in rows),
            "changed_label_precision": _rate(
                transitions["W_to_C"],
                transitions["W_to_C"] + transitions["C_to_W"],
            ),
        },
        "transition_counts": dict(sorted(transitions.items())),
        "selected_family_counts": dict(sorted(family_counts.items())),
        "decision": (
            "freeze_candidate_for_aggregate_audit"
            if transitions["W_to_C"] > 0 and transitions["C_to_W"] == 0
            else "reject_or_revise"
        ),
    }


def run_test_aggregate_audit(
    test_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
    progress_every: int,
) -> dict[str, Any]:
    output_rows = []
    for index, test_row in enumerate(test_rows, 1):
        output_rows.append(
            _run_test_row(test_row, model=model, max_tokens=max_tokens)
        )
        if progress_every and index % progress_every == 0:
            summary = _aggregate_partial(output_rows)
            print(
                f"processed={index}/{len(test_rows)} "
                f"transitions={summary['transition_counts']}"
            )
    return summarize_test_rows(output_rows, test_rows, model=model)


def summarize_test_rows(
    rows: Sequence[Mapping[str, Any]],
    test_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
) -> dict[str, Any]:
    transitions = Counter(str(row["transition"]) for row in rows)
    family_counts = Counter(str(row["selected_family"]) for row in rows)
    base_correct = sum(
        bool(row["score_layers"]["hybrid_adjudicator_raw"]["purist_correct"])
        for row in test_rows
    )
    projected_correct = base_correct + transitions["W_to_C"] - transitions["C_to_W"]
    return {
        "artifact_kind": "gan2026_combined_change_only_switch_layer_test450_aggregate_audit",
        "date": DATE,
        "model": model,
        "policy_name": POLICY_NAME,
        "source_artifact": str(DEFAULT_TEST_INPUT_PATH),
        "claim_boundary": (
            "Frozen locked-test aggregate-only audit for the combined change-only switch "
            "layer. This summary intentionally omits row ids, clinical text, raw model "
            "outputs, and row-level failures."
        ),
        "family_priority": ["det_state_exact", "llm_selector_exact", "keep_current"],
        "metrics": {
            "test_rows": len(test_rows),
            "call_ok_rows": sum(bool(row["call_ok"]) for row in rows),
            "base_correct_rows": base_correct,
            "projected_correct_rows": projected_correct,
            "base_purist_proxy": _rate(base_correct, len(test_rows)),
            "projected_purist_proxy": _rate(projected_correct, len(test_rows)),
            "changed_rows": sum(row["selected_family"] != "keep_current" for row in rows),
            "changed_label_precision": _rate(
                transitions["W_to_C"],
                transitions["W_to_C"] + transitions["C_to_W"],
            ),
        },
        "transition_counts": dict(sorted(transitions.items())),
        "selected_family_counts": dict(sorted(family_counts.items())),
        "decision": (
            "meets_requested_test_threshold"
            if _rate(projected_correct, len(test_rows)) >= 0.9
            else "does_not_meet_goal"
        ),
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(metadata: Mapping[str, Any], path: Path, *, json_path: Path) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Combined Change-Only Switch Layer",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["decision"]),
        "",
        "## Artifacts",
        "",
        f"- Summary JSON: `{json_path}`",
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
    lines.extend(["", "## Selected Families", "", "| Family | Rows |", "| --- | ---: |"])
    for key, value in metadata["selected_family_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _run_test_row(
    test_row: Mapping[str, Any],
    *,
    model: str,
    max_tokens: int,
) -> dict[str, Any]:
    current_label = _normalized_label(
        test_row["score_layers"]["hybrid_adjudicator_raw"]["final_label"]
    )
    gold_label = _normalized_label(test_row["reference"]["gold_normalized_label"])
    selected_family = "keep_current"
    final_label = current_label
    call_ok = True
    for family_name, candidate in [
        ("det_state_exact", _test_det_state_candidate(test_row, current_label)),
        ("llm_selector_exact", _test_llm_candidate(test_row, current_label)),
    ]:
        if not candidate:
            continue
        run_row = {
            "source_row_index": int(test_row["source_row_index"]),
            "split": "test",
            "split_manifest": test_row.get("split_manifest", "gan2026_split_v1"),
            "clinical_text": str(test_row["component_inputs"]["note_text"]),
            "gold_label": gold_label,
            "current_label": current_label,
            "proposed_label": candidate["proposed_label"],
            "proposed_evidence": candidate["proposed_evidence"],
            "candidate_source": candidate["candidate_source"],
            "candidate_kind": candidate["candidate_kind"],
            "candidate_id": candidate["candidate_id"],
        }
        result = det_state_experiment._run_row(
            run_row,
            model=model,
            max_tokens=max_tokens,
            raw_reuse={},
        )
        call_ok = call_ok and result["call_status"] == "ok"
        decision_label = result["verifier_decision"]["label"]
        if decision_label and decision_label != current_label:
            final_label = decision_label
            selected_family = family_name
            break
    current_correct = _purist_correct(current_label, gold_label)
    final_correct = _purist_correct(final_label, gold_label)
    return {
        "call_ok": call_ok,
        "selected_family": selected_family,
        "transition": change_only_candidate_verifier.transition(current_correct, final_correct),
    }


def _test_det_state_candidate(
    row: Mapping[str, Any],
    current_label: str | None,
) -> dict[str, str] | None:
    candidates = []
    inputs = row["component_inputs"]
    for source_name, key in [
        ("deterministic_candidates_all", "deterministic_candidates"),
        ("state_graph_nodes", "state_graph_nodes"),
    ]:
        for candidate in inputs.get(key) or []:
            kind = candidate.get("kind")
            if kind not in {"frequency_rate", "cluster_frequency"}:
                continue
            label = _normalized_label(candidate.get("normalized_label"))
            if label and label != current_label and candidate.get("evidence"):
                candidates.append(
                    {
                        "candidate_source": source_name,
                        "candidate_kind": str(kind),
                        "candidate_id": str(
                            candidate.get("source_id")
                            or candidate.get("event_id")
                            or candidate.get("node_id")
                            or ""
                        ),
                        "proposed_label": label,
                        "proposed_evidence": str(candidate.get("evidence") or ""),
                    }
                )
    if not candidates:
        return None
    return sorted(candidates, key=_det_state_rank_key)[0]


def _test_llm_candidate(
    row: Mapping[str, Any],
    current_label: str | None,
) -> dict[str, str] | None:
    candidates = []
    for candidate in row["component_inputs"].get("llm_candidates") or []:
        kind = candidate.get("kind")
        if kind not in {
            "frequency_rate",
            "unknown_frequency",
            "cluster_frequency",
            "last_event_only",
        }:
            continue
        label = _normalized_label(candidate.get("normalized_label"))
        if label and label != current_label and candidate.get("evidence"):
            candidates.append(
                {
                    "candidate_source": "llm_candidate_selector_raw",
                    "candidate_kind": str(kind),
                    "candidate_id": str(candidate.get("candidate_id") or ""),
                    "proposed_label": label,
                    "proposed_evidence": str(candidate.get("evidence") or ""),
                }
            )
    if not candidates:
        return None
    return sorted(candidates, key=_llm_rank_key)[0]


def _proposal_by_source(
    rows: Sequence[Mapping[str, Any]],
    family_name: str,
) -> dict[int, dict[str, Any]]:
    proposals = {}
    for row in rows:
        current_label = _normalized_label(row.get("current_label"))
        decision = row.get("verifier_decision") or {}
        label = _normalized_label(decision.get("label"))
        if not label or label == current_label:
            continue
        proposals[int(row["source_row_index"])] = {
            "family_name": family_name,
            "label": label,
            "candidate_kind": row.get("candidate_kind"),
            "candidate_source": row.get("candidate_source"),
        }
    return proposals


def _aggregate_partial(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    transitions = Counter(str(row["transition"]) for row in rows)
    return {"transition_counts": dict(sorted(transitions.items()))}


def _det_state_rank_key(candidate: Mapping[str, str]) -> tuple[Any, ...]:
    return (
        candidate.get("candidate_source") != "deterministic_candidates_all",
        candidate.get("candidate_kind") != "frequency_rate",
        candidate.get("proposed_label") or "",
        candidate.get("candidate_id") or "",
        candidate.get("proposed_evidence") or "",
    )


def _llm_rank_key(candidate: Mapping[str, str]) -> tuple[Any, ...]:
    priority = {
        "frequency_rate": 0,
        "unknown_frequency": 1,
        "cluster_frequency": 2,
        "last_event_only": 3,
    }
    return (
        priority.get(candidate.get("candidate_kind") or "", 99),
        candidate.get("proposed_label") or "",
        candidate.get("candidate_id") or "",
        candidate.get("proposed_evidence") or "",
    )


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
    return map_purist(prediction.monthly_frequency) == map_purist(gold.monthly_frequency)


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["validation", "test-aggregate"], default="validation")
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--max-tokens", type=int, default=500)
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--validation-jsonl-path", type=Path, default=DEFAULT_VALIDATION_JSONL_PATH)
    parser.add_argument("--validation-json-path", type=Path, default=DEFAULT_VALIDATION_JSON_PATH)
    parser.add_argument(
        "--validation-report-path",
        type=Path,
        default=DEFAULT_VALIDATION_REPORT_PATH,
    )
    parser.add_argument("--test-input-path", type=Path, default=DEFAULT_TEST_INPUT_PATH)
    parser.add_argument("--test-json-path", type=Path, default=DEFAULT_TEST_JSON_PATH)
    parser.add_argument("--test-report-path", type=Path, default=DEFAULT_TEST_REPORT_PATH)
    args = parser.parse_args(argv)

    if args.mode == "test-aggregate":
        metadata = run_test_aggregate_audit(
            load_jsonl_rows(args.test_input_path),
            model=args.model,
            max_tokens=args.max_tokens,
            progress_every=args.progress_every,
        )
        write_summary_json(metadata, args.test_json_path)
        write_report(metadata, args.test_report_path, json_path=args.test_json_path)
        print(json.dumps(metadata["metrics"], indent=2, sort_keys=True))
        print(metadata["decision"])
        return

    rows, metadata = validation_rows_from_saved_outputs(
        load_jsonl_rows(DEFAULT_DET_STATE_VALIDATION_JSONL_PATH),
        load_jsonl_rows(DEFAULT_LLM_VALIDATION_JSONL_PATH),
    )
    write_jsonl_rows(rows, args.validation_jsonl_path)
    write_summary_json(metadata, args.validation_json_path)
    write_report(metadata, args.validation_report_path, json_path=args.validation_json_path)
    print(json.dumps(metadata["metrics"], indent=2, sort_keys=True))
    print(metadata["decision"])


if __name__ == "__main__":
    main()
