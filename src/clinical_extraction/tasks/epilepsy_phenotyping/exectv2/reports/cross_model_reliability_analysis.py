"""No-call reliability analysis for the ExECTv2 cross-model scorecard.

This module upgrades the 2026-06-22 reliability scorecard with computed dev140
trust evidence. It deliberately keeps two surfaces separate:

* the rich-schema holistic finding assemblies used by the original scorecard;
* the newer LLM-only de-duplicated clinical-fact Phase 6 runs.

No model calls are made here, and no full-200 or holdout rows are loaded.
"""
# ruff: noqa: F401 — re-exports ``FAMILIES`` / ``_CALIBRATION_FEATURES`` accessed via the
# ``reliability`` alias in calibration/robustness/review-routing validation modules.

from __future__ import annotations

from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.calibration import (
    brier_score,
    calibration_proxy,
    calibration_summary_for_family,
    expected_calibration_error,
    fit_logistic_scoring_rule,
    max_adjacent_bin_reversal,
    predict_logistic_probability,
    reliability_bins,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.cells import (
    iter_reliability_cells,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.consistency import (
    active_llm_only_readout,
    deterministic_replay_stability,
    same_prompt_consistency,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.constants import (
    _CALIBRATION_FEATURES,
    ACTIVE_LLM_ONLY_RUNS,
    FAMILIES,
    RICH_SCHEMA_RUNS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.io import (
    REPO_ROOT,
    load_json,
    load_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.review_routing import (
    review_routing,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.scoring import (
    aggregate_scores,
    review_triggers,
    risk_features,
    risk_score,
    row_family_score,
    row_has_call_error,
    row_parse_error_count,
    score_dict,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.summary import (
    coverage_update,
    cross_model_agreement,
    family_error_table,
    family_parity,
    latest_run_check,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.types import (
    ReliabilityRun,
)

# Back-compat for tests and validation reports that import private helpers.
_deterministic_replay_stability = deterministic_replay_stability
_same_prompt_consistency = same_prompt_consistency
_load_jsonl = load_jsonl
_iter_reliability_cells = iter_reliability_cells
_calibration_proxy = calibration_proxy
_fit_logistic_scoring_rule = fit_logistic_scoring_rule
_reliability_bins = reliability_bins
_expected_calibration_error = expected_calibration_error
_brier_score = brier_score
_max_adjacent_bin_reversal = max_adjacent_bin_reversal
_calibration_summary_for_family = calibration_summary_for_family
_predict_logistic_probability = predict_logistic_probability
_row_family_score = row_family_score
_risk_features = risk_features
_risk_score = risk_score
_review_triggers = review_triggers
_score_dict = score_dict
_row_has_call_error = row_has_call_error
_row_parse_error_count = row_parse_error_count
_aggregate_scores = aggregate_scores

__all__ = (
    "ACTIVE_LLM_ONLY_RUNS",
    "ReliabilityRun",
    "RICH_SCHEMA_RUNS",
    "build_cross_model_reliability_analysis",
)


def build_cross_model_reliability_analysis(
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Build the computed reliability package for the scorecard payload."""

    from . import robustness_panels

    rich_rows = {run.candidate: load_jsonl(repo_root / run.rows_path) for run in RICH_SCHEMA_RUNS}
    rich_summaries = {
        run.candidate: load_json(repo_root / run.summary_path)
        for run in RICH_SCHEMA_RUNS
        if run.summary_path is not None
    }
    active_rows = {
        run.candidate: load_jsonl(repo_root / run.rows_path) for run in ACTIVE_LLM_ONLY_RUNS
    }

    cells = list(iter_reliability_cells(rich_rows))
    return {
        "analysis_kind": "exectv2_cross_model_reliability_no_call_dev140",
        "claim_boundary": (
            "Computed from saved dev140 artifacts only; no full-200 or holdout "
            "row-level inspection."
        ),
        "latest_run_check": latest_run_check(),
        "family_error_table": family_error_table(rich_summaries),
        "family_parity": family_parity(rich_summaries),
        "cross_model_agreement": cross_model_agreement(rich_rows),
        "calibration_proxy": calibration_proxy(cells),
        "review_routing": review_routing(cells),
        "robustness_panel_preflight": robustness_panels.build_robustness_panel_payload(
            include_case_text=False
        ),
        "active_llm_only_readout": [
            active_llm_only_readout(run, active_rows[run.candidate]) for run in ACTIVE_LLM_ONLY_RUNS
        ],
        "same_prompt_consistency": same_prompt_consistency(active_rows),
        "deterministic_replay_stability": deterministic_replay_stability(rich_rows),
        "holdout_guardrail": {
            "full_200_or_holdout_rows_loaded": False,
            "blocked_surfaces": ["full-200", "holdout", "test"],
            "policy": (
                "Latest active rows are dev140 only. Any full-200 or holdout "
                "analysis still requires a frozen protocol and explicit authorization."
            ),
        },
        "coverage_update": coverage_update(),
    }
