import type {
  PipelineTrace,
  DecisionRecordArtifactRow,
  FullRecordResponse,
} from "../types";
import { buildScoreFromComparison, buildRepair } from "./utils";

export function adaptDecisionRecordTrace(
  row: DecisionRecordArtifactRow,
  record: FullRecordResponse,
  family: string
): PipelineTrace {
  const dr = row.decision_record;
  const comparison = row.comparison;

  const finalLabel = dr?.final_label ?? "unknown";
  const evidence = dr?.evidence ?? "";
  const rationale = dr?.rationale ?? "";

  return {
    pipelineFamily: family,
    noteText: record.note_text,
    goldLabel: row.reference.gold_label,
    sourceRowIndex: row.source_row_index,
    split: row.split,
    extract: { items: [] },
    normalise: { items: [] },
    select: {
      finalLabel,
      rationale,
      evidence,
      selectedIds: dr?.selected_event_ids,
      rejectedIds: dr?.rejected_event_ids,
    },
    repair: buildRepair(row.repair_changes),
    score: buildScoreFromComparison(comparison ?? undefined, finalLabel, row.reference.gold_label),
  };
}
