"""Helpers for the predeclared decision-0040 dev140 regression analysis."""

from __future__ import annotations

import json
import re
from collections.abc import Collection

_LETTER_ID = re.compile(rb'"letter_id"\s*:\s*("(?:\\.|[^"\\])*")')


def change_direction(source_correct: bool, final_correct: bool) -> str:
    """Name the correctness direction for a row whose clinical keys changed."""

    if source_correct and not final_correct:
        return "correct_to_wrong"
    if not source_correct and final_correct:
        return "wrong_to_correct"
    if source_correct:
        return "changed_still_correct"
    return "changed_still_wrong"


def filter_jsonl_bytes(payload: bytes, *, allowed_ids: Collection[str]) -> bytes:
    """Return exactly the declared development rows from a larger JSONL blob.

    Non-development rows are discarded immediately after reading their identifier.
    Their remaining fields are never retained by this function.
    """

    allowed = set(allowed_ids)
    retained: list[bytes] = []
    seen: set[str] = set()
    for raw_line in payload.splitlines():
        if not raw_line.strip():
            continue
        match = _LETTER_ID.search(raw_line)
        if match is None:
            raise ValueError("JSONL row has no letter_id")
        letter_id = str(json.loads(match.group(1)))
        if letter_id not in allowed:
            continue
        if letter_id in seen:
            raise ValueError(f"duplicate dev row: {letter_id}")
        seen.add(letter_id)
        row = json.loads(raw_line)
        retained.append(json.dumps(row, sort_keys=True).encode("utf-8"))
    missing = sorted(allowed - seen)
    if missing:
        raise ValueError(f"missing dev rows: {missing}")
    return b"\n".join(retained) + (b"\n" if retained else b"")


__all__ = ["change_direction", "filter_jsonl_bytes"]
