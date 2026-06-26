"""Clinical frequency state graph scaffolding for Gan 2026 diagnostics.

Promoted from an oracle/diagnostic into an anchored, ontology-constrained,
dual-validated component generator per the 2026-06-15 KG-grounded
component-generation design note:

- ``edges`` - typed relations (SUPERSEDES / REFINES / CONTRADICTS) over nodes;
- ``ontology`` - the admissible-state lattice (the fixed boundary);
- ``validation`` - the dual (structural + semantic) admission gate;
- ``resolve`` - the final label as an explicit, ablatable graph query.
"""

from .graph import (
    ClinicalFrequencyStateGraph,
    EvidenceSpan,
    GraphNodeKind,
    StateGraphNode,
    build_state_graph,
    build_state_graph_from_atomic_claims,
    graph_invariance_signature,
)
from .claim_table import (
    NORMALIZED_CLAIM_RULE_ID,
    atomic_claim_from_table_claim,
    atomic_claims_from_structured_record,
)
from .edges import GraphEdge, GraphEdgeKind, derive_edges
from .ontology import (
    ADMISSIBLE_STATES,
    UNKNOWN_ONLY_SHAPES,
    AdmissibilityResult,
    AdmissibleStateOntology,
    EvidenceShape,
    classify_evidence_shape,
)
from .validation import (
    EdgeValidation,
    GraphValidation,
    NodeValidation,
    dual_validate_graph,
    validate_node,
)
from .resolve import GraphLabelResolution, resolve_label
from .extract import (
    extract_stage,
    extracted_candidate_from_state_graph_node,
    materialize_state_graph_extract,
    raw_candidate_from_state_graph_node,
    state_graph_candidate_set_from_graph,
)
from .projection import GanGraphProjection, ProjectionPolicy, project_graph_to_gan
from .coverage import (
    AtomicClaimViabilitySummary,
    BandCoverage,
    NodeAdmissionStats,
    OntologyCoverageSummary,
    OracleCoverageSummary,
    ResolveInterpretability,
    atomic_claim_viability_summary,
    graph_node_labels,
    ontology_coverage_summary,
    oracle_coverage_summary,
)

__all__ = [
    "ADMISSIBLE_STATES",
    "NORMALIZED_CLAIM_RULE_ID",
    "UNKNOWN_ONLY_SHAPES",
    "AdmissibilityResult",
    "AdmissibleStateOntology",
    "AtomicClaimViabilitySummary",
    "BandCoverage",
    "NodeAdmissionStats",
    "ResolveInterpretability",
    "ClinicalFrequencyStateGraph",
    "EdgeValidation",
    "EvidenceShape",
    "EvidenceSpan",
    "GanGraphProjection",
    "GraphEdge",
    "GraphEdgeKind",
    "GraphLabelResolution",
    "GraphNodeKind",
    "GraphValidation",
    "NodeValidation",
    "OntologyCoverageSummary",
    "OracleCoverageSummary",
    "ProjectionPolicy",
    "StateGraphNode",
    "atomic_claim_from_table_claim",
    "atomic_claim_viability_summary",
    "atomic_claims_from_structured_record",
    "build_state_graph",
    "build_state_graph_from_atomic_claims",
    "classify_evidence_shape",
    "derive_edges",
    "dual_validate_graph",
    "extract_stage",
    "extracted_candidate_from_state_graph_node",
    "graph_invariance_signature",
    "graph_node_labels",
    "materialize_state_graph_extract",
    "raw_candidate_from_state_graph_node",
    "ontology_coverage_summary",
    "oracle_coverage_summary",
    "project_graph_to_gan",
    "resolve_label",
    "state_graph_candidate_set_from_graph",
    "validate_node",
]
