import type {
  PipelineTrace,
  ParallelHybridArtifactRow,
  FullRecordResponse,
  TraceItem,
} from "../types";
import { candidateToTraceItem } from "./deterministic";
import { findEvidenceSpan, buildScoreFromLayers, buildRepair } from "./utils";

export function adaptParallelHybridTrace(
  row: ParallelHybridArtifactRow,
  record: FullRecordResponse,
  family: string
): PipelineTrace {
  const inputs = row.component_inputs;
  const deterministicCandidates = inputs?.deterministic_candidates ?? [];
  const stateGraphNodes = inputs?.state_graph_nodes ?? [];
  const stateGraphProjection = inputs?.state_graph_projection;
  const adjudicatorRecord = row.structured_adjudicator_record;

  // Extract: deterministic candidates + state graph nodes
  const extractItems: TraceItem[] = [
    ...deterministicCandidates.map(candidateToTraceItem),
    ...stateGraphNodes.map((node, idx) => {
      const span = node.evidence ? findEvidenceSpan(record.note_text, node.evidence) : null;
      return {
        id: `sg_node_${idx}`,
        kind: node.semantic_kind || "state_graph_node",
        rawValue: node.node_normalized_label || node.evidence || "",
        normalizedValue: node.node_normalized_label || undefined,
        evidence: node.evidence || "",
        startChar: span?.start ?? null,
        endChar: span?.end ?? null,
        metadata: {
          rationale: node.rationale,
          source: "state_graph",
        },
      };
    }),
  ];

  // Normalise: deterministic top + state graph projection
  const normaliseItems: TraceItem[] = [];
  if (inputs?.deterministic_top?.selected_decision) {
    normaliseItems.push({
      id: "deterministic_top",
      kind: "deterministic_selection",
      rawValue: inputs.deterministic_top.selected_decision,
      evidence: "",
      startChar: null,
      endChar: null,
      metadata: {
        selected_event_ids: inputs.deterministic_top.selected_event_ids,
        selected_score: inputs.deterministic_top.selected_score,
      },
    });
  }
  if (stateGraphProjection?.final_label) {
    normaliseItems.push({
      id: "state_graph_projection",
      kind: stateGraphProjection.final_kind || "projection",
      rawValue: stateGraphProjection.final_label,
      normalizedValue: stateGraphProjection.final_label,
      evidence: stateGraphProjection.evidence || "",
      startChar: null,
      endChar: null,
      metadata: {
        monthly_frequency: stateGraphProjection.monthly_frequency,
        selected_node_ids: stateGraphProjection.selected_node_ids,
        uncertainty_flags: stateGraphProjection.uncertainty_flags,
      },
    });
  }

  // Select: prefer adjudicator, fall back to state graph projection, then deterministic top
  const selectSource =
    adjudicatorRecord ??
    (stateGraphProjection
      ? {
          final_label: stateGraphProjection.final_label,
          evidence: stateGraphProjection.evidence || "",
          rationale: stateGraphProjection.rationale || "",
          selected_event_ids: stateGraphProjection.selected_node_ids,
        }
      : undefined);

  const finalLabel = selectSource?.final_label ?? "unknown";
  const selectEvidence = selectSource?.evidence ?? "";
  const selectRationale = selectSource?.rationale ?? "";

  return {
    pipelineFamily: family,
    noteText: record.note_text,
    goldLabel: row.reference.gold_label,
    sourceRowIndex: row.source_row_index,
    split: row.split,
    extract: { items: extractItems },
    normalise: { items: normaliseItems },
    select: {
      finalLabel,
      rationale: selectRationale,
      evidence: selectEvidence,
      selectedIds: selectSource?.selected_event_ids,
    },
    repair: buildRepair(row.repair_changes),
    score: buildScoreFromLayers(row.score_layers, row.reference.gold_label),
  };
}
