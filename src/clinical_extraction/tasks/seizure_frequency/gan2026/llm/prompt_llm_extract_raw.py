"""Gan source-near extract prompt.

Self-contained structured-events request. No research metadata.
``gan_llm_extract_raw`` emits this payload. Events and the first label
keep letter wording; they are not the closed codebook forms.
"""

from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord

GAN_LLM_EXTRACT_RAW = "gan_llm_extract_raw"
LLM_EXTRACT_RAW_AUTHORED_KEYS = (
    "task",
    "instructions",
    "event_schema",
    "selection_schema",
    "note_text",
)

TASK = (
    "Read the clinical note. Extract seizure-frequency facts as slim "
    "events, then select the current burden."
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
        "seizure type, select the overall count for final_label rather than only the "
        "clinically most severe subtype count."
    ),
    (
        "Selection final_label may be a normalized label such as 1 per day, "
        "2 to 3 per month, multiple per week, 1 cluster per week, "
        "seizure free for 6 month, unknown, or no seizure frequency reference."
    ),
    (
        "If the selected event has a countable raw_value, prefer putting the source "
        "expression in raw_value and a concise normalized label in final_label."
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

EVENT_SCHEMA = {
    "event_id": "stable string such as e1",
    "kind": [
        "frequency_rate",
        "cluster_frequency",
        "seizure_free",
        "last_event_only",
        "unknown_frequency",
        "no_reference",
    ],
    "raw_value": "source-near expression or null",
    "applies_to": "seizure type or clinical target, or null",
    "time_window": "source-near current/recent/historical window, or null",
    "temporality": ["current", "recent", "historical", "future", "unclear"],
    "assertion_status": [
        "asserted",
        "negated",
        "historical",
        "hypothetical",
        "unknown",
    ],
    "evidence": "exact note substring",
    "notes": "optional short note or null",
}

SELECTION_SCHEMA = {
    "selected_event_ids": "list of selected event_id strings",
    "final_kind": [
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ],
    "final_label": "normalized label, or null if not directly countable",
    "evidence": "exact note substring supporting the final selection",
    "confidence": ["low", "medium", "high"],
    "rationale": "brief clinical reason for selecting these events",
}


def build_llm_extract_raw_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the Gan source-near extract payload."""

    payload = {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "event_schema": dict(EVENT_SCHEMA),
        "selection_schema": dict(SELECTION_SCHEMA),
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
