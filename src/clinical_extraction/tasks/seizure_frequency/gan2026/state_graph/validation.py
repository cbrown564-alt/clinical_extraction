"""Dual validation before a node is admitted as a component.

This is line 3.3 of the KG-grounded component-generation design note - the
SHACL-style dual gate. A node becomes an admitted component only if it passes
both:

- **Structural (shape) validation** - schema-valid ``StateGraphNode`` with no
  builder ``graph_errors``, a located exact-evidence span when it claims
  ``certainty="certain"``, and a normalized label that parses under the scoring
  grammar.
- **Semantic (transition) validation** - the node's ``evidence -> state``
  assignment is admissible under the ontology, and every edge it participates in
  is a legal transition.

Nodes that fail semantic validation are *retained but flagged*, never emitted as
components. An admitted component therefore carries, by construction, its
provenance span, its ``rule_id``, and the constraint it satisfied.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from .edges import GraphEdge, derive_edges
from .graph import ClinicalFrequencyStateGraph, StateGraphNode
from .ontology import AdmissibleStateOntology, label_parses


class NodeValidation(BaseModel):
    model_config = ConfigDict(frozen=True)

    node_id: str
    structural_valid: bool
    semantic_valid: bool
    admitted: bool
    evidence_shape: str | None = None
    failures: tuple[str, ...] = ()


class EdgeValidation(BaseModel):
    model_config = ConfigDict(frozen=True)

    edge: GraphEdge
    admitted: bool
    failures: tuple[str, ...] = ()


class GraphValidation(BaseModel):
    model_config = ConfigDict(frozen=True)

    ontology_id: str
    node_validations: tuple[NodeValidation, ...]
    edge_validations: tuple[EdgeValidation, ...]

    @property
    def admitted_node_ids(self) -> frozenset[str]:
        return frozenset(v.node_id for v in self.node_validations if v.admitted)

    @property
    def rejected_node_ids(self) -> frozenset[str]:
        return frozenset(v.node_id for v in self.node_validations if not v.admitted)

    @property
    def admitted_edges(self) -> tuple[GraphEdge, ...]:
        return tuple(v.edge for v in self.edge_validations if v.admitted)

    def is_admitted(self, node_id: str) -> bool:
        return node_id in self.admitted_node_ids


def validate_node(
    node: StateGraphNode,
    *,
    ontology: AdmissibleStateOntology,
) -> NodeValidation:
    """Run the structural + semantic gate over a single node."""

    failures: list[str] = []

    structural_valid = True
    if node.graph_errors:
        structural_valid = False
        failures.extend(f"graph_error:{error}" for error in node.graph_errors)
    if node.certainty == "certain" and node.evidence.start_char is None:
        structural_valid = False
        failures.append("certain_without_located_span")
    if not label_parses(node.normalized_label):
        structural_valid = False
        failures.append("label_does_not_parse")

    assignment = ontology.is_admissible_assignment(node)
    semantic_valid = assignment.admissible
    if not semantic_valid:
        failures.append(assignment.reason)

    return NodeValidation(
        node_id=node.node_id,
        structural_valid=structural_valid,
        semantic_valid=semantic_valid,
        admitted=structural_valid and semantic_valid,
        evidence_shape=(assignment.evidence_shape.value if assignment.evidence_shape else None),
        failures=tuple(failures),
    )


def dual_validate_graph(
    graph: ClinicalFrequencyStateGraph,
    *,
    ontology: AdmissibleStateOntology | None = None,
) -> GraphValidation:
    """Validate every node and edge, returning the admitted component set."""

    ontology = ontology or AdmissibleStateOntology()
    nodes_by_id = {node.node_id: node for node in graph.nodes}
    node_validations = tuple(validate_node(node, ontology=ontology) for node in graph.nodes)
    admitted_node_ids = {v.node_id for v in node_validations if v.admitted}

    edge_validations: list[EdgeValidation] = []
    for edge in derive_edges(graph):
        edge_validations.append(
            _validate_edge(
                edge,
                nodes_by_id=nodes_by_id,
                admitted_node_ids=admitted_node_ids,
                ontology=ontology,
            )
        )

    return GraphValidation(
        ontology_id=ontology.ontology_id,
        node_validations=node_validations,
        edge_validations=tuple(edge_validations),
    )


def _validate_edge(
    edge: GraphEdge,
    *,
    nodes_by_id: dict[str, StateGraphNode],
    admitted_node_ids: set[str],
    ontology: AdmissibleStateOntology,
) -> EdgeValidation:
    failures: list[str] = []
    source = nodes_by_id.get(edge.source_node_id)
    target = nodes_by_id.get(edge.target_node_id)
    if source is None or target is None:
        return EdgeValidation(edge=edge, admitted=False, failures=("dangling_endpoint",))

    if edge.source_node_id not in admitted_node_ids:
        failures.append("source_not_admitted")
    if edge.target_node_id not in admitted_node_ids:
        failures.append("target_not_admitted")

    transition = ontology.is_admissible_transition(edge, source=source, target=target)
    if not transition.admissible:
        failures.append(transition.reason)

    return EdgeValidation(edge=edge, admitted=not failures, failures=tuple(failures))
