import type {
  PipelineTrace,
  SelectedFactArtifactRow,
  SelectedStateArtifactRow,
  FullRecordResponse,
  TraceItem,
} from "../types";
import { findEvidenceSpan, buildScoreFromLayers, buildRepair } from "./utils";

// ── Selected-fact adapter (llm_heavy_evidence_selection_with_deterministic_adapters) ──

export function adaptSelectedFactTrace(
  row: SelectedFactArtifactRow,
  record: FullRecordResponse,
  family: string
): PipelineTrace {
  const fact = row.structured_record?.selected_fact;
  const mechanical = row.mechanical_adapter;

  const extractItems: TraceItem[] = [];
  if (fact) {
    const span = fact.evidence ? findEvidenceSpan(record.note_text, fact.evidence) : null;
    extractItems.push({
      id: fact.fact_id || "selected_fact",
      kind: fact.clinical_kind || "fact",
      rawValue: fact.raw_value || fact.evidence,
      evidence: fact.evidence,
      startChar: span?.start ?? null,
      endChar: span?.end ?? null,
      metadata: {
        assertion_status: fact.assertion_status,
        temporality: fact.temporality,
        applies_to: fact.applies_to,
        benchmark_caveat_flags: fact.benchmark_caveat_flags,
        competing_fact_summary: fact.competing_fact_summary,
        operands: row.structured_record?.operands,
      },
    });
  }

  const normaliseItems: TraceItem[] = [];
  if (mechanical?.final_label) {
    normaliseItems.push({
      id: "mechanical_adapter",
      kind: "mechanical",
      rawValue: mechanical.final_label,
      normalizedValue: mechanical.final_label,
      evidence: fact?.evidence ?? "",
      startChar: null,
      endChar: null,
      metadata: {
        adapter_families: mechanical.adapter_families,
        operand_complete: mechanical.operand_complete,
        error: mechanical.error,
      },
    });
  }

  const finalLabel = mechanical?.final_label ?? fact?.raw_value ?? "unknown";
  const evidence = fact?.evidence ?? row.evidence_summary?.selected_fact_evidence ?? "";
  const rationale = fact?.rationale ?? "";

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
    },
    repair: buildRepair(row.repair_changes),
    score: buildScoreFromLayers(row.score_layers, row.reference.gold_label),
  };
}

// ── Selected-state adapter (llm_only_simplified/sparse_selected_state_reasoner) ──

export function adaptSelectedStateTrace(
  row: SelectedStateArtifactRow,
  record: FullRecordResponse,
  family: string
): PipelineTrace {
  const state = row.structured_record?.selected_state;

  const extractItems: TraceItem[] = [];
  if (state) {
    const span = state.selected_evidence
      ? findEvidenceSpan(record.note_text, state.selected_evidence)
      : null;
    extractItems.push({
      id: "selected_state",
      kind: state.final_kind || "state",
      rawValue: state.raw_source_phrase || state.raw_llm_final_label || state.selected_evidence,
      normalizedValue: state.raw_llm_final_label || undefined,
      evidence: state.selected_evidence,
      startChar: span?.start ?? null,
      endChar: span?.end ?? null,
      metadata: {
        selection_reason: state.selection_reason,
        uncertainty_flags: state.uncertainty_flags,
        operands: state.operands,
        selected_operation_kind: state.selected_operation_kind,
      },
    });
  }

  const normaliseItems: TraceItem[] = [];
  if (state?.operands) {
    normaliseItems.push({
      id: "operands",
      kind: "operands",
      rawValue: JSON.stringify(state.operands),
      normalizedValue: state.raw_llm_final_label || undefined,
      evidence: state.selected_evidence,
      startChar: null,
      endChar: null,
      metadata: state.operands,
    });
  }

  const finalLabel = state?.raw_llm_final_label ?? "unknown";
  const evidence = state?.selected_evidence ?? row.evidence_summary?.selected_evidence ?? "";
  const rationale = state?.selection_reason ?? "";

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
    },
    repair: buildRepair(row.repair_changes),
    score: buildScoreFromLayers(row.score_layers, row.reference.gold_label),
  };
}
