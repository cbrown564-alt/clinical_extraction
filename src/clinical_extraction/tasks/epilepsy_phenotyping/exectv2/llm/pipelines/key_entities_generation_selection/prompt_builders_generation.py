"""Prompt payload/input builders for generation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.types import (
    PromptProfile,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.constants import (
    _ARCHITECTURE,
    _MODEL_ORIGIN_CONTRACT,
    _OUTPUT_SCHEMA,
    PROMPT_VERSION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.projection import (
    _coerce_record,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.prompt_content import (
    _clinical_rules,
    _forbidden_attribute_combinations,
    _mention_attribute_contract,
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
        "first_pass_model_events": [event.model_dump() for event in record.clinical_events],
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
