"""Holgate-like find request on the Gan event schema.

Clinical ask follows Holgate et al. 2024 three-step query. No persona,
no few-shot examples, and no ``label_forms`` block. Event and selection
schemas stay those of ``gan_llm_extract``. Controlled-experiment
wording; not the cited codebook find.
"""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract_raw import (
    EVENT_SCHEMA,
    SELECTION_SCHEMA,
)

GAN_LLM_EXTRACT_HOLGATE_LIKE = "gan_llm_extract_holgate_like"
LLM_EXTRACT_HOLGATE_LIKE_TEMPLATE_KEYS = (
    "task",
    "instructions",
    "event_schema",
    "selection_schema",
)
LLM_EXTRACT_HOLGATE_LIKE_AUTHORED_KEYS = (
    *LLM_EXTRACT_HOLGATE_LIKE_TEMPLATE_KEYS,
    "note_text",
)

TASK = "Read the following clinical note then work through these 3 steps."

INSTRUCTIONS = [
    (
        "Determine whether the note has any information about the frequency "
        "of the epilepsy patient's seizures."
    ),
    (
        "If the note does not have any information about the frequency of the "
        "epilepsy patient's seizures, then you answer: 'I do not know.'"
    ),
    (
        "If the note does have information about the frequency of the epilepsy "
        "patient's seizures, then you estimate the frequency of the epilepsy "
        "seizures and express the frequency in terms of per year, per month, "
        "per week, or per day, whichever is most relevant."
    ),
    (
        "Return exactly one JSON object that matches the event and selection "
        "schemas, with no markdown. Put the note's wording in raw_value when "
        "a rate or last-event statement is present. Every evidence value must "
        "be an exact substring from the note when possible."
    ),
]


def llm_extract_holgate_like_prompt_template() -> dict[str, Any]:
    """Fixed Holgate-like find request without the letter body."""

    return {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "event_schema": dict(EVENT_SCHEMA),
        "selection_schema": dict(SELECTION_SCHEMA),
    }


def build_llm_extract_holgate_like_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the Holgate-like extract payload."""

    payload = {
        **llm_extract_holgate_like_prompt_template(),
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
