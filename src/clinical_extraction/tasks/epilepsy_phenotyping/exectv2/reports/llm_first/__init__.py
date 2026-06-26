"""Focused modules for the LLM-first essential clinical evaluation."""

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.artifacts import (
    align_predictions_to_gold,
    letters_from_artifact,
    predicted_by_id_from_artifact,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.audits.certainty import (
    certainty_dropped_config_for,
    certainty_projection_audit,
    project_guideline_certainty_negation,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.audits.cui import (
    cui_concept_buckets,
    cui_projection_audit,
    cui_projection_coverage,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.constants import (
    ESSENTIAL_CLINICAL_ENTITIES,
    OWNERSHIP_HYBRID,
    OWNERSHIP_LLM_FIRST,
    OWNERSHIP_RULES_ONLY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.ledger import (
    row_level_error_ledger,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.recovery import (
    aggregate_score_dicts,
    error_taxonomy_summary,
    evidence_validation_summary,
    score_for_primary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.render import (
    architecture_report,
)

__all__ = (
    "ESSENTIAL_CLINICAL_ENTITIES",
    "OWNERSHIP_HYBRID",
    "OWNERSHIP_LLM_FIRST",
    "OWNERSHIP_RULES_ONLY",
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
