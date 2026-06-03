import type {
  PipelineTrace,
  MinimalEvidenceArtifactRow,
  FullRecordResponse,
} from "../types";
import { buildScoreFromLayers, buildRepair } from "./utils";

export function adaptMinimalEvidenceTrace(
  row: MinimalEvidenceArtifactRow,
  record: FullRecordResponse,
  family: string
): PipelineTrace {
  const mr = row.minimal_record;
  const finalLabel = mr?.final_label ?? "unknown";
  const evidence = mr?.evidence ?? mr?.selected_evidence ?? row.evidence_summary?.selected_evidence ?? "";
  const rationale = mr?.rationale ?? "";

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
    },
    repair: buildRepair(row.repair_changes),
    score: buildScoreFromLayers(row.score_layers, row.reference.gold_label),
  };
}
