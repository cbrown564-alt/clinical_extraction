"""Gan codebook extract without example strings.

Same clinical instructions and allowed forms as ``gan_llm_extract``.
The examples arrays are omitted. This is a controlled examples ablation.
"""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_label_forms import (
    label_forms_without_examples_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    INSTRUCTIONS as EXTRACT_INSTRUCTIONS,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    LLM_EXTRACT_AUTHORED_KEYS,
    LLM_EXTRACT_TEMPLATE_KEYS,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract_raw import (
    EVENT_SCHEMA,
    SELECTION_SCHEMA,
    TASK,
)

GAN_LLM_EXTRACT_NO_EXAMPLES = "gan_llm_extract_no_examples"
LLM_EXTRACT_NO_EXAMPLES_TEMPLATE_KEYS = LLM_EXTRACT_TEMPLATE_KEYS
LLM_EXTRACT_NO_EXAMPLES_AUTHORED_KEYS = LLM_EXTRACT_AUTHORED_KEYS

INSTRUCTIONS = [
    (
        "Write the seizure-frequency label using only the allowed forms. "
        "Change the numbers if needed."
        if instruction.startswith("Write the seizure-frequency label using only")
        else instruction
    )
    for instruction in EXTRACT_INSTRUCTIONS
]


def llm_extract_no_examples_prompt_template() -> dict[str, Any]:
    """Fixed no-examples find request without the letter body."""

    return {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "label_forms": label_forms_without_examples_payload(),
        "event_schema": dict(EVENT_SCHEMA),
        "selection_schema": dict(SELECTION_SCHEMA),
    }


def build_llm_extract_no_examples_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the codebook extract payload without example strings."""

    payload = {
        **llm_extract_no_examples_prompt_template(),
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
