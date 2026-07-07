"""Optional extract-stage producer: state graph nodes -> CandidateSet + pipeline events."""

from __future__ import annotations

from clinical_extraction.core.evidence import locate_evidence
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    AssertionStatus,
    CandidateSet,
    Certainty,
    CertaintyReason,
    ClusterDetails,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
    LastEventOnlyDetails,
    SeizureFreeDetails,
    SourcePhraseOnlyDetails,
    Temporality,
    extract_row_context,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateKind as ContractCandidateKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import (
    CandidateEvent,
    _candidate_event,
)

from .graph import ClinicalFrequencyStateGraph, GraphNodeKind, StateGraphNode, build_state_graph

_STATE_GRAPH_COMPONENT_OWNER = "state_graph_extraction"
_STATE_GRAPH_SOURCE_ARTIFACT = "gan2026_state_graph_nodes"


def extract_stage(
    note_text: str,
    *,
    source_row_index: int,
) -> tuple[tuple[RawCandidate, ...], CandidateSet, tuple[CandidateEvent, ...]]:
    """Extract via the clinical frequency state graph harvester.

    Builds a source-near graph, materializes ``CandidateSet`` candidates with
    ``source_type="state_graph_node"``, and shapes compatible ``RawCandidate`` /
    ``CandidateEvent`` tuples for the canonical normalize/select downstream stages.
    """
    graph = build_state_graph(
        note_text,
        source_row_index=source_row_index,
        include_no_reference_fallback=True,
    )
    return materialize_state_graph_extract(graph, note_text=note_text)


def materialize_state_graph_extract(
    graph: ClinicalFrequencyStateGraph,
    *,
    note_text: str,
) -> tuple[tuple[RawCandidate, ...], CandidateSet, tuple[CandidateEvent, ...]]:
    source_row_index = graph.source_row_index or 1
    raw_candidates = tuple(raw_candidate_from_state_graph_node(node) for node in graph.nodes)
    candidate_set = state_graph_candidate_set_from_graph(
        graph,
        note_text=note_text,
        source_row_index=source_row_index,
    )
    candidate_events = tuple(
        _candidate_event(index=index, candidate=candidate, note_text=note_text)
        for index, candidate in enumerate(raw_candidates, start=1)
    )
    return raw_candidates, candidate_set, candidate_events


def state_graph_candidate_set_from_graph(
    graph: ClinicalFrequencyStateGraph,
    *,
    note_text: str,
    source_row_index: int,
    component_owner: str = _STATE_GRAPH_COMPONENT_OWNER,
    source_artifact: str = _STATE_GRAPH_SOURCE_ARTIFACT,
) -> CandidateSet:
    candidates = [
        extracted_candidate_from_state_graph_node(
            node,
            note_text=note_text,
            source_row_index=source_row_index,
            component_owner=component_owner,
            source_artifact=source_artifact,
        )
        for node in graph.nodes
    ]
    return CandidateSet(
        source_row_index=source_row_index,
        component_owner=component_owner,
        source_artifacts=[source_artifact],
        row_context=extract_row_context(note_text),
        candidates=candidates,
    )


def raw_candidate_from_state_graph_node(node: StateGraphNode) -> RawCandidate:
    return RawCandidate(
        kind=_raw_candidate_kind(node.kind),
        label=node.normalized_label,
        evidence=node.evidence.text,
        rule_id=node.rule_id,
    )


def extracted_candidate_from_state_graph_node(
    node: StateGraphNode,
    *,
    note_text: str,
    source_row_index: int,
    component_owner: str = _STATE_GRAPH_COMPONENT_OWNER,
    source_artifact: str = _STATE_GRAPH_SOURCE_ARTIFACT,
) -> ExtractedCandidate:
    candidate_kind = _contract_candidate_kind(node.kind)
    evidence_text = node.evidence.text
    start_char = node.evidence.start_char
    end_char = node.evidence.end_char
    if start_char is None or end_char is None:
        span = locate_evidence(note_text, evidence_text)
        if span:
            start_char, end_char = span
    source_id = (
        f"note:{source_row_index}:span:{start_char}-{end_char}"
        if start_char is not None and end_char is not None
        else f"note:{source_row_index}:node:{node.node_id}"
    )
    issues: list[str] = []
    if node.graph_errors:
        issues.extend(f"state_graph_error:{error}" for error in node.graph_errors)
    if start_char is None or end_char is None:
        issues.append("evidence_span_unresolved")

    certainty, certainty_reason = _certainty_fields(node)
    return ExtractedCandidate(
        candidate_id=f"sg:{source_row_index}:{node.node_id}",
        component_owner=component_owner,
        source_type="state_graph_node",
        source_artifact=source_artifact,
        source_row_index=source_row_index,
        candidate_kind=candidate_kind,
        event_type="seizure",
        event_subtype=node.applies_to,
        frequency=_frequency_details(candidate_kind, evidence_text),
        seizure_free=_seizure_free_details(candidate_kind, evidence_text),
        last_event_only=_last_event_only_details(candidate_kind, evidence_text),
        cluster_details=_cluster_details(candidate_kind, evidence_text),
        unknown_frequency=_unknown_details(candidate_kind, evidence_text),
        no_reference=_no_reference_details(candidate_kind, evidence_text),
        temporality=_temporality(node.temporality),
        certainty=certainty,
        certainty_reason=certainty_reason,
        assertion_status=_assertion_status(node.assertion_status),
        evidence_span=EvidenceSpan(
            text=evidence_text,
            start_char=start_char,
            end_char=end_char,
        ),
        source_ids=[source_id, node.node_id],
        extraction_issues=issues,
        clinical_or_policy="clinical",
    )


def _raw_candidate_kind(kind: GraphNodeKind) -> CandidateKind:
    if kind is GraphNodeKind.LAST_EVENT_ONLY:
        return CandidateKind.UNKNOWN_FREQUENCY
    return CandidateKind(kind.value)


def _contract_candidate_kind(kind: GraphNodeKind) -> ContractCandidateKind:
    return kind.value  # type: ignore[return-value]


def _temporality(value: str) -> Temporality:
    if value in {"current", "recent", "historical", "unclear"}:
        return value  # type: ignore[return-value]
    return "unclear"


def _assertion_status(value: str) -> AssertionStatus:
    if value in {"asserted", "negated", "uncertain", "conditional"}:
        return value  # type: ignore[return-value]
    return "uncertain"


def _certainty_fields(node: StateGraphNode) -> tuple[Certainty, CertaintyReason | None]:
    if node.certainty == "certain" and not node.graph_errors:
        return "certain", None
    reason: CertaintyReason = "other"
    if node.graph_errors:
        reason = "approximate_wording"
    return "uncertain", reason


def _frequency_details(
    candidate_kind: ContractCandidateKind,
    evidence_text: str,
) -> FrequencyDetails | None:
    if candidate_kind != "frequency_rate":
        return None
    return FrequencyDetails(source_phrase=evidence_text)


def _seizure_free_details(
    candidate_kind: ContractCandidateKind,
    evidence_text: str,
) -> SeizureFreeDetails | None:
    if candidate_kind != "seizure_free":
        return None
    return SeizureFreeDetails(source_phrase=evidence_text)


def _last_event_only_details(
    candidate_kind: ContractCandidateKind,
    evidence_text: str,
) -> LastEventOnlyDetails | None:
    if candidate_kind != "last_event_only":
        return None
    return LastEventOnlyDetails(source_phrase=evidence_text)


def _cluster_details(
    candidate_kind: ContractCandidateKind,
    evidence_text: str,
) -> ClusterDetails | None:
    if candidate_kind != "cluster_frequency":
        return None
    return ClusterDetails(cluster_frequency=evidence_text)


def _unknown_details(
    candidate_kind: ContractCandidateKind,
    evidence_text: str,
) -> SourcePhraseOnlyDetails | None:
    if candidate_kind != "unknown_frequency":
        return None
    return SourcePhraseOnlyDetails(source_phrase=evidence_text)


def _no_reference_details(
    candidate_kind: ContractCandidateKind,
    evidence_text: str,
) -> SourcePhraseOnlyDetails | None:
    if candidate_kind != "no_reference":
        return None
    return SourcePhraseOnlyDetails(source_phrase=evidence_text)
