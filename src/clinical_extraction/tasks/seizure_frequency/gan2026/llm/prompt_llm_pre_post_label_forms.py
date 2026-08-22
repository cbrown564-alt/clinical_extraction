"""Gan candidate-suggestion extract with the later-stage label-form list.

Same suggested-evidence rows as ``gan_llm_pre_post``. The extra block
is the closed output dialect. Living ``gan_llm_pre_post`` is unchanged.
"""

from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_label_forms import (
    label_forms_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract_label_forms import (
    INSTRUCTIONS as EXTRACT_LABEL_FORMS_INSTRUCTIONS,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_pre_post import (
    TASK,
    suggested_evidence_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_with_rules import (
    EVENT_SCHEMA,
    SELECTION_SCHEMA,
)

GAN_LLM_PRE_POST_LABEL_FORMS = "gan_llm_pre_post_label_forms"
LLM_PRE_POST_LABEL_FORMS_AUTHORED_KEYS = (
    "task",
    "instructions",
    "label_forms",
    "event_schema",
    "selection_schema",
    "suggested_evidence",
    "note_text",
)

INSTRUCTIONS = [
    "Read the full clinical note.",
    (
        "Treat suggested-evidence rows as possible supporting quotes from a "
        "first scan. Do not include a fact unless the note supports it."
    ),
    "For each suggested row, keep, reject, split, or merge.",
    "Then scan the rest of the letter for any seizure-frequency fact the list missed.",
    *EXTRACT_LABEL_FORMS_INSTRUCTIONS[1:],
]


def build_llm_pre_post_label_forms_prompt_input(record: GanFrequencyRecord) -> str:
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
