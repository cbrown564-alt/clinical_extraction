"""Holgate-like one-label find request.

Clinical ask follows Holgate et al. 2024 three-step query. No event
schema, no selection schema, no forms, no examples, and no quote
obligation. One answer field. Not the published 11-shot prompt.
"""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord

GAN_LLM_EXTRACT_HOLGATE_LABEL = "gan_llm_extract_holgate_label"
LLM_EXTRACT_HOLGATE_LABEL_TEMPLATE_KEYS = (
    "task",
    "instructions",
    "answer_schema",
)
LLM_EXTRACT_HOLGATE_LABEL_AUTHORED_KEYS = (
    *LLM_EXTRACT_HOLGATE_LABEL_TEMPLATE_KEYS,
    "note_text",
)

TASK = "Read the following clinical note then work through these 3 steps."
ANSWER_SCHEMA = {"answer": "the frequency, or I do not know"}
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
    "Return exactly one JSON object with an answer field and no markdown.",
]


def llm_extract_holgate_label_prompt_template() -> dict[str, Any]:
    """Fixed Holgate one-label find request without the letter body."""

    return {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "answer_schema": dict(ANSWER_SCHEMA),
    }


def build_llm_extract_holgate_label_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the Holgate one-label extract payload."""

    payload = {
        **llm_extract_holgate_label_prompt_template(),
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
