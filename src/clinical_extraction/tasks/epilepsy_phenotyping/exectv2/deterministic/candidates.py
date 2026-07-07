"""Candidate types for the anchor + association SeizureFrequency pipeline.

Two kinds of candidate are produced by rules:

``AnchorCandidate``
    A seizure-type / event-description phrase (e.g. "focal seizures with loss
    of awareness"). ``text`` is the phrase used as ``PredictedMention.text`` —
    it must normalize (via scoring.normalize_phrase) to the gold-annotated
    phrase. ``evidence`` must be an exact verbatim substring of the letter
    text.

``AttributeExtraction``
    A nearby frequency/seizure-free/change expression that contributes
    SeizureFrequency *attributes* to the nearest anchor. It carries no
    ``text`` of its own — association merges its ``attributes`` onto an
    anchor's PredictedMention.

Both carry ``span`` (character offsets into the letter text) so the
association stage can compute proximity without re-searching the text.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from .rule_metadata import Portability, RuleGroup


class AttributeKind(StrEnum):
    RATE = "rate"
    SEIZURE_FREE = "seizure_free"
    FREQUENCY_CHANGE = "frequency_change"
    TEMPORAL = "temporal"


@dataclass(frozen=True)
class AnchorCandidate:
    """A seizure-type / event-description phrase candidate."""

    text: str
    evidence: str
    span: tuple[int, int]
    rule_id: str = "unknown"
    rule_group: RuleGroup | None = None
    portability: Portability | None = None


@dataclass(frozen=True)
class AttributeExtraction:
    """A frequency/seizure-free/change expression contributing attributes."""

    evidence: str
    span: tuple[int, int]
    attributes: Mapping[str, str] = field(default_factory=dict)
    kind: AttributeKind = AttributeKind.RATE
    rule_id: str = "unknown"
    rule_group: RuleGroup | None = None
    portability: Portability | None = None
