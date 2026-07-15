"""Evaluate the predeclared Prescription rescue-scope candidate on dev140."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap

if __package__:
    from scripts import analyze_exectv2_model_led_dev140_regressions as baseline_analysis
else:
    import analyze_exectv2_model_led_dev140_regressions as baseline_analysis

CONFIG_DIR = Path("configs/exectv2/model_led_audit")
OUTPUT_PATH = Path(
    "experiments/exectv2_prescription_rescue_scope_candidate_dev140_20260715.json"
)
PROTOCOL_PATH = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_prescription_rescue_scope_candidate_protocol_2026-07-15.md"
)
GENERATED_ON = "2026-07-15"
PRESCRIPTION = "Prescription"


def main() -> None:
    args = _parse_args()
    configs = [
        model_swap.load_model_swap_config(path)
        for path in sorted(args.config_dir.glob("*.json"))
    ]
    payload = evaluate(configs)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "decision": payload["decision"],
                "gate_status": payload["gates"]["status"],
                "changed_rows": len(payload["rows"]),
                "output": args.output.as_posix(),
            },
            sort_keys=True,
        )
    )


def evaluate(configs: list[model_swap.ModelSwapConfig]) -> dict[str, Any]:
    if not PROTOCOL_PATH.exists():
        raise ValueError(f"predeclared protocol is missing: {PROTOCOL_PATH}")
    parity = model_swap.validate_same_core_configs(configs)
    if not parity["component_graph_identical"]:
        raise ValueError(f"model-led configurations differ: {parity['mismatched_candidates']}")
    for config in configs:
        contract = model_swap.validate_model_led_architecture(config)
        if contract["status"] != "pass":
            raise ValueError(f"{config.path}: {contract['violations']}")

    gold = load_letters_for_split("dev")
    if len(gold) != 140:
        raise ValueError(f"expected 140 dev letters, found {len(gold)}")
    dev_ids = {letter.letter_id for letter in gold}
    comparator_records: list[dict[str, Any]] = []
    candidate_records: list[dict[str, Any]] = []
    models: dict[str, Any] = {}
    diagnostics_match = True
    with tempfile.TemporaryDirectory(prefix="exectv2-rx-rescue-scope-dev140-") as temp:
        root = Path(temp)
        for config in configs:
            replay = baseline_analysis._materialize_dev_config(
                config, root / config.candidate_id, dev_ids
            )
            run_args = {
                "generated_on": GENERATED_ON,
                "gold_loader": lambda _split: gold,
                "diagnosis_resolution_candidate": config.diagnosis_resolution_candidate,
            }
            comparator = build_finding_assembly(replay.assembly, **run_args)
            candidate = build_finding_assembly(
                replay.assembly,
                **run_args,
                prescription_rescue_scope_candidate=True,
            )
            comparator_model_records = baseline_analysis._changed_records(
                config, replay, comparator, gold
            )
            candidate_model_records = baseline_analysis._changed_records(
                config, replay, candidate, gold
            )
            comparator_records.extend(comparator_model_records)
            candidate_records.extend(candidate_model_records)
            comparator_diagnostics = comparator.report["lane_diagnostics"]
            candidate_diagnostics = candidate.report["lane_diagnostics"]
            diagnostics_match = diagnostics_match and (
                _failure_counts(comparator_diagnostics)
                == _failure_counts(candidate_diagnostics)
            )
            models[config.model_label] = {
                "comparator": baseline_analysis._model_summary(comparator_model_records),
                "candidate": baseline_analysis._model_summary(candidate_model_records),
                "comparator_stage_scores": baseline_analysis._stage_scores(
                    replay, comparator, gold
                ),
                "candidate_stage_scores": baseline_analysis._stage_scores(
                    replay, candidate, gold
                ),
                "comparator_failure_counts": _failure_counts(comparator_diagnostics),
                "candidate_failure_counts": _failure_counts(candidate_diagnostics),
            }

    rows = _comparison_rows(comparator_records, candidate_records)
    if any(str(row["letter_id"]) not in dev_ids for row in rows):
        raise ValueError("candidate analysis retained a non-dev letter")
    gates = _evaluate_gates(
        comparator_records,
        candidate_records,
        rows,
        diagnostics_match=diagnostics_match,
    )
    return {
        "schema_version": "exectv2_prescription_rescue_scope_candidate_dev140_v1",
        "generated_on": GENERATED_ON,
        "protocol": PROTOCOL_PATH.as_posix(),
        "candidate_id": "decision_0040_rx_rescue_scope_no_residual_dev140_v1",
        "comparator": "decision_0040_model_led_current_policy",
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_policy": "dev140_rows_permitted_test60_forbidden",
        "call_mode": "historical_git_blob_replay_no_model_calls",
        "new_model_calls": 0,
        "environment": _environment_record(configs),
        "models": models,
        "comparator_summary": baseline_analysis._summary(comparator_records),
        "candidate_summary": baseline_analysis._summary(candidate_records),
        "gates": gates,
        "decision": "accept_for_next_frozen_comparison" if gates["status"] == "pass" else "reject",
        "rows": rows,
        "claim_boundary": (
            "Inspected dev140 development evidence for three saved model outputs only. "
            "No test60 row was assembled, scored, serialized, or inspected; no model "
            "was called; this is not holdout evidence or clinical validation."
        ),
    }


def _comparison_rows(
    comparator_records: list[dict[str, Any]],
    candidate_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    def key(row: dict[str, Any]) -> tuple[str, str, str]:
        return row["model_label"], row["family"], row["letter_id"]

    comparator = {key(row): row for row in comparator_records}
    candidate = {key(row): row for row in candidate_records}
    rows: list[dict[str, Any]] = []
    for row_key in sorted(set(comparator) | set(candidate)):
        comparator_row = comparator.get(row_key)
        candidate_row = candidate.get(row_key)
        seed = candidate_row or comparator_row
        assert seed is not None
        model_keys = seed["model_owned_keys"]
        comparator_keys = comparator_row["final_keys"] if comparator_row else model_keys
        candidate_keys = candidate_row["final_keys"] if candidate_row else model_keys
        if comparator_keys == candidate_keys:
            continue
        model_correct = bool(seed["family_local_model_owned_correct"])
        comparator_correct = (
            bool(comparator_row["family_local_final_correct"])
            if comparator_row
            else model_correct
        )
        candidate_correct = (
            bool(candidate_row["family_local_final_correct"])
            if candidate_row
            else model_correct
        )
        rows.append(
            {
                "dataset": "ExECTv2",
                "split": "dev140",
                "letter_id": seed["letter_id"],
                "model": seed["model"],
                "model_label": seed["model_label"],
                "family": seed["family"],
                "source_revision": seed["source_revision"],
                "model_owned_keys": model_keys,
                "comparator_keys": comparator_keys,
                "candidate_keys": candidate_keys,
                "family_local_gold_keys": seed["family_local_gold_keys"],
                "compatibility_gold_keys": seed["compatibility_gold_keys"],
                "model_owned_correct": model_correct,
                "comparator_correct": comparator_correct,
                "candidate_correct": candidate_correct,
                "newly_wrong_from_comparator_correct": comparator_correct
                and not candidate_correct,
                "comparator_family_local_direction": (
                    comparator_row["family_local_change_direction"]
                    if comparator_row
                    else "unchanged"
                ),
                "candidate_family_local_direction": (
                    candidate_row["family_local_change_direction"]
                    if candidate_row
                    else "unchanged"
                ),
                "selected_evidence": seed["selected_evidence"],
                "evidence_status": seed["evidence_status"],
                "comparator_deterministic_actions": (
                    comparator_row["deterministic_actions"] if comparator_row else []
                ),
                "candidate_deterministic_actions": (
                    candidate_row["deterministic_actions"] if candidate_row else []
                ),
                "first_prediction_changing_owner": (
                    candidate_row["first_prediction_changing_owner"]
                    if candidate_row
                    else "prescription_rescue_scope_candidate:restored_model_owned_output"
                ),
                "clinical_subproblem": "temporal_selection",
                "case_tags": ["prescription", "rescue_scope", "residual_removal"],
            }
        )
    return rows


def _evaluate_gates(
    comparator_records: list[dict[str, Any]],
    candidate_records: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    *,
    diagnostics_match: bool,
) -> dict[str, Any]:
    def key(row: dict[str, Any]) -> tuple[str, str, str]:
        return row["model_label"], row["family"], row["letter_id"]

    comparator_rx = [row for row in comparator_records if row["family"] == PRESCRIPTION]
    candidate_rx = [row for row in candidate_records if row["family"] == PRESCRIPTION]
    candidate_by_key = {key(row): row for row in candidate_rx}
    comparator_rescues = {
        key(row)
        for row in comparator_rx
        if row["family_local_change_direction"] == "wrong_to_correct"
    }
    retained = {
        rescue_key
        for rescue_key in comparator_rescues
        if rescue_key in candidate_by_key
        and candidate_by_key[rescue_key]["family_local_change_direction"]
        == "wrong_to_correct"
    }
    directions = Counter(row["family_local_change_direction"] for row in candidate_rx)
    newly_wrong = sum(bool(row["newly_wrong_from_comparator_correct"]) for row in rows)
    non_rx_changes = sum(row["family"] != PRESCRIPTION for row in rows)
    checks = {
        "prescription_correct_to_wrong_below_23": directions["correct_to_wrong"] < 23,
        "prescription_wrong_to_correct_at_least_36": directions["wrong_to_correct"] >= 36,
        "retain_at_least_36_of_41_comparator_prescription_rescues": len(retained) >= 36,
        "zero_newly_wrong_from_comparator_correct": newly_wrong == 0,
        "other_families_identical": non_rx_changes == 0,
        "all_comparator_candidate_changes_exact_evidence": all(
            row["evidence_status"] == "exact" for row in rows
        ),
        "no_new_schema_parse_call_or_fallback_failure": diagnostics_match,
    }
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "candidate_prescription_directions": dict(sorted(directions.items())),
        "comparator_rescue_retention": {
            "comparator_rescues": len(comparator_rescues),
            "retained": len(retained),
            "lost": len(comparator_rescues - retained),
        },
        "newly_wrong_from_comparator_correct": newly_wrong,
        "non_prescription_changed_rows": non_rx_changes,
    }


def _failure_counts(lane_diagnostics: dict[str, Any]) -> dict[str, int]:
    return {
        "call_failures": sum(int(row["call_failures"]) for row in lane_diagnostics.values()),
        "parse_schema_failures": sum(
            int(row["parse_schema_failures"]) for row in lane_diagnostics.values()
        ),
    }


def _environment_record(configs: list[model_swap.ModelSwapConfig]) -> dict[str, Any]:
    status = subprocess.run(
        ["git", "status", "--short"], check=True, capture_output=True, text=True
    ).stdout.splitlines()
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    return {
        "python": sys.version.split()[0],
        "repository_head": head,
        "working_tree_dirty": bool(status),
        "working_tree_changed_path_count": len(status),
        "replay_source_revisions": sorted({config.replay_source_revision for config in configs}),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-dir", type=Path, default=CONFIG_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    return parser.parse_args()


if __name__ == "__main__":
    main()
