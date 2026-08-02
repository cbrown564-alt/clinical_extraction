import type {
  PipelineTrace,
  DecisionRecordArtifactRow,
  FullRecordResponse,
  TraceItem,
} from "../types";
import { buildScoreFromComparison, buildSchemaRepair, findEvidenceSpan } from "./utils";

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

  const extractItems: TraceItem[] = modelDecision?.final_label
    ? [{
        id: "model_decision",
        kind: "llm_decision",
        rawValue: modelDecision.final_label,
        evidence: modelDecision.evidence ?? evidence,
        startChar: evidenceSpan?.start ?? null,
        endChar: evidenceSpan?.end ?? null,
        metadata: {
          answer_kind: modelDecision.answer_kind,
          rationale: modelDecision.rationale,
        },
      }]
    : [];

  const normaliseItems: TraceItem[] = deterministicAdapter?.after_label
    ? [{
        id: "deterministic_adapter",
        kind: "deterministic_adapter",
        rawValue: deterministicAdapter.before_label ?? modelDecision?.final_label ?? finalLabel,
        normalizedValue: deterministicAdapter.after_label,
        evidence,
        startChar: evidenceSpan?.start ?? null,
        endChar: evidenceSpan?.end ?? null,
        portability: deterministicAdapter.rule_category ?? null,
        metadata: {
          events: deterministicAdapter.events ?? [],
          rule_category: deterministicAdapter.rule_category,
        },
      }]
    : [];

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
