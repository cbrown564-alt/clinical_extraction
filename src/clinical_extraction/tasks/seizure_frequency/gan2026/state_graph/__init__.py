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
from .projection import GanGraphProjection, ProjectionPolicy, project_graph_to_gan
from .coverage import (
    BandCoverage,
    OntologyCoverageSummary,
    OracleCoverageSummary,
    graph_node_labels,
    ontology_coverage_summary,
    oracle_coverage_summary,
)

__all__ = [
    "ADMISSIBLE_STATES",
    "UNKNOWN_ONLY_SHAPES",
    "AdmissibilityResult",
    "AdmissibleStateOntology",
    "BandCoverage",
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
    "build_state_graph",
    "build_state_graph_from_atomic_claims",
    "classify_evidence_shape",
    "derive_edges",
    "dual_validate_graph",
    "graph_invariance_signature",
    "graph_node_labels",
    "ontology_coverage_summary",
    "oracle_coverage_summary",
    "project_graph_to_gan",
    "resolve_label",
    "validate_node",
]
