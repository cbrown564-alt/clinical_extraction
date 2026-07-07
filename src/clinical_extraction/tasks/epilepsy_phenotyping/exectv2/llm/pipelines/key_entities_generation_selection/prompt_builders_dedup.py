"""Prompt payload/input builders for dedup."""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.types import (
    DedupFactFamily,
    PromptProfile,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.constants import (
    _ARCHITECTURE,
    PROMPT_VERSION,
    _dedup_fact_decision_tables,
    _dedup_fact_output_schema,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.prompt_builders_single_call_ids import (
    build_single_call_clean_render_ids_prompt_payload,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.prompt_content import (
    _dedup_fact_guidance,
    _dedup_fact_worked_examples,
)


def build_single_call_dedup_facts_prompt_payload(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "compact",
    target_family: DedupFactFamily | None = None,
) -> dict[str, Any]:
    """Build a one-call prompt for direct de-duplicated clinical facts."""

    stage = "single_call_dedup_facts_per_family" if target_family else "single_call_dedup_facts"
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

    fact_guidance = list(_dedup_fact_guidance())
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
        ("Keep repeated source-supported mentions by selecting each separate mention_id."),
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
