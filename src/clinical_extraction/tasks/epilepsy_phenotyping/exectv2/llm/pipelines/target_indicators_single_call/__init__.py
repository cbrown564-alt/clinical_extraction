"""ExECTv2 single-call target-indicators pipeline package.

Pure relocation of ``llm_target_indicators_single_call`` into cohesive
submodules. The legacy module path remains a thin facade re-exporting this API.

Import-order note: ``projection`` is imported before ``records``/``parsing``
because ``projection`` imports ``sf_surface_registry.adapters.projection``
*before* ``deterministic.normalization`` (matching the original module's import
order). Importing the normalization-triggering submodules first would reverse
that order and re-expose the deterministic.normalization <-> scoring circular
import.
"""

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.constants import (
    _CLUSTER_OF_SEIZURES,
    _DIAGNOSIS_ALLOWED_CORE,
    _DIAGNOSIS_PROHIBITED_CORES,
    _GENERALIZED_EPILEPSY_GTCS_ALONE,
    _PLANNED_INVESTIGATION_CONTEXT,
    _PLANNED_PRESCRIPTION_CONTEXT,
    _SEIZURE_FREQUENCY_ANCHOR,
    _SEIZURE_FREQUENCY_PROHIBITED_ANCHOR,
    _SF_STATE_ATTRIBUTES,
    _SF_TEXT_ALIASES,
    _SPECIFIC_SEIZURE_EVIDENCE,
    _UNKNOWN_LIKE_NUMBER,
    COMPONENT_OWNER,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
    Mode,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.parsing import (
    _extract_json_object_field,
    _extract_json_string_field,
    _infer_text_from_evidence,
    _iter_top_level_json_objects,
    _loads_malformed_rationale_mention_object,
    _loads_python_literal_payload,
    _loads_salvageable_mention_object,
    _parse_target_extraction_json,
    _salvage_mentions_from_malformed_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.projection import (
    audit_only_projection_replay_switches,
    to_predicted_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.projection_helpers import (
    _convert_day_period_to_week,
    _dedupe_key,
    _deduplicate_scored_mentions,
    _evidence_has_positive_rate,
    _expand_asymmetric_prescription,
    _expand_diagnosis_projection,
    _expand_seizure_frequency_state,
    _expand_target_mention,
    _investigation_modality,
    _investigation_text_modality,
    _is_allowed_diagnosis_core,
    _is_allowed_sf_anchor,
    _is_frequency_phrase_diagnosis_context,
    _is_investigation_only_diagnosis_context,
    _is_non_target_investigation_text,
    _is_planned_investigation,
    _is_planned_prescription,
    _is_unsupported_eeg_confirmation,
    _is_unsupported_inferred_diagnosis,
    _is_unsupported_investigation_evidence,
    _is_zero_since_only_diagnosis_context,
    _normalize_target_attributes,
    _normalize_target_text,
    _sf_state_drop_reason,
    _sf_type_to_diagnosis_projection_warning,
    _split_range_attribute,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.prompt_builders import (
    _target_attribute_vocabulary,
    _worked_examples,
    build_prompt_input,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.records import (
    ExtractionRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.runner import (
    _count_evidence_invalid_warnings,
    _emit_checkpoint,
    _letters_from_rows,
    run_split,
    summarize_rows,
    write_jsonl,
    write_report,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.signatures import (
    DspyTargetIndicatorsExtractor,
    ExECTv2TargetIndicatorsSignature,
)

__all__ = [
    "COMPONENT_OWNER",
    "DspyTargetIndicatorsExtractor",
    "ExECTv2TargetIndicatorsSignature",
    "ExtractionRecord",
    "Mode",
    "PIPELINE_FAMILY",
    "PROMPT_VERSION",
    "_CLUSTER_OF_SEIZURES",
    "_DIAGNOSIS_ALLOWED_CORE",
    "_DIAGNOSIS_PROHIBITED_CORES",
    "_GENERALIZED_EPILEPSY_GTCS_ALONE",
    "_PLANNED_INVESTIGATION_CONTEXT",
    "_PLANNED_PRESCRIPTION_CONTEXT",
    "_SEIZURE_FREQUENCY_ANCHOR",
    "_SEIZURE_FREQUENCY_PROHIBITED_ANCHOR",
    "_SF_STATE_ATTRIBUTES",
    "_SF_TEXT_ALIASES",
    "_SPECIFIC_SEIZURE_EVIDENCE",
    "_UNKNOWN_LIKE_NUMBER",
    "_convert_day_period_to_week",
    "_count_evidence_invalid_warnings",
    "_dedupe_key",
    "_deduplicate_scored_mentions",
    "_emit_checkpoint",
    "_evidence_has_positive_rate",
    "_expand_asymmetric_prescription",
    "_expand_diagnosis_projection",
    "_expand_seizure_frequency_state",
    "_expand_target_mention",
    "_extract_json_object_field",
    "_extract_json_string_field",
    "_infer_text_from_evidence",
    "_investigation_modality",
    "_investigation_text_modality",
    "_is_allowed_diagnosis_core",
    "_is_allowed_sf_anchor",
    "_is_frequency_phrase_diagnosis_context",
    "_is_investigation_only_diagnosis_context",
    "_is_non_target_investigation_text",
    "_is_planned_investigation",
    "_is_planned_prescription",
    "_is_unsupported_eeg_confirmation",
    "_is_unsupported_inferred_diagnosis",
    "_is_unsupported_investigation_evidence",
    "_is_zero_since_only_diagnosis_context",
    "_iter_top_level_json_objects",
    "_letters_from_rows",
    "_loads_malformed_rationale_mention_object",
    "_loads_python_literal_payload",
    "_loads_salvageable_mention_object",
    "_normalize_target_attributes",
    "_normalize_target_text",
    "_parse_target_extraction_json",
    "_salvage_mentions_from_malformed_json",
    "_sf_state_drop_reason",
    "_sf_type_to_diagnosis_projection_warning",
    "_split_range_attribute",
    "_target_attribute_vocabulary",
    "_worked_examples",
    "audit_only_projection_replay_switches",
    "build_prompt_input",
    "run_split",
    "summarize_rows",
    "to_predicted_letter",
    "write_jsonl",
    "write_report",
]
