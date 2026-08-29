import type {
  PipelineTrace,
  StateGraphArtifactRow,
  FullRecordResponse,
  TraceItem,
} from "../types";
import { findEvidenceSpan, buildRepair, buildScoreFromComparison } from "./utils";

export function adaptStateGraphTrace(
  row: StateGraphArtifactRow,
  record: FullRecordResponse,
  family: string
): PipelineTrace {
  const nodes = row.structured_record?.nodes ?? [];

  const extractItems: TraceItem[] = nodes.map((node, idx) => {
    const span = node.evidence ? findEvidenceSpan(record.note_text, node.evidence) : null;
    return {
      id: `node_${idx}`,
      kind: node.semantic_kind || "graph_node",
      rawValue: node.node_normalized_label || node.evidence,
      normalizedValue: node.node_normalized_label || undefined,
      evidence: node.evidence,
      startChar: span?.start ?? null,
      endChar: span?.end ?? null,
      metadata: {
        assertion_status: node.assertion_status,
        certainty: node.certainty,
        temporality: node.temporality,
        rationale: node.rationale,
      },
    };
  });

  // For boundary-builder rows there may be no final label
  const hasFinalLabel = nodes.some((n) => n.node_normalized_label);
  const representativeNode = nodes[0];
  const finalLabel = representativeNode?.node_normalized_label ?? "unknown";
  const evidence = representativeNode?.evidence ?? "";
  const rationale =
    representativeNode?.rationale ??
    row.structured_record?.no_reference_vs_unknown_rationale ??
    "";
  const score = buildScoreFromComparison(
    undefined,
    hasFinalLabel ? finalLabel : "unknown",
    row.reference.gold_label
  );

  return {
    pipelineFamily: family,
    noteText: record.note_text,
    goldLabel: row.reference.gold_label,
    sourceRowIndex: row.source_row_index,
    split: row.split,
    extract: { items: extractItems },
    normalise: { items: [] },
    select: {
      finalLabel: hasFinalLabel ? finalLabel : "(no final label — boundary builder)",
      rationale,
      evidence,
    },
    repair: buildRepair(row.repair_changes),
    score: {
      ...score,
      match: hasFinalLabel ? Boolean(score.puristMatch) : false,
      evidenceValid: (row.evidence_summary?.exact_evidence_valid ?? 0) > 0,
    },
  };
}
