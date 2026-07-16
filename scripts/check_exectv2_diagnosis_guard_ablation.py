"""Evaluate predeclared Diagnosis guards independently on saved dev140 outputs."""

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
OUTPUT_PATH = Path("experiments/exectv2_diagnosis_guard_ablation_dev140_20260715.json")
PROTOCOL_PATH = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_diagnosis_guard_ablation_protocol_2026-07-15.md"
)
FALLBACK_PATH = Path(
    "experiments/exectv2_model_preserving_policy_candidate_dev140_20260715.json"
)
GENERATED_ON = "2026-07-15"
DIAGNOSIS = "Diagnosis"
DIAGNOSIS_VARIANTS = (
    "default",
    "residual_subsumption_only",
    "absence_preservation_only",
    "combined",
)
ALLOWED_LOST_RESCUES = {
    (model, letter)
    for model in (
        "DeepSeek chat",
        "GPT-4.1-mini",
        "Qwen 3.6 35B repair v02",
    )
    for letter in ("EA0082", "EA0126")
}
BROAD_CONCEPT_REGRESSION_LETTERS = {
    "EA0008",
    "EA0016",
    "EA0067",
    "EA0117",
    "EA0137",
    "EA0178",
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
    records = {variant: [] for variant in DIAGNOSIS_VARIANTS}
    ablation_models: dict[str, dict[str, Any]] = {
        variant: {} for variant in DIAGNOSIS_VARIANTS
    }
    diagnostics_match = True
    with tempfile.TemporaryDirectory(prefix="exectv2-dx-guards-dev140-") as temp:
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
                    diagnosis_policy_variant=variant,
                )
                for variant in DIAGNOSIS_VARIANTS
            }
            default_failures = rx_check._failure_counts(
                runs["default"].report["lane_diagnostics"]
            )
            for variant, run in runs.items():
                model_records = baseline_analysis._changed_records(
                    config, replay, run, gold
                )
                records[variant].extend(model_records)
                failures = rx_check._failure_counts(run.report["lane_diagnostics"])
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
        row["clinical_subproblem"] = (
            "candidate_generation"
            if row["letter_id"] == "EA0156"
            else "evidence_selection"
        )
        row["case_tags"] = [
            "diagnosis",
            "residual_subsumption",
            "absence_phenotype_preservation",
        ]
    if any(str(row["letter_id"]) not in dev_ids for row in rows):
        raise ValueError("Diagnosis analysis retained a non-dev letter")

    ablations: dict[str, Any] = {}
    for variant in DIAGNOSIS_VARIANTS:
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
        }

    gates = _evaluate_gates(
        comparator_records,
        candidate_records,
        rows,
        diagnostics_match=diagnostics_match,
        allowed_lost_rescues=ALLOWED_LOST_RESCUES,
    )
    fallback = json.loads(FALLBACK_PATH.read_text(encoding="utf-8"))
    return {
        "schema_version": "exectv2_diagnosis_guard_ablation_dev140_v1",
        "generated_on": GENERATED_ON,
        "protocol": PROTOCOL_PATH.as_posix(),
        "candidate_id": "decision_0040_diagnosis_guards_dev140_v1",
        "comparator": "decision_0040_model_led_current_policy",
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_policy": "dev140_rows_permitted_test60_forbidden",
        "call_mode": "historical_git_blob_replay_no_model_calls",
        "new_model_calls": 0,
        "environment": rx_check._environment_record(configs),
        "ablations": ablations,
        "comparator_summary": baseline_analysis._summary(comparator_records),
        "candidate_summary": baseline_analysis._summary(candidate_records),
        "fallback_reference": {
            "candidate_id": fallback["candidate_id"],
            "decision": fallback["decision"],
            "diagnosis_summary": fallback["candidate_summary"][
                "primary_family_local"
            ]["by_family"][DIAGNOSIS],
        },
        "gates": gates,
        "decision": (
            "accept_diagnosis_guards_for_fallback"
            if gates["status"] == "pass"
            else "retain_bundled_fallback_by_user_decision"
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
    allowed_lost_rescues: set[tuple[str, str]],
) -> dict[str, Any]:
    def key(row: dict[str, Any]) -> tuple[str, str, str]:
        return row["model_label"], row["family"], row["letter_id"]

    comparator_dx = [row for row in comparator_records if row["family"] == DIAGNOSIS]
    candidate_dx = [row for row in candidate_records if row["family"] == DIAGNOSIS]
    candidate_by_key = {key(row): row for row in candidate_dx}
    comparator_rescues = {
        key(row)
        for row in comparator_dx
        if row["family_local_change_direction"] == "wrong_to_correct"
    }
    retained = {
        rescue_key
        for rescue_key in comparator_rescues
        if rescue_key in candidate_by_key
        and candidate_by_key[rescue_key]["family_local_change_direction"]
        == "wrong_to_correct"
    }
    lost_pairs = {
        (model, letter) for model, _family, letter in comparator_rescues - retained
    }
    directions = Counter(row["family_local_change_direction"] for row in candidate_dx)
    non_dx_changes = sum(row["family"] != DIAGNOSIS for row in rows)
    absence_rows = [row for row in rows if row["letter_id"] == "EA0156"]
    broad_regressions = [
        row
        for row in candidate_dx
        if row["letter_id"] in BROAD_CONCEPT_REGRESSION_LETTERS
        and row["family_local_change_direction"] == "correct_to_wrong"
    ]
    checks = {
        "diagnosis_correct_to_wrong_at_most_3": directions["correct_to_wrong"] <= 3,
        "diagnosis_wrong_to_correct_at_least_88": directions["wrong_to_correct"] >= 88,
        "retain_at_least_75_of_81_comparator_diagnosis_rescues": len(retained) >= 75,
        "lost_rescues_confined_to_predeclared_rows": (
            lost_pairs <= allowed_lost_rescues
        ),
        "absence_preservation_active_on_EA0156": bool(absence_rows)
        and all(bool(row["candidate_correct"]) for row in absence_rows),
        "broad_concept_regression_family_not_reintroduced": not broad_regressions,
        "other_families_identical": non_dx_changes == 0,
        "all_comparator_candidate_changes_exact_evidence": all(
            row["evidence_status"] == "exact" for row in rows
        ),
        "no_new_schema_parse_call_or_fallback_failure": diagnostics_match,
    }
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "candidate_diagnosis_directions": dict(sorted(directions.items())),
        "comparator_rescue_retention": {
            "comparator_rescues": len(comparator_rescues),
            "retained": len(retained),
            "lost": len(comparator_rescues - retained),
        },
        "lost_rescue_identities": sorted([list(row) for row in lost_pairs]),
        "allowed_lost_rescue_identities": sorted(
            [list(row) for row in allowed_lost_rescues]
        ),
        "absence_EA0156_changed_rows": len(absence_rows),
        "broad_concept_regressions": [
            [row["model_label"], row["letter_id"]] for row in broad_regressions
        ],
        "non_diagnosis_changed_rows": non_dx_changes,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-dir", type=Path, default=CONFIG_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    return parser.parse_args()


if __name__ == "__main__":
    main()
