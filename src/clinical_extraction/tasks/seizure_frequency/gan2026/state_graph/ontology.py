"""The admissible-state ontology: the fixed boundary the generator may not cross.

This is line 3.2 of the KG-grounded component-generation design note. The
``FrequencyLabelKind`` lattice is encoded as an explicit constraint object that
governs (a) which ``evidence -> state`` assignments a node may carry and (b)
which typed-edge transitions are legal. Two rules matter most, because they are
the project's two no-correct-component failure shapes:

1. **No over-inference out of ``unknown``.** Last-event-only, open-ended
   "since", vague-count, conditional-only, and relative-trend evidence may only
   anchor an ``unknown``/``no_reference`` node. They may *not* mint a
   ``frequency`` or ``seizure_free`` node. As an ontology constraint this is a
   generation-time guard, so the over-inferred component is never minted - rather
   than being reactively suppressed by a selector micro-gate after the fact.

2. **Cluster cadence preserved, burden refinable.** A cluster node's cadence is
   immutable under ``REFINES``; only events-per-cluster may be refined.
"""

from __future__ import annotations

import re
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)

from .edges import (
    GraphEdge,
    GraphEdgeKind,
    GraphNodeKind,
    cadence_period,
    per_cluster_count_text,
)
from .graph import StateGraphNode

# The legal states of the lattice (design note 3.2).
ADMISSIBLE_STATES: frozenset[FrequencyLabelKind] = frozenset(
    {
        FrequencyLabelKind.FREQUENCY,
        FrequencyLabelKind.SEIZURE_FREE,
        FrequencyLabelKind.UNKNOWN,
        FrequencyLabelKind.NO_REFERENCE,
        FrequencyLabelKind.UNRESOLVED_MULTIPLE,
    }
)

# States a quantifying assignment (frequency / seizure_free) over-infers into when
# the supporting evidence is one of the unknown-only shapes below.
_QUANTIFYING_STATES: frozenset[FrequencyLabelKind] = frozenset(
    {FrequencyLabelKind.FREQUENCY, FrequencyLabelKind.SEIZURE_FREE}
)


class EvidenceShape(StrEnum):
    """The evidence shape an admission decision keys off."""

    LAST_EVENT_ONLY = "last_event_only"
    OPEN_ENDED_SINCE = "open_ended_since"
    VAGUE_COUNT = "vague_count"
    CONDITIONAL_ONLY = "conditional_only"
    RELATIVE_TREND = "relative_trend"
    QUANTIFIED = "quantified"
    OTHER = "other"


# Evidence shapes that may only anchor unknown / no_reference, never a quantified
# frequency or a seizure-free duration.
UNKNOWN_ONLY_SHAPES: frozenset[EvidenceShape] = frozenset(
    {
        EvidenceShape.LAST_EVENT_ONLY,
        EvidenceShape.OPEN_ENDED_SINCE,
        EvidenceShape.VAGUE_COUNT,
        EvidenceShape.CONDITIONAL_ONLY,
        EvidenceShape.RELATIVE_TREND,
    }
)

# rule_id prefixes that already declare an unknown-only shape at build time.
_RULE_SHAPE_PREFIXES: tuple[tuple[str, EvidenceShape], ...] = (
    ("projection_policy.acd_003", EvidenceShape.VAGUE_COUNT),
    ("projection_policy.acd_004", EvidenceShape.CONDITIONAL_ONLY),
    ("projection_policy.acd_005", EvidenceShape.RELATIVE_TREND),
)

_RATE_TOKEN_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:to\s*\d+(?:\.\d+)?\s*)?(?:per|/|a)\s*(?:day|week|month|year)",
    re.IGNORECASE,
)
_PER_PERIOD_RE = re.compile(r"\bper\s+(?:day|week|month|year)s?\b", re.IGNORECASE)
_DENOMINATOR_RE = re.compile(
    r"\b(?:per\s+(?:day|week|month|year)|daily|weekly|monthly|yearly|nightly"
    r"|each\s+(?:day|week|month|year)|a\s+(?:day|week|month|year)"
    r"|last\s+(?:week|month|year)|in\s+the\s+(?:past|last)\s+(?:week|month|year))\b",
    re.IGNORECASE,
)
_LAST_EVENT_RE = re.compile(r"\blast\s+(?:seizure|event|episode|fit|attack)\b", re.IGNORECASE)
_OPEN_ENDED_SINCE_RE = re.compile(r"\bsince\b(?![^.]*\b\d+\b[^.]*\b(?:per|/|a)\b)", re.IGNORECASE)
_VAGUE_COUNT_RE = re.compile(
    r"\b(?:occasional|occasionally|a\s+few|few|several|handful|some|multiple|"
    r"rare|rarely|infrequent|sporadic|intermittent)\b",
    re.IGNORECASE,
)
_RELATIVE_TREND_RE = re.compile(
    r"\b(?:increased|decreased|improved|worsened|reduced|risen|fallen|"
    r"better|worse|more|fewer|less)\b",
    re.IGNORECASE,
)
# A vague *count of clusters* ("several clusters per month") - the counted noun is
# "clusters", distinct from a vague cluster *size* ("multiple per cluster", which
# counts events per cluster). The former must not be rescued into a quantified
# frequency by its trailing cadence denominator (register C4 / v6 null-route).
_VAGUE_CLUSTER_COUNT_RE = re.compile(
    r"\b(?:occasional|a\s+few|few|several|handful|some|multiple|many|numerous|"
    r"rare|sporadic|intermittent)\s+clusters\b",
    re.IGNORECASE,
)

# Node-id prefix the LLM atomic-claim builder assigns
# (graph.py::build_state_graph_from_atomic_claims). Curated deterministic nodes
# carry vetted rule_ids and an ``sg-`` prefix and are trusted; only uncurated,
# LLM-generated nodes are subject to the over-inference guard (ADR 0017 /
# register C2: the guard runs at graph generation, on the prediction-bearing LLM
# component, not over the curated deterministic path).
_LLM_GENERATED_NODE_ID_PREFIX = "llm-sg-"


def is_uncurated_node(node: StateGraphNode) -> bool:
    """Whether a node is an uncurated, LLM-generated component.

    The over-inference-out-of-``unknown`` guard applies only to these; curated
    deterministic nodes are trusted (ADR ``0017``, register C2).
    """

    return node.node_id.startswith(_LLM_GENERATED_NODE_ID_PREFIX)


def classify_evidence_shape(node: StateGraphNode) -> EvidenceShape:
    """Classify the supporting evidence of a node into an admissibility shape.

    Rule-id declarations win first (the deterministic builder already tags the
    acd_003/004/005 shapes), then the node kind, then text heuristics. A node
    whose evidence carries an explicit rate/denominator is ``QUANTIFIED`` and may
    legally bear a frequency state.
    """

    for prefix, shape in _RULE_SHAPE_PREFIXES:
        if node.rule_id.startswith(prefix):
            return shape

    if node.kind is GraphNodeKind.LAST_EVENT_ONLY:
        return EvidenceShape.LAST_EVENT_ONLY

    text = node.evidence.text

    # C4 guard: a vague *count of clusters* is unknown-only despite a trailing
    # cadence denominator. This must run *before* the rate/denominator
    # short-circuit, which would otherwise classify "several clusters per month"
    # as QUANTIFIED (the "per month" hits ``_DENOMINATOR_RE``). A vague cluster
    # *size* ("multiple per cluster") is a different axis, left to VAGUE_COUNT
    # below, and is untouched on the deterministic path.
    if _VAGUE_CLUSTER_COUNT_RE.search(text):
        return EvidenceShape.VAGUE_COUNT

    has_rate = bool(_RATE_TOKEN_RE.search(text) or _PER_PERIOD_RE.search(text))
    has_denominator = bool(_DENOMINATOR_RE.search(text))

    if has_rate or has_denominator:
        return EvidenceShape.QUANTIFIED

    if _LAST_EVENT_RE.search(text):
        return EvidenceShape.LAST_EVENT_ONLY
    if _VAGUE_COUNT_RE.search(text):
        return EvidenceShape.VAGUE_COUNT
    if _RELATIVE_TREND_RE.search(text):
        return EvidenceShape.RELATIVE_TREND
    if _OPEN_ENDED_SINCE_RE.search(text):
        return EvidenceShape.OPEN_ENDED_SINCE
    return EvidenceShape.OTHER


class AdmissibilityResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    admissible: bool
    reason: str
    evidence_shape: EvidenceShape | None = None


class AdmissibleStateOntology(BaseModel):
    """The fixed-boundary constraint object over states and edge transitions."""

    model_config = ConfigDict(frozen=True)

    ontology_id: str = "gan2026_admissible_state_ontology_v1"

    def is_admissible_assignment(self, node: StateGraphNode) -> AdmissibilityResult:
        """Whether a node's ``evidence -> state`` assignment may be admitted."""

        if node.semantic_kind not in ADMISSIBLE_STATES:
            return AdmissibilityResult(
                admissible=False,
                reason=f"state_not_in_lattice:{node.semantic_kind.value}",
            )

        shape = classify_evidence_shape(node)
        # The over-inference guard is graph-path-only (ADR 0017 / register C2): it
        # constrains uncurated, LLM-generated mints; curated deterministic nodes
        # are trusted. Applying it to the curated path regressed Stage A by -82
        # (the v0.10 deterministic-repair lesson), so correctness comes from a new
        # clean competing component, not from suppressing curated over-reads.
        if (
            is_uncurated_node(node)
            and shape in UNKNOWN_ONLY_SHAPES
            and node.semantic_kind in _QUANTIFYING_STATES
        ):
            return AdmissibilityResult(
                admissible=False,
                reason=f"over_inference_out_of_unknown:{shape.value}",
                evidence_shape=shape,
            )
        return AdmissibilityResult(
            admissible=True,
            reason="admissible_assignment",
            evidence_shape=shape,
        )

    def is_admissible_transition(
        self,
        edge: GraphEdge,
        *,
        source: StateGraphNode,
        target: StateGraphNode,
    ) -> AdmissibilityResult:
        """Whether a typed edge is a legal transition under the lattice."""

        if edge.kind is GraphEdgeKind.SUPERSEDES:
            # Recency override is always legal between same-target state nodes.
            return AdmissibilityResult(admissible=True, reason="supersedes_recency")
        if edge.kind is GraphEdgeKind.CONTRADICTS:
            # A contradiction is a flag, not a state change; always legal to record.
            return AdmissibilityResult(admissible=True, reason="contradicts_flag")
        # REFINES: cluster cadence is immutable; only burden / vagueness may refine.
        return self._is_admissible_refinement(source=source, target=target)

    def _is_admissible_refinement(
        self,
        *,
        source: StateGraphNode,
        target: StateGraphNode,
    ) -> AdmissibilityResult:
        both_cluster = (
            source.kind is GraphNodeKind.CLUSTER_FREQUENCY
            and target.kind is GraphNodeKind.CLUSTER_FREQUENCY
        )
        if both_cluster:
            source_period = cadence_period(source)
            target_period = cadence_period(target)
            if (
                source_period is not None
                and target_period is not None
                and source_period != target_period
            ):
                return AdmissibilityResult(
                    admissible=False,
                    reason="refine_changes_cluster_cadence",
                )
            if per_cluster_count_text(source) is None:
                return AdmissibilityResult(
                    admissible=False,
                    reason="cluster_refine_without_burden",
                )
            return AdmissibilityResult(admissible=True, reason="cluster_burden_refinement")
        # Count+window over a vague mention: target must be the vaguer state.
        if target.semantic_kind in {
            FrequencyLabelKind.UNKNOWN,
            FrequencyLabelKind.UNRESOLVED_MULTIPLE,
        }:
            return AdmissibilityResult(admissible=True, reason="count_window_refinement")
        return AdmissibilityResult(admissible=False, reason="refine_target_not_vaguer")


def label_parses(label: str | None) -> bool:
    """Structural check: the normalized label parses under the scoring grammar."""

    if not label:
        return False
    try:
        label_to_frequency_record(label)
    except ValueError:
        return False
    return True
