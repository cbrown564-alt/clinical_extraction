"""Replay the frozen joint Diagnosis and Prescription policy on saved dev140 outputs."""

from __future__ import annotations

import argparse
import json
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
    from scripts import check_exectv2_prescription_bounded_policy_candidate as rx_check
    from scripts import check_exectv2_prescription_rescue_scope_candidate as prior_check
else:
    import analyze_exectv2_model_led_dev140_regressions as baseline_analysis
    import check_exectv2_prescription_bounded_policy_candidate as rx_check
    import check_exectv2_prescription_rescue_scope_candidate as prior_check

CONFIG_DIR = Path("configs/exectv2/model_led_audit")
OUTPUT_PATH = Path(
    "experiments/exectv2_joint_bounded_policy_replay_dev140_20260715.json"
)
PROTOCOL_PATH = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_joint_bounded_policy_replay_protocol_2026-07-15.md"
)
GENERATED_ON = "2026-07-15"
FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
EXPECTED_COMPONENT_DIRECTIONS = {
    "Diagnosis": {
        "changed_still_wrong": 78,
        "correct_to_wrong": 3,
        "wrong_to_correct": 88,
    },
    "SeizureFrequency": {
        "changed_still_wrong": 20,
        "wrong_to_correct": 38,
    },
    "Prescription": {
        "changed_still_wrong": 10,
        "wrong_to_correct": 46,
    },
    "Investigations": {},
}
EXPECTED_LOST_RESCUES = {
    (model, "Diagnosis", letter)
    for model in (
        "DeepSeek chat",
        "GPT-4.1-mini",
        "Qwen 3.6 35B repair v02",
    )
    for letter in ("EA0082", "EA0126")
} | {("Qwen 3.6 35B repair v02", "Prescription", "EA0141")}
REQUIRED_PRESCRIPTION_RESCUES = {
    ("DeepSeek chat", "Prescription", "EA0096"),
    ("GPT-4.1-mini", "Prescription", "EA0096"),
    ("DeepSeek chat", "Prescription", "EA0127"),
    ("Qwen 3.6 35B repair v02", "Prescription", "EA0150"),
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
    policy_names = (
        "current",
        "implemented_fallback",
        "diagnosis_only",
        "prescription_only",
        "joint",
    )
    records = {name: [] for name in policy_names}
    policy_models: dict[str, dict[str, Any]] = {name: {} for name in policy_names}
    diagnostics_match = True
    with tempfile.TemporaryDirectory(prefix="exectv2-joint-bounded-dev140-") as temp:
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
                "current": build_finding_assembly(replay.assembly, **run_args),
                "implemented_fallback": build_finding_assembly(
                    replay.assembly,
                    **run_args,
                    model_preserving_policy_candidate=True,
                ),
                "diagnosis_only": build_finding_assembly(
                    replay.assembly,
                    **run_args,
                    diagnosis_policy_variant="combined",
                ),
                "prescription_only": build_finding_assembly(
                    replay.assembly,
                    **run_args,
                    prescription_policy_variant="combined",
                ),
                "joint": build_finding_assembly(
                    replay.assembly,
                    **run_args,
                    diagnosis_policy_variant="combined",
                    prescription_policy_variant="combined",
                ),
            }
            current_failures = rx_check._failure_counts(
                runs["current"].report["lane_diagnostics"]
            )
            for name, run in runs.items():
                model_records = baseline_analysis._changed_records(
                    config, replay, run, gold
                )
                records[name].extend(model_records)
                failures = rx_check._failure_counts(run.report["lane_diagnostics"])
                diagnostics_match = diagnostics_match and failures == current_failures
                policy_models[name][config.model_label] = {
                    "summary": baseline_analysis._model_summary(model_records),
                    "stage_scores": baseline_analysis._stage_scores(replay, run, gold),
                    "failure_counts": failures,
                }

    current_records = records["current"]
    fallback_records = records["implemented_fallback"]
    joint_records = records["joint"]
    rows = prior_check._comparison_rows(current_records, joint_records)
    for row in rows:
        row["case_tags"] = ["joint_policy", row["family"]]
        if str(row["first_prediction_changing_owner"]).startswith(
            "prescription_rescue_scope_candidate:"
        ):
            row["first_prediction_changing_owner"] = (
                "joint_bounded_policy:restored_model_owned_output"
            )
    if any(str(row["letter_id"]) not in dev_ids for row in rows):
        raise ValueError("joint analysis retained a non-dev letter")
    fallback_rows = prior_check._comparison_rows(fallback_records, joint_records)

    summaries = {
        name: baseline_analysis._summary(policy_records)
        for name, policy_records in records.items()
    }
    component_identity = _component_identity(records)
    gates = _evaluate_gates(
        current_records=current_records,
        fallback_records=fallback_records,
        joint_records=joint_records,
        current_joint_rows=rows,
        summaries=summaries,
        policy_models=policy_models,
        component_identity=component_identity,
        diagnostics_match=diagnostics_match,
    )
    public_policies = {
        name: {
            "models": policy_models[name],
            "summary": summaries[name],
        }
        for name in ("current", "implemented_fallback", "joint")
    }
    return {
        "schema_version": "exectv2_joint_bounded_policy_replay_dev140_v1",
        "generated_on": GENERATED_ON,
        "protocol": PROTOCOL_PATH.as_posix(),
        "candidate_id": "decision_0040_joint_bounded_dev140_v1",
        "comparator": "decision_0040_model_led_current_policy",
        "fallback": "decision_0040_model_preserving_dev140_v1",
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_policy": "dev140_rows_permitted_test60_forbidden",
        "call_mode": "historical_git_blob_replay_no_model_calls",
        "new_model_calls": 0,
        "environment": rx_check._environment_record(configs),
        "policies": public_policies,
        "component_identity": component_identity,
        "gates": gates,
        "decision": (
            "select_joint_bounded_policy_as_disclosed_fallback"
            if gates["status"] == "pass"
            else "retain_implemented_model_preserving_fallback"
        ),
        "rows": rows,
        "fallback_comparison_rows": [
            {
                "model_label": row["model_label"],
                "family": row["family"],
                "letter_id": row["letter_id"],
                "fallback_correct": row["comparator_correct"],
                "joint_correct": row["candidate_correct"],
                "evidence_status": row["evidence_status"],
            }
            for row in fallback_rows
        ],
        "claim_boundary": (
            "Inspected dev140 development evidence for three saved model outputs only. "
            "No test60 row was assembled, scored, serialized, or inspected; no model "
            "was called; this is not holdout evidence or clinical validation."
        ),
    }


def _component_identity(records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    joint = _record_map(records["joint"])
    diagnosis = _record_map(records["diagnosis_only"])
    prescription = _record_map(records["prescription_only"])
    current = _record_map(records["current"])
    checks = {
        "diagnosis_matches_separate_candidate": _family_record_map(joint, "Diagnosis")
        == _family_record_map(diagnosis, "Diagnosis"),
        "prescription_matches_separate_candidate": _family_record_map(
            joint, "Prescription"
        )
        == _family_record_map(prescription, "Prescription"),
        "seizure_frequency_matches_current": _family_record_map(
            joint, "SeizureFrequency"
        )
        == _family_record_map(current, "SeizureFrequency"),
        "investigations_matches_current": _family_record_map(joint, "Investigations")
        == _family_record_map(current, "Investigations"),
    }
    return {"status": "pass" if all(checks.values()) else "fail", "checks": checks}


def _record_map(
    records: list[dict[str, Any]],
) -> dict[tuple[str, str, str], tuple[tuple[str, int], ...]]:
    return {
        (row["model_label"], row["family"], row["letter_id"]): tuple(
            (json.dumps(item["key"], sort_keys=True), int(item["count"]))
            for item in row["final_keys"]
        )
        for row in records
    }


def _family_record_map(
    records: dict[tuple[str, str, str], tuple[tuple[str, int], ...]],
    family: str,
) -> dict[tuple[str, str, str], tuple[tuple[str, int], ...]]:
    return {key: value for key, value in records.items() if key[1] == family}


def _evaluate_gates(
    *,
    current_records: list[dict[str, Any]],
    fallback_records: list[dict[str, Any]],
    joint_records: list[dict[str, Any]],
    current_joint_rows: list[dict[str, Any]],
    summaries: dict[str, Any],
    policy_models: dict[str, dict[str, Any]],
    component_identity: dict[str, Any],
    diagnostics_match: bool,
) -> dict[str, Any]:
    joint_by_family = summaries["joint"]["primary_family_local"]["by_family"]
    normalized_joint_by_family = {
        family: joint_by_family.get(family, {}) for family in FAMILIES
    }
    component_counts_match = normalized_joint_by_family == EXPECTED_COMPONENT_DIRECTIONS
    joint_directions = _direction_counts(joint_records)
    fallback_directions = _direction_counts(fallback_records)
    current_rescues, joint_retained, joint_lost = _rescue_retention(
        current_records, joint_records
    )
    _, fallback_retained, _fallback_lost = _rescue_retention(
        current_records, fallback_records
    )
    score_checks: dict[str, bool] = {}
    for model_label, joint_model in policy_models["joint"].items():
        joint_scores = joint_model["stage_scores"]["final_post_rule"]
        fallback_scores = policy_models["implemented_fallback"][model_label][
            "stage_scores"
        ]["final_post_rule"]
        for score_name in ("overall", "Diagnosis", "Prescription"):
            score_checks[f"{model_label}:{score_name}"] = (
                float(joint_scores[score_name]) >= float(fallback_scores[score_name])
            )
    retained_required = REQUIRED_PRESCRIPTION_RESCUES & joint_retained
    checks = {
        "component_identity_exact": component_identity["status"] == "pass",
        "component_direction_counts_exact": component_counts_match,
        "total_wrong_to_correct_at_least_172": joint_directions["wrong_to_correct"]
        >= 172,
        "total_correct_to_wrong_at_most_3": joint_directions["correct_to_wrong"] <= 3,
        "retain_at_least_150_of_160_current_rescues": len(joint_retained) >= 150,
        "lost_rescues_match_seven_predeclared_identities": (
            joint_lost == EXPECTED_LOST_RESCUES
        ),
        "retain_all_demonstrated_prescription_rescues": (
            retained_required == REQUIRED_PRESCRIPTION_RESCUES
        ),
        "direction_counts_dominate_fallback": _direction_dominates(
            joint_directions, fallback_directions
        ),
        "rescue_retention_exceeds_fallback": len(joint_retained)
        > len(fallback_retained),
        "all_current_joint_changes_exact_evidence": all(
            row["evidence_status"] == "exact" for row in current_joint_rows
        ),
        "all_saved_model_scores_no_worse_than_fallback": all(score_checks.values()),
        "no_new_schema_parse_call_or_fallback_failure": diagnostics_match,
    }
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "component_identity": component_identity,
        "component_directions": normalized_joint_by_family,
        "joint_directions": joint_directions,
        "fallback_directions": fallback_directions,
        "current_rescues": len(current_rescues),
        "joint_rescue_retention": {
            "retained": len(joint_retained),
            "lost": len(joint_lost),
            "lost_identities": sorted([list(row) for row in joint_lost]),
        },
        "fallback_rescue_retention": {
            "retained": len(fallback_retained),
            "lost": len(current_rescues - fallback_retained),
        },
        "retained_required_prescription_rescues": sorted(
            [list(row) for row in retained_required]
        ),
        "score_checks": score_checks,
    }


def _direction_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(row["family_local_change_direction"] for row in records)
    return {
        direction: counts[direction]
        for direction in ("wrong_to_correct", "correct_to_wrong", "changed_still_wrong")
    }


def _direction_dominates(joint: dict[str, int], fallback: dict[str, int]) -> bool:
    return (
        joint["wrong_to_correct"] > fallback["wrong_to_correct"]
        and joint["correct_to_wrong"] < fallback["correct_to_wrong"]
        and joint["changed_still_wrong"] <= fallback["changed_still_wrong"]
    )


def _rescue_retention(
    comparator_records: list[dict[str, Any]],
    candidate_records: list[dict[str, Any]],
) -> tuple[
    set[tuple[str, str, str]],
    set[tuple[str, str, str]],
    set[tuple[str, str, str]],
]:
    def key(row: dict[str, Any]) -> tuple[str, str, str]:
        return row["model_label"], row["family"], row["letter_id"]

    rescues = {
        key(row)
        for row in comparator_records
        if row["family_local_change_direction"] == "wrong_to_correct"
    }
    candidate = {key(row): row for row in candidate_records}
    retained = {
        rescue
        for rescue in rescues
        if rescue in candidate
        and candidate[rescue]["family_local_change_direction"] == "wrong_to_correct"
    }
    return rescues, retained, rescues - retained


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-dir", type=Path, default=CONFIG_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    return parser.parse_args()


if __name__ == "__main__":
    main()
