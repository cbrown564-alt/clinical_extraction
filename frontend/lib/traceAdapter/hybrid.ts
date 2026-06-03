import type { PipelineTrace, HybridArtifactRow, FullRecordResponse } from "../types";
import { candidateToTraceItem, normalisedToTraceItem } from "./deterministic";

export function adaptHybridTrace(
  row: HybridArtifactRow,
  record: FullRecordResponse
): PipelineTrace {
  const dd = row.deterministic_diagnostics;
  const dr = row.decision_record;
  return {
    pipelineFamily: "hybrid_rules_candidates_llm_adjudicator",
    noteText: record.note_text,
    goldLabel: row.reference.gold_label,
    sourceRowIndex: row.source_row_index,
    split: row.split,
    extract: {
      items: dd.candidate_events.map(candidateToTraceItem),
    },
    normalise: {
      items: dd.normalized_events.map((n) =>
        normalisedToTraceItem(n, dd.candidate_events)
      ),
    },
    select: {
      finalLabel: dr.final_label,
      rationale: dr.rationale,
      evidence: dr.evidence,
      monthlyFrequency: undefined,
      selectedIds: dr.accepted_event_ids,
      rejectedIds: dr.rejected_event_ids,
    },
    score: {
      predictedLabel: dr.final_label,
      goldLabel: row.reference.gold_label,
      match: dr.final_label === row.reference.gold_label,
      evidenceValid: dd.evidence_valid,
    },
  };
}
