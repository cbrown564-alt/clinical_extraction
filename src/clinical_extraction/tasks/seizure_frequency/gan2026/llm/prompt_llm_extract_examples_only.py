"""Cited codebook extract with example strings and no closed form list.

Same schema, clinical instructions, and quote rule as ``gan_llm_extract``.
The ``label_forms`` block is replaced by a flat examples list.
"""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_label_forms import (
    label_form_example_strings,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    INSTRUCTIONS as EXTRACT_INSTRUCTIONS,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract_raw import (
    EVENT_SCHEMA,
    SELECTION_SCHEMA,
    TASK,
)

GAN_LLM_EXTRACT_EXAMPLES_ONLY = "gan_llm_extract_examples_only"
LLM_EXTRACT_EXAMPLES_ONLY_TEMPLATE_KEYS = (
    "task",
    "instructions",
    "examples",
    "event_schema",
    "selection_schema",
)
LLM_EXTRACT_EXAMPLES_ONLY_AUTHORED_KEYS = (
    *LLM_EXTRACT_EXAMPLES_ONLY_TEMPLATE_KEYS,
    "note_text",
)


def _rewrite_instruction(instruction: str) -> str:
    if instruction.startswith("Write the seizure-frequency label using only"):
        return "Copy an example and change the numbers if needed."
    return instruction.replace(" from the allowed forms.", ".")


INSTRUCTIONS = [_rewrite_instruction(instruction) for instruction in EXTRACT_INSTRUCTIONS]


def llm_extract_examples_only_prompt_template() -> dict[str, Any]:
    """Fixed examples-only find request without the letter body."""

    return {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "examples": label_form_example_strings(),
        "event_schema": dict(EVENT_SCHEMA),
        "selection_schema": dict(SELECTION_SCHEMA),
    }


def build_llm_extract_examples_only_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the codebook extract payload with examples and no form list."""

    payload = {
        **llm_extract_examples_only_prompt_template(),
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
