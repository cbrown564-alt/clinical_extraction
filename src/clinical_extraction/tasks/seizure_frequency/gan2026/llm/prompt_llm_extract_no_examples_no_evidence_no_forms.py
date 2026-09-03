"""Gan codebook extract without examples, evidence, or closed label forms."""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import INSTRUCTIONS as EXTRACT_INSTRUCTIONS
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract_no_evidence import (
    EVENT_SCHEMA_WITHOUT_EVIDENCE,
    SELECTION_SCHEMA_WITHOUT_EVIDENCE,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract_raw import TASK

GAN_LLM_EXTRACT_NO_EXAMPLES_NO_EVIDENCE_NO_FORMS = "gan_llm_extract_no_examples_no_evidence_no_forms"
LLM_EXTRACT_COMBINED_TEMPLATE_KEYS = ("task", "instructions", "event_schema", "selection_schema")
LLM_EXTRACT_COMBINED_AUTHORED_KEYS = (*LLM_EXTRACT_COMBINED_TEMPLATE_KEYS, "note_text")

INSTRUCTIONS = [
    instruction for instruction in EXTRACT_INSTRUCTIONS
    if not instruction.startswith("Every evidence value must be an exact substring")
    and not instruction.startswith("Write the seizure-frequency label using only")
]

def llm_extract_combined_prompt_template() -> dict[str, Any]:
    return {"task": TASK, "instructions": list(INSTRUCTIONS), "event_schema": dict(EVENT_SCHEMA_WITHOUT_EVIDENCE), "selection_schema": dict(SELECTION_SCHEMA_WITHOUT_EVIDENCE)}

def build_llm_extract_combined_prompt_input(record: GanFrequencyRecord) -> str:
    payload = {**llm_extract_combined_prompt_template(), "note_text": record.note_text}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
