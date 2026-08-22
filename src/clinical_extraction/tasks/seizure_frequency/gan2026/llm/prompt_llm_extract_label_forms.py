"""Gan extract prompt with the later-stage label-form list.

Same event and selection schema as ``gan_llm_with_rules``. The extra
block is the closed output dialect. Events still keep the note wording.
"""

from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_label_forms import (
    label_forms_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_with_rules import (
    EVENT_SCHEMA,
    SELECTION_SCHEMA,
    TASK,
)

GAN_LLM_EXTRACT_LABEL_FORMS = "gan_llm_extract_label_forms"
LLM_EXTRACT_LABEL_FORMS_AUTHORED_KEYS = (
    "task",
    "instructions",
    "label_forms",
    "event_schema",
    "selection_schema",
    "note_text",
)

INSTRUCTIONS = [
    "Read the full clinical note and extract source-near seizure-frequency facts.",
    (
        "Return events as slim clinical facts, not fully normalized answer records. "
        "Use raw_value for the text's stated rate, duration, last-event statement, or "
        "unknown/no-reference cue."
    ),
    (
        "Event kind must be one of frequency_rate, cluster_frequency, seizure_free, "
        "last_event_only, unknown_frequency, or no_reference."
    ),
    (
        "Use one no_reference event only when the note contains no usable "
        "seizure-frequency evidence. Do not use no_reference when seizures are "
        "discussed but frequency is unclear; use unknown_frequency instead."
    ),
    (
        "Keep seizure-free statements separate from unknown or last-event-only "
        "statements. Do not select seizure-free if other current seizure-like events "
        "remain active."
    ),
    (
        "Selection must choose the highest current or recent seizure burden across "
        "semiologies when several current seizure types are present."
    ),
    (
        "If the note gives an overall current seizure count plus a breakdown by "
        "seizure type, select the overall count for the seizure-frequency label "
        "rather than only the clinically most severe subtype count."
    ),
    (
        "Write the seizure-frequency label using only the allowed forms. Copy an "
        "example and change the numbers if needed."
    ),
    (
        "If the selected event has a countable stated rate, put the note's wording "
        "in raw_value and write the seizure-frequency label from the allowed forms."
    ),
    (
        "When the note says a last event occurred on a date and the patient has "
        "been well, stable, or seizure-free since, still extract the dated last-event "
        "fact as its own event even if the selection is seizure-free."
    ),
    (
        "When the note says a count such as 3 or 4 jerks occurred since a dated "
        "last tonic-clonic seizure, keep the source count and the dated anchor "
        "available in the event list."
    ),
    "Every evidence value must be an exact substring from the note when possible.",
    "Return exactly one JSON object with no markdown.",
]


def build_llm_extract_label_forms_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the Gan extract payload that includes the label-form list."""

    payload = {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "label_forms": label_forms_payload(),
        "event_schema": dict(EVENT_SCHEMA),
        "selection_schema": dict(SELECTION_SCHEMA),
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
