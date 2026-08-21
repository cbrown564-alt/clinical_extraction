"""ExECT later-stage encode prompt.

Writes one standard name and details per extract mention.
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
    mention_name,
    mention_sentence,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompt_standard_names import (
    standard_names_payload,
)

EXECT_LLM_ENCODE = "exect_llm_encode"
LLM_ENCODE_AUTHORED_KEYS = (
    "task",
    "instructions",
    "standard_names",
    "row_schema",
    "mentions",
)

TASK = "Write one standard name and the details for each row."

INSTRUCTIONS = [
    (
        "Each row has a mention_id, a clinical family, a clinical name, "
        "a supporting sentence, and details such as a count, dose, date, "
        "or test result."
    ),
    "Leave mention_id unchanged. Return one row for every mention_id.",
    (
        "Write the standard name from that family's list. Do not copy the "
        "clinical name unless it already is the standard name."
    ),
    (
        "Put the count, period, dose, date, result, or status in details. "
        "When the field has a listed set of values, write one of those values. "
        "Use only words already on that row."
    ),
    "Do not add, drop, or merge rows.",
    "Return one JSON object with a mentions list.",
]

ROW_SCHEMA = {
    "mention_id": "copy the given mention_id",
    "standard_name": "usual short name for this fact",
    "details": "count, period, dose, date, result, or status already on the row",
}


def _encode_mention_view(mention: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "mention_id": mention_id(mention),
        "clinical_family": mention_family(mention),
        "clinical_name": mention_name(mention),
        "supporting_sentence": mention_sentence(mention),
        "details": mention_details(mention),
    }


def build_llm_encode_prompt_input(mentions: Sequence[Mapping[str, Any]]) -> str:
    """Build the later-stage encode payload from extract mentions."""

    payload = {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "standard_names": standard_names_payload(),
        "row_schema": dict(ROW_SCHEMA),
        "mentions": [_encode_mention_view(mention) for mention in mentions],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
