from __future__ import annotations

import re
from collections.abc import Sequence
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.core.evidence import locate_evidence
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic import (
    deterministic_extraction,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.deterministic_text import (
    exact_evidence,
    fallback_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import repair_prediction_label


class GraphNodeKind(StrEnum):
    FREQUENCY_RATE = "frequency_rate"
    CLUSTER_FREQUENCY = "cluster_frequency"
    SEIZURE_FREE = "seizure_free"
    LAST_EVENT_ONLY = "last_event_only"
    UNKNOWN_FREQUENCY = "unknown_frequency"
    NO_REFERENCE = "no_reference"


class EvidenceSpan(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str
    start_char: int | None = None
    end_char: int | None = None


class StateGraphNode(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_id: str
    kind: GraphNodeKind
    normalized_label: str | None
    semantic_kind: FrequencyLabelKind
    monthly_frequency: float
    evidence: EvidenceSpan
    assertion_status: str = "asserted"
    temporality: str = "current"
    certainty: str = "certain"
    applies_to: str | None = None
    rule_id: str = "unknown"
    graph_errors: tuple[str, ...] = ()

    @property
    def evidence_text(self) -> str:
        return self.evidence.text

    @property
    def evidence_start(self) -> int | None:
        return self.evidence.start_char

    @property
    def evidence_end(self) -> int | None:
        return self.evidence.end_char


class ClinicalFrequencyStateGraph(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_row_index: int | None = None
    nodes: tuple[StateGraphNode, ...] = ()
    competing_hypothesis_node_ids: tuple[str, ...] = ()
    missing_variable_flags: tuple[str, ...] = ()
    graph_builder: str = "deterministic_oracle_span_harvester_v0"
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


def build_state_graph(
    note_text: str,
    *,
    source_row_index: int | None = None,
    include_no_reference_fallback: bool = True,
) -> ClinicalFrequencyStateGraph:
    """Build a source-near graph from high-recall deterministic span candidates."""

    candidates = _state_graph_candidates(note_text)
    if include_no_reference_fallback and not candidates:
        candidates = [
            RawCandidate(
                kind=CandidateKind.NO_REFERENCE,
                label="no seizure frequency reference",
                evidence=fallback_evidence(note_text),
                rule_id="state_graph.no_reference_fallback",
            )
        ]

    nodes = _candidate_nodes(note_text, candidates)
    return ClinicalFrequencyStateGraph(
        source_row_index=source_row_index,
        nodes=tuple(nodes),
        competing_hypothesis_node_ids=_competing_hypothesis_ids(nodes),
        missing_variable_flags=_missing_variable_flags(nodes),
        metadata={"candidate_count": len(candidates)},
    )


def build_state_graph_from_atomic_claims(
    note_text: str,
    claims: Sequence[dict[str, Any]],
    *,
    source_row_index: int | None = None,
    graph_builder: str = "llm_atomic_claim_graph_builder_v0",
) -> ClinicalFrequencyStateGraph:
    """Build graph nodes from atomic claim rows after exact-evidence gating."""

    nodes = [
        _node_from_atomic_claim(index=index, claim=claim, note_text=note_text)
        for index, claim in enumerate(claims, start=1)
    ]
    return ClinicalFrequencyStateGraph(
        source_row_index=source_row_index,
        nodes=tuple(nodes),
        competing_hypothesis_node_ids=_competing_hypothesis_ids(nodes),
        missing_variable_flags=_missing_variable_flags(nodes),
        graph_builder=graph_builder,
        metadata={"claim_count": len(claims)},
    )


def graph_invariance_signature(graph: ClinicalFrequencyStateGraph) -> tuple[tuple[str, ...], ...]:
    """Return the graph fields expected to survive counterfactual paraphrase."""

    return tuple(
        sorted(
            (
                node.kind.value,
                node.semantic_kind.value,
                node.normalized_label or "",
                str(round(node.monthly_frequency, 4)),
                node.assertion_status,
                node.temporality,
                node.certainty,
            )
            for node in graph.nodes
        )
    )


def _candidate_nodes(note_text: str, candidates: Sequence[RawCandidate]) -> list[StateGraphNode]:
    ordered_candidates = sorted(
        candidates,
        key=lambda candidate: (_kind_sort_key(candidate.kind), candidate.evidence.lower()),
    )
    return [
        _node_from_candidate(index=index, candidate=candidate, note_text=note_text)
        for index, candidate in enumerate(ordered_candidates, start=1)
    ]


def _state_graph_candidates(note_text: str) -> list[RawCandidate]:
    candidates = [
        *deterministic_extraction._extract_candidates(note_text),
        *_partial_seizure_free_candidates(note_text),
    ]
    return _dedupe_overlapping_candidates(candidates)


def _partial_seizure_free_candidates(note_text: str) -> list[RawCandidate]:
    duration_tokens = (
        r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve"
    )
    pattern = re.compile(
        rf"\bNo\s+(?P<target>[\w -]+?)\s+seizures?\s+for\s+"
        rf"(?P<duration>{duration_tokens})\s+"
        r"(?P<unit>day|week|month|year)s?\b",
        re.IGNORECASE,
    )
    candidates: list[RawCandidate] = []
    for match in pattern.finditer(note_text):
        duration = _duration_value(match.group("duration"))
        unit = match.group("unit").lower()
        candidates.append(
            RawCandidate(
                kind=CandidateKind.SEIZURE_FREE,
                label=f"seizure free for {duration} {unit}",
                evidence=match.group(0),
                rule_id="state_graph.partial_seizure_free_duration",
                match_groups=match.groupdict(),
            )
        )
    return candidates


def _duration_value(token: str) -> str:
    return {
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
        "eleven": "11",
        "twelve": "12",
    }.get(token.lower(), token)


def _dedupe_overlapping_candidates(candidates: Sequence[RawCandidate]) -> list[RawCandidate]:
    selected: list[RawCandidate] = []
    candidates = _drop_reporting_context_overlaps(candidates)
    for candidate in sorted(candidates, key=lambda item: len(item.evidence)):
        candidate_key = (candidate.kind, repair_prediction_label(candidate.label))
        candidate_evidence = candidate.evidence.lower()
        if any(
            candidate_key == (existing.kind, repair_prediction_label(existing.label))
            and candidate_evidence in existing.evidence.lower()
            for existing in selected
        ):
            continue
        selected = [
            existing
            for existing in selected
            if not (
                candidate_key == (existing.kind, repair_prediction_label(existing.label))
                and existing.evidence.lower() in candidate_evidence
            )
        ]
        selected.append(candidate)
    return selected


def _drop_reporting_context_overlaps(candidates: Sequence[RawCandidate]) -> list[RawCandidate]:
    filtered: list[RawCandidate] = []
    for candidate in candidates:
        evidence = candidate.evidence.lower()
        has_better_contained_candidate = any(
            other is not candidate
            and other.kind is candidate.kind
            and other.evidence.lower() in evidence
            and len(other.evidence) < len(candidate.evidence)
            for other in candidates
        )
        if has_better_contained_candidate and re.match(
            r"^(?:one|another|later|earlier)\s+(?:section|note|diary|summary)\s+says\b",
            evidence,
        ):
            continue
        filtered.append(candidate)
    return filtered


def _node_from_candidate(
    *,
    index: int,
    candidate: RawCandidate,
    note_text: str,
) -> StateGraphNode:
    evidence = exact_evidence(note_text, candidate.evidence)
    span = locate_evidence(note_text, evidence)
    start_char, end_char = span if span else (None, None)
    normalized_label = repair_prediction_label(candidate.label)
    errors: tuple[str, ...] = ()
    try:
        label_record = label_to_frequency_record(normalized_label)
    except ValueError as exc:
        label_record = label_to_frequency_record("unknown")
        normalized_label = "unknown"
        errors = (str(exc),)

    return StateGraphNode(
        node_id=f"sg-{index:03d}",
        kind=_graph_kind(candidate.kind),
        normalized_label=normalized_label,
        semantic_kind=label_record.kind,
        monthly_frequency=label_record.monthly_frequency,
        evidence=EvidenceSpan(text=evidence, start_char=start_char, end_char=end_char),
        rule_id=candidate.rule_id,
        graph_errors=errors,
    )


def _node_from_atomic_claim(
    *,
    index: int,
    claim: dict[str, Any],
    note_text: str,
) -> StateGraphNode:
    evidence_text = str(claim.get("evidence") or "")
    span = locate_evidence(note_text, evidence_text) if evidence_text else None
    start_char, end_char = span if span else (None, None)
    errors: list[str] = []
    if span is None:
        errors.append("atomic_claim_evidence_not_exact")

    normalized_label = _atomic_claim_label(claim)
    try:
        label_record = label_to_frequency_record(normalized_label)
    except ValueError as exc:
        label_record = label_to_frequency_record("unknown")
        normalized_label = "unknown"
        errors.append(str(exc))

    return StateGraphNode(
        node_id=f"llm-sg-{index:03d}",
        kind=_atomic_graph_kind(str(claim.get("kind") or claim.get("claim_type") or "")),
        normalized_label=normalized_label,
        semantic_kind=label_record.kind,
        monthly_frequency=label_record.monthly_frequency,
        evidence=EvidenceSpan(text=evidence_text, start_char=start_char, end_char=end_char),
        assertion_status=str(claim.get("assertion_status") or "unknown"),
        temporality=str(claim.get("temporality") or "unclear"),
        certainty="certain" if span is not None else "unknown",
        applies_to=_optional_text(claim.get("applies_to") or claim.get("semiology")),
        rule_id=str(claim.get("rule_id") or "llm.atomic_claim"),
        graph_errors=tuple(errors),
    )


def _atomic_claim_label(claim: dict[str, Any]) -> str:
    raw_label = claim.get("normalized_label") or claim.get("final_label")
    kind = str(claim.get("kind") or claim.get("claim_type") or "")
    if raw_label:
        return repair_prediction_label(str(raw_label))
    if kind == "no_reference":
        return "no seizure frequency reference"
    return "unknown"


def _atomic_graph_kind(kind: str) -> GraphNodeKind:
    return {
        "frequency_rate": GraphNodeKind.FREQUENCY_RATE,
        "frequency": GraphNodeKind.FREQUENCY_RATE,
        "cluster_frequency": GraphNodeKind.CLUSTER_FREQUENCY,
        "seizure_free": GraphNodeKind.SEIZURE_FREE,
        "last_event_only": GraphNodeKind.LAST_EVENT_ONLY,
        "unknown_frequency": GraphNodeKind.UNKNOWN_FREQUENCY,
        "unknown": GraphNodeKind.UNKNOWN_FREQUENCY,
        "no_reference": GraphNodeKind.NO_REFERENCE,
    }.get(kind, GraphNodeKind.UNKNOWN_FREQUENCY)


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _graph_kind(candidate_kind: CandidateKind) -> GraphNodeKind:
    return {
        CandidateKind.FREQUENCY_RATE: GraphNodeKind.FREQUENCY_RATE,
        CandidateKind.CLUSTER_FREQUENCY: GraphNodeKind.CLUSTER_FREQUENCY,
        CandidateKind.SEIZURE_FREE: GraphNodeKind.SEIZURE_FREE,
        CandidateKind.UNKNOWN_FREQUENCY: GraphNodeKind.UNKNOWN_FREQUENCY,
        CandidateKind.NO_REFERENCE: GraphNodeKind.NO_REFERENCE,
    }[candidate_kind]


def _kind_sort_key(candidate_kind: CandidateKind) -> int:
    return {
        CandidateKind.FREQUENCY_RATE: 0,
        CandidateKind.CLUSTER_FREQUENCY: 1,
        CandidateKind.SEIZURE_FREE: 2,
        CandidateKind.UNKNOWN_FREQUENCY: 3,
        CandidateKind.NO_REFERENCE: 4,
    }[candidate_kind]


def _competing_hypothesis_ids(nodes: Sequence[StateGraphNode]) -> tuple[str, ...]:
    frequency_nodes = [
        node
        for node in nodes
        if node.semantic_kind is FrequencyLabelKind.FREQUENCY
        and node.temporality == "current"
        and node.assertion_status == "asserted"
    ]
    labels = {node.normalized_label for node in frequency_nodes}
    if len(labels) <= 1:
        return ()
    return tuple(node.node_id for node in frequency_nodes)


def _missing_variable_flags(nodes: Sequence[StateGraphNode]) -> tuple[str, ...]:
    flags: list[str] = []
    if any(node.semantic_kind is FrequencyLabelKind.UNKNOWN for node in nodes):
        flags.append("frequency_unquantified")
    if any(node.graph_errors for node in nodes):
        flags.append("normalization_error")
    return tuple(flags)
