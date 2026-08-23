"""Stage-volume counts for paper extract / encode / select stops.

ExECT tracks predicted mention objects. Gan tracks predicted event
candidates. Both are inventory sizes, not scored headline units.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def count_predicted_mentions(mentions: Sequence[Any] | None) -> int:
    """Count predicted ExECT mentions at one stage stop."""

    return 0 if mentions is None else len(mentions)


def gan_row_candidate_count(row: Mapping[str, Any]) -> int:
    """Count predicted Gan candidates on one paper or later-stage row."""

    encoded = row.get("encoded_events")
    if encoded is not None:
        return len(encoded)
    structured = row.get("structured_record")
    if isinstance(structured, Mapping):
        return len(structured.get("events") or [])
    return len(row.get("normalized_events") or [])
