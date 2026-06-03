import type {
  PipelineTrace,
  OperationsArtifactRow,
  FullRecordResponse,
  TraceItem,
} from "../types";
import { findEvidenceSpan, buildScoreFromLayers, buildRepair } from "./utils";

export function adaptOperationsTrace(
  row: OperationsArtifactRow,
  record: FullRecordResponse,
  family: string
): PipelineTrace {
  const operations = row.structured_record?.operations ?? [];
  const selection = row.structured_record?.selection;

  const extractItems: TraceItem[] = operations.map((op, idx) => {
    const span = op.evidence ? findEvidenceSpan(record.note_text, op.evidence) : null;
    return {
      id: op.operation_id || `op_${idx}`,
      kind: op.operation_kind,
      rawValue: op.raw_phrase || op.evidence,
      normalizedValue: op.model_normalized_clinical_label || undefined,
      evidence: op.evidence,
      startChar: span?.start ?? null,
      endChar: span?.end ?? null,
      metadata: {
        operands: op.operands,
        assertion_status: op.assertion_status,
        certainty: op.certainty,
        temporality: op.temporality,
      },
    };
  });

  const normaliseItems: TraceItem[] = operations
    .filter((op) => op.model_normalized_clinical_label)
    .map((op, idx) => ({
      id: op.operation_id || `op_${idx}`,
      kind: op.operation_kind,
      rawValue: op.raw_phrase || op.evidence,
      normalizedValue: op.model_normalized_clinical_label,
      evidence: op.evidence,
      startChar: null,
      endChar: null,
      metadata: {
        operands: op.operands,
      },
    }));

  const finalLabel = selection?.final_clinical_state ?? "unknown";
  const evidence = selection?.selected_evidence ?? row.evidence_summary?.selected_evidence ?? "";
  const rationale = selection?.rationale ?? "";

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
      rationale,
      evidence,
      selectedIds: selection?.selected_operation_ids,
      rejectedIds: selection?.rejected_operation_ids,
    },
    repair: buildRepair(row.repair_changes),
    score: buildScoreFromLayers(row.score_layers, row.reference.gold_label),
  };
}
