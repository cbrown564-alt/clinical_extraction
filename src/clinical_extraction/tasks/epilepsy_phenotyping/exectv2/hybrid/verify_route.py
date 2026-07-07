"""Verify / route stage for the hybrid SeizureFrequency extractor.

Thin SF-facing wrapper around ``all_entity_gate.gate_mentions``. The canonical
gate implementation lives in ``all_entity_gate``; this module preserves the
historical ``verify_and_route`` import path used by ``clinical_assessment``.
"""

from __future__ import annotations

from collections.abc import Sequence

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)

from .all_entity_gate import (
    RoutedMention,
    gate_mentions,
    routed_taxonomy,
)

__all__ = ("RoutedMention", "routed_taxonomy", "verify_and_route")


def verify_and_route(
    mentions: Sequence[PredictedMention],
    *,
    note_text: str,
) -> tuple[list[PredictedMention], list[RoutedMention]]:
    """Partition mentions into (kept, routed) via the all-entity gate."""
    return gate_mentions(mentions, note_text=note_text)
