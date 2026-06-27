"""Prompt payload/input builders for qwen pool."""

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
