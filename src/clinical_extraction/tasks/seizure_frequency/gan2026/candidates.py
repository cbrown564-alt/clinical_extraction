from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    Portability,
    RuleGroup,
)


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
