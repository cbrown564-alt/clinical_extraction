"""Historical enveloped Gan hybrid request.

Replay only. Not the paper method. The paper request lives in
``prompt_llm_with_rules.py``.
"""

from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_with_rules import (
    EVENT_SCHEMA,
    INSTRUCTIONS,
    SELECTION_SCHEMA,
)

PROMPT_VERSION_V0_5 = "gan2026_hybrid_structured_events_v0.5"
_V05_TASK = (
    "Gan 2026 LLM-only structured-events extraction and clinical selection"
)


def build_llm_with_rules_v05_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the historical enveloped hybrid payload."""

    payload = {
        "prompt_version": PROMPT_VERSION_V0_5,
        "task": _V05_TASK,
        "source_row_index": record.source_row_index,
        "instructions": list(INSTRUCTIONS),
        "event_schema": dict(EVENT_SCHEMA),
        "selection_schema": dict(SELECTION_SCHEMA),
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
