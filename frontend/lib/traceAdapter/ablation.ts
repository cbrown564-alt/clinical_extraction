import type {
  PipelineTrace,
  ReplacementAblationArtifactRow,
  FullRecordResponse,
} from "../types";

export function adaptAblationTrace(
  row: ReplacementAblationArtifactRow,
  record: FullRecordResponse,
  family: string
): PipelineTrace {
  const rawLabel = row.raw_label ?? "unknown";
  const finalLabel = row.final_label ?? "unknown";
  const goldLabel = row.gold_label ?? "unknown";

  return {
    pipelineFamily: family,
    noteText: record.note_text,
    goldLabel,
    sourceRowIndex: row.source_row_index,
    split: row.split,
    extract: { items: [] },
    normalise: { items: [] },
    select: {
      finalLabel: rawLabel,
      rationale: `Pre-repair label selected by ${row.prediction_owner || "unknown"}`,
      evidence: "",
    },
    repair: {
      changes: [
        `${row.repair_mode}: "${rawLabel}" → "${finalLabel}"`,
        ...(row.transition_reason ? [`Reason: ${row.transition_reason}`] : []),
      ],
      beforeLabel: rawLabel,
      afterLabel: finalLabel,
    },
    score: {
      predictedLabel: finalLabel,
      goldLabel,
      match: finalLabel === goldLabel,
      evidenceValid: row.purist_correct ?? false,
    },
  };
}
