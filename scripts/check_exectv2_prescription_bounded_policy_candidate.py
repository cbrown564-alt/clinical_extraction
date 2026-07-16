"""Evaluate the predeclared bounded Prescription policy on saved dev140 outputs."""

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
    from scripts import check_exectv2_prescription_rescue_scope_candidate as prior_check
else:
    import analyze_exectv2_model_led_dev140_regressions as baseline_analysis
    import check_exectv2_prescription_rescue_scope_candidate as prior_check

CONFIG_DIR = Path("configs/exectv2/model_led_audit")
OUTPUT_PATH = Path(
    "experiments/exectv2_prescription_bounded_policy_candidate_dev140_20260715.json"
)
PROTOCOL_PATH = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_prescription_bounded_policy_candidate_protocol_2026-07-15.md"
)
FALLBACK_PATH = Path(
    "experiments/exectv2_model_preserving_policy_candidate_dev140_20260715.json"
)
GENERATED_ON = "2026-07-15"
PRESCRIPTION = "Prescription"
PRESCRIPTION_VARIANTS = (
    "default",
    "local_scope_only",
    "current_guard_only",
    "residual_explicit_current_only",
    "combined",
)
REQUIRED_RESCUES = {
    ("DeepSeek chat", "EA0096"),
    ("GPT-4.1-mini", "EA0096"),
    ("DeepSeek chat", "EA0127"),
    ("Qwen 3.6 35B repair v02", "EA0150"),
}


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
    if not FALLBACK_PATH.exists():
        raise ValueError(f"fallback artifact is missing: {FALLBACK_PATH}")
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
    records = {variant: [] for variant in PRESCRIPTION_VARIANTS}
    ablation_models: dict[str, dict[str, Any]] = {
        variant: {} for variant in PRESCRIPTION_VARIANTS
    }
    diagnostics_match = True
    with tempfile.TemporaryDirectory(prefix="exectv2-rx-bounded-dev140-") as temp:
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
            runs = {
                variant: build_finding_assembly(
                    replay.assembly,
                    **run_args,
                    prescription_policy_variant=variant,
                )
                for variant in PRESCRIPTION_VARIANTS
            }
            default_failures = _failure_counts(runs["default"].report["lane_diagnostics"])
            for variant, run in runs.items():
                model_records = baseline_analysis._changed_records(
                    config, replay, run, gold
                )
                records[variant].extend(model_records)
                failures = _failure_counts(run.report["lane_diagnostics"])
                diagnostics_match = diagnostics_match and failures == default_failures
                ablation_models[variant][config.model_label] = {
                    "summary": baseline_analysis._model_summary(model_records),
                    "stage_scores": baseline_analysis._stage_scores(replay, run, gold),
                    "failure_counts": failures,
                }

    comparator_records = records["default"]
    candidate_records = records["combined"]
    rows = prior_check._comparison_rows(comparator_records, candidate_records)
    for row in rows:
        row["case_tags"] = [
            "prescription",
            "bounded_policy",
            "local_rescue_scope",
            "current_selection",
            "residual_rule_group_ablation",
        ]
        row["residual_rule_groups"] = _row_residual_rule_groups(row)
    if any(str(row["letter_id"]) not in dev_ids for row in rows):
        raise ValueError("candidate analysis retained a non-dev letter")

    ablations: dict[str, Any] = {}
    for variant in PRESCRIPTION_VARIANTS:
        variant_rows = (
            []
            if variant == "default"
            else prior_check._comparison_rows(comparator_records, records[variant])
        )
        ablations[variant] = {
            "models": ablation_models[variant],
            "summary": baseline_analysis._summary(records[variant]),
            "changed_from_default_rows": [
                {
                    "model_label": row["model_label"],
                    "letter_id": row["letter_id"],
                    "family": row["family"],
                    "evidence_status": row["evidence_status"],
                }
                for row in variant_rows
            ],
            "residual_rule_group_counts": _residual_rule_group_counts(records[variant]),
        }

    gates = _evaluate_gates(
        comparator_records,
        candidate_records,
        rows,
        diagnostics_match=diagnostics_match,
        required_rescues=REQUIRED_RESCUES,
    )
    fallback = json.loads(FALLBACK_PATH.read_text(encoding="utf-8"))
    return {
        "schema_version": "exectv2_prescription_bounded_policy_candidate_dev140_v1",
        "generated_on": GENERATED_ON,
        "protocol": PROTOCOL_PATH.as_posix(),
        "candidate_id": "decision_0040_rx_bounded_policy_dev140_v1",
        "comparator": "decision_0040_model_led_current_policy",
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_policy": "dev140_rows_permitted_test60_forbidden",
        "call_mode": "historical_git_blob_replay_no_model_calls",
        "new_model_calls": 0,
        "environment": _environment_record(configs),
        "ablations": ablations,
        "comparator_summary": baseline_analysis._summary(comparator_records),
        "candidate_summary": baseline_analysis._summary(candidate_records),
        "fallback_reference": {
            "candidate_id": fallback["candidate_id"],
            "decision": fallback["decision"],
            "prescription_summary": fallback["candidate_summary"][
                "primary_family_local"
            ]["by_family"][PRESCRIPTION],
            "comparator_rescue_retention": fallback["gates"][
                "comparator_rescue_retention"
            ],
        },
        "gates": gates,
        "decision": (
            "accept_for_next_frozen_comparison"
            if gates["status"] == "pass"
            else "use_implemented_model_preserving_fallback"
        ),
        "rows": rows,
        "claim_boundary": (
            "Inspected dev140 development evidence for three saved model outputs only. "
            "No test60 row was assembled, scored, serialized, or inspected; no model "
            "was called; this is not holdout evidence or clinical validation."
        ),
    }


def _evaluate_gates(
    comparator_records: list[dict[str, Any]],
    candidate_records: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    *,
    diagnostics_match: bool,
    required_rescues: set[tuple[str, str]],
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
    retained_pairs = {(model, letter) for model, _family, letter in retained}
    directions = Counter(row["family_local_change_direction"] for row in candidate_rx)
    newly_wrong = sum(bool(row["newly_wrong_from_comparator_correct"]) for row in rows)
    non_rx_changes = sum(row["family"] != PRESCRIPTION for row in rows)
    residual_groups = _residual_rule_group_counts(candidate_rx)
    checks = {
        "prescription_correct_to_wrong_below_23": directions["correct_to_wrong"] < 23,
        "prescription_wrong_to_correct_at_least_39": directions["wrong_to_correct"] >= 39,
        "retain_at_least_39_of_41_comparator_prescription_rescues": len(retained) >= 39,
        "retain_all_demonstrated_missing_regimen_rescues": (
            required_rescues <= retained_pairs
        ),
        "zero_newly_wrong_from_comparator_correct": newly_wrong == 0,
        "other_families_identical": non_rx_changes == 0,
        "all_comparator_candidate_changes_exact_evidence": all(
            row["evidence_status"] == "exact" for row in rows
        ),
        "retained_residuals_are_explicit_current_only": (
            not residual_groups
            or set(residual_groups) == {"explicit_current_regimen_recovery"}
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
        "required_rescues": sorted([list(row) for row in required_rescues]),
        "retained_required_rescues": sorted(
            [list(row) for row in required_rescues & retained_pairs]
        ),
        "newly_wrong_from_comparator_correct": newly_wrong,
        "non_prescription_changed_rows": non_rx_changes,
        "candidate_residual_rule_group_counts": residual_groups,
    }


def _row_residual_rule_groups(row: dict[str, Any]) -> list[str]:
    return sorted(
        {
            str(action["detail"]["residual_rule_group"])
            for action in row["candidate_deterministic_actions"]
            if action.get("action") == "added_prescription_residual_from_dictionary"
            and action.get("detail", {}).get("residual_rule_group")
        }
    )


def _residual_rule_group_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in records:
        for action in row.get("deterministic_actions", []):
            if action.get("action") != "added_prescription_residual_from_dictionary":
                continue
            group = action.get("detail", {}).get("residual_rule_group")
            if group:
                counts[str(group)] += 1
    return dict(sorted(counts.items()))


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
        "replay_source_revisions": sorted(
            {config.replay_source_revision for config in configs}
        ),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-dir", type=Path, default=CONFIG_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    return parser.parse_args()


if __name__ == "__main__":
    main()
