from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

from .rule_metadata import (
    Portability,
    RuleGroup,
)

if TYPE_CHECKING:
    from .find_encode import FindFact


class DeferredDrop(StrEnum):
    """Select-owned drops that find still emits onto the ledger."""

    RULE_EXCLUDE = "select.rule_exclude_drop"
    MEDICATION_DOSE_DISTRACTOR = "select.medication_dose_distractor_drop"
    HISTORICAL_LEAD_IN = "select.historical_lead_in_drop"


class CandidateKind(StrEnum):
    FREQUENCY_RATE = "frequency_rate"
    CLUSTER_FREQUENCY = "cluster_frequency"
    SEIZURE_FREE = "seizure_free"
    UNKNOWN_FREQUENCY = "unknown_frequency"
    NO_REFERENCE = "no_reference"


@dataclass(frozen=True)
class RawCandidate:
    kind: CandidateKind
    label: str | None
    evidence: str
    rule_id: str = "unknown"
    rule_group: RuleGroup | None = None
    portability: Portability | None = None
    match_groups: Mapping[str, str | None] = field(default_factory=dict)
    find_fact: FindFact | None = None
    deferred_drop: str | None = None
