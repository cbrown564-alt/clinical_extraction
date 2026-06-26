"""LLM-first essential clinical evaluation (plan satellite 11).

Analysis-only. Replays existing ExECTv2 prediction artifacts under the
ownership-aware layer ladder from
``docs/plans/exectv2/11_llm_first_essential_clinical_evaluation_plan.md``.

Implementation lives in ``reports/llm_first/``; this module re-exports the
public API for backward compatibility.
"""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first import (
    ESSENTIAL_CLINICAL_ENTITIES,
    OWNERSHIP_HYBRID,
    OWNERSHIP_LLM_FIRST,
    OWNERSHIP_RULES_ONLY,
    aggregate_score_dicts,
    align_predictions_to_gold,
    architecture_report,
    certainty_dropped_config_for,
    certainty_projection_audit,
    cui_concept_buckets,
    cui_projection_audit,
    cui_projection_coverage,
    error_taxonomy_summary,
    evidence_validation_summary,
    letters_from_artifact,
    predicted_by_id_from_artifact,
    project_guideline_certainty_negation,
    row_level_error_ledger,
    score_for_primary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.projection import (
    strip_and_project as _strip_and_project,
    strip_gold_cui as _strip_gold_cui,
    strip_prediction_cui as _strip_prediction_cui,
)

# Backward-compatible private aliases for internal callers.
_aggregate_score_dicts = aggregate_score_dicts
_score_for_primary = score_for_primary
_strip_and_project = _strip_and_project
_strip_gold_cui = _strip_gold_cui
_strip_prediction_cui = _strip_prediction_cui

__all__ = (
    "ESSENTIAL_CLINICAL_ENTITIES",
    "OWNERSHIP_HYBRID",
    "OWNERSHIP_LLM_FIRST",
    "OWNERSHIP_RULES_ONLY",
    "_aggregate_score_dicts",
    "_score_for_primary",
    "_strip_and_project",
    "_strip_gold_cui",
    "_strip_prediction_cui",
    "aggregate_score_dicts",
    "align_predictions_to_gold",
    "architecture_report",
    "certainty_dropped_config_for",
    "certainty_projection_audit",
    "cui_concept_buckets",
    "cui_projection_audit",
    "cui_projection_coverage",
    "error_taxonomy_summary",
    "evidence_validation_summary",
    "letters_from_artifact",
    "predicted_by_id_from_artifact",
    "project_guideline_certainty_negation",
    "row_level_error_ledger",
    "score_for_primary",
)
