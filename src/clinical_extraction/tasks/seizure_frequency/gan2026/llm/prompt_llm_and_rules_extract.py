"""Gan both-extract prompt: rules candidates plus a codebook-form request.

Suggested-evidence rows come from the rules-only candidate extractor.
The extra block is the closed output dialect.
"""

from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_canonical_stages import (
    extract_stage,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_label_forms import (
    label_forms_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    INSTRUCTIONS as EXTRACT_INSTRUCTIONS,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract_raw import (
    EVENT_SCHEMA,
    SELECTION_SCHEMA,
)

GAN_LLM_AND_RULES_EXTRACT = "gan_llm_and_rules_extract"
LLM_AND_RULES_EXTRACT_AUTHORED_KEYS = (
    "task",
    "instructions",
    "label_forms",
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
    *EXTRACT_INSTRUCTIONS[1:],
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


def build_llm_and_rules_extract_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the candidate-suggestion payload that includes the label-form list."""

    payload = {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "label_forms": label_forms_payload(),
        "event_schema": dict(EVENT_SCHEMA),
        "selection_schema": dict(SELECTION_SCHEMA),
        "suggested_evidence": suggested_evidence_rows(record),
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
