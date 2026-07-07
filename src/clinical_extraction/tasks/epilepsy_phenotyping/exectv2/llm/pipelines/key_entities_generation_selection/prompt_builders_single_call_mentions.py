"""Prompt payload/input builders for single-call mention/inventory strategies."""

from __future__ import annotations

import json
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
    _INVENTORY_OUTPUT_SCHEMA,
    _MENTION_OUTPUT_SCHEMA,
    _TYPED_MENTION_OUTPUT_SCHEMA,
    PROMPT_VERSION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.prompt_content import (
    _clinical_rules,
    _forbidden_attribute_combinations,
    _mention_attribute_contract,
    _worked_examples,
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
            ("Each final mention must carry all needed attributes in its own attributes object."),
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
        ("Each final mention must carry all needed attributes in its own attributes object."),
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
