"""Prompt payload/input builders for every generation-selection call strategy."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.types import (
    DedupFactFamily,
    PromptProfile,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.constants import (
    PROMPT_VERSION,
    _ARCHITECTURE,
    _CLEAN_RENDER_ID_OUTPUT_SCHEMA,
    _INVENTORY_OUTPUT_SCHEMA,
    _MENTION_ID_OUTPUT_SCHEMA,
    _MENTION_OUTPUT_SCHEMA,
    _MODEL_ORIGIN_CONTRACT,
    _OUTPUT_SCHEMA,
    _POOL_ADJUDICATION_OUTPUT_SCHEMA,
    _POOL_GROUP_ADJUDICATION_OUTPUT_SCHEMA,
    _RENDER_ID_OUTPUT_SCHEMA,
    _TYPED_MENTION_OUTPUT_SCHEMA,
    _dedup_fact_decision_tables,
    _dedup_fact_output_schema,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.parsing import (
    coerce_mention_list,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.projection import (
    _coerce_record,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.prompt_content import (
    _clean_render_text_policy,
    _clinical_rules,
    _dedup_fact_worked_examples,
    _forbidden_attribute_combinations,
    _mention_attribute_contract,
    _render_text_policy,
    _worked_examples,
)


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

    pool_mentions, pool_notes = coerce_mention_list(
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

    pool_mentions, pool_notes = coerce_mention_list(
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
