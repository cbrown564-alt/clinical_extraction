"""Shared prompt assembly for entity verifiers."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.config import (
    VerifierConfig,
)


def attribute_vocabulary(entity_name: str) -> dict[str, Any]:
    spec = ENTITY_REGISTRY[entity_name]
    attrs: dict[str, Any] = {}
    for attr in sorted(spec.legal_attributes):
        if attr in {"CUI", "CUIPhrase"}:
            attrs[attr] = "Do not emit this; deterministic projection fills it later."
        elif attr in spec.closed_vocab:
            attrs[attr] = sorted(spec.closed_vocab[attr])
        else:
            attrs[attr] = "string copied or normalized from the letter."
    return attrs


def attribute_vocabulary_for_config(config: VerifierConfig) -> dict[str, Any]:
    entity_names = config.draft_entity_names or (config.entity_name,)
    if len(entity_names) > 1:
        return {entity: attribute_vocabulary(entity) for entity in entity_names}
    return attribute_vocabulary(config.entity_name)


def build_prompt_input(
    letter: ExectLetter,
    draft_mentions: Sequence[Mapping[str, Any]],
    config: VerifierConfig,
    timeline_context: str | None = None,
) -> str:
    payload = {
        "prompt_version": config.prompt_version,
        "task": config.task_text,
        "output_schema": dict(config.output_schema),
        config.draft_field_name: list(draft_mentions),
        "attribute_vocabulary": attribute_vocabulary_for_config(config),
        "clinical_rules": config.clinical_rules(),
        "worked_examples": config.worked_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    if timeline_context is not None:
        # Optional pre-extraction context (Phase C, see
        # docs/plans/supervisor_brief_gap_closure_plan_2026-07-01.md). Only
        # added to the payload when the caller opts in, so the prompt/JSONL
        # produced for existing runs is byte-identical when unset.
        payload["timeline_context"] = timeline_context
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
