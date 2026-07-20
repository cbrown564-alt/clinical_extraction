"""Build the exectv2 side of the shared reliability scorecard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from clinical_extraction.core.shared_reliability_schema import (
    SIX_MODELS,
    make_record,
)


@dataclass(frozen=True)
class ExectMeasurementInputs:
    artifact_index: Any
    calibration_paths: Any
    calibration_summary: Any
    common_exect: Any
    component_path: Any
    component_summary: Any
    confidence_path: Any
    confidence_summary: Any
    dev_f1: Any
    exact_evidence: Any
    exact_evidence_denominators: Any
    exect_dev_paths: Any
    exect_ops: Any
    exect_sources: Any
    family_f1: Any
    hosted_path: Any
    regression_path: Any
    regression_summary: Any
    review_paths: Any
    review_substrate: Any
    runtime_maps: Any
    sf_path: Any
    sf_summary: Any
    stage_f1: Any
    temperatures: Any
    test_f1: Any
    token_limits: Any


def build_exectv2_measurements(inputs: ExectMeasurementInputs) -> list[dict[str, Any]]:
    """Return retained exectv2 measurements without rescoring or model calls."""

    return [
        make_record(
            **inputs.common_exect,
            criterion_id="clinical_correctness_generalization",
            measurement_id="exectv2_six_model_dev140_clinical_headline_f1",
            model_scope=SIX_MODELS,
            split="dev140",
            row_scope="development_rows_permitted",
            denominator=140,
            denominator_status="defined_letters; F1 uses model-specific fact counts",
            unit="clinical_headline_f1",
            score_stage="final",
            scorer="ExECTv2 de-duplicated clinical_headline scorer",
            repair_policy="decision-0040 family boundary with selected joint bounded policy",
            value=inputs.dev_f1,
            evidence_state="development_answer",
            comparability="construct_only",
            source_artifacts=inputs.exect_dev_paths,
            claim_boundary=(
                "Development internal scorer; not the published ExECT benchmark or "
                "clinical validation."
            ),
            prompt_program="exectv2_hybrid_key_family_event_ledger_v0.9.24",
            row_inspection_rule="dev140 row inspection permitted",
            reproducibility_command="python scripts/run_exectv2_six_model_comparison.py --help",
            unique_rows=140,
            model_row_count=840,
        ),
        make_record(
            **inputs.common_exect,
            criterion_id="clinical_correctness_generalization",
            measurement_id="exectv2_six_model_test60_clinical_headline_f1",
            model_scope=SIX_MODELS,
            split="test60",
            row_scope="aggregate_only_rows_sealed",
            denominator=59,
            denominator_status="defined_loadable_letters",
            unit="clinical_headline_f1",
            score_stage="final",
            scorer="ExECTv2 de-duplicated clinical_headline scorer",
            repair_policy="decision-0040 family boundary with selected joint bounded policy",
            value=inputs.test_f1,
            evidence_state="aggregate_holdout_evidence",
            comparability="construct_only",
            source_artifacts=[inputs.hosted_path],
            claim_boundary=(
                "Aggregate-only internal holdout; not the published ExECT benchmark or "
                "clinical validation."
            ),
            prompt_program="exectv2_hybrid_key_family_event_ledger_v0.9.24",
            row_inspection_rule="aggregate-only test60; sealed row artifacts excluded",
            reproducibility_command="python scripts/check_retained_evidence_manifest.py",
            unique_rows=59,
            model_row_count=354,
        ),
        make_record(
            **inputs.common_exect,
            criterion_id="clinical_selection_unsupported_inference",
            measurement_id="exectv2_sf_unknown_only_active_rate_overread_rate",
            model_scope=SIX_MODELS,
            split="dev140",
            row_scope="development_rows_permitted",
            denominator=0,
            denominator_status="predeclared_unknown_only_gold_denominator_is_zero",
            unit="rate",
            score_stage="projected",
            scorer="change-aware frequency_state_faithful state set",
            repair_policy="deterministic SF state projection and unknown suppression",
            value=None,
            evidence_state="diagnostic",
            comparability="not_comparable",
            source_artifacts=[inputs.sf_path],
            claim_boundary=(
                "No unsupported-selection rate or Gan-to-ExECT transfer claim; "
                "empty-gold rows are diagnostic only."
            ),
            prompt_program="exectv2_hybrid_key_family_event_ledger_v0.9.24",
            row_inspection_rule="dev140 rows permitted; no test60 row accessed",
            reproducibility_command=(
                "python scripts/build_exectv2_six_model_sf_overinference.py --check"
            ),
            unique_rows=140,
            model_row_count=840,
            result_state="not_measurable_current_data",
            not_measured_reason=(
                "The unknown-only denominator is zero, and annotation omission prevents "
                "treating empty-gold letters as unknown."
            ),
            empty_gold_substitution_allowed=False,
            independence_claim=False,
        ),
        make_record(
            **inputs.common_exect,
            criterion_id="evidence_support_faithfulness",
            measurement_id="exectv2_final_exact_evidence_rate",
            model_scope=SIX_MODELS,
            split="dev140",
            row_scope="development_rows_permitted",
            denominator=inputs.exact_evidence_denominators,
            denominator_status="defined_final_scored_mentions_by_model",
            unit="exact_evidence_rate",
            score_stage="final",
            scorer="exact evidence substring check after assembly",
            repair_policy="decision-0040 family boundary with selected joint bounded policy",
            value=inputs.exact_evidence,
            evidence_state="development_answer",
            comparability="construct_only",
            source_artifacts=inputs.exect_dev_paths,
            claim_boundary=(
                "Textual source presence only; not semantic support or clinical faithfulness."
            ),
            prompt_program="exectv2_hybrid_key_family_event_ledger_v0.9.24",
            row_inspection_rule="dev140 row inspection permitted",
            reproducibility_command="python scripts/check_retained_evidence_manifest.py",
            unique_rows=140,
            model_row_count=840,
        ),
        make_record(
            artifact_index=inputs.artifact_index,
            task="exectv2",
            criterion_id="evidence_support_faithfulness",
            measurement_id="exectv2_semantic_support_review",
            model_scope=SIX_MODELS,
            split="dev140_sample",
            row_scope="development_rows_permitted",
            denominator=48,
            denominator_status="sample_prepared_review_not_started",
            unit="semantic_support_review_items",
            score_stage="final",
            scorer="independent clinical review protocol",
            repair_policy="review the retained final conclusion without changing it",
            value=None,
            evidence_state="not_measured",
            comparability="construct_only",
            source_artifacts=inputs.review_paths,
            claim_boundary=(
                "Unreviewed sample only; not semantic-support evidence or independent "
                "clinical validation."
            ),
            route_runtime=inputs.runtime_maps,
            temperature=inputs.temperatures,
            token_limit=inputs.token_limits,
            cache_replay_mode="no-call deterministic sample from retained dev140 outputs",
            prompt_program="exectv2_hybrid_key_family_event_ledger_v0.9.24",
            row_inspection_rule="dev140 only; two evidence-valid findings per model-family stratum",
            locked_row_controls="test60 excluded by source and validator",
            independent_clinical_review="pending",
            reproducibility_command=(
                "python scripts/build_exectv2_semantic_support_review_substrate.py --check"
            ),
            pooling_unit="review_item",
            unique_rows=None,
            model_row_count=48,
            result_state="not_measured",
            not_measured_reason=(
                "The substrate is prepared but independent clinical review has not started."
            ),
        ),
        make_record(
            artifact_index=inputs.artifact_index,
            task="exectv2",
            criterion_id="uncertainty_selective_action",
            measurement_id="exectv2_internal_scoring_rule_calibration",
            model_scope=["internal grouped logistic scoring rule"],
            split="full200_aggregate",
            row_scope="aggregate_only_rows_sealed",
            denominator=200,
            denominator_status="defined_letters; aggregate-only full200 result",
            unit="calibration",
            score_stage="final",
            scorer="ExECT grouped logistic correctness scoring rule",
            repair_policy="not_applicable_internal_scoring_rule",
            value={
                "brier": inputs.calibration_summary["brier"],
                "base_rate_brier": inputs.calibration_summary["base_rate_brier"],
                "ece": inputs.calibration_summary["ece"],
            },
            evidence_state="diagnostic",
            comparability="construct_only",
            source_artifacts=inputs.calibration_paths,
            claim_boundary=(
                "Internal scoring-rule calibration; not model-reported confidence or "
                "deployment calibration."
            ),
            route_runtime="saved-output scoring rule",
            temperature="not_applicable",
            token_limit="not_applicable",
            cache_replay_mode="no-call aggregate replay",
            prompt_program="internal grouped logistic scoring rule",
            row_inspection_rule="full200 aggregate only; test60 rows not emitted",
            locked_row_controls="test60 contribution retained as aggregate only",
            independent_clinical_review="not_completed",
            reproducibility_command="python scripts/check_retained_evidence_manifest.py",
            pooling_unit="letter",
            unique_rows=200,
            model_row_count=200,
        ),
        make_record(
            artifact_index=inputs.artifact_index,
            task="exectv2",
            criterion_id="uncertainty_selective_action",
            measurement_id="exectv2_historical_model_reported_confidence_failure_auroc",
            model_scope=[
                "openai/gpt-4.1-mini",
                "deepseek/deepseek-chat",
                "ollama_chat/qwen3.6:35b",
            ],
            split="test60",
            row_scope="aggregate_only_rows_sealed",
            denominator=240,
            denominator_status="60 letters x four family cells per historical model",
            unit="failure_auroc",
            score_stage="final",
            scorer="exact family-cell clinical_headline correctness",
            repair_policy="historical decision-0040 audit replay",
            value={
                "openai/gpt-4.1-mini": inputs.confidence_summary["gpt41mini_failure_auroc_test60"],
                "deepseek/deepseek-chat": inputs.confidence_summary[
                    "historical_deepseek_failure_auroc_test60"
                ],
                "ollama_chat/qwen3.6:35b": inputs.confidence_summary["qwen_failure_auroc_test60"],
            },
            evidence_state="aggregate_holdout_evidence",
            comparability="construct_only",
            source_artifacts=[inputs.confidence_path],
            claim_boundary=(
                "Historical three-model negative result; not a six-model, "
                "DeepSeek V4 Flash, or deployment conclusion."
            ),
            route_runtime="historical saved outputs; incomplete DeepSeek runtime metadata",
            temperature={
                "openai/gpt-4.1-mini": 0,
                "deepseek/deepseek-chat": 0,
                "ollama_chat/qwen3.6:35b": 0,
            },
            token_limit="recorded in source configuration",
            cache_replay_mode="no-call split replay; test60 aggregate only",
            prompt_program="historical fixed family outputs",
            row_inspection_rule="aggregate-only test60; rows not emitted",
            locked_row_controls="test60 rows sealed and excluded from output",
            independent_clinical_review="not_completed",
            reproducibility_command="python scripts/check_exectv2_model_reported_confidence.py",
            pooling_unit="family_cell",
            unique_rows=60,
            model_row_count=720,
            review_policy_adopted=False,
        ),
        make_record(
            **inputs.common_exect,
            criterion_id="robustness_stability",
            measurement_id="exectv2_six_model_dev_to_test_f1_change",
            model_scope=SIX_MODELS,
            split="dev140_to_test60",
            row_scope="aggregate_only_rows_sealed",
            denominator={"dev140": 140, "test60": 59},
            denominator_status="defined_letters; F1 uses fact counts",
            unit="clinical_headline_f1_change",
            score_stage="final",
            scorer="ExECTv2 de-duplicated clinical_headline scorer",
            repair_policy="decision-0040 family boundary with selected joint bounded policy",
            value={
                model: round(inputs.test_f1[model] - inputs.dev_f1[model], 4)
                for model in SIX_MODELS
            },
            evidence_state="aggregate_holdout_evidence",
            comparability="construct_only",
            source_artifacts=[*inputs.exect_dev_paths, inputs.hosted_path],
            claim_boundary=(
                "Development-to-holdout aggregate change only; not perturbation "
                "robustness or self-consistency."
            ),
            prompt_program="exectv2_hybrid_key_family_event_ledger_v0.9.24",
            row_inspection_rule="dev140 rows permitted; test60 aggregate only",
            reproducibility_command="python scripts/check_retained_evidence_manifest.py",
            unique_rows=199,
            model_row_count=1194,
        ),
        make_record(
            artifact_index=inputs.artifact_index,
            task="exectv2",
            criterion_id="component_attribution_correction_safety",
            measurement_id="exectv2_dev140_normalization_component_delta",
            model_scope=["saved-output ExECT development subject"],
            split="dev140",
            row_scope="development_rows_permitted",
            denominator=140,
            denominator_status="defined_letters",
            unit="clinical_headline_f1_delta",
            score_stage="normalized",
            scorer="ExECT clinical_headline scorer",
            repair_policy="normalization/shared dictionary ablation",
            value=inputs.component_summary["normalization_delta_exectv2"],
            evidence_state="development_answer",
            comparability="construct_only",
            source_artifacts=[inputs.component_path],
            claim_boundary=(
                "Saved-output development ablation; the numerical delta is not pooled with Gan."
            ),
            route_runtime="no-call saved-output replay",
            temperature="not_applicable_no_call_replay",
            token_limit="not_applicable_no_call_replay",
            cache_replay_mode="saved-output no-call replay",
            prompt_program="retained component ablation",
            row_inspection_rule="dev140 development rows permitted",
            locked_row_controls="no locked rows used",
            independent_clinical_review="not_completed",
            reproducibility_command="python scripts/cross_task_shared_component_ablation.py",
            pooling_unit="letter",
            unique_rows=140,
            model_row_count=140,
        ),
        make_record(
            **inputs.common_exect,
            criterion_id="component_attribution_correction_safety",
            measurement_id="exectv2_six_model_score_stage_f1",
            model_scope=SIX_MODELS,
            split="dev140",
            row_scope="development_rows_permitted",
            denominator=140,
            denominator_status="defined_letters; stage F1 uses model-specific fact counts",
            unit="clinical_headline_f1_by_stage",
            score_stage="raw_to_final",
            scorer="ExECT clinical_headline and named companion stage scorers",
            repair_policy="decision-0040 family boundary with selected joint bounded policy",
            value=inputs.stage_f1,
            evidence_state="development_answer",
            comparability="construct_only",
            source_artifacts=inputs.exect_dev_paths,
            claim_boundary=(
                "Development stage attribution; projected companion and final clinical "
                "scores remain distinct."
            ),
            prompt_program="exectv2_hybrid_key_family_event_ledger_v0.9.24",
            row_inspection_rule="dev140 development rows permitted",
            reproducibility_command="python scripts/check_retained_evidence_manifest.py",
            unique_rows=140,
            model_row_count=840,
        ),
        make_record(
            artifact_index=inputs.artifact_index,
            task="exectv2",
            criterion_id="component_attribution_correction_safety",
            measurement_id="exectv2_historical_deterministic_correction_transitions",
            model_scope=[
                "openai/gpt-4.1-mini",
                "deepseek/deepseek-chat",
                "ollama_chat/qwen3.6:35b",
            ],
            split="dev140",
            row_scope="development_rows_permitted",
            denominator=inputs.regression_summary["changed_model_family_rows"],
            denominator_status="defined_changed_model_family_rows",
            unit="transition_counts",
            score_stage="final",
            scorer="family-local clinical_headline key equality",
            repair_policy="decision-0040 historical model-led replay",
            value={
                "wrong_to_correct": inputs.regression_summary["family_local_wrong_to_correct"],
                "correct_to_wrong": inputs.regression_summary["family_local_correct_to_wrong"],
                "changed_still_wrong": inputs.regression_summary[
                    "family_local_changed_still_wrong"
                ],
            },
            evidence_state="development_answer",
            comparability="construct_only",
            source_artifacts=[inputs.regression_path],
            claim_boundary=(
                "Three historical dev140 model conditions; not final six-model or holdout evidence."
            ),
            route_runtime="historical saved-output replay",
            temperature="recorded by historical source",
            token_limit="recorded by historical source",
            cache_replay_mode="no-call dev140 replay",
            prompt_program="historical family programs",
            row_inspection_rule="dev140 rows permitted; exact evidence required on changed rows",
            locked_row_controls="no test60 rows used",
            independent_clinical_review="not_completed",
            reproducibility_command=(
                "python scripts/analyze_exectv2_model_led_dev140_regressions.py --check"
            ),
            pooling_unit="model_family_letter",
            unique_rows=140,
            model_row_count=420,
        ),
        make_record(
            **inputs.common_exect,
            criterion_id="component_attribution_correction_safety",
            measurement_id="exectv2_six_model_sf_correction_transitions",
            model_scope=SIX_MODELS,
            split="dev140",
            row_scope="development_rows_permitted",
            denominator=840,
            denominator_status="six_model_letter_panels",
            unit="transition_counts",
            score_stage="projected_to_final",
            scorer="change-aware frequency_state_faithful state set",
            repair_policy="deterministic SF state projection and unknown suppression",
            value={
                "wrong_to_correct": inputs.sf_summary["wrong_to_correct_transitions"],
                "correct_to_wrong": inputs.sf_summary["correct_to_wrong_transitions"],
                "final_exact_evidence_rate": inputs.sf_summary[
                    "final_exact_evidence_rate_all_models"
                ],
            },
            evidence_state="development_answer",
            comparability="construct_only",
            source_artifacts=[inputs.sf_path],
            claim_boundary=(
                "Descriptive six-panel counts; the same 140 letters repeat across models "
                "and are not independent rows."
            ),
            prompt_program="exectv2_hybrid_key_family_event_ledger_v0.9.24",
            row_inspection_rule="dev140 rows permitted; no test60 row accessed",
            reproducibility_command=(
                "python scripts/build_exectv2_six_model_sf_overinference.py --check"
            ),
            unique_rows=140,
            model_row_count=840,
            independence_claim=False,
        ),
        make_record(
            **inputs.common_exect,
            criterion_id="coverage_clinical_slice_behavior",
            measurement_id="exectv2_six_model_dev140_family_f1",
            model_scope=SIX_MODELS,
            split="dev140",
            row_scope="development_rows_permitted",
            denominator=140,
            denominator_status="defined_letters; family F1 uses model-specific fact counts",
            unit="clinical_headline_f1_by_family",
            score_stage="final",
            scorer="ExECT clinical_headline family scorers",
            repair_policy="decision-0040 family boundary with selected joint bounded policy",
            value=inputs.family_f1,
            evidence_state="development_answer",
            comparability="construct_only",
            source_artifacts=inputs.exect_dev_paths,
            claim_boundary=(
                "Four clinical families on dev140; not demographic fairness or clinical validation."
            ),
            prompt_program="exectv2_hybrid_key_family_event_ledger_v0.9.24",
            row_inspection_rule="dev140 development rows permitted",
            reproducibility_command="python scripts/check_retained_evidence_manifest.py",
            unique_rows=140,
            model_row_count=840,
        ),
        make_record(
            artifact_index=inputs.artifact_index,
            task="exectv2",
            criterion_id="coverage_clinical_slice_behavior",
            measurement_id="exectv2_demographic_fairness",
            model_scope=["not_applicable_current_data"],
            split="not_measured",
            row_scope="synthetic_fixture",
            denominator=None,
            denominator_status="not_measured",
            unit="fairness_measure",
            score_stage="final",
            scorer="not_defined",
            repair_policy="not_applicable",
            value=None,
            evidence_state="not_measured",
            comparability="not_comparable",
            source_artifacts=[inputs.sf_path],
            claim_boundary="No demographic fairness claim.",
            route_runtime="not_applicable",
            temperature="not_applicable",
            token_limit="not_applicable",
            cache_replay_mode="not_applicable",
            prompt_program="not_applicable",
            row_inspection_rule="no demographic substrate",
            locked_row_controls="test60 remains sealed",
            independent_clinical_review="not_started",
            reproducibility_command="python scripts/check_retained_evidence_manifest.py",
            pooling_unit="not_applicable",
            unique_rows=None,
            model_row_count=None,
            result_state="not_measured",
            not_measured_reason=(
                "Suitable demographic attributes, sample sizes, and a clinically "
                "meaningful fairness question are absent."
            ),
        ),
        make_record(
            **inputs.common_exect,
            criterion_id="operational_reliability",
            measurement_id="exectv2_six_model_test60_operational_events",
            model_scope=SIX_MODELS,
            split="test60",
            row_scope="aggregate_only_rows_sealed",
            denominator=59,
            denominator_status="defined_loadable_letters_per_model",
            unit="event_counts",
            score_stage="final",
            scorer="aggregate run event accounting",
            repair_policy="decision-0040 family boundary with selected joint bounded policy",
            value=inputs.exect_ops,
            evidence_state="aggregate_holdout_evidence",
            comparability="construct_only",
            source_artifacts=[inputs.hosted_path],
            claim_boundary=(
                "Observed aggregate events with hosted/local routes separate; no matched "
                "latency, token, cost, or efficiency ranking."
            ),
            prompt_program="exectv2_hybrid_key_family_event_ledger_v0.9.24",
            row_inspection_rule="aggregate-only test60; sealed row artifacts excluded",
            reproducibility_command="python scripts/check_retained_evidence_manifest.py",
            unique_rows=59,
            model_row_count=354,
        ),
    ]
