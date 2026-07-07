from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import boundary_band, map_purist

from .graph import ClinicalFrequencyStateGraph, StateGraphNode, build_state_graph
from .ontology import AdmissibleStateOntology, classify_evidence_shape
from .projection import project_graph_to_gan
from .resolve import resolve_label
from .validation import dual_validate_graph


class OracleCoverageSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    row_count: int
    representable_count: int
    representable_rate: float
    by_gold_kind: dict[str, dict[str, int | float]]
    missing_source_row_indices: tuple[int, ...]


def oracle_coverage_summary(records: Sequence[GanFrequencyRecord]) -> OracleCoverageSummary:
    row_count = len(records)
    representable = 0
    by_kind_total: Counter[str] = Counter()
    by_kind_representable: Counter[str] = Counter()
    missing_indices: list[int] = []

    for record in records:
        gold_kind = record.gold_label_kind.value
        by_kind_total[gold_kind] += 1
        graph = build_state_graph(
            record.note_text,
            source_row_index=record.source_row_index,
            include_no_reference_fallback=True,
        )
        if _gold_is_representable(record, graph_node_labels(graph)):
            representable += 1
            by_kind_representable[gold_kind] += 1
        else:
            missing_indices.append(record.source_row_index)

    return OracleCoverageSummary(
        row_count=row_count,
        representable_count=representable,
        representable_rate=_rounded_rate(representable, row_count),
        by_gold_kind={
            kind: {
                "total": by_kind_total[kind],
                "representable": by_kind_representable[kind],
                "representable_rate": _rounded_rate(
                    by_kind_representable[kind],
                    by_kind_total[kind],
                ),
            }
            for kind in sorted(by_kind_total)
        },
        missing_source_row_indices=tuple(missing_indices),
    )


def graph_node_labels(graph) -> tuple[tuple[FrequencyLabelKind, str | None], ...]:
    return tuple((node.semantic_kind, node.normalized_label) for node in graph.nodes)


def _gold_is_representable(
    record: GanFrequencyRecord,
    node_labels: Sequence[tuple[FrequencyLabelKind, str | None]],
) -> bool:
    if record.gold_label_kind in {
        FrequencyLabelKind.UNKNOWN,
        FrequencyLabelKind.NO_REFERENCE,
        FrequencyLabelKind.SEIZURE_FREE,
    }:
        return any(kind is record.gold_label_kind for kind, _label in node_labels)
    return any(label == record.gold_normalized_label for _kind, label in node_labels)


def _rounded_rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


# --------------------------------------------------------------------------- #
# Stage A - ontology/edge-enriched oracle uplift, broken out by family band.
# --------------------------------------------------------------------------- #


class BandCoverage(BaseModel):
    model_config = ConfigDict(frozen=True)

    band: str
    total: int
    baseline_representable: int
    admitted_representable: int
    projection_correct: int
    resolve_correct: int


class OntologyCoverageSummary(BaseModel):
    """Stage A readout: representability and label correctness after the ontology
    + typed-edge enrichment, compared against the pre-enrichment baseline.

    ``projection_correct`` is the existing ``project_graph_to_gan`` Purist
    correctness; ``resolve_correct`` is the new edge-aware ``resolve_label``
    query. The Stage A gate asks whether ``resolve_label`` lifts Purist
    correctness over the no-correct-component residual - concentrated in
    ``band_unknown`` and ``band_weekly`` - without breaking bands the baseline
    already handled.
    """

    model_config = ConfigDict(frozen=True)

    ontology_id: str
    row_count: int
    baseline_representable: int
    admitted_representable: int
    projection_correct: int
    resolve_correct: int
    resolve_minus_projection: int
    by_band: dict[str, BandCoverage]
    resolve_gain_source_row_indices: tuple[int, ...]
    resolve_regression_source_row_indices: tuple[int, ...]


def ontology_coverage_summary(
    records: Sequence[GanFrequencyRecord],
    *,
    ontology: AdmissibleStateOntology | None = None,
) -> OntologyCoverageSummary:
    """Compute Stage A oracle uplift over the deterministic graph (no model spend)."""

    ontology = ontology or AdmissibleStateOntology()
    bands: dict[str, dict[str, int]] = {}
    gains: list[int] = []
    regressions: list[int] = []

    for record in records:
        band = boundary_band(record.gold_monthly_frequency)
        stats = bands.setdefault(
            band,
            {
                "total": 0,
                "baseline_representable": 0,
                "admitted_representable": 0,
                "projection_correct": 0,
                "resolve_correct": 0,
            },
        )
        stats["total"] += 1

        graph = build_state_graph(
            record.note_text,
            source_row_index=record.source_row_index,
            include_no_reference_fallback=True,
        )
        validation = dual_validate_graph(graph, ontology=ontology)
        admitted_nodes = tuple(node for node in graph.nodes if validation.is_admitted(node.node_id))

        baseline_repr = _gold_is_representable(record, graph_node_labels(graph))
        admitted_repr = _gold_is_representable(record, _node_labels(admitted_nodes))
        projection_correct = _purist_correct(record, project_graph_to_gan(graph).monthly_frequency)
        resolve_correct = _purist_correct(
            record, resolve_label(graph, ontology=ontology, validation=validation).monthly_frequency
        )

        stats["baseline_representable"] += int(baseline_repr)
        stats["admitted_representable"] += int(admitted_repr)
        stats["projection_correct"] += int(projection_correct)
        stats["resolve_correct"] += int(resolve_correct)

        if resolve_correct and not projection_correct:
            gains.append(record.source_row_index)
        elif projection_correct and not resolve_correct:
            regressions.append(record.source_row_index)

    by_band = {band: BandCoverage(band=band, **stats) for band, stats in sorted(bands.items())}
    return OntologyCoverageSummary(
        ontology_id=ontology.ontology_id,
        row_count=len(records),
        baseline_representable=sum(b.baseline_representable for b in by_band.values()),
        admitted_representable=sum(b.admitted_representable for b in by_band.values()),
        projection_correct=sum(b.projection_correct for b in by_band.values()),
        resolve_correct=sum(b.resolve_correct for b in by_band.values()),
        resolve_minus_projection=(
            sum(b.resolve_correct for b in by_band.values())
            - sum(b.projection_correct for b in by_band.values())
        ),
        by_band=by_band,
        resolve_gain_source_row_indices=tuple(gains),
        resolve_regression_source_row_indices=tuple(regressions),
    )


def _node_labels(
    nodes: Sequence[StateGraphNode],
) -> tuple[tuple[FrequencyLabelKind, str | None], ...]:
    return tuple((node.semantic_kind, node.normalized_label) for node in nodes)


def _purist_correct(record: GanFrequencyRecord, predicted_monthly: float) -> bool:
    return map_purist(predicted_monthly) == map_purist(record.gold_monthly_frequency)


# --------------------------------------------------------------------------- #
# Stage B - atomic-claim graph viability gate (gold-free, no model spend).
# --------------------------------------------------------------------------- #


_OVER_INFERENCE_PREFIX = "over_inference_out_of_unknown"


class NodeAdmissionStats(BaseModel):
    """Node-level admission outcomes over a set of atomic-claim graphs.

    ``over_inference_rejected`` is the count of nodes the ontology guard blocks
    for over-inferring a quantified state out of an unknown-only evidence shape -
    the C2 guard's target. ``structural_rejected`` is the count failing the shape
    gate (e.g. evidence not an exact note substring). The two are reported apart
    so a clean run is distinguishable from one where the guard never fired.
    """

    model_config = ConfigDict(frozen=True)

    total_nodes: int
    structural_valid: int
    exact_evidence: int
    semantic_valid: int
    admitted: int
    over_inference_rejected: int
    structural_rejected: int
    rejection_reasons: dict[str, int]
    evidence_shape_counts: dict[str, int]


class ResolveInterpretability(BaseModel):
    """Whether ``resolve_label`` produces interpretable, component-localized output.

    A row is *component-localized* when its final label is attributable to one or
    more admitted nodes of that same graph (non-empty ``selected_node_ids``, all
    admitted). Rows that default to no-reference because nothing was admitted carry
    a decision trace but no node-localized selection, and are counted separately.
    """

    model_config = ConfigDict(frozen=True)

    row_count: int
    rows_with_decision_trace: int
    rows_with_localized_selection: int
    rows_defaulted_no_admission: int
    final_kind_counts: dict[str, int]


class AtomicClaimViabilitySummary(BaseModel):
    """Stage B readout: the LLM atomic-claim graph as a candidate component pool.

    Stage B is the viability gate of the validation-only ladder - gold-free, no
    model spend. It asks whether the atomic-claim graph (a) is schema-valid with
    exact evidence, (b) is policed by the ontology over-inference guard, and (c)
    resolves to an interpretable, component-localized label. It is the first place
    the C2 guard runs over uncurated (``llm-sg-``) nodes; whether the guard
    actually fires depends on whether the atomic-claim builder mints quantifying
    states for it to police (see ``over_inference_rejected``).
    """

    model_config = ConfigDict(frozen=True)

    ontology_id: str
    row_count: int
    node_admission: NodeAdmissionStats
    resolve: ResolveInterpretability


def atomic_claim_viability_summary(
    graphs: Sequence[ClinicalFrequencyStateGraph],
    *,
    ontology: AdmissibleStateOntology | None = None,
) -> AtomicClaimViabilitySummary:
    """Compute the Stage B viability gate over pre-built atomic-claim graphs."""

    ontology = ontology or AdmissibleStateOntology()

    total = struct_valid = exact = sem_valid = admitted = 0
    over_inference = structural_rejected = 0
    reasons: Counter[str] = Counter()
    shapes: Counter[str] = Counter()

    rows_trace = rows_localized = rows_defaulted = 0
    final_kinds: Counter[str] = Counter()

    for graph in graphs:
        validation = dual_validate_graph(graph, ontology=ontology)
        for node, node_validation in zip(graph.nodes, validation.node_validations, strict=False):
            total += 1
            struct_valid += int(node_validation.structural_valid)
            exact += int(node.evidence.start_char is not None)
            sem_valid += int(node_validation.semantic_valid)
            admitted += int(node_validation.admitted)
            shapes[classify_evidence_shape(node).value] += 1
            if not node_validation.admitted:
                for failure in node_validation.failures:
                    reasons[failure] += 1
                if not node_validation.structural_valid:
                    structural_rejected += 1
                if not node_validation.semantic_valid and any(
                    failure.startswith(_OVER_INFERENCE_PREFIX)
                    for failure in node_validation.failures
                ):
                    over_inference += 1

        resolution = resolve_label(graph, ontology=ontology, validation=validation)
        final_kinds[resolution.final_kind.value] += 1
        if resolution.decision_trace:
            rows_trace += 1
        admitted_ids = validation.admitted_node_ids
        if resolution.selected_node_ids and all(
            node_id in admitted_ids for node_id in resolution.selected_node_ids
        ):
            rows_localized += 1
        elif not resolution.selected_node_ids:
            rows_defaulted += 1

    return AtomicClaimViabilitySummary(
        ontology_id=ontology.ontology_id,
        row_count=len(graphs),
        node_admission=NodeAdmissionStats(
            total_nodes=total,
            structural_valid=struct_valid,
            exact_evidence=exact,
            semantic_valid=sem_valid,
            admitted=admitted,
            over_inference_rejected=over_inference,
            structural_rejected=structural_rejected,
            rejection_reasons=dict(sorted(reasons.items())),
            evidence_shape_counts=dict(sorted(shapes.items())),
        ),
        resolve=ResolveInterpretability(
            row_count=len(graphs),
            rows_with_decision_trace=rows_trace,
            rows_with_localized_selection=rows_localized,
            rows_defaulted_no_admission=rows_defaulted,
            final_kind_counts=dict(sorted(final_kinds.items())),
        ),
    )
