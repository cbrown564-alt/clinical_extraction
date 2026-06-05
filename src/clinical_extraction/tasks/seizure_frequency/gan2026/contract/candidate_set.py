"""Source-near candidate-set contract for the Gan 2026 architecture reset."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from clinical_extraction.core.evidence import locate_evidence
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind as DeterministicCandidateKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    RawCandidate,
)

SCHEMA_VERSION = "gan2026_candidate_set_source_near_v0"

CandidateKind = Literal[
    "frequency_rate",
    "cluster_frequency",
    "seizure_free",
    "last_event_only",
    "unknown_frequency",
    "no_reference",
]
SourceType = Literal["deterministic_candidate", "state_graph_node", "llm_candidate"]
EventType = Literal["seizure", "seizure_like_event", "non_epileptic_event", "unclear_event"]
Temporality = Literal["current", "recent", "historical", "unclear"]
Certainty = Literal["certain", "uncertain"]
CertaintyReason = Literal[
    "vague_count",
    "unclear_time_period",
    "approximate_wording",
    "conditional_statement",
    "other",
]
AssertionStatus = Literal["asserted", "negated", "uncertain", "conditional"]


class EvidenceSpan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    start_char: int | None = None
    end_char: int | None = None


class FrequencyDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: str | None = None
    count_range: str | None = None
    time_period: str | None = None
    time_period_range: str | None = None
    source_phrase: str


class SeizureFreeDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    duration: str | None = None
    anchor: str | None = None
    source_phrase: str


class LastEventOnlyDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_timing: str | None = None
    event_count: str | None = None
    source_phrase: str


class ClusterDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cluster_frequency: str | None = None
    events_per_cluster: str | None = None
    cluster_count: str | None = None
    cluster_period: str | None = None


class SourcePhraseOnlyDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_phrase: str


class ExtractedCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    component_owner: str
    source_type: SourceType
    source_artifact: str
    source_row_index: int
    candidate_kind: CandidateKind
    event_type: EventType
    event_subtype: str | None = None
    frequency: FrequencyDetails | None = None
    seizure_free: SeizureFreeDetails | None = None
    last_event_only: LastEventOnlyDetails | None = None
    cluster_details: ClusterDetails | None = None
    unknown_frequency: SourcePhraseOnlyDetails | None = None
    no_reference: SourcePhraseOnlyDetails | None = None
    temporality: Temporality
    certainty: Certainty
    certainty_reason: CertaintyReason | None = None
    assertion_status: AssertionStatus
    evidence_span: EvidenceSpan
    source_ids: list[str]
    extraction_issues: list[str] = Field(default_factory=list)
    clinical_or_policy: Literal["clinical"]

    @model_validator(mode="after")
    def validate_kind_detail(self) -> ExtractedCandidate:
        detail_by_kind = {
            "frequency_rate": self.frequency,
            "cluster_frequency": self.cluster_details,
            "seizure_free": self.seizure_free,
            "last_event_only": self.last_event_only,
            "unknown_frequency": self.unknown_frequency,
            "no_reference": self.no_reference,
        }
        populated = [name for name, value in detail_by_kind.items() if value is not None]
        if populated != [self.candidate_kind]:
            raise ValueError(
                "candidate_kind must have exactly one matching detail object; "
                f"candidate_kind={self.candidate_kind!r}, populated={populated!r}"
            )
        if self.certainty == "certain" and self.certainty_reason is not None:
            raise ValueError("certainty_reason must be null when certainty is certain")
        if self.certainty == "uncertain" and self.certainty_reason is None:
            raise ValueError("certainty_reason is required when certainty is uncertain")
        return self


class CandidateSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_row_index: int
    component_owner: str
    source_artifacts: list[str]
    candidates: list[ExtractedCandidate]
    assembly_issues: list[str] = Field(default_factory=list)
    schema_version: Literal["gan2026_candidate_set_source_near_v0"] = SCHEMA_VERSION


def candidate_source_phrase(candidate: ExtractedCandidate) -> str | None:
    if candidate.frequency is not None:
        return candidate.frequency.source_phrase
    if candidate.cluster_details is not None:
        return (
            candidate.cluster_details.cluster_frequency
            or candidate.cluster_details.events_per_cluster
            or candidate.cluster_details.cluster_count
            or candidate.cluster_details.cluster_period
        )
    if candidate.seizure_free is not None:
        return candidate.seizure_free.source_phrase
    if candidate.last_event_only is not None:
        return candidate.last_event_only.source_phrase
    if candidate.unknown_frequency is not None:
        return candidate.unknown_frequency.source_phrase
    if candidate.no_reference is not None:
        return candidate.no_reference.source_phrase
    return None


def deterministic_candidate_set_from_raw(
    raw_candidates: Sequence[RawCandidate],
    *,
    note_text: str,
    source_row_index: int,
    component_owner: str = "deterministic_candidate_extraction",
    source_artifact: str = "gan2026_deterministic_raw_candidates",
) -> CandidateSet:
    candidates = [
        extracted_candidate_from_raw(
            raw_candidate,
            index=index,
            note_text=note_text,
            source_row_index=source_row_index,
            component_owner=component_owner,
            source_artifact=source_artifact,
        )
        for index, raw_candidate in enumerate(raw_candidates, start=1)
    ]
    return CandidateSet(
        source_row_index=source_row_index,
        component_owner=component_owner,
        source_artifacts=[source_artifact],
        candidates=candidates,
    )


def extracted_candidate_from_raw(
    raw_candidate: RawCandidate,
    *,
    index: int,
    note_text: str,
    source_row_index: int,
    component_owner: str = "deterministic_candidate_extraction",
    source_artifact: str = "gan2026_deterministic_raw_candidates",
) -> ExtractedCandidate:
    evidence = raw_candidate.evidence
    span = locate_evidence(note_text, evidence)
    start_char, end_char = span if span else (None, None)
    source_id = (
        f"note:{source_row_index}:span:{start_char}-{end_char}"
        if span
        else f"note:{source_row_index}:span:unresolved:{index}"
    )
    issues = []
    if raw_candidate.label:
        issues.append("deterministic_label_carried_as_extraction_provenance_only")
    if span is None:
        issues.append("evidence_span_unresolved")
    return ExtractedCandidate(
        candidate_id=f"det:{source_row_index}:{index}",
        component_owner=component_owner,
        source_type="deterministic_candidate",
        source_artifact=source_artifact,
        source_row_index=source_row_index,
        candidate_kind=_candidate_kind(raw_candidate.kind),
        event_type="seizure",
        event_subtype=None,
        frequency=_frequency_details(raw_candidate),
        seizure_free=_seizure_free_details(raw_candidate),
        last_event_only=None,
        cluster_details=_cluster_details(raw_candidate),
        unknown_frequency=_unknown_details(raw_candidate),
        no_reference=_no_reference_details(raw_candidate),
        temporality="unclear",
        certainty="certain",
        certainty_reason=None,
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence, start_char=start_char, end_char=end_char),
        source_ids=[source_id],
        extraction_issues=issues,
        clinical_or_policy="clinical",
    )


def _candidate_kind(kind: DeterministicCandidateKind) -> CandidateKind:
    return kind.value  # type: ignore[return-value]


def _frequency_details(raw_candidate: RawCandidate) -> FrequencyDetails | None:
    if raw_candidate.kind is not DeterministicCandidateKind.FREQUENCY_RATE:
        return None
    return FrequencyDetails(source_phrase=raw_candidate.evidence)


def _seizure_free_details(raw_candidate: RawCandidate) -> SeizureFreeDetails | None:
    if raw_candidate.kind is not DeterministicCandidateKind.SEIZURE_FREE:
        return None
    return SeizureFreeDetails(source_phrase=raw_candidate.evidence)


def _cluster_details(raw_candidate: RawCandidate) -> ClusterDetails | None:
    if raw_candidate.kind is not DeterministicCandidateKind.CLUSTER_FREQUENCY:
        return None
    return ClusterDetails(cluster_frequency=raw_candidate.evidence)


def _unknown_details(raw_candidate: RawCandidate) -> SourcePhraseOnlyDetails | None:
    if raw_candidate.kind is not DeterministicCandidateKind.UNKNOWN_FREQUENCY:
        return None
    return SourcePhraseOnlyDetails(source_phrase=raw_candidate.evidence)


def _no_reference_details(raw_candidate: RawCandidate) -> SourcePhraseOnlyDetails | None:
    if raw_candidate.kind is not DeterministicCandidateKind.NO_REFERENCE:
        return None
    return SourcePhraseOnlyDetails(source_phrase=raw_candidate.evidence)
