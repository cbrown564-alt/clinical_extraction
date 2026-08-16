"""Event-local hybrid rules for the semantic-inventory research lane.

Compatibility shim: implementation lives in mention_unit_shared so the
mention-unit lane can survive deletion of this module.
"""

from __future__ import annotations

from .mention_unit_shared import (
    _heading_split_phrases,
    _is_pending_investigation,
    _is_uncoded_phenomenology,
    project_hybrid_event,
)

__all__ = [
    "project_hybrid_event",
    "_heading_split_phrases",
    "_is_pending_investigation",
    "_is_uncoded_phenomenology",
]
