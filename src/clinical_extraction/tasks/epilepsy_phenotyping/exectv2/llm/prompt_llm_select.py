"""ExECT later-stage select prompt.

Keeps, drops, relabels, merges, or also lists a fact in the other family.
No letter text. No name list. No research metadata.
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

EXECT_LLM_SELECT = "exect_llm_select"
LLM_SELECT_AUTHORED_KEYS = (
    "task",
    "instructions",
    "row_schema",
    "mentions",
)

TASK = (
    "Keep, drop, merge, or also list a kept fact in the other family."
)

INSTRUCTIONS = [
    (
        "Each row already has a standard name. Treat that name as the "
        "short-name style to keep. When you merge rows or also list a fact "
        "in the other family, use the same kind of short name."
    ),
    "Keep a row when it is its own fact.",
    (
        "Drop a row when it repeats another row, or when it does not name "
        "a real fact from those rows."
    ),
    (
        "Merge when two rows are the same fact. Keep one mention_id and "
        "point the other at it."
    ),
    (
        "You may write a new standard name or details for a kept row. Use "
        "only words already on that row, or on both rows when you merge. "
        "Match the given standard-name style."
    ),
    (
        "You may also list a kept fact in the other family. Copy that "
        "row's supporting sentence and standard name. Do this only when "
        "the same name belongs in both diagnosis and seizure frequency."
    ),
    "Do not write a new quote. Do not add a name the kept row did not already carry.",
    (
        "Return one row for every given mention_id. Use action drop on a "
        "row you do not keep. An also-listed fact is an extra row."
    ),
    "Return one JSON object with a mentions list.",
]

ROW_SCHEMA = {
    "mention_id": "copy the given mention_id, or omit when also listing in the other family",
    "action": "keep, drop, merge, or also_list",
    "standard_name": "new short name when you relabel; otherwise omit",
    "details": "new count, dose, date, or result when you rewrite them; otherwise omit",
    "merge_into": "mention_id to merge into, only when action is merge",
    "from_mention_id": "kept mention_id, only when action is also_list",
    "clinical_family": "the other family, only when action is also_list",
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
        "row_schema": dict(ROW_SCHEMA),
        "mentions": [_select_mention_view(mention) for mention in mentions],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
