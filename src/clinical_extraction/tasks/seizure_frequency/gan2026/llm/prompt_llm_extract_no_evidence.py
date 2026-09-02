"""Cited codebook extract without the quote obligation.

Same events, selection, instructions, forms, and examples as
``gan_llm_extract``. The ``evidence`` keys and the exact-substring
instruction are omitted. Controlled-experiment wording.
"""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_label_forms import (
    label_forms_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    INSTRUCTIONS as EXTRACT_INSTRUCTIONS,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract_raw import (
    EVENT_SCHEMA,
    SELECTION_SCHEMA,
    TASK,
)

GAN_LLM_EXTRACT_NO_EVIDENCE = "gan_llm_extract_no_evidence"
LLM_EXTRACT_NO_EVIDENCE_TEMPLATE_KEYS = (
    "task",
    "instructions",
    "label_forms",
    "event_schema",
    "selection_schema",
)
LLM_EXTRACT_NO_EVIDENCE_AUTHORED_KEYS = (*LLM_EXTRACT_NO_EVIDENCE_TEMPLATE_KEYS, "note_text")

INSTRUCTIONS = [
    instruction
    for instruction in EXTRACT_INSTRUCTIONS
    if not instruction.startswith("Every evidence value must be an exact substring")
]
EVENT_SCHEMA_WITHOUT_EVIDENCE = {
    key: value for key, value in EVENT_SCHEMA.items() if key != "evidence"
}
SELECTION_SCHEMA_WITHOUT_EVIDENCE = {
    key: value for key, value in SELECTION_SCHEMA.items() if key != "evidence"
}


def llm_extract_no_evidence_prompt_template() -> dict[str, Any]:
    """Fixed codebook find request without evidence keys."""

    return {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "label_forms": label_forms_payload(),
        "event_schema": dict(EVENT_SCHEMA_WITHOUT_EVIDENCE),
        "selection_schema": dict(SELECTION_SCHEMA_WITHOUT_EVIDENCE),
    }


def build_llm_extract_no_evidence_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the codebook extract payload without the quote obligation."""

    payload = {
        **llm_extract_no_evidence_prompt_template(),
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
