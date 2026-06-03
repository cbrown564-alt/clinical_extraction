import type { PipelineTrace, LLMArtifactRow, FullRecordResponse } from "../types";
import { findEvidenceSpan } from "./utils";

export function adaptClaimTableTrace(
  row: LLMArtifactRow,
  record: FullRecordResponse
): PipelineTrace {
  const claims = row.structured_record?.claims ?? [];
  const fq = row.structured_record?.final_query ?? {
    final_label: null,
    answer_kind: "unknown",
    evidence: "",
    rationale: "",
    confidence: "low",
    conversion_note: null,
    raw_selected_frequency: null,
    selected_claim_ids: "",
  };

  const claimItems = claims.map((claim, idx) => {
    const evidence = claim.evidence;
    const span = evidence ? findEvidenceSpan(record.note_text, evidence) : null;
    return {
      id: claim.claim_id || `claim_${idx}`,
      kind: claim.claim_type,
      rawValue: claim.raw_frequency || claim.anchor_text,
      normalizedValue: claim.raw_frequency || undefined,
      evidence: claim.evidence,
      startChar: span?.start ?? null,
      endChar: span?.end ?? null,
      metadata: {
        temporality: claim.temporality,
        assertion_status: claim.assertion_status,
        uncertainty: claim.uncertainty,
        section: claim.section,
        semiology: claim.semiology,
      },
    };
  });

  const normalisedItems = fq.final_label
    ? [
        {
          id: "final_query",
          kind: fq.answer_kind,
          rawValue: fq.raw_selected_frequency || fq.final_label,
          normalizedValue: fq.final_label,
          evidence: fq.evidence,
          startChar: null as number | null,
          endChar: null as number | null,
          metadata: {
            confidence: fq.confidence,
            conversion_note: fq.conversion_note,
          },
        },
      ]
    : [];

  const repairChanges = row.repair_changes;
  const repair =
    repairChanges && repairChanges.length > 0
      ? { changes: repairChanges as string[] }
      : undefined;

  return {
    pipelineFamily: "llm_only_claim_table_selector",
    noteText: record.note_text,
    goldLabel: row.reference.gold_label,
    sourceRowIndex: row.source_row_index,
    split: row.split,
    extract: { items: claimItems },
    normalise: { items: normalisedItems },
    select: {
      finalLabel: fq.final_label || fq.answer_kind,
      rationale: fq.rationale,
      evidence: fq.evidence,
      selectedIds: fq.selected_claim_ids ? [fq.selected_claim_ids] : undefined,
    },
    repair,
    score: {
      predictedLabel: fq.final_label || fq.answer_kind,
      goldLabel: row.reference.gold_label,
      match: (fq.final_label || fq.answer_kind) === row.reference.gold_label,
      evidenceValid: row.evidence_summary?.selected_evidence_valid ?? false,
    },
  };
}
