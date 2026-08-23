"""ExECTv2 mention scoring: match keys, entity PRF1, and clinical-recovery components."""

from clinical_extraction.core.scoring import multiset_prf1, prf1_from_counts
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.drug_lexicon import (
    canonicalize_medication_name,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.investigations import (
    InvestigationsComponentScores,
    _investigation_component_keys,
    score_investigations_components,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (  # noqa: F401
    DEFAULT_IGNORE_ATTRIBUTES,
    HEADLINE_DEDUPLICATED,
    HEADLINE_DISTINCT_ASSERTION,
    PHRASE_AND_FEATURES,
    PHRASE_ONLY,
    SF_BENCHMARK,
    SF_GUIDELINE_IGNORED,
    SF_SEMANTIC,
    ClinicalRecoveryPRF1,
    ConceptIdentityScores,
    EntityScore,
    MatchConfig,
    OverallScore,
    SourceNearDiagnostic,
    SourceNearEntityDiagnostic,
    SourceNearOverallDiagnostic,
    _concept_keys,
    _keys,
    _letters_by_id,
    benchmark_config_for,
    benchmark_ignore_for,
    clinical_headline_unit_keys,
    clinical_inventory_unit_keys,
    headline_duplicate_tags,
    inventory_unit_keys,
    match_key,
    score_concept_identity,
    score_entity,
    score_overall,
    semantic_config_for,
    semantic_ignore_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.normalize import (
    canonicalize_attribute_value,
    canonicalize_point_range_attributes,
    resolve_point_range,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.prescription import (
    PrescriptionBenchmarkProjectionScores,
    PrescriptionComponentScores,
    _prescription_component_key,
    _prescription_component_keys,
    score_prescription_benchmark_projection,
    score_prescription_components,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    FrequencyStateScores,
    _frequency_state_keys,
    frequency_state_direction_deconf,
    frequency_state_directional,
    frequency_state_faithful,
    frequency_state_magnitude,
    score_frequency_state,
)

# Public aliases for report-layer consumers (avoid underscore imports from reports).
concept_keys = _concept_keys
frequency_state_keys = _frequency_state_keys
investigation_component_keys = _investigation_component_keys
prescription_component_key = _prescription_component_key
prescription_component_keys = _prescription_component_keys

__all__ = [
    "DEFAULT_IGNORE_ATTRIBUTES",
    "HEADLINE_DEDUPLICATED",
    "HEADLINE_DISTINCT_ASSERTION",
    "PHRASE_AND_FEATURES",
    "PHRASE_ONLY",
    "SF_BENCHMARK",
    "SF_GUIDELINE_IGNORED",
    "SF_SEMANTIC",
    "ClinicalRecoveryPRF1",
    "ConceptIdentityScores",
    "EntityScore",
    "FrequencyStateScores",
    "InvestigationsComponentScores",
    "MatchConfig",
    "OverallScore",
    "PrescriptionBenchmarkProjectionScores",
    "PrescriptionComponentScores",
    "SourceNearDiagnostic",
    "SourceNearEntityDiagnostic",
    "SourceNearOverallDiagnostic",
    "benchmark_config_for",
    "benchmark_ignore_for",
    "canonicalize_attribute_value",
    "canonicalize_medication_name",
    "canonicalize_point_range_attributes",
    "clinical_headline_unit_keys",
    "clinical_inventory_unit_keys",
    "inventory_unit_keys",
    "concept_keys",
    "frequency_state_direction_deconf",
    "frequency_state_directional",
    "frequency_state_faithful",
    "frequency_state_keys",
    "frequency_state_magnitude",
    "headline_duplicate_tags",
    "investigation_component_keys",
    "match_key",
    "multiset_prf1",
    "normalize_phrase",
    "prescription_component_key",
    "prescription_component_keys",
    "prf1_from_counts",
    "resolve_point_range",
    "score_concept_identity",
    "score_entity",
    "score_frequency_state",
    "score_investigations_components",
    "score_overall",
    "score_prescription_benchmark_projection",
    "score_prescription_components",
    "semantic_config_for",
    "semantic_ignore_for",
    "source_near_diagnostic",
]
