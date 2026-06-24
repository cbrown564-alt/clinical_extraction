from __future__ import annotations

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

    assert analysis["calibration_proxy"]["bin_count"] >= 3
    assert 0.0 <= analysis["calibration_proxy"]["expected_calibration_error"] <= 1.0
    assert analysis["review_routing"]["reviewed_cells"] > 0
    assert analysis["review_routing"]["caught_error_cells"] > 0
    operating_points = {
        row["id"]: row
        for row in analysis["review_routing"]["operating_points"]
    }
    assert operating_points["high_recall_predeclared"]["review_burden"] == 0.9408
    assert operating_points["high_recall_predeclared"]["catch_rate"] == 0.8897
    assert operating_points["balanced_dev_candidate"]["review_burden"] == 0.7567
    assert operating_points["balanced_dev_candidate"]["catch_rate"] == 0.8028
    assert (
        operating_points["balanced_dev_candidate"][
            "review_burden_delta_vs_high_recall"
        ]
        < -0.18
    )
    assert analysis["cross_model_agreement"]["overall"]["mean_pairwise_jaccard"] > 0.5


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
