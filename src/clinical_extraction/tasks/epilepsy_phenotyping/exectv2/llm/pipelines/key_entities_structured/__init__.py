"""ExECTv2 llm_only structured key-family event-ledger pipeline package.

Pure relocation of ``llm_only_key_entities_structured`` into cohesive
submodules. The legacy module path remains a thin facade re-exporting this API.

Private helpers (and the ``parse_json_payload_with_schema_repair`` /
``write_jsonl`` pass-throughs) are deliberately re-exported here because other
modules import the legacy module as ``structured`` and reach those attributes
directly.
"""
# ruff: noqa: F401 — thin re-export facade for the legacy ``structured`` API.

from .constants import (
    _DIAGNOSIS_RE,
    _INVESTIGATION_RE,
    _MEDICATION_RE,
    _SEIZURE_STATE_RE,
    ALLOWED_EVENT_FAMILIES,
    COMPONENT_OWNER,
    KEY_ENTITY_ITEM_F1_TARGET,
    KEY_ENTITY_NAMES,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
    PROMPT_VERSION_V0_9_24,
    PROMPT_VERSION_V0_9_25_LUNA_SF_BOUNDARY_DX,
    PROMPT_VERSION_V0_9_25_LUNA_SF_STATE,
    PROMPT_VERSION_V10,
    PROMPT_VERSION_V11,
    PROMPT_VERSION_V12,
    PROMPT_VERSION_V13,
    PROMPT_VERSION_V14,
    PROMPT_VERSION_V15,
    PROMPT_VERSION_V16,
    PROMPT_VERSION_V17,
    PUBLISHED_PER_ENTITY_ITEM_F1,
    QWEN_COMPACT_PROMPT_VERSION,
    EventFamily,
    PromptProfile,
    prompt_version_for,
    set_active_prompt_version,
)
from .parsing import (
    _coerce_structured_payload,
    _legacy_mention_to_event,
    _stringify_mapping,
    _strip_non_scored_rationale_fields,
    flatten_events,
    parse_json_payload_with_schema_repair,
    parse_structured_events_json,
)

# NOTE: ``projection`` (which pulls ``benchmark_projection``) MUST be imported
# before ``prompt_content`` (which pulls ``deterministic``). The legacy single
# module imported ``benchmark_projection`` first, and that import primes a
# pre-existing deterministic.normalization <-> scoring circular import. Loading
# ``prompt_content`` first re-triggers that cycle, so keep this order.
from .projection import (
    _SF_STATE_ATTRS,
    _apply_render_safety_gates,
    _drop_duplicate_modality_only_investigations,
    _has_investigation_result,
    _has_sf_state,
    _investigation_modalities,
    _repair_evidence_from_mention_text,
    _strip_model_supplied_projection_attrs,
    to_predicted_letter,
)
from .prompt_builders import (
    _build_qwen_compact_prompt_input,
    build_prompt_input,
)
from .prompt_content import (
    _attribute_vocabulary,
    _decision_procedure,
    _diagnosis_lane_hint,
    _event_lane_guide,
    _family_guidance,
    _first_match_text,
    _investigation_lane_hint,
    _medication_lane_hint,
    _qwen_compact_examples,
    _seizure_anchor_hint,
    _seizure_frequency_lane_hint,
    _sentence_spans,
    _worked_examples,
    candidate_evidence_ledger_for_letter,
    high_priority_evidence_ledger_for_letter,
)
from .records import (
    MedicationHistoryRecord,
    MentionForEvidence,
    PatientHistoryRecord,
    RenderedMentionRecord,
    StructuredClinicalEvent,
    StructuredExtractionRecord,
)
from .runner import (
    _checkpoint_report_path,
    _clinical_recovery_lines,
    _diagnostic_ladder_lines,
    _emit_checkpoint,
    _key_clinical_recovery_to_dict,
    _mention_to_row,
    _overall_to_dict,
    _prf1_to_dict,
    _reconstruct_letters,
    _score_lines,
    _source_near_to_dict,
    run_split,
    summarize_rows,
    write_jsonl,
    write_report,
)
from .signatures import (
    DspyKeyEntitiesStructuredExtractor,
    ExECTv2KeyEntitiesStructuredSignature,
)

__all__ = [
    "ALLOWED_EVENT_FAMILIES",
    "COMPONENT_OWNER",
    "DspyKeyEntitiesStructuredExtractor",
    "EventFamily",
    "ExECTv2KeyEntitiesStructuredSignature",
    "KEY_ENTITY_ITEM_F1_TARGET",
    "KEY_ENTITY_NAMES",
    "MentionForEvidence",
    "MedicationHistoryRecord",
    "PatientHistoryRecord",
    "PIPELINE_FAMILY",
    "PROMPT_VERSION",
    "PROMPT_VERSION_V0_9_24",
    "PROMPT_VERSION_V0_9_25_LUNA_SF_BOUNDARY_DX",
    "PROMPT_VERSION_V0_9_25_LUNA_SF_STATE",
    "PROMPT_VERSION_V10",
    "PROMPT_VERSION_V11",
    "PROMPT_VERSION_V12",
    "PROMPT_VERSION_V13",
    "PROMPT_VERSION_V14",
    "PROMPT_VERSION_V15",
    "PROMPT_VERSION_V16",
    "PROMPT_VERSION_V17",
    "PUBLISHED_PER_ENTITY_ITEM_F1",
    "PromptProfile",
    "QWEN_COMPACT_PROMPT_VERSION",
    "RenderedMentionRecord",
    "StructuredClinicalEvent",
    "StructuredExtractionRecord",
    "build_prompt_input",
    "candidate_evidence_ledger_for_letter",
    "flatten_events",
    "high_priority_evidence_ledger_for_letter",
    "parse_json_payload_with_schema_repair",
    "parse_structured_events_json",
    "prompt_version_for",
    "run_split",
    "set_active_prompt_version",
    "summarize_rows",
    "to_predicted_letter",
    "write_jsonl",
    "write_report",
]
