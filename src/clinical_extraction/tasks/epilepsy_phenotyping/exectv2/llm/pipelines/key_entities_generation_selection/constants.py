"""Attribution, architecture, and JSON output-schema constants for the generation-selection route."""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompts.key_entities.loader import (
    load_dedup_fact_decision_tables,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.types import (
    DedupFactFamily,
)


PROMPT_VERSION = "exectv2_llm_only_key_entities_generation_selection_v0.5"
PIPELINE_FAMILY = "exectv2_llm_only_key_entities_generation_selection"
COMPONENT_OWNER = "qwen_llm_only_generation_selection"
FACT_ORIGIN = "target_model_generated"

_ARCHITECTURE = {
    "name": "llm_only_generation_then_llm_selection",
    "pipeline_family": PIPELINE_FAMILY,
    "generation_owner": "target_model",
    "selection_owner": "target_model",
    "program_role": "json_schema_validation_evidence_validation_projection_reporting",
}


def component_owner_for_model(model: str | None) -> str:
    """Return the attribution owner label for a concrete source model."""

    model_key = (model or "").lower()
    if "deepseek" in model_key:
        return "deepseek_llm_only_generation_selection"
    if "qwen" in model_key:
        return COMPONENT_OWNER
    if "gpt" in model_key or "openai" in model_key:
        return "gpt_llm_only_generation_selection"
    return "target_model_llm_only_generation_selection"


def report_model_label(model: str | None) -> str:
    """Short display label used in Markdown reports."""

    model_key = (model or "").lower()
    if "deepseek" in model_key:
        return "DeepSeek"
    if "qwen" in model_key:
        return "Qwen"
    if "gpt" in model_key or "openai" in model_key:
        return "GPT"
    return "Target-Model"

_OUTPUT_SCHEMA = {
    "clinical_events": [
        {
            "family": "medication|diagnosis|seizure_frequency|investigation",
            "anchor_text": "short source-near event anchor",
            "evidence": "exact substring copied from the letter",
            "event_state": "object with source-supported state fields",
            "mentions": [
                {
                    "entity": "Prescription|Diagnosis|SeizureFrequency|Investigations",
                    "text": "final mention text",
                    "attributes": (
                        "entity-specific scoring attributes; all count, date, "
                        "certainty, negation, dose, result, and performed "
                        "fields required for scoring must be here"
                    ),
                }
            ],
            "confidence": "low|medium|high",
            "rationale": "one short source-grounding sentence",
        }
    ]
}

_INVENTORY_OUTPUT_SCHEMA = {
    "generated_events": _OUTPUT_SCHEMA["clinical_events"],
    "final_events": _OUTPUT_SCHEMA["clinical_events"],
    "selection_summary": [
        {
            "final_anchor_text": "anchor text of a final event",
            "source": "kept|revised|merged|split|added_after_reread",
            "reason": "short source-grounded reason for the selection",
        }
    ],
}

_MENTION_OUTPUT_SCHEMA = {
    "generated_mentions": [
        {
            "entity": "Prescription|Diagnosis|SeizureFrequency|Investigations",
            "text": "short exact clinical concept span from the letter",
            "attributes": "entity-specific attributes needed to render this mention",
            "evidence": "exact substring copied from the letter",
            "confidence": "low|medium|high",
            "rationale": "one short source-grounding sentence",
        }
    ],
    "final_mentions": [
        {
            "entity": "Prescription|Diagnosis|SeizureFrequency|Investigations",
            "text": "short exact clinical concept span from the letter",
            "attributes": "entity-specific attributes needed to render this mention",
            "evidence": "exact substring copied from the letter",
            "confidence": "low|medium|high",
            "rationale": "one short source-grounding sentence",
        }
    ],
    "selection_summary": [
        {
            "final_text": "text of a final mention",
            "source": "kept|revised|split|added_after_reread",
            "reason": "short source-grounded reason for the selection",
        }
    ],
}

_TYPED_MENTION_OUTPUT_SCHEMA = {
    "generated_typed_mentions": [
        {
            "entity": "Prescription|Diagnosis|SeizureFrequency|Investigations",
            "text": "final clinical concept/state anchor",
            "evidence": "exact substring copied from the letter",
            "confidence": "low|medium|high",
            "rationale": "one short source-grounding sentence",
            "DrugName": "Prescription only",
            "DrugDose": "Prescription only",
            "DoseUnit": "Prescription only",
            "Frequency": "Prescription only",
            "DiagCategory": "Diagnosis only",
            "Certainty": "Diagnosis only",
            "Negation": "Diagnosis only",
            "NumberOfSeizures": "SeizureFrequency only",
            "LowerNumberOfSeizures": "SeizureFrequency range only",
            "UpperNumberOfSeizures": "SeizureFrequency range only",
            "TimeSince_or_TimeOfEvent": "SeizureFrequency only",
            "MonthDate": "SeizureFrequency only",
            "PointInTime": "SeizureFrequency only",
            "TimePeriod": "SeizureFrequency only",
            "LowerNumberOfTimePeriods": "SeizureFrequency interval range only",
            "UpperNumberOfTimePeriods": "SeizureFrequency interval range only",
            "FrequencyChange": "SeizureFrequency change only",
            "MRI_Performed": "Investigations only",
            "MRI_Results": "Investigations only",
            "EEG_Performed": "Investigations only",
            "EEG_Results": "Investigations only",
            "CT_Performed": "Investigations only",
            "CT_Results": "Investigations only",
        }
    ],
    "final_typed_mentions": "same shape as generated_typed_mentions",
    "selection_summary": [
        {
            "final_text": "text of final typed mention",
            "source": "kept|revised|split|added_after_reread",
            "reason": "short source-grounded reason",
        }
    ],
}

_MENTION_ID_OUTPUT_SCHEMA = {
    "generated_mentions": [
        {
            "mention_id": "stable short ID such as m1",
            "entity": "Prescription|Diagnosis|SeizureFrequency|Investigations",
            "text": "short exact clinical concept span from the letter",
            "attributes": "entity-specific attributes needed to render this mention",
            "evidence": "exact substring copied from the letter",
            "confidence": "low|medium|high",
            "rationale": "one short source-grounding sentence",
        }
    ],
    "final_mention_ids": ["mention_id values selected from generated_mentions"],
    "selection_summary": [
        {
            "mention_id": "selected or rejected mention ID",
            "decision": "keep|reject",
            "reason": "short source-grounded reason for the selection",
        }
    ],
}

_RENDER_ID_OUTPUT_SCHEMA = {
    "generated_mentions": [
        {
            "mention_id": "stable short ID such as m1",
            "entity": "Prescription|Diagnosis|SeizureFrequency|Investigations",
            "source_text": "short source span naming the mention",
            "text": "final rendered mention text for this clinical fact",
            "attributes": "entity-specific attributes needed to render this mention",
            "evidence": "exact substring copied from the letter",
            "confidence": "low|medium|high",
            "rationale": "one short source-grounding sentence",
        }
    ],
    "final_mention_ids": ["mention_id values selected from generated_mentions"],
    "selection_summary": [
        {
            "mention_id": "selected or rejected mention ID",
            "decision": "keep|reject",
            "reason": "short source-grounded reason for the selection",
        }
    ],
}

_CLEAN_RENDER_ID_OUTPUT_SCHEMA = {
    "generated_mentions": [
        {
            "mention_id": "stable short ID such as m1",
            "entity": "Prescription|Diagnosis|SeizureFrequency|Investigations",
            "source_text": "short exact source span naming the fact",
            "clean_text": "compact final mention text for this clinical fact",
            "attributes": "entity-specific attributes needed to render this mention",
            "evidence": "exact substring copied from the letter",
            "confidence": "low|medium|high",
            "rationale": "one short source-grounding sentence",
        }
    ],
    "final_mention_ids": ["mention_id values selected from generated_mentions"],
    "selection_summary": [
        {
            "mention_id": "selected or rejected mention ID",
            "decision": "keep|reject",
            "reason": "short source-grounded reason for the selection",
        }
    ],
}

_DEDUP_FACT_OUTPUT_SCHEMA = {
    "clinical_facts": [
        {
            "family": "diagnosis",
            "concept": "short diagnosis concept",
            "negation": "affirmed|negated",
            "evidence": "exact substring copied from the letter",
        },
        {
            "family": "seizure_frequency",
            "seizure_type": "named seizure type, or seizures if generic",
            "state": "active_rate|seizure_free|changed|unknown",
            "evidence": "exact substring copied from the letter",
        },
        {
            "family": "prescription",
            "drug": "current drug name",
            "dose": "number only when stated",
            "dose_unit": "mg|g",
            "frequency": "1|2|3|As_Required",
            "source_text": "optional replay-only rendered mention text",
            "evidence": "exact substring copied from the letter",
        },
        {
            "family": "investigation",
            "modality": "MRI|CT|EEG|telemetry",
            "performed": "yes|no, optional and replay-only; new route should emit completed tests",
            "result": "normal|abnormal|unknown",
            "evidence": "exact substring copied from the letter",
        },
    ],
}


def _dedup_fact_decision_tables(
    target_family: DedupFactFamily | None = None,
) -> dict[str, list[dict[str, str]]]:
    tables = load_dedup_fact_decision_tables()
    if target_family is None:
        return tables
    return {target_family: tables[target_family]}


def _dedup_fact_output_schema(
    target_family: DedupFactFamily | None = None,
) -> dict[str, Any]:
    if target_family is None:
        return _DEDUP_FACT_OUTPUT_SCHEMA
    return {
        "clinical_facts": [
            fact
            for fact in _DEDUP_FACT_OUTPUT_SCHEMA["clinical_facts"]
            if fact.get("family") == target_family
        ]
    }

_POOL_ADJUDICATION_OUTPUT_SCHEMA = {
    "final_mention_ids": ["mention_id values selected from model_generated_mentions"],
    "selection_summary": [
        {
            "mention_id": "selected or rejected mention ID",
            "decision": "keep|reject",
            "reason": "short source-grounded reason for the selection",
        }
    ],
}

_POOL_GROUP_ADJUDICATION_OUTPUT_SCHEMA = {
    "fact_groups": [
        {
            "group_id": "stable short ID such as g1",
            "decision": "include|exclude",
            "representative_mention_id": "one selected mention_id for an included group",
            "equivalent_mention_ids": ["all mention_id values describing the same clinical fact"],
            "reason": "short source-grounded reason",
        }
    ]
}

_MODEL_ORIGIN_CONTRACT = [
    "The first pass must generate every clinical event from the letter text.",
    (
        "The selection pass must decide the final events from the letter text "
        "and first-pass model events."
    ),
    "Do not assume any precomputed span list, regex hit list, proposal set, or upstream target.",
    "Return only the final JSON object; do not include chain-of-thought or private reasoning.",
]
