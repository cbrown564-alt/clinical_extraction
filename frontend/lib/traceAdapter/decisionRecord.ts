import type {
  PipelineTrace,
  DecisionRecordArtifactRow,
  FullRecordResponse,
  TraceItem,
} from "../types";
import {
  buildSchemaRepair,
  buildScoreFromComparison,
  canonicalSemanticKind,
  findEvidenceSpan,
  monthlyFrequencyFromLabel,
} from "./utils";

export function adaptDecisionRecordTrace(
  row: DecisionRecordArtifactRow,
  record: FullRecordResponse,
  family: string
): PipelineTrace {
  const dr = row.decision_record;
  const comparison = row.comparison;
  const modelDecision = row.row_trace?.model_prediction?.record ?? dr;
  const deterministicAdapter = row.row_trace?.deterministic_adapter;

  const finalLabel = dr?.final_label ?? "unknown";
  const evidence = dr?.evidence ?? "";
  const rationale = dr?.rationale ?? "";
  const evidenceSpan = evidence ? findEvidenceSpan(record.note_text, evidence) : null;
  const normLabel = deterministicAdapter?.after_label ?? modelDecision?.final_label ?? finalLabel;
  const rawLabel = deterministicAdapter?.before_label ?? modelDecision?.final_label ?? finalLabel;
  const kind = canonicalSemanticKind(modelDecision?.answer_kind, normLabel);
  const monthlyFreq = monthlyFrequencyFromLabel(normLabel);

  const extractItems: TraceItem[] = modelDecision?.final_label
    ? [{
        id: "e1",
        kind: canonicalSemanticKind(modelDecision.answer_kind, modelDecision.final_label),
        rawValue: modelDecision.final_label,
        evidence: modelDecision.evidence ?? evidence,
        startChar: evidenceSpan?.start ?? null,
        endChar: evidenceSpan?.end ?? null,
        metadata: {
          answer_kind: modelDecision.answer_kind ?? kind,
          ...(modelDecision.rationale ? { rationale: modelDecision.rationale } : {}),
        },
      }]
    : [];

  const normaliseItems: TraceItem[] = [
    {
      id: "n1",
      kind,
      rawValue: rawLabel,
      normalizedValue: normLabel,
      evidence: evidence || (modelDecision?.evidence ?? ""),
      startChar: evidenceSpan?.start ?? null,
      endChar: evidenceSpan?.end ?? null,
      ruleId: deterministicAdapter?.rule_category ?? "benchmark_format_repair",
      ruleGroup: "benchmark_repair",
      portability: deterministicAdapter?.rule_category ?? null,
      metadata: {
        original_label: rawLabel,
        ...(monthlyFreq !== undefined ? { monthly_frequency: monthlyFreq } : {}),
      },
    },
  ];

  const isCombinedModelDecision =
    family === "llm_only_direct_labeler" ||
    family === "llm" ||
    family === "llm_only_canonical_pipeline";

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
      isDistinctStage: !isCombinedModelDecision,
      selectedIds: dr?.selected_event_ids,
      rejectedIds: dr?.rejected_event_ids,
    },
    repair: buildSchemaRepair(
      row.row_trace?.format_repair,
      row.raw_output,
      modelDecision,
      row.repair_changes
    ),
    score: buildScoreFromComparison(comparison ?? undefined, finalLabel, row.reference.gold_label),
  };
}
