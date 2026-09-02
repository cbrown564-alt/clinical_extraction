"""One-call Gan find, encode, and select.

Same codebook extract request as ``gan_llm_extract``, plus the living
select cases from ``gan_llm_select``. The letter is in the request.
This is a controlled bundling ablation, not the cited extract.
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
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_select import (
    select_cases_payload,
)

GAN_LLM_EXTRACT_ENCODE_SELECT = "gan_llm_extract_encode_select"
LLM_EXTRACT_ENCODE_SELECT_TEMPLATE_KEYS = (
    "task",
    "instructions",
    "cases",
    "label_forms",
    "event_schema",
    "selection_schema",
)
LLM_EXTRACT_ENCODE_SELECT_AUTHORED_KEYS = (
    *LLM_EXTRACT_ENCODE_SELECT_TEMPLATE_KEYS,
    "note_text",
)

SELECT_BRIDGE = (
    "When choosing the current answer, apply the cases below. Treat "
    "your first pick as the first choice in those cases. Keep it unless "
    "a case applies. You may write a new seizure-frequency label only "
    "when no single event is the answer."
)

INSTRUCTIONS = [*EXTRACT_INSTRUCTIONS, SELECT_BRIDGE]


def llm_extract_encode_select_prompt_template() -> dict[str, Any]:
    """Fixed one-call request without the letter body."""

    return {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "cases": select_cases_payload(),
        "label_forms": label_forms_payload(),
        "event_schema": dict(EVENT_SCHEMA),
        "selection_schema": dict(SELECTION_SCHEMA),
    }


def build_llm_extract_encode_select_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the one-call find, encode, and select payload."""

    payload = {
        **llm_extract_encode_select_prompt_template(),
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
