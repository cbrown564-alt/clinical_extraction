from __future__ import annotations

from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    cross_model_reliability_analysis as reliability_analysis,
)

QWEN_PHASE6_ROWS = (
    "phase6_seq_decision_table_sf_inv_dev140_qwen36_side11435_20260624.jsonl"
)
QWEN_RICH_SCHEMA_CANDIDATE = (
    "exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140"
)


def test_cross_model_reliability_analysis_uses_latest_runs_by_surface() -> None:
    analysis = reliability_analysis.build_cross_model_reliability_analysis()

    by_surface = {
        surface["surface_id"]: surface
        for surface in analysis["latest_run_check"]["surfaces"]
    }

    rich_schema = by_surface["rich_schema_reliability"]
    assert rich_schema["latest_deepseek"]["candidate"] == (
        "exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140"
    )
    assert rich_schema["latest_qwen"]["candidate"] == (
        "exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140"
    )
    assert rich_schema["replacement_policy"] == "same-surface comparators retained"

    llm_only = by_surface["active_llm_only"]
    assert llm_only["latest_deepseek"]["rows_path"].endswith(
        "phase6_seq_decision_table_sf_inv_dev140_deepseek_chat_20260624.jsonl"
    )
    assert llm_only["latest_qwen"]["rows_path"].endswith(
        "phase6_seq_decision_table_sf_inv_dev140_qwen36_side11435_20260624.jsonl"
    )
    assert llm_only["replacement_policy"] == "reported separately; different claim surface"


def test_cross_model_reliability_analysis_populates_scorecard_upgrade_tables() -> None:
    analysis = reliability_analysis.build_cross_model_reliability_analysis()

    assert len(analysis["family_error_table"]) == 16
    qwen_dx = next(
        row
        for row in analysis["family_error_table"]
        if (
            row["candidate"] == QWEN_RICH_SCHEMA_CANDIDATE
            and row["family"] == "Diagnosis"
        )
    )
    assert qwen_dx["miss_rate"] > 0.1
    assert qwen_dx["over_emission_rate"] > 0.1

    calibration = analysis["calibration_proxy"]
    assert calibration["model_type"] == (
        "grouped_cross_validated_logistic_scoring_rule"
    )
    assert calibration["leakage_audit"]["group_key"] == "letter_id"
    assert calibration["leakage_audit"]["fold_count"] == 5
    assert calibration["leakage_audit"]["shared_letter_between_train_and_test"] is False
    assert calibration["bin_count"] >= 4
    assert 0.0 <= calibration["expected_calibration_error"] <= 1.0
    assert 0.0 <= calibration["brier_score"] <= 1.0
    assert calibration["brier_score"] < calibration["constant_base_rate_brier_score"]
    assert set(calibration["feature_set"]) >= {
        "evidence_invalid",
        "low_confidence",
        "source_final_delta",
        "deterministic_action_count",
    }
    assert {
        row["family"]
        for row in calibration["per_family"]
    } == {"Diagnosis", "SeizureFrequency", "Prescription", "Investigations"}
    assert analysis["review_routing"]["reviewed_cells"] > 0
    assert analysis["review_routing"]["caught_error_cells"] > 0
    operating_points = {
        row["id"]: row
        for row in analysis["review_routing"]["operating_points"]
    }
    assert operating_points["high_recall_predeclared"]["review_burden"] == 0.9408
    assert operating_points["high_recall_predeclared"]["catch_rate"] == 0.8897
    assert operating_points["balanced_dev_candidate"]["review_burden"] == 0.7521
    assert operating_points["balanced_dev_candidate"]["catch_rate"] == 0.8028
    assert (
        operating_points["balanced_dev_candidate"][
            "review_burden_delta_vs_high_recall"
        ]
        < -0.18
    )
    assert analysis["cross_model_agreement"]["overall"]["mean_pairwise_jaccard"] > 0.5
    robustness = analysis["robustness_panel_preflight"]
    assert robustness["panel_coverage"]["minimum_coverage_met"] is True
    assert robustness["promotion_gate"]["scorecard_ready_for_frozen_candidate_run"] is True
    assert robustness["holdout_guardrail"]["full_200_or_holdout_rows_loaded"] is False


def test_cross_model_reliability_analysis_scores_active_llm_only_latest_rows() -> None:
    analysis = reliability_analysis.build_cross_model_reliability_analysis()

    active = {
        row["model_label"]: row
        for row in analysis["active_llm_only_readout"]
    }

    assert active["DeepSeek chat"]["clinical_headline_f1"] > active["Qwen 3.6 35B"][
        "clinical_headline_f1"
    ]
    assert active["DeepSeek chat"]["rows"] == 140
    assert active["Qwen 3.6 35B"]["rows"] == 140
    assert active["Qwen 3.6 35B"]["rows_path"].endswith(
        QWEN_PHASE6_ROWS
    )


def test_same_prompt_consistency_panel_keeps_live_resampling_separate_from_replay(
    monkeypatch,
) -> None:
    run = reliability_analysis.ReliabilityRun(
        candidate="same_prompt_seed_1",
        model_label="GPT-4.1-mini",
        rows_path=Path("experiments/same_prompt_seed_1.jsonl"),
        surface_id="active_llm_only",
        role="fixture",
        claim_boundary="dev fixture",
    )
    rows = [
        {
            "letter_id": "EA1",
            "mode": "live",
            "prompt_version": "prompt_v1",
            "prompt_profile": "decision_table",
            "call_error": None,
            "parse_errors": [],
            "n_mentions_raw": 2,
            "n_evidence_invalid": 1,
            "predicted_mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "focal epilepsy",
                    "attributes": {"Negation": "Affirmed"},
                }
            ],
        }
    ]
    monkeypatch.setattr(reliability_analysis, "ACTIVE_LLM_ONLY_RUNS", (run,))

    consistency = reliability_analysis._same_prompt_consistency({run.candidate: rows})
    assert consistency["evidence_type"] == "same_prompt_cross_seed_resampling"
    assert consistency["deterministic_replay_included"] is False
    panel = consistency["panels"][0]
    assert panel["status"] == "blocked_needs_at_least_two_saved_live_repeats"
    assert panel["call_failures"] == 0
    assert panel["schema_validity_rate"] == 1.0
    assert panel["evidence_validity_rate"] == 0.5
    assert panel["family_cell_agreement"]["exact_family_cell_agreement_rate"] is None
    assert {
        "Diagnosis",
        "SeizureFrequency",
        "Prescription",
        "Investigations",
    } == {
        row["family"]
        for row in panel["per_family_disagreement_rates"]
    }

    replay = reliability_analysis._deterministic_replay_stability(
        {"saved_replay": [{"letter_id": "EA1", "call_error": None, "parse_errors": []}]}
    )
    assert replay["evidence_type"] == "deterministic_replay_stability"
    assert replay["same_prompt_consistency_included"] is False
    assert replay["rows"] > 0


def test_same_prompt_consistency_panel_computes_saved_repeat_agreement(
    monkeypatch,
) -> None:
    runs = (
        reliability_analysis.ReliabilityRun(
            candidate="same_prompt_seed_1",
            model_label="GPT-4.1-mini",
            rows_path=Path("experiments/same_prompt_seed_1.jsonl"),
            surface_id="active_llm_only",
        ),
        reliability_analysis.ReliabilityRun(
            candidate="same_prompt_seed_2",
            model_label="GPT-4.1-mini",
            rows_path=Path("experiments/same_prompt_seed_2.jsonl"),
            surface_id="active_llm_only",
        ),
    )
    base_row = {
        "letter_id": "EA1",
        "mode": "live",
        "prompt_version": "prompt_v1",
        "prompt_profile": "decision_table",
        "call_error": None,
        "parse_errors": [],
        "n_mentions_raw": 1,
        "n_evidence_invalid": 0,
    }
    active_rows = {
        "same_prompt_seed_1": [
            {
                **base_row,
                "predicted_mentions": [
                    {
                        "entity": "Diagnosis",
                        "text": "focal epilepsy",
                        "attributes": {"Negation": "Affirmed"},
                    }
                ],
            }
        ],
        "same_prompt_seed_2": [
            {
                **base_row,
                "predicted_mentions": [
                    {
                        "entity": "Diagnosis",
                        "text": "generalised epilepsy",
                        "attributes": {"Negation": "Affirmed"},
                    }
                ],
            }
        ],
    }
    monkeypatch.setattr(reliability_analysis, "ACTIVE_LLM_ONLY_RUNS", runs)

    panel = reliability_analysis._same_prompt_consistency(active_rows)["panels"][0]

    assert panel["status"] == "computed_saved_live_repeats"
    assert panel["family_cell_agreement"]["pairwise_comparisons"] == 1
    assert panel["family_cell_agreement"]["cell_count"] == 4
    assert panel["family_cell_agreement"]["exact_family_cell_agreement_rate"] == 0.75
    diagnosis = next(
        row for row in panel["per_family_disagreement_rates"]
        if row["family"] == "Diagnosis"
    )
    assert diagnosis["disagreement_rate"] == 1.0
