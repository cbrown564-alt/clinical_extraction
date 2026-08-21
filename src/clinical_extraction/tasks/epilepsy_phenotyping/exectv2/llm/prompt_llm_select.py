"""ExECT later-stage select prompt.

Keeps, drops, relabels, or groups already named rows.
No letter text. No research metadata.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompt_mention_view import (
    mention_details,
    mention_family,
    mention_id,
    mention_sentence,
    mention_standard_name,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompt_standard_names import (
    standard_names_payload,
)

EXECT_LLM_SELECT = "exect_llm_select"
LLM_SELECT_AUTHORED_KEYS = (
    "task",
    "instructions",
    "standard_names",
    "row_schema",
    "mentions",
)

TASK = "Keep, drop, relabel, or group the named rows."

INSTRUCTIONS = [
    (
        "Each row already has a standard name, details, and a "
        "supporting sentence."
    ),
    "Keep a row, drop it, or merge it into another mention_id.",
    (
        "You may write a new standard name or details for a kept "
        "row. Use only words already on that row, or on both rows "
        "when you merge."
    ),
    (
        "You may add one companion row that copies a kept row's supporting "
        "sentence and standard name into the other family. Do this only when "
        "the same name belongs in both diagnosis and seizure frequency."
    ),
    "Do not write a new quote. Do not add a name the kept row did not already carry.",
    "Return one JSON object with a mentions list.",
]

ROW_SCHEMA = {
    "mention_id": "copy the given mention_id, or omit on a companion",
    "action": "keep, drop, merge, or companion",
    "standard_name": "new standard name when you relabel; otherwise omit",
    "details": "new count, dose, date, or result when you rewrite them; otherwise omit",
    "merge_into": "mention_id to merge into, only when action is merge",
    "from_mention_id": "kept mention_id, only when action is companion",
    "clinical_family": "the other family, only when action is companion",
}


def _select_mention_view(mention: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "mention_id": mention_id(mention),
        "clinical_family": mention_family(mention),
        "standard_name": mention_standard_name(mention),
        "supporting_sentence": mention_sentence(mention),
        "details": mention_details(mention),
    }


def build_llm_select_prompt_input(mentions: Sequence[Mapping[str, Any]]) -> str:
    """Build the later-stage select payload from encoded mentions."""

    payload = {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "standard_names": standard_names_payload(),
        "row_schema": dict(ROW_SCHEMA),
        "mentions": [_select_mention_view(mention) for mention in mentions],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
