"""Gan candidate-suggestion paper prompt.

Same event schema as ``gan_llm_with_rules``, plus suggested quotes from
the existing deterministic candidate extractor. No research metadata.
"""

from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_canonical_stages import (
    extract_stage,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_with_rules import (
    EVENT_SCHEMA,
    SELECTION_SCHEMA,
)

GAN_LLM_PRE_POST = "gan_llm_pre_post"
LLM_PRE_POST_AUTHORED_KEYS = (
    "task",
    "instructions",
    "event_schema",
    "selection_schema",
    "suggested_evidence",
    "note_text",
)

TASK = (
    "Read the clinical note. Use the suggested evidence as a starting "
    "point, then extract seizure-frequency facts as slim events, then "
    "select the current burden."
)

INSTRUCTIONS = [
    "Read the full clinical note.",
    (
        "Treat suggested-evidence rows as possible supporting quotes from a "
        "first scan. Do not include a fact unless the note supports it."
    ),
    "For each suggested row, keep, reject, split, or merge.",
    "Then scan the rest of the letter for any seizure-frequency fact the list missed.",
    (
        "Return events as slim clinical facts. Use raw_value for the wording "
        "in the note: the stated rate, duration, last-event statement, or "
        "unknown or no-reference cue."
    ),
    (
        "Event kind must be one of frequency_rate, cluster_frequency, seizure_free, "
        "last_event_only, unknown_frequency, or no_reference."
    ),
    (
        "Use one no_reference event only when the note contains no usable "
        "seizure-frequency evidence. If seizures are discussed but frequency is "
        "unclear, use unknown_frequency."
    ),
    (
        "Keep seizure-free statements separate from unknown or last-event-only "
        "statements. Do not select seizure-free if other current seizure-like "
        "events remain active."
    ),
    (
        "Selection must choose the highest current or recent seizure burden "
        "across seizure types when several current types are present."
    ),
    (
        "If the note gives an overall current seizure count plus a breakdown by "
        "seizure type, put the overall count in the seizure-frequency label "
        "rather than only the most severe subtype count."
    ),
    (
        "The seizure-frequency label may be a short form such as 1 per day, "
        "2 to 3 per month, multiple per week, 1 cluster per week, "
        "seizure free for 6 month, unknown, or no seizure frequency reference."
    ),
    (
        "If the selected event has a countable raw_value, put the note's "
        "wording in raw_value and a short label in the seizure-frequency label."
    ),
    (
        "When the note says a last event occurred on a date and the patient has "
        "been well, stable, or seizure-free since, still extract the dated "
        "last-event fact as its own event even if the selection is seizure-free."
    ),
    (
        "When the note says a count such as 3 or 4 jerks occurred since a dated "
        "last tonic-clonic seizure, keep the source count and the dated anchor "
        "in the event list."
    ),
    "Every evidence value must be an exact copy from the note when possible.",
    "Return exactly one JSON object with no markdown.",
]


def suggested_evidence_rows(record: GanFrequencyRecord) -> list[dict[str, str]]:
    """Reuse the rules-only candidate extractor. Do not invent a second engine."""

    _, _, events = extract_stage(
        record.note_text, source_row_index=record.source_row_index
    )
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for event in events:
        evidence = event.evidence
        kind = str(event.kind)
        key = (kind, evidence)
        if not evidence or key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "kind": kind,
                "evidence": evidence,
                "name_hint": event.raw_value or kind.replace("_", " "),
            }
        )
    return rows


def build_llm_pre_post_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the Gan candidate-suggestion paper payload."""

    payload = {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "event_schema": dict(EVENT_SCHEMA),
        "selection_schema": dict(SELECTION_SCHEMA),
        "suggested_evidence": suggested_evidence_rows(record),
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
