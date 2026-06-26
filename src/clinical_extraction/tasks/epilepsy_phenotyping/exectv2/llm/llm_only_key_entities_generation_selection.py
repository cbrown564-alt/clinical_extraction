"""Attribution-clean generation-selection scaffold for ExECTv2 key entities."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict

from clinical_extraction.core.run_resume import merge_rows, pending_items, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection import (
    STRATEGY_REGISTRY,
    StrategyContext,
    StrategyPrograms,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.types import (
    DEDUP_FACT_FAMILIES,
    DECISION_TABLE_FAMILIES,
    CallStrategy,
    DedupFactFamily,
    PromptProfile,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

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
    tables: dict[str, list[dict[str, str]]] = {
        "diagnosis": [
            {
                "source_pattern": "epilepsy heading or diagnosis line",
                "emit": (
                    "the most specific epilepsy concept stated: epilepsy, focal "
                    "epilepsy/focal-onset epilepsy, temporal lobe epilepsy, "
                    "generalised epilepsy, genetic generalised epilepsy, or "
                    "intractable epilepsy"
                ),
                "do_not_emit": (
                    "a generic epilepsy fact instead of a more specific stated "
                    "epilepsy concept"
                ),
            },
            {
                "source_pattern": "seizure type named in a seizure type/frequency statement",
                "emit": (
                    "the seizure type diagnosis, e.g. focal seizures, focal seizures "
                    "with altered awareness, focal to bilateral convulsive seizures, "
                    "generalised tonic clonic seizures, complex partial seizures"
                ),
                "do_not_emit": (
                    "an epilepsy syndrome such as focal epilepsy or temporal lobe "
                    "epilepsy unless the source states that syndrome separately"
                ),
            },
            {
                "source_pattern": (
                    "febrile seizures, dissociative/non-epileptic events, isolated "
                    "jerks, migraine, syncope, blackouts, or uncertain attacks"
                ),
                "emit": (
                    "nothing unless the phrase is explicitly listed as the patient's "
                    "current epileptic seizure type"
                ),
                "do_not_emit": (
                    "mimics, historical febrile seizures, or symptoms as "
                    "diagnosis facts"
                ),
            },
            {
                "source_pattern": "no absences/no focal seizures/no convulsive seizures",
                "emit": "a negated diagnosis fact for the named target seizure type",
                "do_not_emit": "an affirmed diagnosis fact for the negated phrase",
            },
        ],
        "seizure_frequency": [
            {
                "source_pattern": "explicit nonzero count, rate, cadence, or interval",
                "emit": (
                    "state=active_rate for that exact seizure type; examples include "
                    "2 per month, twice weekly, every 3 weeks, one seizure last week, "
                    "3 since last clinic"
                ),
                "do_not_emit": "active_rate without an explicit burden expression",
            },
            {
                "source_pattern": (
                    "continues to get, ongoing, returned, occasional, frequent, "
                    "infrequent"
                ),
                "emit": (
                    "state=unknown only when this is a seizure type/frequency target "
                    "statement; otherwise omit"
                ),
                "do_not_emit": (
                    "active_rate, and never invent NumberOfSeizures=1 for qualitative "
                    "language"
                ),
            },
            {
                "source_pattern": "last event, last seizure, no seizures since, seizure-free",
                "emit": "state=seizure_free for the named seizure type, or seizures if generic",
                "do_not_emit": "active_rate from a last-event date",
            },
            {
                "source_pattern": "same seizure type has two distinct stated states",
                "emit": (
                    "one fact per distinct state, e.g. an infrequent/unknown state "
                    "and a last-event/seizure_free state may both be present"
                ),
                "do_not_emit": "collapse different states for the same seizure type",
            },
            {
                "source_pattern": (
                    "specific seizure type and generic overall seizure statement "
                    "both appear"
                ),
                "emit": (
                    "specific seizure-type facts for specific evidence; generic "
                    "seizures only for a separate overall statement"
                ),
                "do_not_emit": (
                    "generic seizures from evidence that only names a specific "
                    "seizure type"
                ),
            },
        ],
        "prescription": [
            {
                "source_pattern": (
                    "current medication/current anti-seizure medication/she is "
                    "taking/she is on"
                ),
                "emit": (
                    "each standing current anti-seizure regimen with drug, dose, "
                    "unit, frequency"
                ),
                "do_not_emit": "non-antiepileptic medicines or previous trials",
            },
            {
                "source_pattern": "planned increase, taper, option, start later, reduce slowly",
                "emit": "only the dose/frequency the patient is currently taking now",
                "do_not_emit": "future target doses or medication-change plans",
            },
            {
                "source_pattern": "can take, if necessary, rescue, PRN/as required",
                "emit": (
                    "nothing unless the source explicitly lists it as a current "
                    "standing regimen"
                ),
                "do_not_emit": "contingency or rescue medication as ordinary current treatment",
            },
        ],
        "investigation": [
            {
                "source_pattern": "completed MRI/CT/EEG/telemetry with normal or abnormal result",
                "emit": "the modality with result normal or abnormal",
                "do_not_emit": "dates or planned repeat tests",
            },
            {
                "source_pattern": "completed test mentioned but result not stated",
                "emit": "the modality with result unknown",
                "do_not_emit": "unknown for a planned or requested test",
            },
            {
                "source_pattern": "arranging/requested/awaiting/repeat/planned/future test",
                "emit": "nothing",
                "do_not_emit": "a completed investigation fact, even with result unknown",
            },
        ],
    }
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


class QwenGenerationSelectionExtractor:
    """Two-call DSPy wrapper: model generation followed by model finalization."""

    def __init__(self) -> None:
        self.predict = dspy.Predict(structured.ExECTv2KeyEntitiesStructuredSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    __call__ = forward


class ExECTv2KeyEntitiesInventorySelectionSignature(dspy.Signature):
    """Read one clinical letter and emit generated events plus final selected events.

    Return exactly one JSON object with generated_events and final_events. No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"generated_events\": [...], "
            "\"final_events\": [...], \"selection_summary\": [...]}. Each event "
            "uses family, anchor_text, evidence, event_state, mentions, confidence, "
            "and rationale. Do not include analysis or first-person reasoning."
        )
    )


class QwenSingleCallInventoryExtractor:
    """Single-call wrapper: Qwen emits generated inventory and final selection."""

    def __init__(self) -> None:
        self.predict = dspy.Predict(ExECTv2KeyEntitiesInventorySelectionSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    __call__ = forward


class ExECTv2KeyEntitiesMentionSelectionSignature(dspy.Signature):
    """Read one clinical letter and emit generated mentions plus final mentions.

    Return exactly one JSON object with generated_mentions and final_mentions.
    No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"generated_mentions\": [...], "
            "\"final_mentions\": [...], \"selection_summary\": [...]}. Each mention "
            "uses entity, text, attributes, evidence, confidence, and rationale. "
            "Do not include analysis or first-person reasoning."
        )
    )


class QwenSingleCallMentionExtractor:
    """Single-call wrapper: Qwen emits generated and final rendered mentions."""

    def __init__(self) -> None:
        self.predict = dspy.Predict(ExECTv2KeyEntitiesMentionSelectionSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    __call__ = forward


class ExECTv2KeyEntitiesMentionIdSelectionSignature(dspy.Signature):
    """Read one clinical letter and emit generated mentions plus selected IDs.

    Return exactly one JSON object with generated_mentions and final_mention_ids.
    No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"generated_mentions\": [...], "
            "\"final_mention_ids\": [...], \"selection_summary\": [...]}. Each "
            "generated mention uses mention_id, entity, text, attributes, evidence, "
            "confidence, and rationale. Do not include analysis or first-person "
            "reasoning."
        )
    )


class QwenSingleCallMentionIdExtractor:
    """Single-call wrapper: Qwen emits mentions once and selects by ID."""

    def __init__(self) -> None:
        self.predict = dspy.Predict(ExECTv2KeyEntitiesMentionIdSelectionSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    __call__ = forward


class ExECTv2DedupClinicalFactsSignature(dspy.Signature):
    """Read one clinical letter and emit de-duplicated clinical facts.

    Return exactly one JSON object with clinical_facts. No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and de-duplicated fact instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"clinical_facts\": [...]}. Each fact uses "
            "family-specific simplified fields plus exact evidence. Do not include "
            "analysis or first-person reasoning."
        )
    )


class QwenSingleCallDedupFactsExtractor:
    """Single-call wrapper: model emits de-duplicated clinical facts directly."""

    def __init__(self) -> None:
        self.predict = dspy.Predict(ExECTv2DedupClinicalFactsSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    __call__ = forward


class ExECTv2KeyEntitiesPoolAdjudicationSignature(dspy.Signature):
    """Read one letter and select final IDs from Qwen-generated mention tables.

    Return exactly one JSON object with final_mention_ids. No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, model-generated mentions, and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"final_mention_ids\": [...], "
            "\"selection_summary\": [...]}. Select only mention_id values that "
            "appear in model_generated_mentions. Do not include analysis or "
            "first-person reasoning."
        )
    )


class QwenPoolAdjudicationExtractor:
    """Replay wrapper: Qwen selects among prior Qwen-generated mention IDs."""

    def __init__(self) -> None:
        self.predict = dspy.Predict(ExECTv2KeyEntitiesPoolAdjudicationSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

    __call__ = forward


class StructuredGenerationSelectionRecord(BaseModel):
    """Model-emitted inventory and final selection in one response."""

    model_config = ConfigDict(extra="ignore")

    generated_events: list[structured.StructuredClinicalEvent] = []
    final_events: list[structured.StructuredClinicalEvent] = []
    selection_summary: list[dict[str, Any]] = []


class StructuredMentionSelectionRecord(BaseModel):
    """Model-emitted mention inventory and final mention selection."""

    model_config = ConfigDict(extra="ignore")

    generated_mentions: list[structured.MentionForEvidence] = []
    final_mentions: list[structured.MentionForEvidence] = []
    selection_summary: list[dict[str, Any]] = []


class StructuredMentionIdSelectionRecord(BaseModel):
    """Model-emitted generated mentions plus model-selected mention IDs."""

    model_config = ConfigDict(extra="ignore")

    generated_mentions: list[dict[str, Any]] = []
    final_mention_ids: list[str] = []
    selection_summary: list[dict[str, Any]] = []


class StructuredPoolAdjudicationRecord(BaseModel):
    """Model-selected final mention IDs over prior Qwen-generated mentions."""

    model_config = ConfigDict(extra="ignore")

    final_mention_ids: list[str] = []
    selection_summary: list[dict[str, Any]] = []


class StructuredPoolGroupAdjudicationRecord(BaseModel):
    """Model-emitted duplicate groups plus representative selected IDs."""

    model_config = ConfigDict(extra="ignore")

    fact_groups: list[dict[str, Any]] = []
    final_mention_ids: list[str] = []
    selection_summary: list[dict[str, Any]] = []


class DedupClinicalFactRecord(BaseModel):
    """Simplified model-emitted de-duplicated clinical fact."""

    model_config = ConfigDict(extra="ignore")

    family: str
    evidence: str
    concept: str = ""
    negation: str = ""
    seizure_type: str = ""
    state: str = ""
    drug: str = ""
    dose: str = ""
    dose_unit: str = ""
    frequency: str = ""
    modality: str = ""
    performed: str = ""
    result: str = ""
    source_text: str = ""
    attributes: dict[str, str] = {}


class DedupClinicalFactsRecord(BaseModel):
    """Model-emitted de-duplicated clinical-fact inventory."""

    model_config = ConfigDict(extra="ignore")

    clinical_facts: list[DedupClinicalFactRecord] = []


def build_generation_prompt_payload(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> dict[str, Any]:
    """Build a note-only prompt payload for the Qwen generation pass."""

    return {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": prompt_profile,
        "architecture": _ARCHITECTURE,
        "stage": "generation",
        "model_origin_contract": _MODEL_ORIGIN_CONTRACT,
        "letter": {"letter_id": letter.letter_id, "note_text": letter.note_text},
        "target_entities": structured.KEY_ENTITY_NAMES,
        "event_lane_guide": structured._event_lane_guide(),
        "family_guidance": structured._family_guidance(),
        "attribute_vocabulary": structured._attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "mention_attribute_contract": _mention_attribute_contract(),
        "forbidden_attribute_combinations": _forbidden_attribute_combinations(),
        "worked_examples": _worked_examples(prompt_profile),
        "output_schema": _OUTPUT_SCHEMA,
    }


def build_generation_prompt_input(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> str:
    return json.dumps(
        build_generation_prompt_payload(letter, prompt_profile=prompt_profile),
        sort_keys=True,
    )


def build_selection_prompt_payload(
    letter: ExectLetter,
    first_pass_record: structured.StructuredExtractionRecord | Mapping[str, Any],
    *,
    prompt_profile: PromptProfile = "compact",
) -> dict[str, Any]:
    """Build the Qwen-owned final selection prompt from Qwen's first-pass events."""

    record = _coerce_record(first_pass_record)
    return {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": prompt_profile,
        "architecture": _ARCHITECTURE,
        "stage": "selection",
        "model_origin_contract": _MODEL_ORIGIN_CONTRACT,
        "selection_instructions": [
            "Re-read the letter and the first-pass model events.",
            "Emit the final event set as complete clinical_events JSON.",
            (
                "Preserve a supported first-pass event unless the letter clearly "
                "contradicts it, duplicates it, or shows it is only future/planned."
            ),
            (
                "You may keep, revise, merge, split, add, or remove first-pass "
                "events when the letter supports it."
            ),
            "Every retained mention must have exact source evidence in the letter.",
            (
                "Put all scoring attributes inside each mention.attributes object; "
                "event_state is transparency only."
            ),
        ],
        "letter": {"letter_id": letter.letter_id, "note_text": letter.note_text},
        "first_pass_model_events": [
            event.model_dump() for event in record.clinical_events
        ],
        "target_entities": structured.KEY_ENTITY_NAMES,
        "event_lane_guide": structured._event_lane_guide(),
        "family_guidance": structured._family_guidance(),
        "attribute_vocabulary": structured._attribute_vocabulary(),
        "mention_attribute_contract": _mention_attribute_contract(),
        "forbidden_attribute_combinations": _forbidden_attribute_combinations(),
        "output_schema": _OUTPUT_SCHEMA,
    }


def build_selection_prompt_input(
    letter: ExectLetter,
    first_pass_record: structured.StructuredExtractionRecord | Mapping[str, Any],
    *,
    prompt_profile: PromptProfile = "compact",
) -> str:
    return json.dumps(
        build_selection_prompt_payload(
            letter,
            first_pass_record,
            prompt_profile=prompt_profile,
        ),
        sort_keys=True,
    )


def build_single_call_inventory_prompt_payload(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> dict[str, Any]:
    """Build a one-call model-generated inventory plus final selection prompt."""

    return {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": prompt_profile,
        "architecture": {
            **_ARCHITECTURE,
            "name": "llm_only_single_call_inventory_selection",
        },
        "stage": "single_call_inventory_selection",
        "model_origin_contract": [
            (
                "First emit generated_events: the complete set of clinical events "
                "you find in the letter."
            ),
            (
                "Then emit final_events: the final selected event set after your "
                "own review of generated_events and the letter."
            ),
            (
                "Every final event must be present in generated_events or be an "
                "explicit add-after-reread item in selection_summary."
            ),
            (
                "Do not assume any precomputed span list, regex hit list, "
                "proposal set, or upstream target."
            ),
            "Return only the JSON object; do not include chain-of-thought or private reasoning.",
        ],
        "selection_instructions": [
            "Generate broadly, then finalize conservatively.",
            "Retain supported current facts and completed-result investigations.",
            "Remove duplicates, planned/future-only facts, and unsupported inferences.",
            (
                "Put all scoring attributes inside each mention.attributes object; "
                "event_state is transparency only."
            ),
            (
                "For final_events, mention text should be the clinical concept or "
                "state anchor, not a count phrase or rationale fragment."
            ),
        ],
        "letter": {"letter_id": letter.letter_id, "note_text": letter.note_text},
        "target_entities": structured.KEY_ENTITY_NAMES,
        "event_lane_guide": structured._event_lane_guide(),
        "family_guidance": structured._family_guidance(),
        "attribute_vocabulary": structured._attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "mention_attribute_contract": _mention_attribute_contract(),
        "forbidden_attribute_combinations": _forbidden_attribute_combinations(),
        "worked_examples": _worked_examples(prompt_profile),
        "output_schema": _INVENTORY_OUTPUT_SCHEMA,
    }


def build_single_call_inventory_prompt_input(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> str:
    return json.dumps(
        build_single_call_inventory_prompt_payload(
            letter,
            prompt_profile=prompt_profile,
        ),
        sort_keys=True,
    )


def build_single_call_mentions_prompt_payload(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> dict[str, Any]:
    """Build a one-call direct rendered-mention generation/selection prompt."""

    return {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": prompt_profile,
        "architecture": {
            **_ARCHITECTURE,
            "name": "llm_only_single_call_mention_selection",
        },
        "stage": "single_call_mention_selection",
        "model_origin_contract": [
            (
                "First emit generated_mentions: every source-supported rendered "
                "mention you find in the letter."
            ),
            (
                "Then emit final_mentions: the final selected mention set after "
                "your own review of generated_mentions and the letter."
            ),
            (
                "Every final mention must be present in generated_mentions or be "
                "an explicit add-after-reread item in selection_summary."
            ),
            (
                "Do not assume any precomputed span list, regex hit list, "
                "proposal set, or upstream target."
            ),
            "Return only the JSON object; do not include chain-of-thought or private reasoning.",
        ],
        "selection_instructions": [
            "Generate broadly, then finalize conservatively.",
            "Retain supported current facts and completed-result investigations.",
            "Remove duplicates, planned/future-only facts, and unsupported inferences.",
            (
                "Each final mention must carry all needed attributes in its own "
                "attributes object."
            ),
            (
                "Mention text should be the clinical concept or state anchor, not "
                "a count phrase, full sentence, or rationale fragment."
            ),
            (
                "Use one final mention for each explicit source event, including "
                "repeated source-supported diagnoses or frequency states in "
                "different sections."
            ),
        ],
        "letter": {"letter_id": letter.letter_id, "note_text": letter.note_text},
        "target_entities": structured.KEY_ENTITY_NAMES,
        "family_guidance": structured._family_guidance(),
        "attribute_vocabulary": structured._attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "mention_attribute_contract": _mention_attribute_contract(),
        "forbidden_attribute_combinations": _forbidden_attribute_combinations(),
        "worked_examples": _worked_examples(prompt_profile),
        "output_schema": _MENTION_OUTPUT_SCHEMA,
    }


def build_single_call_mentions_prompt_input(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> str:
    return json.dumps(
        build_single_call_mentions_prompt_payload(
            letter,
            prompt_profile=prompt_profile,
        ),
        sort_keys=True,
    )


def build_single_call_per_entity_mentions_prompt_payload(
    letter: ExectLetter,
    *,
    target_entity: str,
    prompt_profile: PromptProfile = "compact",
) -> dict[str, Any]:
    """Build a one-call generated/final mention prompt for one entity."""

    payload = build_single_call_mentions_prompt_payload(
        letter,
        prompt_profile=prompt_profile,
    )
    payload["architecture"] = {
        **payload["architecture"],
        "name": "llm_only_single_call_per_entity_mention_selection",
    }
    payload["stage"] = "single_call_per_entity_mention_selection"
    payload["target_entity"] = target_entity
    payload["target_entities"] = [target_entity]
    payload["model_origin_contract"] = [
        (
            "First emit generated_mentions: every source-supported rendered "
            f"{target_entity} mention you find in the letter."
        ),
        (
            "Then emit final_mentions: the final selected "
            f"{target_entity} mention set after your own review of "
            "generated_mentions and the letter."
        ),
        (
            "Every final mention must be present in generated_mentions or be "
            "an explicit add-after-reread item in selection_summary."
        ),
        (
            "Do not emit mentions for other entities, and do not assume any "
            "precomputed span list, regex hit list, proposal set, or upstream target."
        ),
        "Return only the JSON object; do not include chain-of-thought or private reasoning.",
    ]
    payload["selection_instructions"] = [
        f"Generate broadly for {target_entity}, then finalize conservatively.",
        f"Every generated_mentions and final_mentions item must have entity {target_entity}.",
        "Retain supported current facts and completed-result investigations.",
        "Remove duplicates, planned/future-only facts, and unsupported inferences.",
        (
            "Each final mention must carry all needed attributes in its own "
            "attributes object."
        ),
        (
            "Mention text should be the clinical concept or state anchor, not "
            "a count phrase, full sentence, or rationale fragment."
        ),
        (
            "Use one final mention for each explicit source event, including "
            "repeated source-supported facts in different sections."
        ),
    ]
    return payload


def build_single_call_per_entity_mentions_prompt_input(
    letter: ExectLetter,
    *,
    target_entity: str,
    prompt_profile: PromptProfile = "compact",
) -> str:
    return json.dumps(
        build_single_call_per_entity_mentions_prompt_payload(
            letter,
            target_entity=target_entity,
            prompt_profile=prompt_profile,
        ),
        sort_keys=True,
    )


def build_single_call_typed_mentions_prompt_payload(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> dict[str, Any]:
    """Build a one-call generated/final typed-mention prompt."""

    return {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": prompt_profile,
        "architecture": {
            **_ARCHITECTURE,
            "name": "llm_only_single_call_typed_mention_selection",
        },
        "stage": "single_call_typed_mention_selection",
        "model_origin_contract": [
            (
                "First emit generated_typed_mentions: every source-supported "
                "rendered mention you find in the letter using the explicit "
                "typed fields in the schema."
            ),
            (
                "Then emit final_typed_mentions: the final selected typed mention "
                "set after your own review of generated_typed_mentions and the letter."
            ),
            (
                "Every final typed mention must be present in generated_typed_mentions "
                "or be an explicit add-after-reread item in selection_summary."
            ),
            (
                "Do not assume any precomputed span list, regex hit list, proposal "
                "set, or upstream target."
            ),
            "Return only the JSON object; do not include chain-of-thought or private reasoning.",
        ],
        "selection_instructions": [
            "Generate broadly, then finalize conservatively.",
            "Retain supported current facts and completed-result investigations.",
            "Remove duplicates, planned/future-only facts, and unsupported inferences.",
            (
                "Use the typed fields directly instead of nesting an attributes "
                "object unless a field is not available in the schema."
            ),
            (
                "Leave unused typed fields absent or empty. Do not put range text "
                "such as '2 to 3' in NumberOfSeizures; use LowerNumberOfSeizures "
                "and UpperNumberOfSeizures."
            ),
            (
                "Mention text should be the clinical concept or state anchor, not "
                "a count phrase, full sentence, or rationale fragment."
            ),
        ],
        "letter": {"letter_id": letter.letter_id, "note_text": letter.note_text},
        "target_entities": structured.KEY_ENTITY_NAMES,
        "family_guidance": structured._family_guidance(),
        "attribute_vocabulary": structured._attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "mention_attribute_contract": _mention_attribute_contract(),
        "forbidden_attribute_combinations": _forbidden_attribute_combinations(),
        "worked_examples": _worked_examples(prompt_profile),
        "output_schema": _TYPED_MENTION_OUTPUT_SCHEMA,
    }


def build_single_call_typed_mentions_prompt_input(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> str:
    return json.dumps(
        build_single_call_typed_mentions_prompt_payload(
            letter,
            prompt_profile=prompt_profile,
        ),
        sort_keys=True,
    )


def build_single_call_mention_ids_prompt_payload(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> dict[str, Any]:
    """Build a one-call generated-mention table plus selected-ID prompt."""

    return {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": prompt_profile,
        "architecture": {
            **_ARCHITECTURE,
            "name": "llm_only_single_call_mention_id_selection",
        },
        "stage": "single_call_mention_id_selection",
        "model_origin_contract": [
            (
                "First emit generated_mentions: every source-supported rendered "
                "mention you find in the letter. Give each mention a unique "
                "mention_id such as m1, m2, m3."
            ),
            (
                "Then emit final_mention_ids: the mention_id values you select "
                "as the final answer after reviewing generated_mentions and the "
                "letter."
            ),
            (
                "Do not rewrite selected mentions in a separate final_mentions "
                "list. Select by ID so the generated mention text, attributes, "
                "evidence, confidence, and rationale stay unchanged."
            ),
            (
                "Do not assume any precomputed span list, regex hit list, "
                "proposal set, or upstream target."
            ),
            "Return only the JSON object; do not include chain-of-thought or private reasoning.",
        ],
        "selection_instructions": [
            "Generate broadly, then select conservatively by mention_id.",
            "Retain supported current facts and completed-result investigations.",
            "Reject planned/future-only facts and unsupported inferences.",
            (
                "Keep repeated source-supported mentions by selecting each "
                "separate mention_id."
            ),
            (
                "Each selected generated mention must carry all needed attributes "
                "in its own attributes object."
            ),
            (
                "Mention text should be the clinical concept or state anchor, not "
                "a count phrase, full sentence, or rationale fragment."
            ),
        ],
        "letter": {"letter_id": letter.letter_id, "note_text": letter.note_text},
        "target_entities": structured.KEY_ENTITY_NAMES,
        "family_guidance": structured._family_guidance(),
        "attribute_vocabulary": structured._attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "mention_attribute_contract": _mention_attribute_contract(),
        "forbidden_attribute_combinations": _forbidden_attribute_combinations(),
        "worked_examples": _worked_examples(prompt_profile),
        "output_schema": _MENTION_ID_OUTPUT_SCHEMA,
    }


def build_single_call_mention_ids_prompt_input(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> str:
    return json.dumps(
        build_single_call_mention_ids_prompt_payload(
            letter,
            prompt_profile=prompt_profile,
        ),
        sort_keys=True,
    )


def build_single_call_render_ids_prompt_payload(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> dict[str, Any]:
    """Build a one-call generated-render table plus selected-ID prompt."""

    return {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": prompt_profile,
        "architecture": {
            **_ARCHITECTURE,
            "name": "llm_only_single_call_render_id_selection",
        },
        "stage": "single_call_render_id_selection",
        "model_origin_contract": [
            (
                "First emit generated_mentions: every source-supported rendered "
                "mention you find in the letter. Give each mention a unique "
                "mention_id such as m1, m2, m3."
            ),
            (
                "Then emit final_mention_ids: the mention_id values you select "
                "as the final answer after reviewing generated_mentions and the "
                "letter."
            ),
            (
                "Do not rewrite selected mentions in a separate final_mentions "
                "list. Select by ID so the generated mention text, attributes, "
                "evidence, confidence, and rationale stay unchanged."
            ),
            (
                "Do not assume any precomputed span list, regex hit list, "
                "proposal set, or upstream target."
            ),
            "Return only the JSON object; do not include chain-of-thought or private reasoning.",
        ],
        "selection_instructions": [
            "Generate broadly, then select conservatively by mention_id.",
            "Retain supported current facts and completed-result investigations.",
            "Reject planned/future-only facts and unsupported inferences.",
            (
                "Keep repeated source-supported mentions by selecting each "
                "separate mention_id."
            ),
            (
                "Each selected generated mention must carry all needed attributes "
                "in its own attributes object."
            ),
        ],
        "render_text_policy": _render_text_policy(),
        "letter": {"letter_id": letter.letter_id, "note_text": letter.note_text},
        "target_entities": structured.KEY_ENTITY_NAMES,
        "family_guidance": structured._family_guidance(),
        "attribute_vocabulary": structured._attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "mention_attribute_contract": _mention_attribute_contract(),
        "forbidden_attribute_combinations": _forbidden_attribute_combinations(),
        "worked_examples": _worked_examples(prompt_profile),
        "output_schema": _RENDER_ID_OUTPUT_SCHEMA,
    }


def build_single_call_render_ids_prompt_input(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> str:
    return json.dumps(
        build_single_call_render_ids_prompt_payload(
            letter,
            prompt_profile=prompt_profile,
        ),
        sort_keys=True,
    )


def build_single_call_clean_render_ids_prompt_payload(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> dict[str, Any]:
    """Build a one-call source-span plus clean-render selected-ID prompt."""

    return {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": prompt_profile,
        "architecture": {
            **_ARCHITECTURE,
            "name": "llm_only_single_call_clean_render_id_selection",
        },
        "stage": "single_call_clean_render_id_selection",
        "model_origin_contract": [
            (
                "First emit generated_mentions: every source-supported clinical "
                "fact you find in the letter. Give each mention a unique "
                "mention_id such as m1, m2, m3."
            ),
            (
                "For each generated mention, source_text is the exact span in the "
                "letter and clean_text is your compact final mention text for "
                "that same fact."
            ),
            (
                "Then emit final_mention_ids: the mention_id values you select "
                "as the final answer after reviewing generated_mentions and the "
                "letter."
            ),
            (
                "Do not rewrite selected mentions in a separate final_mentions "
                "list. Select by ID so clean_text, attributes, evidence, "
                "confidence, and rationale stay unchanged."
            ),
            (
                "Do not assume any precomputed span list, regex hit list, "
                "proposal set, or upstream target."
            ),
            "Return only the JSON object; do not include chain-of-thought or private reasoning.",
        ],
        "selection_instructions": [
            "Generate broadly, then select conservatively by mention_id.",
            "Retain supported current facts and completed-result investigations.",
            "Reject planned/future-only facts and unsupported inferences.",
            (
                "Keep repeated source-supported mentions by selecting each "
                "separate mention_id."
            ),
            (
                "Each selected generated mention must carry all needed attributes "
                "in its own attributes object."
            ),
            (
                "Prefer a short clean_text over a full sentence: name the concept "
                "or state, and put dose, count, date, result, certainty, and "
                "negation details in attributes."
            ),
        ],
        "clean_text_policy": _clean_render_text_policy(),
        "letter": {"letter_id": letter.letter_id, "note_text": letter.note_text},
        "target_entities": structured.KEY_ENTITY_NAMES,
        "family_guidance": structured._family_guidance(),
        "attribute_vocabulary": structured._attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "mention_attribute_contract": _mention_attribute_contract(),
        "forbidden_attribute_combinations": _forbidden_attribute_combinations(),
        "worked_examples": _worked_examples(prompt_profile),
        "output_schema": _CLEAN_RENDER_ID_OUTPUT_SCHEMA,
    }


def build_single_call_clean_render_ids_prompt_input(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
) -> str:
    return json.dumps(
        build_single_call_clean_render_ids_prompt_payload(
            letter,
            prompt_profile=prompt_profile,
        ),
        sort_keys=True,
    )


def build_single_call_dedup_facts_prompt_payload(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
    target_family: DedupFactFamily | None = None,
) -> dict[str, Any]:
    """Build a one-call prompt for direct de-duplicated clinical facts."""

    stage = (
        "single_call_dedup_facts_per_family"
        if target_family
        else "single_call_dedup_facts"
    )
    architecture_name = (
        "llm_only_single_call_dedup_facts_per_family"
        if target_family
        else "llm_only_single_call_dedup_facts"
    )
    model_origin_contract = [
        (
            "Emit clinical_facts directly from the letter. The model must "
            "generate every scored fact; deterministic code only validates "
            "evidence, maps representation fields, and scores."
        ),
        (
            "Do not assume any precomputed span list, regex hit list, proposal "
            "set, upstream target, or candidate evidence ledger."
        ),
        (
            "De-duplicate at the source: emit each distinct clinical fact once. "
            "Do not repeat a diagnosis, seizure-type state, drug regimen, or "
            "investigation that you have already listed."
        ),
        "Every clinical_fact.evidence must be an exact substring copied from the letter.",
        "Return only the JSON object; do not include chain-of-thought or private reasoning.",
    ]
    if target_family:
        model_origin_contract.insert(
            0,
            (
                f"Emit only {target_family} clinical_facts for this call. Omit every "
                "other family even when present in the letter; separate calls will "
                "handle those families."
            ),
        )

    fact_guidance = [
        (
            "Diagnosis: one fact per distinct diagnosis concept. Use negation "
            "affirmed or negated; do not emit Certainty or DiagCategory."
        ),
        (
            "Diagnosis target scope is epilepsy, epilepsy syndromes, and named "
            "seizure types only. Do not emit unrelated comorbidities, brain "
            "lesions, symptoms, causes, or medication side effects as diagnoses."
        ),
        (
            "Do not emit migraine, anxiety, alcohol use, blackouts, syncope, "
            "dissociative seizures, non-epileptic events, febrile seizures, or "
            "isolated myoclonic jerks as diagnosis facts unless the same phrase "
            "is explicitly named as the patient's epileptic seizure type."
        ),
        (
            "Split compound diagnosis headings into separate facts. For example, "
            "focal epilepsy-Probable temporal supports focal epilepsy and "
            "temporal lobe epilepsy; genetic generalised epilepsy-epilepsy with "
            "generalised tonic clonic seizures alone supports both named epilepsy "
            "concepts. Treat source typos such as tonic chronic as tonic clonic "
            "when the surrounding phrase is a seizure type."
        ),
        (
            "When a seizure-frequency sentence names a seizure type, also emit "
            "a diagnosis fact for that named seizure type, such as focal seizures, "
            "focal seizures with altered awareness, secondary generalised seizures, "
            "absence-like seizures, or generalised tonic clonic seizures."
        ),
        (
            "SeizureFrequency: one fact per distinct seizure type and coarse "
            "state. Use active_rate for any stated nonzero count/rate/interval, "
            "including historical years or named months; seizure_free for zero/no "
            "seizures or seizure-free intervals; changed for explicit worsened/"
            "improved/controlled/increased/decreased/change statements; and "
            "unknown when a seizure-frequency reference has no recoverable coarse "
            "state."
        ),
        (
            "SeizureFrequency state boundary: active_rate requires an explicit "
            "count, cadence, or interval such as 2 per month, twice a week, every "
            "3 weeks, or one seizure last week. Phrases such as occasional, "
            "frequent, infrequent, well controlled, continues to get, returned, "
            "or improved are qualitative; use unknown for those only when they are "
            "a target seizure-frequency statement, and omit them when they are "
            "only narrative without a clear target seizure type."
        ),
        (
            "SeizureFrequency last-event boundary: if the source says last event, "
            "last seizure, no seizures since, or seizure-free since a date, use "
            "seizure_free for that seizure type. Do not turn a last-event date "
            "into active_rate."
        ),
        (
            "Do not emit a SeizureFrequency fact for a one-off narrative event, "
            "a first single seizure, a suspected attack, or a possible non-epileptic "
            "loss-of-consciousness episode unless the letter also states a count, "
            "rate, interval, seizure-free window, or frequency-change statement."
        ),
        (
            "SeizureFrequency: scan the whole letter for counts, rates, intervals, "
            "since/over/during windows, last-seizure statements, seizure-free "
            "statements, and frequency-change statements. Do not skip a frequency "
            "fact just because it is in past history."
        ),
        (
            "SeizureFrequency: do not add a generic seizures fact when the same "
            "evidence only supports a more specific seizure type you already "
            "emitted. Add generic seizures only for a separate source statement "
            "about overall seizures, overall seizure freedom, or overall change."
        ),
        (
            "Prescription: current anti-seizure/antiepileptic medications only, "
            "as drug plus stated dose, dose_unit, and frequency. Do not emit "
            "non-antiepileptic medication-list items, prior trials, future "
            "plans, options, or medications without a recoverable dose and "
            "frequency."
        ),
        (
            "Investigation: completed tests only. Use modality MRI, CT, EEG, "
            "or telemetry and result normal, abnormal, or unknown."
        ),
        (
            "Investigation: prior/previous/old dated MRI, CT, EEG, video EEG, "
            "VEEG, or telemetry findings are completed tests when a result is "
            "stated. Omit requested, arranged, awaiting, repeat, planned, or "
            "future-only investigations."
        ),
        (
            "Evidence: copy an exact contiguous substring from the letter. If a "
            "full sentence is hard to copy exactly, use the shortest exact phrase "
            "that still supports the fact; never paraphrase evidence."
        ),
    ]
    if target_family:
        fact_guidance = [
            (
                f"Family gate: emit only family={target_family}; output an empty "
                "clinical_facts list if the letter has no source-supported "
                f"{target_family} facts."
            ),
            *fact_guidance,
        ]
    if prompt_profile == "decision_table":
        fact_guidance = [
            (
                "Before emitting facts, apply the decision_tables exactly. If a "
                "decision table says omit, do not emit that fact even if the phrase "
                "looks clinically related."
            ),
            *fact_guidance,
        ]

    payload = {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": prompt_profile,
        "architecture": {
            **_ARCHITECTURE,
            "name": architecture_name,
            "scored_surface": "clinical_headline",
        },
        "stage": stage,
        "model_origin_contract": model_origin_contract,
        "fact_guidance": fact_guidance,
        "adapter_contract": [
            (
                "The adapter maps each diagnosis fact to Diagnosis concept+Negation; "
                "each seizure_frequency fact to SeizureFrequency seizure type+state; "
                "each prescription fact to DrugName/DrugDose/DoseUnit/Frequency; "
                "and each investigation fact to modality Performed=Yes plus Result."
            ),
            (
                "The adapter must not add missing facts, select a state the model "
                "omitted, expand ontology companions, or de-duplicate facts."
            ),
        ],
        "letter": {"letter_id": letter.letter_id, "note_text": letter.note_text},
        "target_surface": {
            "name": "clinical_headline",
            "diagnosis_component": "concept_negation",
        },
        "output_schema": _dedup_fact_output_schema(target_family),
        "worked_examples": _dedup_fact_worked_examples(
            prompt_profile,
            target_family=target_family,
        ),
    }
    if prompt_profile == "decision_table":
        payload["decision_tables"] = _dedup_fact_decision_tables(target_family)
    if target_family:
        payload["target_family"] = target_family
        payload["target_families"] = [target_family]
    return payload


def build_single_call_dedup_facts_prompt_input(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
    target_family: DedupFactFamily | None = None,
) -> str:
    return json.dumps(
        build_single_call_dedup_facts_prompt_payload(
            letter,
            prompt_profile=prompt_profile,
            target_family=target_family,
        ),
        sort_keys=True,
    )


def build_single_call_per_entity_clean_render_ids_prompt_payload(
    letter: ExectLetter,
    *,
    target_entity: str,
    prompt_profile: PromptProfile = "compact",
) -> dict[str, Any]:
    """Build a source-span plus clean-render selected-ID prompt for one entity."""

    payload = build_single_call_clean_render_ids_prompt_payload(
        letter,
        prompt_profile=prompt_profile,
    )
    payload["architecture"] = {
        **payload["architecture"],
        "name": "llm_only_single_call_per_entity_clean_render_id_selection",
    }
    payload["stage"] = "single_call_per_entity_clean_render_id_selection"
    payload["target_entity"] = target_entity
    payload["target_entities"] = [target_entity]
    payload["model_origin_contract"] = [
        (
            "First emit generated_mentions: every source-supported "
            f"{target_entity} fact you find in the letter. Give each mention "
            "a unique mention_id such as m1, m2, m3."
        ),
        (
            "For each generated mention, source_text is the exact span in the "
            "letter and clean_text is your compact final mention text for that "
            f"{target_entity} fact."
        ),
        (
            "Then emit final_mention_ids: the mention_id values you select as "
            f"the final {target_entity} answer after reviewing generated_mentions "
            "and the letter."
        ),
        (
            "Do not emit mentions for other entities. Do not rewrite selected "
            "mentions in a separate final_mentions list."
        ),
        (
            "Do not assume any precomputed span list, regex hit list, proposal "
            "set, or upstream target."
        ),
        "Return only the JSON object; do not include chain-of-thought or private reasoning.",
    ]
    payload["selection_instructions"] = [
        f"Generate broadly for {target_entity}, then select conservatively by mention_id.",
        f"Every generated_mentions item must have entity {target_entity}.",
        "Retain supported current facts and completed-result investigations.",
        "Reject planned/future-only facts and unsupported inferences.",
        (
            "Keep repeated source-supported mentions by selecting each separate "
            "mention_id."
        ),
        (
            "Each selected generated mention must carry all needed attributes "
            "in its own attributes object."
        ),
    ]
    return payload


def build_single_call_per_entity_clean_render_ids_prompt_input(
    letter: ExectLetter,
    *,
    target_entity: str,
    prompt_profile: PromptProfile = "compact",
) -> str:
    return json.dumps(
        build_single_call_per_entity_clean_render_ids_prompt_payload(
            letter,
            target_entity=target_entity,
            prompt_profile=prompt_profile,
        ),
        sort_keys=True,
    )


def build_qwen_pool_adjudication_prompt_payload(
    letter: ExectLetter,
    model_generated_mentions: Sequence[Mapping[str, Any]],
    *,
    prompt_profile: PromptProfile = "compact",
) -> dict[str, Any]:
    """Build a Qwen self-adjudication prompt over prior Qwen mention emissions."""

    pool_mentions, pool_notes = _coerce_mention_list(
        list(model_generated_mentions),
        prefix="model_generated_mentions",
        require_mention_id=True,
    )
    return {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": prompt_profile,
        "architecture": {
            **_ARCHITECTURE,
            "name": "llm_only_qwen_pool_self_adjudication",
        },
        "stage": "qwen_pool_adjudication",
        "model_origin_contract": [
            (
                "model_generated_mentions contains only prior Qwen model-emitted "
                "mentions for this same letter from attribution-clean llm_only runs."
            ),
            (
                "Select final_mention_ids from model_generated_mentions after "
                "re-reading the letter. Do not emit new mention objects."
            ),
            (
                "Select only IDs that appear in model_generated_mentions so the "
                "selected mention text, attributes, evidence, confidence, and "
                "rationale stay unchanged."
            ),
            (
                "Do not assume any precomputed span list, regex hit list, or "
                "upstream target."
            ),
            "Return only the JSON object; do not include chain-of-thought or private reasoning.",
        ],
        "selection_instructions": [
            "Prefer source-supported current facts and completed-result investigations.",
            "Reject planned/future-only facts and unsupported inferences.",
            (
                "Do not select every valid row. Choose a compact final set that "
                "represents each clinical fact once."
            ),
            (
                "Different source_run or source_surface values are provenance "
                "only; they never make duplicate rows into separate facts."
            ),
            (
                "When duplicate rows describe the same source-supported fact, "
                "select exactly one ID for that fact, not one ID from each run."
            ),
            (
                "For duplicate facts, prefer a structured_mentions_final row, "
                "then a structured_events_final row, then the row with the "
                "clearest complete attributes."
            ),
            (
                "Keep repeated source-supported mentions when they represent "
                "separate documented facts or separate sections in the letter, "
                "not when they only repeat across prior model runs."
            ),
            (
                "Every selected ID must have exact source evidence in the letter "
                "and entity-specific attributes needed for rendering."
            ),
            "Keep each selection_summary reason under 18 words with no deliberation.",
        ],
        "letter": {"letter_id": letter.letter_id, "note_text": letter.note_text},
        "model_generated_mentions": pool_mentions,
        "pool_validation_notes": pool_notes,
        "target_entities": structured.KEY_ENTITY_NAMES,
        "family_guidance": structured._family_guidance(),
        "attribute_vocabulary": structured._attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "mention_attribute_contract": _mention_attribute_contract(),
        "forbidden_attribute_combinations": _forbidden_attribute_combinations(),
        "worked_examples": _worked_examples(prompt_profile),
        "output_schema": _POOL_ADJUDICATION_OUTPUT_SCHEMA,
    }


def build_qwen_pool_entity_adjudication_prompt_payload(
    letter: ExectLetter,
    model_generated_mentions: Sequence[Mapping[str, Any]],
    *,
    target_entity: str,
    prompt_profile: PromptProfile = "compact",
) -> dict[str, Any]:
    """Build a Qwen self-adjudication prompt for one entity-specific pool."""

    payload = build_qwen_pool_adjudication_prompt_payload(
        letter,
        model_generated_mentions,
        prompt_profile=prompt_profile,
    )
    payload["architecture"] = {
        **payload["architecture"],
        "name": "llm_only_qwen_pool_entity_self_adjudication",
    }
    payload["stage"] = "qwen_pool_entity_adjudication"
    payload["target_entity"] = target_entity
    payload["target_entities"] = [target_entity]
    payload["model_origin_contract"] = [
        (
            "model_generated_mentions contains only prior Qwen model-emitted "
            f"{target_entity} mentions for this same letter from "
            "attribution-clean llm_only runs."
        ),
        (
            "Select final_mention_ids from this one-entity pool after "
            "re-reading the letter. Do not emit new mention objects."
        ),
        (
            "Select only IDs that appear in model_generated_mentions so the "
            "selected mention text, attributes, evidence, confidence, and "
            "rationale stay unchanged."
        ),
        "Rows for the same fact across source_run values are duplicates, not separate facts.",
        "Return only the JSON object; do not include chain-of-thought or private reasoning.",
    ]
    payload["selection_instructions"] = [
        f"Select only final {target_entity} IDs.",
        "Reject rows for other entities if any appear in this pool.",
        "Prefer source-supported current facts and completed-result investigations.",
        "Reject planned/future-only facts and unsupported inferences.",
        (
            "Do not select every valid row. Choose a compact final set that "
            "represents each clinical fact once."
        ),
        (
            "Different source_run or source_surface values are provenance "
            "only; they never make duplicate rows into separate facts."
        ),
        (
            "When duplicate rows describe the same source-supported fact, "
            "select exactly one ID for that fact, not one ID from each run."
        ),
        (
            "For duplicate facts, prefer a structured_mentions_final row, "
            "then a structured_events_final row, then the row with the "
            "clearest complete attributes."
        ),
        (
            "Keep repeated source-supported mentions when they represent "
            "separate documented facts or separate sections in the letter, "
            "not when they only repeat across prior model runs."
        ),
        (
            "Every selected ID must have exact source evidence in the letter "
            "and entity-specific attributes needed for rendering."
        ),
        "Keep each selection_summary reason under 18 words with no deliberation.",
    ]
    return payload


def build_qwen_pool_adjudication_prompt_input(
    letter: ExectLetter,
    model_generated_mentions: Sequence[Mapping[str, Any]],
    *,
    prompt_profile: PromptProfile = "compact",
) -> str:
    return json.dumps(
        build_qwen_pool_adjudication_prompt_payload(
            letter,
            model_generated_mentions,
            prompt_profile=prompt_profile,
        ),
        sort_keys=True,
    )


def build_qwen_pool_entity_adjudication_prompt_input(
    letter: ExectLetter,
    model_generated_mentions: Sequence[Mapping[str, Any]],
    *,
    target_entity: str,
    prompt_profile: PromptProfile = "compact",
) -> str:
    return json.dumps(
        build_qwen_pool_entity_adjudication_prompt_payload(
            letter,
            model_generated_mentions,
            target_entity=target_entity,
            prompt_profile=prompt_profile,
        ),
        sort_keys=True,
    )


def build_qwen_pool_group_adjudication_prompt_payload(
    letter: ExectLetter,
    model_generated_mentions: Sequence[Mapping[str, Any]],
    *,
    prompt_profile: PromptProfile = "compact",
) -> dict[str, Any]:
    """Build a Qwen self-adjudication prompt that groups duplicate facts."""

    pool_mentions, pool_notes = _coerce_mention_list(
        list(model_generated_mentions),
        prefix="model_generated_mentions",
        require_mention_id=True,
    )
    return {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": prompt_profile,
        "architecture": {
            **_ARCHITECTURE,
            "name": "llm_only_qwen_pool_group_self_adjudication",
        },
        "stage": "qwen_pool_group_adjudication",
        "model_origin_contract": [
            (
                "model_generated_mentions contains only prior Qwen model-emitted "
                "mentions for this same letter from attribution-clean llm_only runs."
            ),
            (
                "First group rows that describe the same clinical fact. Then decide "
                "whether each group belongs in the final answer."
            ),
            (
                "For each included group, choose exactly one representative_mention_id "
                "from that group. Do not emit new mention objects."
            ),
            (
                "Different source_run or source_surface values are provenance only; "
                "they never make duplicate rows into separate facts."
            ),
            "Return only the JSON object; do not include chain-of-thought or private reasoning.",
        ],
        "selection_instructions": [
            "Return fact_groups, not a flat list.",
            "Each row ID must appear in at most one fact group.",
            "Use decision include for current supported facts and completed-result investigations.",
            "Use decision exclude for planned/future-only facts and unsupported inferences.",
            (
                "For duplicate facts, include one group with one representative ID, "
                "not one included group per source run."
            ),
            (
                "For duplicate facts, prefer a structured_mentions_final row, "
                "then a structured_events_final row, then the row with the "
                "clearest complete attributes."
            ),
            (
                "Keep repeated source-supported mentions only when they are separate "
                "facts or separate sections in the letter."
            ),
            (
                "Every representative ID must have exact source evidence in the "
                "letter and complete entity-specific attributes."
            ),
            "Keep each reason under 18 words with no deliberation.",
        ],
        "letter": {"letter_id": letter.letter_id, "note_text": letter.note_text},
        "model_generated_mentions": pool_mentions,
        "pool_validation_notes": pool_notes,
        "target_entities": structured.KEY_ENTITY_NAMES,
        "family_guidance": structured._family_guidance(),
        "attribute_vocabulary": structured._attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "mention_attribute_contract": _mention_attribute_contract(),
        "forbidden_attribute_combinations": _forbidden_attribute_combinations(),
        "worked_examples": _worked_examples(prompt_profile),
        "output_schema": _POOL_GROUP_ADJUDICATION_OUTPUT_SCHEMA,
    }


def build_qwen_pool_group_adjudication_prompt_input(
    letter: ExectLetter,
    model_generated_mentions: Sequence[Mapping[str, Any]],
    *,
    prompt_profile: PromptProfile = "compact",
) -> str:
    return json.dumps(
        build_qwen_pool_group_adjudication_prompt_payload(
            letter,
            model_generated_mentions,
            prompt_profile=prompt_profile,
        ),
        sort_keys=True,
    )


def parse_events_json(
    raw_output: str,
) -> tuple[structured.StructuredExtractionRecord | None, list[str]]:
    return structured.parse_structured_events_json(raw_output)


def parse_generation_selection_json(
    raw_output: str,
) -> tuple[StructuredGenerationSelectionRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            structured._extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    generated_events, generated_notes = _coerce_event_list(
        payload.get("generated_events") or payload.get("clinical_events") or [],
        prefix="generated_events",
    )
    final_events, final_notes = _coerce_event_list(
        payload.get("final_events") or payload.get("clinical_events") or [],
        prefix="final_events",
    )
    notes.extend(generated_notes)
    notes.extend(final_notes)
    try:
        record = StructuredGenerationSelectionRecord.model_validate(
            {
                **payload,
                "generated_events": generated_events,
                "final_events": final_events,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def parse_generation_selection_mentions_json(
    raw_output: str,
) -> tuple[StructuredMentionSelectionRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            structured._extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    generated_mentions, generated_notes = _coerce_mention_list(
        payload.get("generated_mentions") or payload.get("mentions") or [],
        prefix="generated_mentions",
    )
    final_mentions, final_notes = _coerce_mention_list(
        payload.get("final_mentions") or payload.get("mentions") or [],
        prefix="final_mentions",
    )
    notes.extend(generated_notes)
    notes.extend(final_notes)
    try:
        record = StructuredMentionSelectionRecord.model_validate(
            {
                **payload,
                "generated_mentions": generated_mentions,
                "final_mentions": final_mentions,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


_TYPED_ATTRIBUTE_FIELDS = {
    "DrugName",
    "DrugDose",
    "DoseUnit",
    "Frequency",
    "DiagCategory",
    "Certainty",
    "Negation",
    "NumberOfSeizures",
    "LowerNumberOfSeizures",
    "UpperNumberOfSeizures",
    "TimeSince_or_TimeOfEvent",
    "MonthDate",
    "PointInTime",
    "TimePeriod",
    "LowerNumberOfTimePeriods",
    "UpperNumberOfTimePeriods",
    "FrequencyChange",
    "MRI_Performed",
    "MRI_Results",
    "EEG_Performed",
    "EEG_Results",
    "CT_Performed",
    "CT_Results",
}


def parse_generation_selection_typed_mentions_json(
    raw_output: str,
) -> tuple[StructuredMentionSelectionRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            structured._extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    generated_mentions, generated_notes = _coerce_typed_mention_list(
        payload.get("generated_typed_mentions")
        or payload.get("generated_mentions")
        or [],
        prefix="generated_typed_mentions",
    )
    final_mentions, final_notes = _coerce_typed_mention_list(
        payload.get("final_typed_mentions")
        or payload.get("final_mentions")
        or [],
        prefix="final_typed_mentions",
    )
    notes.extend(generated_notes)
    notes.extend(final_notes)
    try:
        record = StructuredMentionSelectionRecord.model_validate(
            {
                **payload,
                "generated_mentions": generated_mentions,
                "final_mentions": final_mentions,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def _coerce_typed_mention_list(
    mentions: Any,
    *,
    prefix: str,
) -> tuple[list[Any], list[str]]:
    if mentions is None:
        return [], []
    if not isinstance(mentions, list):
        return [], [f"{prefix}:schema_validation_error: mentions_not_list"]

    normalized: list[dict[str, Any]] = []
    notes: list[str] = []
    for index, mention in enumerate(mentions):
        if not isinstance(mention, Mapping):
            notes.append(f"{prefix}:dropped_malformed_mention: mention[{index}]")
            continue
        attrs: dict[str, Any] = {}
        raw_attrs = mention.get("attributes") or {}
        if isinstance(raw_attrs, Mapping):
            attrs.update(raw_attrs)
        for field in _TYPED_ATTRIBUTE_FIELDS:
            value = mention.get(field)
            if value is None or value == "":
                continue
            attrs[field] = value
        normalized.append(
            {
                "entity": mention.get("entity"),
                "text": mention.get("text"),
                "attributes": attrs,
                "evidence": mention.get("evidence"),
                "confidence": mention.get("confidence") or "medium",
                "rationale": mention.get("rationale") or "",
            }
        )
    return _coerce_mention_list(normalized, prefix=prefix)


def parse_generation_selection_mention_ids_json(
    raw_output: str,
) -> tuple[StructuredMentionIdSelectionRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            structured._extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    generated_mentions, generated_notes = _coerce_mention_list(
        payload.get("generated_mentions") or payload.get("mentions") or [],
        prefix="generated_mentions",
        require_mention_id=True,
    )
    final_ids, final_id_notes = _coerce_final_mention_ids(payload)
    notes.extend(generated_notes)
    notes.extend(final_id_notes)
    try:
        record = StructuredMentionIdSelectionRecord.model_validate(
            {
                **payload,
                "generated_mentions": generated_mentions,
                "final_mention_ids": final_ids,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def parse_generation_selection_clean_render_ids_json(
    raw_output: str,
) -> tuple[StructuredMentionIdSelectionRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            structured._extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    generated_mentions, generated_notes = _coerce_clean_render_mention_list(
        payload.get("generated_mentions") or payload.get("mentions") or [],
        prefix="generated_mentions",
    )
    final_ids, final_id_notes = _coerce_final_mention_ids(payload)
    notes.extend(generated_notes)
    notes.extend(final_id_notes)
    try:
        record = StructuredMentionIdSelectionRecord.model_validate(
            {
                **payload,
                "generated_mentions": generated_mentions,
                "final_mention_ids": final_ids,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def parse_dedup_clinical_facts_json(
    raw_output: str,
) -> tuple[DedupClinicalFactsRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            structured._extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    facts, fact_notes = _coerce_dedup_clinical_facts(
        payload.get("clinical_facts") or payload.get("facts") or [],
        prefix="clinical_facts",
    )
    notes.extend(fact_notes)
    try:
        record = DedupClinicalFactsRecord.model_validate(
            {**payload, "clinical_facts": facts}
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def parse_qwen_pool_adjudication_json(
    raw_output: str,
) -> tuple[StructuredPoolAdjudicationRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            structured._extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    final_ids, final_id_notes = _coerce_final_mention_ids(payload)
    notes.extend(final_id_notes)
    selection_summary = payload.get("selection_summary") or []
    if not isinstance(selection_summary, list):
        notes.append("selection_summary:schema_validation_error: summary_not_list")
        selection_summary = []
    try:
        record = StructuredPoolAdjudicationRecord.model_validate(
            {
                **payload,
                "final_mention_ids": final_ids,
                "selection_summary": selection_summary,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def parse_qwen_pool_group_adjudication_json(
    raw_output: str,
) -> tuple[StructuredPoolGroupAdjudicationRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            structured._extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    raw_groups = payload.get("fact_groups") or payload.get("groups") or []
    if not isinstance(raw_groups, list):
        raw_groups = []
        notes.append("fact_groups:schema_validation_error: groups_not_list")

    fact_groups: list[dict[str, Any]] = []
    final_ids: list[str] = []
    selection_summary: list[dict[str, Any]] = []
    if not raw_groups:
        alias_ids, alias_notes = _coerce_final_mention_ids(payload)
        notes.extend(alias_notes)
        if alias_ids:
            final_ids.extend(alias_ids)
            notes.append("fact_groups:used_model_emitted_final_mention_ids_alias")
            raw_summary = payload.get("selection_summary") or []
            if isinstance(raw_summary, list):
                selection_summary = [
                    (
                        dict(item)
                        if isinstance(item, Mapping)
                        else {"reason": str(item)}
                    )
                    for item in raw_summary
                ]

    for group_index, raw_group in enumerate(raw_groups):
        if not isinstance(raw_group, Mapping):
            notes.append(f"fact_groups:dropped_malformed_group: group[{group_index}]")
            continue
        group = dict(raw_group)
        decision = str(group.get("decision") or "").strip().lower()
        if decision not in {"include", "exclude"}:
            decision = "exclude"
            notes.append(f"fact_groups:coerced_unknown_decision_to_exclude: group[{group_index}]")
        equivalent_ids, equivalent_notes = _coerce_id_list(
            group.get("equivalent_mention_ids") or group.get("mention_ids") or [],
            prefix=f"fact_groups.group[{group_index}].equivalent_mention_ids",
        )
        notes.extend(equivalent_notes)
        representative_id = str(group.get("representative_mention_id") or "").strip()
        if decision == "include":
            if representative_id:
                final_ids.append(representative_id)
            else:
                notes.append(
                    f"fact_groups:included_group_missing_representative_id: group[{group_index}]"
                )
        group["decision"] = decision
        group["representative_mention_id"] = representative_id
        group["equivalent_mention_ids"] = equivalent_ids
        fact_groups.append(group)
        selection_summary.append(
            {
                "group_id": str(group.get("group_id") or f"group[{group_index}]"),
                "decision": decision,
                "mention_id": representative_id,
                "reason": str(group.get("reason") or ""),
            }
        )

    try:
        record = StructuredPoolGroupAdjudicationRecord.model_validate(
            {
                **payload,
                "fact_groups": fact_groups,
                "final_mention_ids": final_ids,
                "selection_summary": selection_summary,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def load_model_generated_mention_pool(
    jsonl_paths: Sequence[Path],
    *,
    include_event_surfaces: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    """Load raw Qwen-generated mention surfaces from prior llm_only JSONL artifacts."""

    pool_by_letter: dict[str, list[dict[str, Any]]] = {}
    for source_index, path in enumerate(jsonl_paths, start=1):
        source_run = path.stem
        if not path.exists():
            raise FileNotFoundError(path)
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    continue
                letter_id = str(row.get("letter_id") or "").strip()
                if not letter_id:
                    continue
                pool_by_letter.setdefault(letter_id, []).extend(
                    model_generated_mentions_from_row(
                        row,
                        source_run=source_run,
                        source_slot=f"s{source_index}",
                        source_row=line_number,
                        include_event_surfaces=include_event_surfaces,
                    )
                )
    return pool_by_letter


def model_generated_mentions_from_row(
    row: Mapping[str, Any],
    *,
    source_run: str,
    source_slot: str | None = None,
    source_row: int | None = None,
    include_event_surfaces: bool = True,
) -> list[dict[str, Any]]:
    """Extract only Qwen-emitted mention surfaces from one saved route row."""

    mentions: list[dict[str, Any]] = []
    for surface in ("structured_mentions_generation", "structured_mentions_final"):
        raw_mentions = row.get(surface) or []
        if not isinstance(raw_mentions, list):
            continue
        for raw_mention in raw_mentions:
            if not isinstance(raw_mention, Mapping):
                continue
            mentions.append(
                _pool_mention_from_mapping(
                    raw_mention,
                    source_run=source_run,
                    source_slot=source_slot,
                    source_surface=surface,
                    source_row=source_row,
                    pool_index=len(mentions) + 1,
                )
            )

    if include_event_surfaces:
        for surface in ("structured_events_generation", "structured_events_final"):
            raw_events = row.get(surface) or []
            if not isinstance(raw_events, list):
                continue
            try:
                record = structured.StructuredExtractionRecord.model_validate(
                    {"clinical_events": raw_events}
                )
            except Exception:
                continue
            for mention in structured.flatten_events(record):
                mentions.append(
                    _pool_mention_from_mapping(
                        mention.model_dump(),
                        source_run=source_run,
                        source_slot=source_slot,
                        source_surface=surface,
                        source_row=source_row,
                        pool_index=len(mentions) + 1,
                    )
                )
    return mentions


def _pool_mention_from_mapping(
    mention: Mapping[str, Any],
    *,
    source_run: str,
    source_slot: str | None,
    source_surface: str,
    source_row: int | None,
    pool_index: int,
) -> dict[str, Any]:
    source_slug = _safe_id_piece(source_slot or source_run)
    surface_slug = _surface_id_piece(source_surface)
    raw_id = str(mention.get("mention_id") or "").strip()
    mention_id = f"{source_slug}_{surface_slug}_{pool_index}"
    attributes = mention.get("attributes") or {}
    if not isinstance(attributes, Mapping):
        attributes = {}
    return {
        "mention_id": mention_id,
        "source_run": source_run,
        "source_surface": source_surface,
        "source_row": source_row,
        "original_mention_id": raw_id,
        "entity": str(mention.get("entity") or ""),
        "text": str(mention.get("text") or mention.get("source_text") or ""),
        "attributes": {
            str(key): str(value)
            for key, value in attributes.items()
            if value is not None and str(key) not in {"CUI", "CUIPhrase"}
        },
        "evidence": str(mention.get("evidence") or ""),
        "confidence": str(mention.get("confidence") or "medium"),
        "rationale": str(mention.get("rationale") or ""),
    }


def _safe_id_piece(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in value)
    return cleaned.strip("_") or "source"


def _surface_id_piece(value: str) -> str:
    if value == "structured_mentions_generation":
        return "mg"
    if value == "structured_mentions_final":
        return "mf"
    if value == "structured_events_generation":
        return "eg"
    if value == "structured_events_final":
        return "ef"
    return _safe_id_piece(value)


def final_record_from_generation_selection(
    record: StructuredGenerationSelectionRecord,
) -> structured.StructuredExtractionRecord:
    return structured.StructuredExtractionRecord(clinical_events=record.final_events)


def final_mentions_from_generation_selection(
    record: StructuredMentionSelectionRecord,
) -> list[structured.MentionForEvidence]:
    return list(record.final_mentions)


def final_mentions_from_mention_id_selection(
    record: StructuredMentionIdSelectionRecord,
) -> tuple[list[structured.MentionForEvidence], list[str]]:
    by_id: dict[str, dict[str, Any]] = {}
    notes: list[str] = []
    for mention in record.generated_mentions:
        mention_id = str(mention.get("mention_id") or "").strip()
        if not mention_id:
            continue
        if mention_id in by_id:
            notes.append(f"duplicate_generated_mention_id: {mention_id}")
        by_id[mention_id] = mention

    selected: list[structured.MentionForEvidence] = []
    for mention_id in record.final_mention_ids:
        mention = by_id.get(str(mention_id))
        if mention is None:
            notes.append(f"unknown_final_mention_id: {mention_id}")
            continue
        selected.append(structured.MentionForEvidence.model_validate(mention))
    return selected, notes


def _coerce_event_list(events: Any, *, prefix: str) -> tuple[list[Any], list[str]]:
    payload, notes = structured._coerce_structured_payload({"clinical_events": events or []})
    prefixed_notes = [f"{prefix}:{note}" for note in notes]
    if not isinstance(payload, dict) or not isinstance(payload.get("clinical_events"), list):
        return [], [*prefixed_notes, f"{prefix}:schema_validation_error: events_not_list"]
    return list(payload["clinical_events"]), prefixed_notes


def _coerce_mention_list(
    mentions: Any,
    *,
    prefix: str,
    require_mention_id: bool = False,
) -> tuple[list[Any], list[str]]:
    notes: list[str] = []
    if mentions is None:
        return [], notes
    if not isinstance(mentions, list):
        return [], [f"{prefix}:schema_validation_error: mentions_not_list"]

    coerced_mentions: list[Any] = []
    for mention_index, mention in enumerate(mentions):
        if not isinstance(mention, dict):
            notes.append(f"{prefix}:dropped_malformed_mention: mention[{mention_index}]")
            continue
        mention = dict(mention)
        missing = [
            key
            for key in (
                ("mention_id", "entity", "text", "evidence")
                if require_mention_id
                else ("entity", "text", "evidence")
            )
            if not str(mention.get(key) or "").strip()
        ]
        if missing:
            notes.append(
                f"{prefix}:dropped_malformed_mention: "
                f"mention[{mention_index}] missing={','.join(missing)}"
            )
            continue
        mention["attributes"] = structured._stringify_mapping(
            mention.get("attributes") or {},
            notes=notes,
            prefix=f"{prefix}.mention[{mention_index}].attributes",
        )
        if require_mention_id:
            mention["mention_id"] = str(mention["mention_id"])
        coerced_mentions.append(mention)
    return coerced_mentions, notes


def _coerce_clean_render_mention_list(
    mentions: Any,
    *,
    prefix: str,
) -> tuple[list[Any], list[str]]:
    notes: list[str] = []
    if mentions is None:
        return [], notes
    if not isinstance(mentions, list):
        return [], [f"{prefix}:schema_validation_error: mentions_not_list"]

    normalized: list[dict[str, Any]] = []
    for mention_index, mention in enumerate(mentions):
        if not isinstance(mention, Mapping):
            notes.append(f"{prefix}:dropped_malformed_mention: mention[{mention_index}]")
            continue
        clean_text = (
            mention.get("clean_text")
            or mention.get("rendered_text")
            or mention.get("text")
            or ""
        )
        source_text = mention.get("source_text") or ""
        evidence = mention.get("evidence") or source_text
        normalized.append(
            {
                **dict(mention),
                "text": clean_text,
                "evidence": evidence,
            }
        )
        if clean_text and "text" not in mention:
            notes.append(f"{prefix}.mention[{mention_index}].clean_text:used_as_text")
        if evidence and "evidence" not in mention and source_text:
            notes.append(f"{prefix}.mention[{mention_index}].source_text:used_as_evidence")
    coerced, coerced_notes = _coerce_mention_list(
        normalized,
        prefix=prefix,
        require_mention_id=True,
    )
    return coerced, [*notes, *coerced_notes]


_DEDUP_FACT_FAMILIES = {
    "diagnosis",
    "seizure_frequency",
    "prescription",
    "investigation",
}


def _coerce_dedup_clinical_facts(
    facts: Any,
    *,
    prefix: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    notes: list[str] = []
    if facts is None:
        return [], notes
    if not isinstance(facts, list):
        return [], [f"{prefix}:schema_validation_error: facts_not_list"]

    coerced: list[dict[str, Any]] = []
    for fact_index, fact in enumerate(facts):
        if not isinstance(fact, Mapping):
            notes.append(f"{prefix}:dropped_malformed_fact: fact[{fact_index}]")
            continue
        normalized = {
            str(key): "" if value is None else str(value).strip()
            for key, value in fact.items()
        }
        family = _normalize_fact_family(normalized.get("family", ""))
        if family not in _DEDUP_FACT_FAMILIES:
            notes.append(
                f"{prefix}:dropped_malformed_fact: fact[{fact_index}] "
                f"family={normalized.get('family')!r}"
            )
            continue
        normalized["family"] = family
        if not normalized.get("evidence"):
            notes.append(
                f"{prefix}:dropped_malformed_fact: fact[{fact_index}] missing=evidence"
            )
            continue
        coerced.append(normalized)
    return coerced, notes


def _coerce_final_mention_ids(payload: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    raw_ids = (
        payload.get("final_mention_ids")
        or payload.get("selected_mention_ids")
        or payload.get("final_ids")
        or []
    )
    notes: list[str] = []
    if isinstance(raw_ids, str):
        raw_ids = [raw_ids]
        notes.append("coerced_final_mention_ids_string_to_list")
    if not isinstance(raw_ids, list):
        return [], ["final_mention_ids:schema_validation_error: ids_not_list"]
    final_ids: list[str] = []
    for index, raw_id in enumerate(raw_ids):
        if raw_id is None:
            continue
        mention_id = str(raw_id).strip()
        if not mention_id:
            notes.append(f"final_mention_ids:dropped_blank_id: index[{index}]")
            continue
        final_ids.append(mention_id)
    return final_ids, notes


def _coerce_id_list(ids: Any, *, prefix: str) -> tuple[list[str], list[str]]:
    notes: list[str] = []
    if isinstance(ids, str):
        ids = [ids]
        notes.append(f"{prefix}:coerced_string_to_list")
    if not isinstance(ids, list):
        return [], [f"{prefix}:schema_validation_error: ids_not_list"]
    coerced: list[str] = []
    for index, raw_id in enumerate(ids):
        if raw_id is None:
            continue
        mention_id = str(raw_id).strip()
        if not mention_id:
            notes.append(f"{prefix}:dropped_blank_id: index[{index}]")
            continue
        coerced.append(mention_id)
    return coerced, notes


def clinical_facts_to_mentions(
    facts: Sequence[DedupClinicalFactRecord | Mapping[str, Any]],
) -> tuple[list[structured.MentionForEvidence], list[dict[str, Any]], list[str]]:
    """Map model-emitted simplified facts to scorer-facing mentions one-to-one."""

    mentions: list[structured.MentionForEvidence] = []
    provenance: list[dict[str, Any]] = []
    notes: list[str] = []
    for index, raw_fact in enumerate(facts):
        fact = (
            raw_fact
            if isinstance(raw_fact, DedupClinicalFactRecord)
            else DedupClinicalFactRecord.model_validate(raw_fact)
        )
        mention = _clinical_fact_to_mention(fact, index=index, notes=notes)
        if mention is None:
            continue
        mentions.append(mention)
        provenance.append(
            {
                "fact_index": index,
                "family": fact.family,
                "action": "representation_mapping_only",
                "target_entity": mention.entity,
                "added_fact": False,
                "deduplicated_by_adapter": False,
            }
        )
    return mentions, provenance, notes


def _clinical_fact_to_mention(
    fact: DedupClinicalFactRecord,
    *,
    index: int,
    notes: list[str],
) -> structured.MentionForEvidence | None:
    family = _normalize_fact_family(fact.family)
    evidence = fact.evidence.strip()
    confidence: Literal["low", "medium", "high"] = "medium"
    if fact.attributes:
        entity_by_family = {
            "diagnosis": "Diagnosis",
            "seizure_frequency": "SeizureFrequency",
            "prescription": "Prescription",
            "investigation": "Investigations",
        }
        text_by_family = {
            "diagnosis": fact.source_text.strip() or fact.concept.strip(),
            "seizure_frequency": fact.source_text.strip()
            or fact.seizure_type.strip()
            or "seizures",
            "prescription": fact.source_text.strip() or fact.drug.strip(),
            "investigation": fact.source_text.strip() or _normalize_modality(fact.modality) or "",
        }
        entity = entity_by_family.get(family)
        text = text_by_family.get(family, "")
        if entity and text:
            return structured.MentionForEvidence(
                entity=entity,
                text=text,
                attributes=dict(fact.attributes),
                evidence=evidence,
                confidence=confidence,
                rationale="mapped from replayed model-emitted de-duplicated fact",
            )
    if family == "diagnosis":
        text = fact.concept.strip()
        if not text:
            notes.append(f"clinical_facts.fact[{index}]:missing_diagnosis_concept")
            return None
        negation = _normalize_negation(fact.negation)
        return structured.MentionForEvidence(
            entity="Diagnosis",
            text=text,
            attributes={"Negation": negation},
            evidence=evidence,
            confidence=confidence,
            rationale="mapped from model-emitted de-duplicated diagnosis fact",
        )
    if family == "seizure_frequency":
        text = fact.seizure_type.strip() or "seizures"
        attrs = _seizure_state_attributes(fact.state, notes=notes, index=index)
        return structured.MentionForEvidence(
            entity="SeizureFrequency",
            text=text,
            attributes=attrs,
            evidence=evidence,
            confidence=confidence,
            rationale="mapped from model-emitted de-duplicated seizure-frequency fact",
        )
    if family == "prescription":
        drug = fact.drug.strip()
        if not drug:
            notes.append(f"clinical_facts.fact[{index}]:missing_prescription_drug")
            return None
        attrs = {"DrugName": drug}
        if fact.dose.strip():
            attrs["DrugDose"] = fact.dose.strip()
        if fact.dose_unit.strip():
            attrs["DoseUnit"] = _normalize_dose_unit(fact.dose_unit)
        if fact.frequency.strip():
            attrs["Frequency"] = _normalize_frequency(fact.frequency)
        return structured.MentionForEvidence(
            entity="Prescription",
            text=fact.source_text.strip() or drug,
            attributes=attrs,
            evidence=evidence,
            confidence=confidence,
            rationale="mapped from model-emitted de-duplicated prescription fact",
        )
    if family == "investigation":
        modality = _normalize_modality(fact.modality)
        if modality is None:
            notes.append(f"clinical_facts.fact[{index}]:unsupported_modality={fact.modality!r}")
            return None
        attrs = {
            f"{modality}_Performed": _normalize_performed(fact.performed),
            f"{modality}_Results": _normalize_result(fact.result),
        }
        return structured.MentionForEvidence(
            entity="Investigations",
            text=modality,
            attributes=attrs,
            evidence=evidence,
            confidence=confidence,
            rationale="mapped from model-emitted de-duplicated investigation fact",
        )
    notes.append(f"clinical_facts.fact[{index}]:unsupported_family={fact.family!r}")
    return None


def _normalize_fact_family(value: str) -> str:
    family = value.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "medication": "prescription",
        "medications": "prescription",
        "rx": "prescription",
        "investigations": "investigation",
        "seizurefrequency": "seizure_frequency",
        "seizure_frequency_state": "seizure_frequency",
    }
    return aliases.get(family, family)


def _normalize_negation(value: str) -> str:
    negation = value.strip().lower()
    if negation in {"negated", "negative", "denied", "absent", "no"}:
        return "Negated"
    return "Affirmed"


def _seizure_state_attributes(
    state: str,
    *,
    notes: list[str],
    index: int,
) -> dict[str, str]:
    normalized = state.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in {"active", "active_rate", "ongoing", "rate"}:
        return {"NumberOfSeizures": "1"}
    if normalized in {"seizure_free", "free", "none", "zero"}:
        return {"NumberOfSeizures": "0"}
    if normalized in {"changed", "change", "increased", "decreased", "worse", "improved"}:
        change = "Increased" if normalized in {"increased", "worse"} else "Same"
        return {"FrequencyChange": change}
    if normalized in {"unknown", ""}:
        return {}
    notes.append(
        f"clinical_facts.fact[{index}]:unknown_seizure_state={state!r}_mapped_unknown"
    )
    return {}


def _normalize_dose_unit(value: str) -> str:
    unit = value.strip().lower()
    if unit in {"g", "gram", "grams"}:
        return "g"
    return "mg"


def _normalize_frequency(value: str) -> str:
    frequency = value.strip().lower()
    aliases = {
        "once": "1",
        "once daily": "1",
        "od": "1",
        "mane": "1",
        "nocte": "1",
        "twice": "2",
        "twice daily": "2",
        "bd": "2",
        "bid": "2",
        "three times daily": "3",
        "tds": "3",
        "tid": "3",
        "as required": "As_Required",
        "prn": "As_Required",
    }
    return aliases.get(frequency, value.strip())


def _normalize_modality(value: str) -> str | None:
    modality = value.strip().lower()
    if modality in {"mri", "mri scan", "brain mri"}:
        return "MRI"
    if modality in {"ct", "ct scan"}:
        return "CT"
    if modality in {"eeg", "standard eeg", "sleep deprived eeg", "sleep-deprived eeg"}:
        return "EEG"
    if modality in {"telemetry", "video telemetry", "videotelemetry"}:
        return "EEG"
    return None


def _normalize_performed(value: str) -> str:
    performed = value.strip().lower()
    if performed in {"no", "n", "false", "not performed"}:
        return "No"
    return "Yes"


def _normalize_result(value: str) -> str:
    result = value.strip().lower()
    if result in {"normal", "negative"}:
        return "Normal"
    if result in {"abnormal", "positive", "abnormality"}:
        return "Abnormal"
    return "Unknown"


def clinical_facts_from_mentions(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Build simplified facts from saved model-emitted mention rows for replay checks."""

    facts: list[dict[str, Any]] = []
    notes: list[str] = []
    for index, mention in enumerate(mentions):
        entity = str(mention.get("entity") or "")
        attrs = mention.get("attributes") or {}
        if not isinstance(attrs, Mapping):
            attrs = {}
        evidence = str(mention.get("evidence") or "")
        text = str(mention.get("text") or "")
        if entity == "Diagnosis":
            facts.append(
                {
                    "family": "diagnosis",
                    "concept": text,
                    "negation": str(attrs.get("Negation") or "Affirmed").lower(),
                    "attributes": {str(key): str(value) for key, value in attrs.items()},
                    "source_text": text,
                    "evidence": evidence or text,
                }
            )
        elif entity == "SeizureFrequency":
            facts.append(
                {
                    "family": "seizure_frequency",
                    "seizure_type": text or "seizures",
                    "state": _fact_state_from_seizure_attrs(attrs),
                    "attributes": {str(key): str(value) for key, value in attrs.items()},
                    "source_text": text,
                    "evidence": evidence or text,
                }
            )
        elif entity == "Prescription":
            facts.append(
                {
                    "family": "prescription",
                    "drug": str(attrs.get("DrugName") or text),
                    "dose": str(attrs.get("DrugDose") or ""),
                    "dose_unit": str(attrs.get("DoseUnit") or ""),
                    "frequency": str(attrs.get("Frequency") or ""),
                    "source_text": text,
                    "attributes": {str(key): str(value) for key, value in attrs.items()},
                    "evidence": evidence or text,
                }
            )
        elif entity == "Investigations":
            fact = _investigation_fact_from_attrs(attrs, text=text, evidence=evidence)
            if fact:
                facts.append(fact)
            else:
                notes.append(f"mention[{index}]:investigation_without_supported_modality")
        else:
            notes.append(f"mention[{index}]:out_of_scope_entity={entity!r}")
    return facts, notes


def _fact_state_from_seizure_attrs(attrs: Mapping[str, Any]) -> str:
    count_values = [
        str(attrs.get("NumberOfSeizures") or ""),
        str(attrs.get("LowerNumberOfSeizures") or ""),
        str(attrs.get("UpperNumberOfSeizures") or ""),
    ]
    if any(value == "0" for value in count_values):
        return "seizure_free"
    if any(value for value in count_values):
        return "active_rate"
    if attrs.get("FrequencyChange"):
        return "changed"
    return "unknown"


def _investigation_fact_from_attrs(
    attrs: Mapping[str, Any],
    *,
    text: str,
    evidence: str,
) -> dict[str, Any] | None:
    text_upper = text.upper()
    for modality in ("MRI", "CT", "EEG"):
        performed = str(attrs.get(f"{modality}_Performed") or "")
        result = str(attrs.get(f"{modality}_Results") or "")
        if performed or result or modality in text_upper.split():
            return {
                "family": "investigation",
                "modality": modality,
                "performed": performed.lower() or "yes",
                "result": result.lower() or "unknown",
                "attributes": {str(key): str(value) for key, value in attrs.items()},
                "source_text": text,
                "evidence": evidence or text,
            }
    return None


def replay_dedup_facts_from_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    source_key: str = "predicted_mentions",
    split: str = "dev",
    model: str = "no-call-replay",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Replay saved model mention rows through the simplified fact adapter."""

    component_owner = component_owner_for_model(model)
    replay_rows: list[dict[str, Any]] = []
    for row in rows:
        facts, fact_notes = clinical_facts_from_mentions(row.get(source_key) or [])
        mentions, provenance, adapter_notes = clinical_facts_to_mentions(facts)
        letter = ExectLetter(
            letter_id=str(row.get("letter_id") or ""),
            note_text=" ".join(
                str(mention.get("evidence") or "")
                for mention in row.get(source_key) or []
                if isinstance(mention, Mapping)
            ),
            annotations=tuple(),
        )
        replay_row = row_from_final_dedup_facts(
            letter,
            DedupClinicalFactsRecord.model_validate({"clinical_facts": facts}),
            split=split,
            model=model,
            mode="replay",
            raw_generation_output="",
            generation_parse_errors=[],
        )
        replay_row["gold_mentions"] = list(row.get("gold_mentions") or [])
        replay_row["adapter_provenance"] = provenance
        replay_row["adapter_parse_errors"] = [*fact_notes, *adapter_notes]
        replay_row["structured_mentions_final"] = [
            mention.model_dump() for mention in mentions
        ]
        replay_rows.append(replay_row)
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": "replay",
        "call_strategy": "single_call_dedup_facts",
        "pipeline_family": PIPELINE_FAMILY,
        "component_owner": component_owner,
        "fact_origin": FACT_ORIGIN,
        "model": model,
        "mode": "replay",
        "split": split,
        "n_letters": len(replay_rows),
        "summary": summarize_rows(replay_rows),
    }
    return replay_rows, metadata


def to_predicted_letter(
    letter: ExectLetter,
    final_record: structured.StructuredExtractionRecord | Mapping[str, Any],
    *,
    component_owner: str = COMPONENT_OWNER,
) -> tuple[PredictedLetter, list[str]]:
    record = _coerce_record(final_record)
    return structured.to_predicted_letter(
        letter.letter_id,
        structured.flatten_events(record),
        note_text=letter.note_text,
        prompt_version=PROMPT_VERSION,
        component_owner=component_owner,
        pipeline_family=PIPELINE_FAMILY,
    )


def to_predicted_letter_from_mentions(
    letter: ExectLetter,
    final_mentions: Sequence[structured.MentionForEvidence | Mapping[str, Any]],
    *,
    component_owner: str = COMPONENT_OWNER,
) -> tuple[PredictedLetter, list[str]]:
    mentions = _coerce_mentions(final_mentions)
    return structured.to_predicted_letter(
        letter.letter_id,
        mentions,
        note_text=letter.note_text,
        prompt_version=PROMPT_VERSION,
        component_owner=component_owner,
        pipeline_family=PIPELINE_FAMILY,
    )


def to_predicted_letter_from_dedup_facts(
    letter: ExectLetter,
    record: DedupClinicalFactsRecord | Mapping[str, Any],
    *,
    component_owner: str = COMPONENT_OWNER,
) -> tuple[PredictedLetter, list[str], list[dict[str, Any]], list[str]]:
    fact_record = (
        record
        if isinstance(record, DedupClinicalFactsRecord)
        else DedupClinicalFactsRecord.model_validate(record)
    )
    mentions, provenance, adapter_notes = clinical_facts_to_mentions(
        fact_record.clinical_facts
    )
    predicted, gate_warnings = to_predicted_letter_from_mentions(
        letter,
        mentions,
        component_owner=component_owner,
    )
    return predicted, gate_warnings, provenance, adapter_notes


def row_from_final_record(
    letter: ExectLetter,
    final_record: structured.StructuredExtractionRecord | Mapping[str, Any],
    *,
    split: str,
    model: str,
    mode: str,
    raw_generation_output: str = "",
    raw_selection_output: str = "",
    generation_parse_errors: Sequence[str] = (),
    selection_parse_errors: Sequence[str] = (),
) -> dict[str, Any]:
    """Project final model-selected events to the benchmark row format."""

    record = _coerce_record(final_record)
    component_owner = component_owner_for_model(model)
    predicted_letter, gate_warnings = to_predicted_letter(
        letter,
        record,
        component_owner=component_owner,
    )
    mentions_raw = structured.flatten_events(record)
    return {
        "letter_id": letter.letter_id,
        "split": split,
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "component_owner": component_owner,
        "fact_origin": FACT_ORIGIN,
        "model": model,
        "mode": mode,
        "raw_generation_output": raw_generation_output,
        "raw_selection_output": raw_selection_output,
        "generation_parse_errors": list(generation_parse_errors),
        "selection_parse_errors": list(selection_parse_errors),
        "gate_warnings": gate_warnings,
        "n_events_final": len(record.clinical_events),
        "n_mentions_raw": len(mentions_raw),
        "n_mentions_scored": len(predicted_letter.mentions),
        "n_evidence_invalid": len(mentions_raw) - len(predicted_letter.mentions),
        "structured_events_final": [
            event.model_dump() for event in record.clinical_events
        ],
        "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
        "gold_mentions": [
            {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
            for a in letter.annotations
            if a.entity in structured.KEY_ENTITY_NAMES
        ],
    }


def row_from_final_dedup_facts(
    letter: ExectLetter,
    record: DedupClinicalFactsRecord | Mapping[str, Any],
    *,
    split: str,
    model: str,
    mode: str,
    raw_generation_output: str = "",
    generation_parse_errors: Sequence[str] = (),
) -> dict[str, Any]:
    """Project model-selected de-duplicated facts to the benchmark row format."""

    fact_record = (
        record
        if isinstance(record, DedupClinicalFactsRecord)
        else DedupClinicalFactsRecord.model_validate(record)
    )
    mentions, provenance, adapter_notes = clinical_facts_to_mentions(
        fact_record.clinical_facts
    )
    component_owner = component_owner_for_model(model)
    predicted_letter, gate_warnings = to_predicted_letter_from_mentions(
        letter,
        mentions,
        component_owner=component_owner,
    )
    return {
        "letter_id": letter.letter_id,
        "split": split,
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "component_owner": component_owner,
        "fact_origin": FACT_ORIGIN,
        "model": model,
        "mode": mode,
        "raw_generation_output": raw_generation_output,
        "raw_selection_output": raw_generation_output,
        "generation_parse_errors": list(generation_parse_errors),
        "selection_parse_errors": list(generation_parse_errors),
        "adapter_parse_errors": adapter_notes,
        "gate_warnings": [*adapter_notes, *gate_warnings],
        "n_events_final": 0,
        "n_mentions_raw": len(mentions),
        "n_mentions_scored": len(predicted_letter.mentions),
        "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
        "n_clinical_facts_final": len(fact_record.clinical_facts),
        "clinical_facts_final": [fact.model_dump() for fact in fact_record.clinical_facts],
        "adapter_provenance": provenance,
        "structured_events_final": [],
        "structured_mentions_final": [mention.model_dump() for mention in mentions],
        "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
        "gold_mentions": [
            {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
            for a in letter.annotations
            if a.entity in structured.KEY_ENTITY_NAMES
        ],
    }


def row_from_final_mentions(
    letter: ExectLetter,
    final_mentions: Sequence[structured.MentionForEvidence | Mapping[str, Any]],
    *,
    split: str,
    model: str,
    mode: str,
    raw_generation_output: str = "",
    raw_selection_output: str = "",
    generation_parse_errors: Sequence[str] = (),
    selection_parse_errors: Sequence[str] = (),
) -> dict[str, Any]:
    """Project final model-selected direct mentions to the benchmark row format."""

    mentions = _coerce_mentions(final_mentions)
    component_owner = component_owner_for_model(model)
    predicted_letter, gate_warnings = to_predicted_letter_from_mentions(
        letter,
        mentions,
        component_owner=component_owner,
    )
    return {
        "letter_id": letter.letter_id,
        "split": split,
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "component_owner": component_owner,
        "fact_origin": FACT_ORIGIN,
        "model": model,
        "mode": mode,
        "raw_generation_output": raw_generation_output,
        "raw_selection_output": raw_selection_output,
        "generation_parse_errors": list(generation_parse_errors),
        "selection_parse_errors": list(selection_parse_errors),
        "gate_warnings": gate_warnings,
        "n_events_final": 0,
        "n_mentions_raw": len(mentions),
        "n_mentions_scored": len(predicted_letter.mentions),
        "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
        "structured_events_final": [],
        "structured_mentions_final": [mention.model_dump() for mention in mentions],
        "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
        "gold_mentions": [
            {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
            for a in letter.annotations
            if a.entity in structured.KEY_ENTITY_NAMES
        ],
    }


def run_split(
    letters: Sequence[ExectLetter],
    *,
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
    prompt_profile: PromptProfile = "compact",
    call_strategy: CallStrategy = "two_stage",
    pool_mentions_by_letter: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    programs = StrategyPrograms(
        two_stage=QwenGenerationSelectionExtractor(),
        inventory=QwenSingleCallInventoryExtractor(),
        mention=QwenSingleCallMentionExtractor(),
        mention_id=QwenSingleCallMentionIdExtractor(),
        dedup_facts=QwenSingleCallDedupFactsExtractor(),
        pool=QwenPoolAdjudicationExtractor(),
    )
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
            )
        )

    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None,
        key="letter_id",
    )
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    strategy_handler = STRATEGY_REGISTRY[call_strategy]

    for letter in todo:
        outcome = strategy_handler(
            StrategyContext(
                letter=letter,
                mode=mode,
                prompt_profile=prompt_profile,
                programs=programs,
                split=split,
                model=model,
                pool_mentions_by_letter=pool_mentions_by_letter,
            )
        )
        row = outcome.row
        generation_prompt_input_json = outcome.generation_prompt_input_json
        selection_prompt_input_json = outcome.selection_prompt_input_json
        generation_call_error = outcome.generation_call_error
        selection_call_error = outcome.selection_call_error
        generation_parse_errors = outcome.generation_parse_errors
        selection_parse_errors = outcome.selection_parse_errors
        first_pass_record = outcome.first_pass_record
        final_record = outcome.final_record
        inventory_details = outcome.inventory_details
        row.update(
            {
                "prompt_profile": prompt_profile,
                "call_strategy": call_strategy,
                "generation_prompt_input_json": generation_prompt_input_json,
                "selection_prompt_input_json": selection_prompt_input_json,
                "generation_call_error": generation_call_error,
                "selection_call_error": selection_call_error,
                "call_error": generation_call_error or selection_call_error,
                "parse_errors": [
                    f"generation:{error}" for error in generation_parse_errors
                ]
                + [f"selection:{error}" for error in selection_parse_errors],
                "n_events_generation": len(first_pass_record.clinical_events),
                "n_events_raw": len(final_record.clinical_events),
                "structured_events_generation": [
                    event.model_dump() for event in first_pass_record.clinical_events
                ],
                **inventory_details,
            }
        )
        rows.append(row)

        if progress_every and (len(rows) - n_resumed) % progress_every == 0:
            _emit_checkpoint(
                rows,
                total=len(letters),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
                split=split,
                model=model,
                mode=mode,
                prompt_profile=prompt_profile,
                call_strategy=call_strategy,
            )

    rows = merge_rows(rows, order, key="letter_id")
    component_owner = component_owner_for_model(model)
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "prompt_profile": prompt_profile,
        "call_strategy": call_strategy,
        "pipeline_family": PIPELINE_FAMILY,
        "component_owner": component_owner,
        "fact_origin": FACT_ORIGIN,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_letters": len(letters),
        "n_resumed": n_resumed,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }
    if pool_mentions_by_letter is not None:
        metadata["pool_letters"] = len(pool_mentions_by_letter)
        metadata["pool_mentions_total"] = sum(
            len(mentions) for mentions in pool_mentions_by_letter.values()
        )
    metadata["summary"] = summarize_rows(rows)
    return rows, metadata


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    summary = structured.summarize_rows(rows)
    summary["generation_parse_failures"] = sum(
        _has_parse_or_schema_error(r.get("generation_parse_errors")) for r in rows
    )
    summary["selection_parse_failures"] = sum(
        _has_parse_or_schema_error(r.get("selection_parse_errors")) for r in rows
    )
    summary["generation_call_failures"] = sum(
        bool(r.get("generation_call_error")) for r in rows
    )
    summary["selection_call_failures"] = sum(
        bool(r.get("selection_call_error")) for r in rows
    )
    summary["inventory_parse_failures"] = sum(
        _has_parse_or_schema_error(r.get("inventory_parse_errors")) for r in rows
    )
    summary["inventory_call_failures"] = sum(bool(r.get("inventory_call_error")) for r in rows)
    summary["fact_origin"] = {FACT_ORIGIN: sum(int(r.get("n_mentions_scored", 0)) for r in rows)}
    summary["protocol_surfaces"] = {
        "model_preserving_canonical": summary.get("scores", {})
        .get("benchmark", {})
        .get("per_item", {}),
        "hybrid_full_stack": None,
    }
    return summary


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: dict[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_rows(rows)
    is_checkpoint = bool(metadata.get("is_checkpoint"))
    total_letters = int(metadata.get("total_letters") or metadata.get("n_letters") or 0)
    lines = [
        f"# ExECTv2 {report_model_label(str(metadata.get('model') or ''))} "
        "LLM-Only Generation-Selection",
        "",
    ]
    if is_checkpoint:
        processed = summary.get("examples", len(rows))
        total = total_letters or processed
        lines.extend([f"CHECKPOINT ONLY: processed {processed} / {total} letters", ""])
    n_generation_events = sum(int(r.get("n_events_generation", 0)) for r in rows)
    lines.extend(
        [
            f"- JSONL: `{jsonl_path}`",
            f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
            f"- Prompt profile: `{metadata.get('prompt_profile', 'compact')}`",
            f"- Call strategy: `{metadata.get('call_strategy', 'two_stage')}`",
            f"- Pipeline family: `{metadata.get('pipeline_family', PIPELINE_FAMILY)}`",
            f"- Component owner: `{metadata.get('component_owner', COMPONENT_OWNER)}`",
            f"- Fact origin: `{metadata.get('fact_origin', FACT_ORIGIN)}`",
            f"- Split: `{metadata.get('split')}`",
            f"- Model: `{metadata.get('model')}`",
            f"- Mode: `{metadata.get('mode')}`",
            f"- Letters: {summary.get('examples', 0)}",
            f"- Pool letters: {metadata.get('pool_letters', 'not-used')}",
            f"- Pool mentions total: {metadata.get('pool_mentions_total', 'not-used')}",
            "",
            "## Model-Call And Gate Summary",
            "",
            f"- Generation call failures: {summary.get('generation_call_failures', 0)}",
            f"- Selection call failures: {summary.get('selection_call_failures', 0)}",
            f"- Inventory call failures: {summary.get('inventory_call_failures', 0)}",
            f"- Generation parse/schema failures: {summary.get('generation_parse_failures', 0)}",
            f"- Selection parse/schema failures: {summary.get('selection_parse_failures', 0)}",
            f"- Inventory parse/schema failures: {summary.get('inventory_parse_failures', 0)}",
            f"- Clinical events generation: {n_generation_events}",
            f"- Clinical events final: {summary.get('n_events_raw', 0)}",
            f"- Mentions raw final: {summary.get('n_mentions_raw', 0)}",
            f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
            f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
            f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0.0):.4f}",
            "",
            "## Protocol Surfaces",
            "",
            "| Surface | P | R | F1 | TP | FP | FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    canonical = summary.get("protocol_surfaces", {}).get("model_preserving_canonical", {})
    lines.append(
        "| model_preserving_canonical | "
        f"{canonical.get('precision', 0):.3f} | "
        f"{canonical.get('recall', 0):.3f} | "
        f"{canonical.get('f1', 0):.3f} | "
        f"{canonical.get('tp', 0)} | "
        f"{canonical.get('fp', 0)} | "
        f"{canonical.get('fn', 0)} |"
    )
    lines.append("| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |")
    lines.extend(["", "## Overall Scores", ""])
    for config_name in ("benchmark", "semantic", "phrase_only"):
        lines.extend(
            structured._score_lines(
                config_name,
                summary.get("scores", {}).get(config_name, {}),
            )
        )
    lines.extend(structured._clinical_recovery_lines(summary.get("clinical_recovery", {})))
    lines.extend(structured._diagnostic_ladder_lines(summary.get("diagnostic_ladder", {})))
    path.write_text("\n".join(lines), encoding="utf-8")


def _run_two_stage_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenGenerationSelectionExtractor,
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    generation_prompt_input_json = build_generation_prompt_input(
        letter,
        prompt_profile=prompt_profile,
    )
    raw_generation_output = ""
    generation_call_error: str | None = None
    if mode == "live":
        try:
            generation_prediction = program(generation_prompt_input_json)
            raw_generation_output = str(generation_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            generation_call_error = f"{type(exc).__name__}: {exc}"

    generation_record, generation_parse_errors = (
        parse_events_json(raw_generation_output)
        if raw_generation_output
        else (None, ["not_run"])
    )
    first_pass_record = generation_record or structured.StructuredExtractionRecord()

    selection_prompt_input_json = build_selection_prompt_input(
        letter,
        first_pass_record,
        prompt_profile=prompt_profile,
    )
    raw_selection_output = ""
    selection_call_error: str | None = None
    if mode == "live":
        try:
            selection_prediction = program(selection_prompt_input_json)
            raw_selection_output = str(selection_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            selection_call_error = f"{type(exc).__name__}: {exc}"

    final_record, selection_parse_errors = (
        parse_events_json(raw_selection_output)
        if raw_selection_output
        else (None, ["not_run"])
    )
    return (
        generation_prompt_input_json,
        selection_prompt_input_json,
        raw_generation_output,
        raw_selection_output,
        generation_call_error,
        selection_call_error,
        generation_parse_errors,
        selection_parse_errors,
        first_pass_record,
        final_record or structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": "",
            "raw_inventory_output": "",
            "inventory_call_error": None,
            "inventory_parse_errors": [],
            "inventory_selection_summary": [],
        },
    )


def _run_qwen_pool_adjudication_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenPoolAdjudicationExtractor,
    model_generated_mentions: Sequence[Mapping[str, Any]],
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    pool_mentions, pool_notes = _coerce_mention_list(
        list(model_generated_mentions),
        prefix="model_generated_mentions",
        require_mention_id=True,
    )
    pool_prompt_input_json = build_qwen_pool_adjudication_prompt_input(
        letter,
        pool_mentions,
        prompt_profile=prompt_profile,
    )
    raw_selection_output = ""
    selection_call_error: str | None = None
    if mode == "live":
        try:
            selection_prediction = program(pool_prompt_input_json)
            raw_selection_output = str(selection_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            selection_call_error = f"{type(exc).__name__}: {exc}"

    selection_record, selection_parse_errors = (
        parse_qwen_pool_adjudication_json(raw_selection_output)
        if raw_selection_output
        else (None, ["not_run"])
    )
    selection_record = selection_record or StructuredPoolAdjudicationRecord()
    final_mentions, selection_notes = final_mentions_from_mention_id_selection(
        StructuredMentionIdSelectionRecord(
            generated_mentions=pool_mentions,
            final_mention_ids=selection_record.final_mention_ids,
            selection_summary=selection_record.selection_summary,
        )
    )
    all_selection_notes = [*pool_notes, *selection_parse_errors, *selection_notes]
    return (
        "",
        pool_prompt_input_json,
        "",
        raw_selection_output,
        None,
        selection_call_error,
        [],
        all_selection_notes,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": pool_prompt_input_json,
            "raw_inventory_output": raw_selection_output,
            "inventory_call_error": selection_call_error,
            "inventory_parse_errors": all_selection_notes,
            "inventory_selection_summary": selection_record.selection_summary,
            "structured_mentions_generation": pool_mentions,
            "structured_mentions_final": [
                mention.model_dump() for mention in final_mentions
            ],
            "final_mention_ids": list(selection_record.final_mention_ids),
            "n_mentions_generation": len(pool_mentions),
            "pool_size": len(pool_mentions),
        },
    )


def _run_qwen_pool_entity_adjudication_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenPoolAdjudicationExtractor,
    model_generated_mentions: Sequence[Mapping[str, Any]],
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    pool_mentions, pool_notes = _coerce_mention_list(
        list(model_generated_mentions),
        prefix="model_generated_mentions",
        require_mention_id=True,
    )
    prompts_by_entity: dict[str, dict[str, Any]] = {}
    raw_outputs_by_entity: dict[str, str] = {}
    final_ids_by_entity: dict[str, list[str]] = {}
    selection_summary_by_entity: dict[str, list[dict[str, Any]]] = {}
    entity_pool_sizes: dict[str, int] = {}
    selection_call_errors: list[str] = []
    selection_parse_errors: list[str] = list(pool_notes)

    for target_entity in structured.KEY_ENTITY_NAMES:
        entity_mentions = [
            mention
            for mention in pool_mentions
            if str(mention.get("entity") or "") == target_entity
        ]
        entity_pool_sizes[target_entity] = len(entity_mentions)
        if not entity_mentions:
            prompts_by_entity[target_entity] = {}
            raw_outputs_by_entity[target_entity] = ""
            final_ids_by_entity[target_entity] = []
            selection_summary_by_entity[target_entity] = []
            continue

        prompt_input_json = build_qwen_pool_entity_adjudication_prompt_input(
            letter,
            entity_mentions,
            target_entity=target_entity,
            prompt_profile=prompt_profile,
        )
        prompts_by_entity[target_entity] = json.loads(prompt_input_json)
        raw_entity_output = ""
        if mode == "live":
            try:
                entity_prediction = program(prompt_input_json)
                raw_entity_output = str(entity_prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                selection_call_errors.append(
                    f"{target_entity}:{type(exc).__name__}: {exc}"
                )
        raw_outputs_by_entity[target_entity] = raw_entity_output

        entity_record, entity_errors = (
            parse_qwen_pool_adjudication_json(raw_entity_output)
            if raw_entity_output
            else (None, [])
        )
        entity_record = entity_record or StructuredPoolAdjudicationRecord()
        final_ids_by_entity[target_entity] = list(entity_record.final_mention_ids)
        selection_summary_by_entity[target_entity] = list(
            entity_record.selection_summary
        )
        selection_parse_errors.extend(
            f"{target_entity}:{error}" for error in entity_errors
        )

    final_ids = [
        mention_id
        for target_entity in structured.KEY_ENTITY_NAMES
        for mention_id in final_ids_by_entity.get(target_entity, [])
    ]
    final_mentions, selection_notes = final_mentions_from_mention_id_selection(
        StructuredMentionIdSelectionRecord(
            generated_mentions=pool_mentions,
            final_mention_ids=final_ids,
            selection_summary=[
                summary
                for target_entity in structured.KEY_ENTITY_NAMES
                for summary in selection_summary_by_entity.get(target_entity, [])
            ],
        )
    )
    all_selection_notes = [*selection_parse_errors, *selection_notes]
    prompt_bundle = {
        "stage": "qwen_pool_entity_adjudication",
        "entity_prompt_inputs": prompts_by_entity,
    }
    raw_output_bundle = {
        "stage": "qwen_pool_entity_adjudication",
        "entity_raw_outputs": raw_outputs_by_entity,
    }
    selection_call_error = "; ".join(selection_call_errors) or None
    return (
        "",
        json.dumps(prompt_bundle, sort_keys=True),
        "",
        json.dumps(raw_output_bundle, sort_keys=True),
        None,
        selection_call_error,
        [],
        all_selection_notes,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": json.dumps(prompt_bundle, sort_keys=True),
            "raw_inventory_output": json.dumps(raw_output_bundle, sort_keys=True),
            "inventory_call_error": selection_call_error,
            "inventory_parse_errors": all_selection_notes,
            "inventory_selection_summary": selection_summary_by_entity,
            "structured_mentions_generation": pool_mentions,
            "structured_mentions_final": [
                mention.model_dump() for mention in final_mentions
            ],
            "final_mention_ids": final_ids,
            "final_mention_ids_by_entity": final_ids_by_entity,
            "entity_pool_sizes": entity_pool_sizes,
            "n_mentions_generation": len(pool_mentions),
            "pool_size": len(pool_mentions),
        },
    )


def _run_qwen_pool_group_adjudication_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenPoolAdjudicationExtractor,
    model_generated_mentions: Sequence[Mapping[str, Any]],
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    pool_mentions, pool_notes = _coerce_mention_list(
        list(model_generated_mentions),
        prefix="model_generated_mentions",
        require_mention_id=True,
    )
    group_prompt_input_json = build_qwen_pool_group_adjudication_prompt_input(
        letter,
        pool_mentions,
        prompt_profile=prompt_profile,
    )
    raw_group_output = ""
    group_call_error: str | None = None
    if mode == "live":
        try:
            group_prediction = program(group_prompt_input_json)
            raw_group_output = str(group_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            group_call_error = f"{type(exc).__name__}: {exc}"

    group_record, group_parse_errors = (
        parse_qwen_pool_group_adjudication_json(raw_group_output)
        if raw_group_output
        else (None, ["not_run"])
    )
    group_record = group_record or StructuredPoolGroupAdjudicationRecord()
    final_mentions, selection_notes = final_mentions_from_mention_id_selection(
        StructuredMentionIdSelectionRecord(
            generated_mentions=pool_mentions,
            final_mention_ids=group_record.final_mention_ids,
            selection_summary=group_record.selection_summary,
        )
    )
    all_parse_errors = [*pool_notes, *group_parse_errors, *selection_notes]
    return (
        "",
        group_prompt_input_json,
        "",
        raw_group_output,
        None,
        group_call_error,
        [],
        all_parse_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": group_prompt_input_json,
            "raw_inventory_output": raw_group_output,
            "inventory_call_error": group_call_error,
            "inventory_parse_errors": all_parse_errors,
            "inventory_selection_summary": group_record.selection_summary,
            "structured_mentions_generation": pool_mentions,
            "structured_mentions_final": [
                mention.model_dump() for mention in final_mentions
            ],
            "final_mention_ids": list(group_record.final_mention_ids),
            "fact_groups": list(group_record.fact_groups),
            "n_fact_groups": len(group_record.fact_groups),
            "n_mentions_generation": len(pool_mentions),
            "pool_size": len(pool_mentions),
        },
    )


def _run_single_call_dedup_facts_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenSingleCallDedupFactsExtractor,
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    prompt_input_json = build_single_call_dedup_facts_prompt_input(
        letter,
        prompt_profile=prompt_profile,
    )
    raw_output = ""
    call_error: str | None = None
    if mode == "live":
        try:
            prediction = program(prompt_input_json)
            raw_output = str(prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            call_error = f"{type(exc).__name__}: {exc}"

    fact_record, parse_errors = (
        parse_dedup_clinical_facts_json(raw_output)
        if raw_output
        else (None, ["not_run"])
    )
    fact_record = fact_record or DedupClinicalFactsRecord()
    mentions, provenance, adapter_notes = clinical_facts_to_mentions(
        fact_record.clinical_facts
    )
    all_errors = [*parse_errors, *adapter_notes]
    return (
        prompt_input_json,
        "",
        raw_output,
        raw_output,
        call_error,
        call_error,
        all_errors,
        all_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": prompt_input_json,
            "raw_inventory_output": raw_output,
            "inventory_call_error": call_error,
            "inventory_parse_errors": all_errors,
            "inventory_selection_summary": [],
            "clinical_facts_final": [fact.model_dump() for fact in fact_record.clinical_facts],
            "adapter_provenance": provenance,
            "structured_mentions_generation": [mention.model_dump() for mention in mentions],
            "structured_mentions_final": [mention.model_dump() for mention in mentions],
            "n_mentions_generation": len(mentions),
            "n_clinical_facts_final": len(fact_record.clinical_facts),
            "dedup_adapter_added_facts": 0,
            "dedup_adapter_deduplicated_facts": 0,
        },
    )


def _run_single_call_dedup_facts_per_family_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenSingleCallDedupFactsExtractor,
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    prompt_by_family: dict[str, str] = {}
    raw_by_family: dict[str, str] = {}
    call_error_by_family: dict[str, str] = {}
    parse_errors: list[str] = []
    facts: list[dict[str, Any]] = []

    for family in DEDUP_FACT_FAMILIES:
        family_prompt_profile = _dedup_fact_prompt_profile_for_family(
            prompt_profile,
            family,
        )
        prompt_input_json = build_single_call_dedup_facts_prompt_input(
            letter,
            prompt_profile=family_prompt_profile,
            target_family=family,
        )
        prompt_by_family[family] = prompt_input_json
        raw_output = ""
        call_error: str | None = None
        if mode == "live":
            try:
                prediction = program(prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"

        raw_by_family[family] = raw_output
        if call_error:
            call_error_by_family[family] = call_error

        fact_record, family_parse_errors = (
            parse_dedup_clinical_facts_json(raw_output)
            if raw_output
            else (None, ["not_run"])
        )
        parse_errors.extend(f"{family}:{error}" for error in family_parse_errors)
        for fact in (fact_record or DedupClinicalFactsRecord()).clinical_facts:
            facts.append(fact.model_dump())

    combined_record = DedupClinicalFactsRecord.model_validate({"clinical_facts": facts})
    mentions, provenance, adapter_notes = clinical_facts_to_mentions(
        combined_record.clinical_facts
    )
    all_errors = [*parse_errors, *adapter_notes]
    prompt_bundle = json.dumps(prompt_by_family, sort_keys=True)
    raw_bundle = json.dumps(raw_by_family, sort_keys=True)
    combined_call_error = (
        json.dumps(call_error_by_family, sort_keys=True) if call_error_by_family else None
    )
    return (
        prompt_bundle,
        "",
        raw_bundle,
        raw_bundle,
        combined_call_error,
        combined_call_error,
        all_errors,
        all_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": prompt_bundle,
            "raw_inventory_output": raw_bundle,
            "inventory_call_error": combined_call_error,
            "inventory_parse_errors": all_errors,
            "inventory_selection_summary": [],
            "clinical_facts_final": [fact.model_dump() for fact in combined_record.clinical_facts],
            "adapter_provenance": provenance,
            "structured_mentions_generation": [mention.model_dump() for mention in mentions],
            "structured_mentions_final": [mention.model_dump() for mention in mentions],
            "dedup_fact_prompt_inputs_by_family": prompt_by_family,
            "dedup_fact_raw_outputs_by_family": raw_by_family,
            "dedup_fact_call_errors_by_family": call_error_by_family,
            "n_mentions_generation": len(mentions),
            "n_clinical_facts_final": len(combined_record.clinical_facts),
            "dedup_adapter_added_facts": 0,
            "dedup_adapter_deduplicated_facts": 0,
        },
    )


def _dedup_fact_prompt_profile_for_family(
    prompt_profile: PromptProfile,
    family: DedupFactFamily,
) -> PromptProfile:
    if prompt_profile == "decision_table_sf_inv":
        return "decision_table" if family in DECISION_TABLE_FAMILIES else "compact"
    return prompt_profile


def _run_single_call_inventory_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenSingleCallInventoryExtractor,
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    inventory_prompt_input_json = build_single_call_inventory_prompt_input(
        letter,
        prompt_profile=prompt_profile,
    )
    raw_inventory_output = ""
    inventory_call_error: str | None = None
    if mode == "live":
        try:
            inventory_prediction = program(inventory_prompt_input_json)
            raw_inventory_output = str(inventory_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            inventory_call_error = f"{type(exc).__name__}: {exc}"

    inventory_record, inventory_parse_errors = (
        parse_generation_selection_json(raw_inventory_output)
        if raw_inventory_output
        else (None, ["not_run"])
    )
    inventory_record = inventory_record or StructuredGenerationSelectionRecord()
    first_pass_record = structured.StructuredExtractionRecord(
        clinical_events=inventory_record.generated_events
    )
    final_record = final_record_from_generation_selection(inventory_record)
    return (
        inventory_prompt_input_json,
        "",
        raw_inventory_output,
        raw_inventory_output,
        inventory_call_error,
        inventory_call_error,
        inventory_parse_errors,
        inventory_parse_errors,
        first_pass_record,
        final_record,
        {
            "inventory_prompt_input_json": inventory_prompt_input_json,
            "raw_inventory_output": raw_inventory_output,
            "inventory_call_error": inventory_call_error,
            "inventory_parse_errors": inventory_parse_errors,
            "inventory_selection_summary": inventory_record.selection_summary,
        },
    )


def _run_single_call_mentions_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenSingleCallMentionExtractor,
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    mention_prompt_input_json = build_single_call_mentions_prompt_input(
        letter,
        prompt_profile=prompt_profile,
    )
    raw_mention_output = ""
    mention_call_error: str | None = None
    if mode == "live":
        try:
            mention_prediction = program(mention_prompt_input_json)
            raw_mention_output = str(mention_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            mention_call_error = f"{type(exc).__name__}: {exc}"

    mention_record, mention_parse_errors = (
        parse_generation_selection_mentions_json(raw_mention_output)
        if raw_mention_output
        else (None, ["not_run"])
    )
    mention_record = mention_record or StructuredMentionSelectionRecord()
    final_mentions = final_mentions_from_generation_selection(mention_record)
    return (
        mention_prompt_input_json,
        "",
        raw_mention_output,
        raw_mention_output,
        mention_call_error,
        mention_call_error,
        mention_parse_errors,
        mention_parse_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": mention_prompt_input_json,
            "raw_inventory_output": raw_mention_output,
            "inventory_call_error": mention_call_error,
            "inventory_parse_errors": mention_parse_errors,
            "inventory_selection_summary": mention_record.selection_summary,
            "structured_mentions_generation": [
                mention.model_dump() for mention in mention_record.generated_mentions
            ],
            "structured_mentions_final": [
                mention.model_dump() for mention in final_mentions
            ],
            "n_mentions_generation": len(mention_record.generated_mentions),
        },
    )


def _run_single_call_per_entity_mentions_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenSingleCallMentionExtractor,
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    prompt_inputs_by_entity: dict[str, dict[str, Any]] = {}
    raw_outputs_by_entity: dict[str, str] = {}
    parse_errors: list[str] = []
    call_errors: list[str] = []
    generated_mentions: list[dict[str, Any]] = []
    final_mentions: list[dict[str, Any]] = []
    selection_summary_by_entity: dict[str, list[dict[str, Any]]] = {}

    for target_entity in structured.KEY_ENTITY_NAMES:
        prompt_input_json = build_single_call_per_entity_mentions_prompt_input(
            letter,
            target_entity=target_entity,
            prompt_profile=prompt_profile,
        )
        prompt_inputs_by_entity[target_entity] = json.loads(prompt_input_json)
        raw_entity_output = ""
        if mode == "live":
            try:
                entity_prediction = program(prompt_input_json)
                raw_entity_output = str(entity_prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_errors.append(f"{target_entity}:{type(exc).__name__}: {exc}")
        raw_outputs_by_entity[target_entity] = raw_entity_output

        mention_record, entity_parse_errors = (
            parse_generation_selection_mentions_json(raw_entity_output)
            if raw_entity_output
            else (None, [])
        )
        mention_record = mention_record or StructuredMentionSelectionRecord()
        generated_mentions.extend(
            mention.model_dump() for mention in mention_record.generated_mentions
        )
        final_mentions.extend(
            mention.model_dump() for mention in mention_record.final_mentions
        )
        selection_summary_by_entity[target_entity] = list(
            mention_record.selection_summary
        )
        parse_errors.extend(f"{target_entity}:{error}" for error in entity_parse_errors)

    prompt_bundle = {
        "stage": "single_call_per_entity_mention_selection",
        "entity_prompt_inputs": prompt_inputs_by_entity,
    }
    raw_output_bundle = {
        "stage": "single_call_per_entity_mention_selection",
        "entity_raw_outputs": raw_outputs_by_entity,
    }
    call_error = "; ".join(call_errors) or None
    return (
        json.dumps(prompt_bundle, sort_keys=True),
        "",
        json.dumps(raw_output_bundle, sort_keys=True),
        json.dumps(raw_output_bundle, sort_keys=True),
        call_error,
        call_error,
        parse_errors,
        parse_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": json.dumps(prompt_bundle, sort_keys=True),
            "raw_inventory_output": json.dumps(raw_output_bundle, sort_keys=True),
            "inventory_call_error": call_error,
            "inventory_parse_errors": parse_errors,
            "inventory_selection_summary": selection_summary_by_entity,
            "structured_mentions_generation": generated_mentions,
            "structured_mentions_final": final_mentions,
            "n_mentions_generation": len(generated_mentions),
            "n_entity_calls": len(structured.KEY_ENTITY_NAMES),
        },
    )


def _run_single_call_typed_mentions_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenSingleCallMentionExtractor,
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    typed_prompt_input_json = build_single_call_typed_mentions_prompt_input(
        letter,
        prompt_profile=prompt_profile,
    )
    raw_typed_output = ""
    typed_call_error: str | None = None
    if mode == "live":
        try:
            typed_prediction = program(typed_prompt_input_json)
            raw_typed_output = str(typed_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            typed_call_error = f"{type(exc).__name__}: {exc}"

    typed_record, typed_parse_errors = (
        parse_generation_selection_typed_mentions_json(raw_typed_output)
        if raw_typed_output
        else (None, ["not_run"])
    )
    typed_record = typed_record or StructuredMentionSelectionRecord()
    return (
        typed_prompt_input_json,
        "",
        raw_typed_output,
        raw_typed_output,
        typed_call_error,
        typed_call_error,
        typed_parse_errors,
        typed_parse_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": typed_prompt_input_json,
            "raw_inventory_output": raw_typed_output,
            "inventory_call_error": typed_call_error,
            "inventory_parse_errors": typed_parse_errors,
            "inventory_selection_summary": typed_record.selection_summary,
            "structured_mentions_generation": [
                mention.model_dump() for mention in typed_record.generated_mentions
            ],
            "structured_mentions_final": [
                mention.model_dump() for mention in typed_record.final_mentions
            ],
            "n_mentions_generation": len(typed_record.generated_mentions),
        },
    )


def _run_single_call_mention_ids_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenSingleCallMentionIdExtractor,
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    mention_prompt_input_json = build_single_call_mention_ids_prompt_input(
        letter,
        prompt_profile=prompt_profile,
    )
    raw_mention_output = ""
    mention_call_error: str | None = None
    if mode == "live":
        try:
            mention_prediction = program(mention_prompt_input_json)
            raw_mention_output = str(mention_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            mention_call_error = f"{type(exc).__name__}: {exc}"

    mention_record, mention_parse_errors = (
        parse_generation_selection_mention_ids_json(raw_mention_output)
        if raw_mention_output
        else (None, ["not_run"])
    )
    mention_record = mention_record or StructuredMentionIdSelectionRecord()
    final_mentions, selection_notes = final_mentions_from_mention_id_selection(
        mention_record
    )
    all_parse_errors = [*mention_parse_errors, *selection_notes]
    return (
        mention_prompt_input_json,
        "",
        raw_mention_output,
        raw_mention_output,
        mention_call_error,
        mention_call_error,
        all_parse_errors,
        all_parse_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": mention_prompt_input_json,
            "raw_inventory_output": raw_mention_output,
            "inventory_call_error": mention_call_error,
            "inventory_parse_errors": all_parse_errors,
            "inventory_selection_summary": mention_record.selection_summary,
            "structured_mentions_generation": mention_record.generated_mentions,
            "structured_mentions_final": [
                mention.model_dump() for mention in final_mentions
            ],
            "final_mention_ids": list(mention_record.final_mention_ids),
            "n_mentions_generation": len(mention_record.generated_mentions),
        },
    )


def _run_single_call_render_ids_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenSingleCallMentionIdExtractor,
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    mention_prompt_input_json = build_single_call_render_ids_prompt_input(
        letter,
        prompt_profile=prompt_profile,
    )
    raw_mention_output = ""
    mention_call_error: str | None = None
    if mode == "live":
        try:
            mention_prediction = program(mention_prompt_input_json)
            raw_mention_output = str(mention_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            mention_call_error = f"{type(exc).__name__}: {exc}"

    mention_record, mention_parse_errors = (
        parse_generation_selection_mention_ids_json(raw_mention_output)
        if raw_mention_output
        else (None, ["not_run"])
    )
    mention_record = mention_record or StructuredMentionIdSelectionRecord()
    final_mentions, selection_notes = final_mentions_from_mention_id_selection(
        mention_record
    )
    all_parse_errors = [*mention_parse_errors, *selection_notes]
    return (
        mention_prompt_input_json,
        "",
        raw_mention_output,
        raw_mention_output,
        mention_call_error,
        mention_call_error,
        all_parse_errors,
        all_parse_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": mention_prompt_input_json,
            "raw_inventory_output": raw_mention_output,
            "inventory_call_error": mention_call_error,
            "inventory_parse_errors": all_parse_errors,
            "inventory_selection_summary": mention_record.selection_summary,
            "structured_mentions_generation": mention_record.generated_mentions,
            "structured_mentions_final": [
                mention.model_dump() for mention in final_mentions
            ],
            "final_mention_ids": list(mention_record.final_mention_ids),
            "n_mentions_generation": len(mention_record.generated_mentions),
        },
    )


def _run_single_call_clean_render_ids_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenSingleCallMentionIdExtractor,
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    mention_prompt_input_json = build_single_call_clean_render_ids_prompt_input(
        letter,
        prompt_profile=prompt_profile,
    )
    raw_mention_output = ""
    mention_call_error: str | None = None
    if mode == "live":
        try:
            mention_prediction = program(mention_prompt_input_json)
            raw_mention_output = str(mention_prediction.extraction_json)
        except Exception as exc:  # pragma: no cover
            mention_call_error = f"{type(exc).__name__}: {exc}"

    mention_record, mention_parse_errors = (
        parse_generation_selection_clean_render_ids_json(raw_mention_output)
        if raw_mention_output
        else (None, ["not_run"])
    )
    mention_record = mention_record or StructuredMentionIdSelectionRecord()
    final_mentions, selection_notes = final_mentions_from_mention_id_selection(
        mention_record
    )
    all_parse_errors = [*mention_parse_errors, *selection_notes]
    return (
        mention_prompt_input_json,
        "",
        raw_mention_output,
        raw_mention_output,
        mention_call_error,
        mention_call_error,
        all_parse_errors,
        all_parse_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": mention_prompt_input_json,
            "raw_inventory_output": raw_mention_output,
            "inventory_call_error": mention_call_error,
            "inventory_parse_errors": all_parse_errors,
            "inventory_selection_summary": mention_record.selection_summary,
            "structured_mentions_generation": mention_record.generated_mentions,
            "structured_mentions_final": [
                mention.model_dump() for mention in final_mentions
            ],
            "final_mention_ids": list(mention_record.final_mention_ids),
            "n_mentions_generation": len(mention_record.generated_mentions),
        },
    )


def _run_single_call_per_entity_clean_render_ids_letter(
    letter: ExectLetter,
    *,
    mode: Literal["live", "prompt-only"],
    prompt_profile: PromptProfile,
    program: QwenSingleCallMentionIdExtractor,
) -> tuple[
    str,
    str,
    str,
    str,
    str | None,
    str | None,
    list[str],
    list[str],
    structured.StructuredExtractionRecord,
    structured.StructuredExtractionRecord,
    dict[str, Any],
]:
    prompt_inputs_by_entity: dict[str, dict[str, Any]] = {}
    raw_outputs_by_entity: dict[str, str] = {}
    parse_errors: list[str] = []
    call_errors: list[str] = []
    generated_mentions: list[dict[str, Any]] = []
    final_mentions: list[dict[str, Any]] = []
    final_ids_by_entity: dict[str, list[str]] = {}
    selection_summary_by_entity: dict[str, list[dict[str, Any]]] = {}

    for target_entity in structured.KEY_ENTITY_NAMES:
        prompt_input_json = build_single_call_per_entity_clean_render_ids_prompt_input(
            letter,
            target_entity=target_entity,
            prompt_profile=prompt_profile,
        )
        prompt_inputs_by_entity[target_entity] = json.loads(prompt_input_json)
        raw_entity_output = ""
        if mode == "live":
            try:
                entity_prediction = program(prompt_input_json)
                raw_entity_output = str(entity_prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_errors.append(f"{target_entity}:{type(exc).__name__}: {exc}")
        raw_outputs_by_entity[target_entity] = raw_entity_output

        mention_record, entity_parse_errors = (
            parse_generation_selection_clean_render_ids_json(raw_entity_output)
            if raw_entity_output
            else (None, [])
        )
        mention_record = mention_record or StructuredMentionIdSelectionRecord()
        entity_final_mentions, selection_notes = final_mentions_from_mention_id_selection(
            mention_record
        )
        generated_mentions.extend(
            dict(mention) for mention in mention_record.generated_mentions
        )
        final_mentions.extend(mention.model_dump() for mention in entity_final_mentions)
        final_ids_by_entity[target_entity] = list(mention_record.final_mention_ids)
        selection_summary_by_entity[target_entity] = list(
            mention_record.selection_summary
        )
        parse_errors.extend(f"{target_entity}:{error}" for error in entity_parse_errors)
        parse_errors.extend(f"{target_entity}:{error}" for error in selection_notes)

    prompt_bundle = {
        "stage": "single_call_per_entity_clean_render_id_selection",
        "entity_prompt_inputs": prompt_inputs_by_entity,
    }
    raw_output_bundle = {
        "stage": "single_call_per_entity_clean_render_id_selection",
        "entity_raw_outputs": raw_outputs_by_entity,
    }
    call_error = "; ".join(call_errors) or None
    return (
        json.dumps(prompt_bundle, sort_keys=True),
        "",
        json.dumps(raw_output_bundle, sort_keys=True),
        json.dumps(raw_output_bundle, sort_keys=True),
        call_error,
        call_error,
        parse_errors,
        parse_errors,
        structured.StructuredExtractionRecord(),
        structured.StructuredExtractionRecord(),
        {
            "inventory_prompt_input_json": json.dumps(prompt_bundle, sort_keys=True),
            "raw_inventory_output": json.dumps(raw_output_bundle, sort_keys=True),
            "inventory_call_error": call_error,
            "inventory_parse_errors": parse_errors,
            "inventory_selection_summary": selection_summary_by_entity,
            "structured_mentions_generation": generated_mentions,
            "structured_mentions_final": final_mentions,
            "final_mention_ids_by_entity": final_ids_by_entity,
            "n_mentions_generation": len(generated_mentions),
            "n_entity_calls": len(structured.KEY_ENTITY_NAMES),
        },
    )


def _coerce_record(
    record: structured.StructuredExtractionRecord | Mapping[str, Any],
) -> structured.StructuredExtractionRecord:
    if isinstance(record, structured.StructuredExtractionRecord):
        return record
    return structured.StructuredExtractionRecord.model_validate(record)


def _coerce_mentions(
    mentions: Sequence[structured.MentionForEvidence | Mapping[str, Any]],
) -> list[structured.MentionForEvidence]:
    return [
        mention
        if isinstance(mention, structured.MentionForEvidence)
        else structured.MentionForEvidence.model_validate(mention)
        for mention in mentions
    ]


def _mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
        "component_owner": mention.component_owner,
    }


def _emit_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
    prompt_profile: PromptProfile,
    call_strategy: CallStrategy,
) -> None:
    if jsonl_path:
        write_jsonl(rows, jsonl_path)
    if report_path:
        write_report(
            rows,
            {
                "prompt_version": PROMPT_VERSION,
                "prompt_profile": prompt_profile,
                "call_strategy": call_strategy,
                "pipeline_family": PIPELINE_FAMILY,
                "component_owner": component_owner_for_model(model),
                "fact_origin": FACT_ORIGIN,
                "split": split,
                "model": model,
                "mode": mode,
                "summary": summarize_rows(rows),
                "is_checkpoint": True,
                "total_letters": total,
            },
            _checkpoint_report_path(report_path),
            jsonl_path=jsonl_path or Path(""),
        )


def _checkpoint_report_path(path: Path) -> Path:
    if path.stem.endswith("_checkpoint"):
        return path
    return path.with_name(f"{path.stem}_checkpoint{path.suffix}")


def _has_parse_or_schema_error(errors: Any) -> bool:
    return any(
        str(error).startswith(("invalid_json:", "schema_validation_error:"))
        for error in (errors or [])
    )


def _clinical_rules() -> list[str]:
    return [
        (
            "Scan the whole letter for current anti-seizure medication, diagnoses, "
            "seizure-frequency states, and completed investigations."
        ),
        (
            "Use exact substrings for evidence; source-near evidence is required "
            "for every final mention."
        ),
        (
            "Render mention text as the clinical concept; put dose, count, date, "
            "result, and certainty details in attributes."
        ),
        (
            "For SeizureFrequency, mention text should be the seizure type or "
            "state anchor, such as focal seizures or secondary generalised "
            "seizures, not the count phrase."
        ),
        (
            "For dated seizure counts such as in March, use MonthDate plus "
            "TimeSince_or_TimeOfEvent='During'; do not convert a dated count "
            "into a per-month rate unless the letter says per month."
        ),
        (
            "MonthDate must be numeric, e.g. January='1' and March='3'. "
            "Do not use PointInTime='Last_Month' or NumberOfTimePeriods for a "
            "named calendar month. Do not add TimePeriod for a named calendar "
            "month unless the note says per month."
        ),
        (
            "A SeizureFrequency mention must include count, date, interval, "
            "seizure-free, or change-state attributes directly in "
            "mention.attributes."
        ),
        (
            "Separate patient-level epilepsy diagnoses from named seizure-type "
            "diagnoses when both are stated."
        ),
        (
            "When a Diagnosis heading says focal epilepsy-probable temporal, "
            "emit both focal epilepsy and temporal lobe epilepsy; probable "
            "temporal is not a standalone mention."
        ),
        (
            "Do not de-duplicate repeated source-supported facts across different "
            "source events. If the same diagnosis or seizure-frequency state is "
            "explicitly represented in both a diagnosis/list section and a "
            "seizure-frequency statement, emit a rendered mention for each "
            "source event."
        ),
        (
            "Final mentions may repeat the same entity, text, and attributes when "
            "different evidence clauses support separate rendered mentions. Keep "
            "the repeated mentions instead of merging them."
        ),
        (
            "For generic epilepsy headings such as epilepsy-unclassified, render "
            "the core Diagnosis text as epilepsy unless a more specific epilepsy "
            "syndrome is explicitly stated."
        ),
        (
            "Named seizure types such as focal seizures, absence seizures, and "
            "secondary generalised seizures use Diagnosis DiagCategory "
            "MultipleSeizures."
        ),
        (
            "When a source sentence gives a frequency for a named plural seizure "
            "type, emit both a Diagnosis mention for that seizure type and a "
            "SeizureFrequency mention for the same source sentence."
        ),
        (
            "For count ranges such as 2 to 3, several, or between 4 and 6, do "
            "not put the range phrase in NumberOfSeizures. Use "
            "LowerNumberOfSeizures and UpperNumberOfSeizures."
        ),
        (
            "Do not render planned investigations or future medication changes "
            "as completed/current facts."
        ),
        (
            "Retain prior completed MRI, CT, EEG, VEEG, video EEG, or telemetry "
            "mentions when the letter states a result. Words such as previous, "
            "prior, old, or 2012 do not make a completed result future or planned."
        ),
        (
            "For Investigations mention text, include the modality plus test word "
            "as the source span when present, such as MRI scan, CT head, EEG, "
            "video EEG, VEEG, or telemetry."
        ),
        (
            "Do not emit not-performed Investigation facts for planned, repeat, "
            "awaiting, or future tests; omit those tests instead."
        ),
        "Never emit a SeizureFrequency mention with empty state attributes.",
    ]


def _mention_attribute_contract() -> dict[str, list[str]]:
    return {
        "Prescription": [
            "DrugName, DrugDose, DoseUnit, and Frequency belong in mention.attributes.",
            "Do not place medication scoring fields only in event_state.",
        ],
        "Diagnosis": [
            "DiagCategory, Certainty, and Negation belong in mention.attributes.",
            "Named seizure types should use DiagCategory='MultipleSeizures'.",
        ],
        "SeizureFrequency": [
            (
                "NumberOfSeizures, LowerNumberOfSeizures, UpperNumberOfSeizures, "
                "NumberOfTimePeriods, TimePeriod, MonthDate, YearDate, "
                "TimeSince_or_TimeOfEvent, PointInTime, and FrequencyChange "
                "belong in mention.attributes."
            ),
            (
                "Do not put diagnosis attributes such as DiagCategory on "
                "SeizureFrequency mentions."
            ),
        ],
        "Investigations": [
            (
                "MRI_Performed, MRI_Results, EEG_Performed, EEG_Results, "
                "CT_Performed, and CT_Results belong in mention.attributes."
            ),
            "Do not emit planned, repeat, awaiting, or future investigation requests.",
        ],
    }


def _render_text_policy() -> list[str]:
    return [
        (
            "Use source_text for the short exact source span that names the fact; "
            "use text for the final rendered mention text."
        ),
        (
            "The text field may be a compact normalized clinical render and does "
            "not need to be an exact source substring. The evidence field must "
            "still be an exact source substring."
        ),
        (
            "For Diagnosis, use one named concept per mention: epilepsy, focal "
            "epilepsy, temporal lobe epilepsy, genetic generalised epilepsy, "
            "epilepsy with generalised tonic clonic seizures alone, focal-onset "
            "epilepsy, focal seizures, secondary generalised seizures, or "
            "generalised tonic clonic seizures when supported."
        ),
        (
            "Do not combine multiple Diagnosis concepts into one text value. "
            "Split compound diagnosis headings into separate generated_mentions."
        ),
        (
            "For singular seizure events, use singular text and "
            "DiagCategory='SingleSeizure'. For plural seizure types, use plural "
            "text and DiagCategory='MultipleSeizures'."
        ),
        (
            "For Prescription text, include the medication name plus dose and "
            "frequency. If the source line starts with Current medication or "
            "Current antiepileptic medication, source_text may include that label "
            "when it is part of the medication statement."
        ),
        (
            "For Investigations text, include modality plus visible year or result "
            "words when present, such as MRI 2012 normal, MRI scan, EEG 2015 "
            "normal, EEG abnormal, CT head normal, or video EEG."
        ),
        (
            "For SeizureFrequency text, use the seizure type or state anchor, "
            "such as seizures, focal seizures, absence-like seizures, "
            "generalised tonic clonic seizures, or seizure-free."
        ),
    ]


def _clean_render_text_policy() -> list[str]:
    return [
        (
            "source_text must be copied from the letter. clean_text should be a "
            "compact clinical label for the same fact, not a full sentence."
        ),
        (
            "For Prescription clean_text, copy the medication phrase from the "
            "letter as closely as possible, preserving abbreviations such as BD, "
            "mane, nocte, OD, PRN, and source spelling of the dose/frequency. "
            "Keep DrugName as the generic medication name in attributes."
        ),
        (
            "For Diagnosis clean_text, emit one concept per mention. Split "
            "compound headings into separate rows such as epilepsy, focal "
            "epilepsy, temporal lobe epilepsy, focal seizures, or generalised "
            "tonic clonic seizures when each is supported."
        ),
        (
            "For named seizure types, emit a Diagnosis row for every source "
            "statement that names the seizure type. If a frequency sentence "
            "names focal seizures or secondary generalised seizures, emit both "
            "the Diagnosis row and the SeizureFrequency row from that sentence, "
            "even if the same seizure type was named earlier."
        ),
        (
            "For SeizureFrequency clean_text, name the seizure type or state, "
            "such as seizures, focal seizures, secondary generalised seizures, "
            "generalised tonic clonic seizures, or seizure-free. Put counts, "
            "dates, intervals, and changes in attributes."
        ),
        (
            "For Investigations clean_text, prefer the compact test phrase "
            "that names the modality, such as MRI scan, MRI, EEG, CT head, "
            "video EEG, VEEG, or telemetry. Put normal/abnormal result state "
            "in attributes rather than lengthening clean_text unless the source "
            "phrase itself is only a result phrase such as EEG abnormal."
        ),
        (
            "When the same clinical fact is explicitly stated in separate source "
            "events, emit separate generated rows with separate mention_id values."
        ),
    ]


def _forbidden_attribute_combinations() -> list[dict[str, str]]:
    return [
        {
            "entity": "SeizureFrequency",
            "when": "MonthDate is present because the letter names a calendar month",
            "forbid": "NumberOfTimePeriods, TimePeriod, and PointInTime",
            "reason": (
                "A calendar month is a date anchor, not a rate denominator or "
                "relative point-in-time."
            ),
        },
        {
            "entity": "Investigations",
            "when": "the test is planned, requested, repeat, awaiting, or future",
            "forbid": "MRI_Performed, EEG_Performed, CT_Performed, and result attributes",
            "reason": "Future tests are omitted from final_events.",
        },
    ]


def _dedup_fact_worked_examples(
    prompt_profile: PromptProfile,
    *,
    target_family: DedupFactFamily | None = None,
) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = [
        {
            "note_fragment": (
                "She has focal epilepsy. No seizures since last review. "
                "Current treatment is lamotrigine 200 mg twice daily. "
                "MRI brain was normal."
            ),
            "clinical_facts": [
                {
                    "family": "diagnosis",
                    "concept": "focal epilepsy",
                    "negation": "affirmed",
                    "evidence": "She has focal epilepsy.",
                },
                {
                    "family": "seizure_frequency",
                    "seizure_type": "seizures",
                    "state": "seizure_free",
                    "evidence": "No seizures since last review.",
                },
                {
                    "family": "prescription",
                    "drug": "lamotrigine",
                    "dose": "200",
                    "dose_unit": "mg",
                    "frequency": "2",
                    "evidence": "Current treatment is lamotrigine 200 mg twice daily.",
                },
                {
                    "family": "investigation",
                    "modality": "MRI",
                    "result": "normal",
                    "evidence": "MRI brain was normal.",
                },
            ],
        },
        {
            "note_fragment": (
                "She has no absences now. EEG has shown temporal slowing. "
                "Repeat MRI has been requested."
            ),
            "clinical_facts": [
                {
                    "family": "diagnosis",
                    "concept": "absences",
                    "negation": "negated",
                    "evidence": "She has no absences now.",
                },
                {
                    "family": "investigation",
                    "modality": "EEG",
                    "result": "abnormal",
                    "evidence": "EEG has shown temporal slowing.",
                },
            ],
            "omission_note": "The requested repeat MRI is future/planned, so it is omitted.",
        },
        {
            "note_fragment": (
                "Diagnosis: focal epilepsy-Probable temporal. Since review she "
                "has had four secondary generalised seizures."
            ),
            "clinical_facts": [
                {
                    "family": "diagnosis",
                    "concept": "focal epilepsy",
                    "negation": "affirmed",
                    "evidence": "Diagnosis: focal epilepsy-Probable temporal.",
                },
                {
                    "family": "diagnosis",
                    "concept": "temporal lobe epilepsy",
                    "negation": "affirmed",
                    "evidence": "Diagnosis: focal epilepsy-Probable temporal.",
                },
                {
                    "family": "diagnosis",
                    "concept": "secondary generalised seizures",
                    "negation": "affirmed",
                    "evidence": "Since review she has had four secondary generalised seizures.",
                },
                {
                    "family": "seizure_frequency",
                    "seizure_type": "secondary generalised seizures",
                    "state": "active_rate",
                    "evidence": "Since review she has had four secondary generalised seizures.",
                },
            ],
        },
        {
            "note_fragment": (
                "Diagnosis: genetic generalised epilepsy-epilepsy with generalised "
                "tonic chronic seizures alone. Previous MRI in 2012 was normal. "
                "I am arranging a repeat EEG."
            ),
            "clinical_facts": [
                {
                    "family": "diagnosis",
                    "concept": "genetic generalised epilepsy",
                    "negation": "affirmed",
                    "evidence": (
                        "Diagnosis: genetic generalised epilepsy-epilepsy with "
                        "generalised tonic chronic seizures alone."
                    ),
                },
                {
                    "family": "diagnosis",
                    "concept": "epilepsy with generalised tonic clonic seizures alone",
                    "negation": "affirmed",
                    "evidence": (
                        "Diagnosis: genetic generalised epilepsy-epilepsy with "
                        "generalised tonic chronic seizures alone."
                    ),
                },
                {
                    "family": "diagnosis",
                    "concept": "generalised tonic clonic seizures",
                    "negation": "affirmed",
                    "evidence": (
                        "Diagnosis: genetic generalised epilepsy-epilepsy with "
                        "generalised tonic chronic seizures alone."
                    ),
                },
                {
                    "family": "investigation",
                    "modality": "MRI",
                    "result": "normal",
                    "evidence": "Previous MRI in 2012 was normal.",
                },
            ],
            "omission_note": "The arranged repeat EEG is future/planned, so it is omitted.",
        },
        {
            "note_fragment": (
                "Seizure type and frequency: generalised tonic clonic seizure - "
                "last event July 2016. He has had roughly two seizures per year "
                "since onset."
            ),
            "clinical_facts": [
                {
                    "family": "diagnosis",
                    "concept": "generalised tonic clonic seizures",
                    "negation": "affirmed",
                    "evidence": (
                        "Seizure type and frequency: generalised tonic clonic "
                        "seizure - last event July 2016."
                    ),
                },
                {
                    "family": "seizure_frequency",
                    "seizure_type": "generalised tonic clonic seizures",
                    "state": "seizure_free",
                    "evidence": "generalised tonic clonic seizure - last event July 2016.",
                },
                {
                    "family": "seizure_frequency",
                    "seizure_type": "seizures",
                    "state": "active_rate",
                    "evidence": "roughly two seizures per year",
                },
            ],
        },
        {
            "note_fragment": (
                "She continues to get complex partial seizures. I will arrange "
                "an MRI scan."
            ),
            "clinical_facts": [
                {
                    "family": "diagnosis",
                    "concept": "complex partial seizures",
                    "negation": "affirmed",
                    "evidence": "She continues to get complex partial seizures.",
                },
            ],
            "omission_note": (
                "Continues to get has no count/rate/window, so no seizure_frequency "
                "fact is emitted. The MRI is planned, so it is omitted."
            ),
        },
    ]
    if prompt_profile == "full_examples":
        selected_examples = examples
    elif prompt_profile == "decision_table":
        selected_examples = [examples[index] for index in (0, 2, 4, 5)]
    else:
        selected_examples = examples[:4]
    if target_family is None:
        return selected_examples

    filtered_examples: list[dict[str, Any]] = []
    for example in selected_examples:
        family_facts = [
            fact
            for fact in example.get("clinical_facts", [])
            if fact.get("family") == target_family
        ]
        filtered = {
            "note_fragment": example["note_fragment"],
            "clinical_facts": family_facts,
        }
        if not family_facts and "omission_note" in example:
            filtered["omission_note"] = example["omission_note"]
        elif not family_facts:
            filtered["omission_note"] = (
                f"No source-supported {target_family} facts are emitted for this "
                "family-specific call."
            )
        elif "omission_note" in example:
            filtered["omission_note"] = example["omission_note"]
        filtered_examples.append(filtered)
    return filtered_examples


def _worked_examples(prompt_profile: PromptProfile) -> list[dict[str, Any]]:
    examples = structured._worked_examples()
    if prompt_profile == "full_examples":
        return examples
    compact_indexes = (
        0,
        1,
        2,
        5,
        10,
        11,
        12,
        21,
        22,
        23,
        24,
        36,
        38,
        39,
        40,
    )
    return [examples[index] for index in compact_indexes if index < len(examples)]
