"""Prompt payload/input builders for single-call ID-selection strategies."""

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
    _dedup_fact_guidance,
    _dedup_fact_worked_examples,
    _forbidden_attribute_combinations,
    _mention_attribute_contract,
    _render_text_policy,
    _worked_examples,
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
