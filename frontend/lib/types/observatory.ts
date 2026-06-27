import type { CategoryMetrics } from "./shared";

// ── Gold Audit ──

export type RQ10Class =
  | "true_extraction_failure"
  | "benchmark_convention_dominated"
  | "underdetermined_note"
  | "clinically_defensible_alternative"
  | "possible_gold_weakness"
  | "instrumentation_gap";

export interface GoldAuditRow {
  manual_ambiguity_label: string;
  manual_notes: string;
  manual_corrected_gold_label: string;
  validation_order: string;
  source_row_index: string;
  split: string;
  gold_label: string;
  gold_label_kind: string;
  gold_reference: string;
  codex_initial_ambiguity_label: string;
  codex_ambiguity_reasons: string;
  codex_ambiguity_rationale: string;
  gold_monthly_frequency: string;
  gold_yearly_bounds: string;
  row_ok: string;
  labels_match_all_categories: string;
  quotes_ok_all_categories: string;
  reference_found_in_note: string;
  reference_context: string;
  note_text_single_line: string;
  has_decision?: boolean;
  priority_score?: number;
  predicted_simple_class?: "correct" | "ambiguous" | "wrong";
  predicted_correct_prob?: number;
  predicted_ambiguous_prob?: number;
  predicted_wrong_prob?: number;
  prediction_confidence?: number;
  prediction_uncertainty?: number;
  active_learning_score?: number;
  active_learning_reason?: string;
}

export interface GoldAuditDecision {
  source_row_index: number;
  split: string;
  simple_class: "correct" | "ambiguous" | "wrong";
  rq10_class: RQ10Class | null;
  notes: string;
  corrected_gold_label: string | null;
  benchmark_convention_flag: boolean;
  all_system_fail: boolean;
  exact_evidence_but_scorer_wrong: boolean;
  clinically_defensible_alternative: boolean;
  likely_gold_defect: boolean;
  timestamp?: string;
  auditor?: string;
}

export interface GoldAuditRowsResponse {
  split: string;
  total: number;
  decided: number;
  class_counts: Record<string, number>;
  sampling_model?: {
    model_kind: string;
    decision_count: number;
    minimum_modelled_decisions: number;
    is_calibrated_enough: boolean;
    class_counts: Record<string, number>;
    global_probs: Record<string, number>;
    class_rate_intervals_95: Record<string, unknown>;
    projected_class_rate_intervals_95: Record<string, unknown>;
    claim_language: string;
  };
  rows: GoldAuditRow[];
}

export interface GoldAuditDecisionsResponse {
  decisions: GoldAuditDecision[];
  count: number;
}

export interface GoldAuditNextResponse {
  split: string;
  row: GoldAuditRow | null;
  message?: string;
}

export interface GoldAuditDecisionResponse {
  status: string;
  decision: GoldAuditDecision;
}

// ── Observatory (Phase 3) ──

export interface RowScore {
  predictedCategory: string;
  goldCategory: string;
  puristCorrect: boolean;
  pragmaticCorrect: boolean;
  predictedLabel: string;
  goldLabel: string;
  split?: string;
  evidence?: string;
  rationale?: string;
  sourceRowIndex: number;
  evidenceValid?: boolean;
  repairChangesCount?: number;
}

export interface RunSummary {
  runId: string;
  pipelineFamily: string;
  split: string;
  rowCount: number;
  date: string;
  decision: string;
  puristAccuracy: number;
  pragmaticAccuracy: number;
  puristF1: number;
  pragmaticF1: number;
  confusionMatrix: Map<string, Map<string, number>>;
  perCategoryMetrics: Record<string, CategoryMetrics>;
  validationMetrics?: {
    puristAccuracy: number;
    pragmaticAccuracy: number;
    rowCount: number;
  };
  testMetrics?: {
    puristAccuracy: number;
    pragmaticAccuracy: number;
    rowCount: number;
  };
  rows?: RowScore[];
}