import type { CategoryMetrics, LaneId } from "./shared";

// ── Gold Audit ──

export type RQ10Class =
  | "true_extraction_failure"
  | "benchmark_convention_dominated"
  | "underdetermined_note"
  | "clinically_defensible_alternative"
  | "possible_gold_weakness"
  | "instrumentation_gap";

export interface GoldAuditRow {
  audit_id?: string;
  fact_id?: string;
  queue_position?: number;
  letter_id?: string;
  entity?: string;
  full_letter_text?: string;
  source_context?: string;
  source_span?: string;
  span_offsets?: number[];
  context_offsets?: number[];
  manual_ambiguity_label?: string;
  manual_notes?: string;
  manual_corrected_gold_label?: string;
  validation_order?: string;
  source_row_index?: string;
  split: string;
  gold_label?: string;
  gold_label_kind?: string;
  gold_reference?: string;
  codex_initial_ambiguity_label?: string;
  codex_ambiguity_reasons?: string;
  codex_ambiguity_rationale?: string;
  gold_monthly_frequency?: string;
  gold_yearly_bounds?: string;
  row_ok?: string;
  labels_match_all_categories?: string;
  quotes_ok_all_categories?: string;
  reference_found_in_note?: string;
  reference_context?: string;
  note_text_single_line?: string;
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
  dataset?: "gan2026" | "exectv2";
  audit_id?: string | null;
  source_row_index?: number | null;
  split: string;
  simple_class?: "correct" | "ambiguous" | "wrong" | null;
  rq10_class?: RQ10Class | null;
  notes?: string;
  corrected_gold_label?: string | null;
  benchmark_convention_flag?: boolean;
  all_system_fail?: boolean;
  exact_evidence_but_scorer_wrong?: boolean;
  clinically_defensible_alternative?: boolean;
  likely_gold_defect?: boolean;
  assertion_status?: "present" | "negated" | "historical" | "future" | "uncertain" | "unsupported" | null;
  attribute_entailment?: "entailed" | "plausible" | "ambiguous" | "contradicted" | "absent" | null;
  fact_boundaries?: string | null;
  clinical_interpretation?: string | null;
  reviewer_rationale?: string | null;
  review_confidence?: "low" | "medium" | "high" | null;
  timestamp?: string;
  auditor?: string;
}

export interface GoldAuditRowsResponse {
  dataset?: "gan2026" | "exectv2";
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
    confidence_counts?: Record<string, number>;
  };
  rows: GoldAuditRow[];
}

export interface GoldAuditDecisionsResponse {
  decisions: GoldAuditDecision[];
  count: number;
}

export interface GoldAuditNextResponse {
  dataset?: "gan2026" | "exectv2";
  split: string;
  row: GoldAuditRow | null;
  message?: string;
}

export interface GoldAuditDecisionResponse {
  status: string;
  decision: GoldAuditDecision;
}

// ── Qualified consensus-incorrect review ──

export type CorrectnessVerdict = "correct" | "incorrect";

export interface QualifiedLinkedEvent {
  fact_id: string;
  entity: string;
  span_offsets: number[];
  source_span: string;
  relation_to_focus?: string;
}

export interface QualifiedEventContext {
  window_policy?: string;
  event_radius?: number;
  window_offsets?: number[];
  window_text?: string;
  linked_events?: QualifiedLinkedEvent[];
}

export interface QualifiedTerminologyLookup {
  resource?: string;
  attribute_name?: string;
  closed_vocab?: string[];
  review_rule?: string;
  codebook_hits?: Array<Record<string, unknown>>;
}

export interface QualifiedCertaintyScale {
  attribute?: string;
  domain?: string[];
  source?: string;
  levels?: Record<string, { label: string; meaning: string }>;
  review_rule?: string;
  triggers?: Array<{ trigger: string; level: string }>;
}

export interface QualifiedReviewPacket {
  attribute_review_id: string;
  fact_id: string;
  queue_position?: number;
  letter_id: string;
  entity: string;
  attribute_name: string;
  attribute_value: string;
  full_letter_text?: string;
  source_context?: string;
  source_span: string;
  span_offsets?: number[];
  context_offsets?: number[];
  event_linked_context?: QualifiedEventContext;
  supports?: {
    terminology_lookup?: QualifiedTerminologyLookup;
    certainty_scale?: QualifiedCertaintyScale;
  };
  triage?: { selection?: string; note?: string };
  stage?: string;
  has_decision?: boolean;
}

export interface QualifiedReviewDecision {
  attribute_review_id: string;
  fact_id?: string | null;
  letter_id?: string | null;
  attribute_name?: string | null;
  attribute_value?: string | null;
  reviewer_id: string;
  correctness: CorrectnessVerdict;
  review_notes?: string | null;
  timestamp?: string;
  revision?: number;
}

export interface QualifiedReviewPacketsResponse {
  total: number;
  decided: number;
  packets: QualifiedReviewPacket[];
  certainty_scale?: QualifiedCertaintyScale;
}

export interface QualifiedReviewDecisionsResponse {
  reviewer_id: string;
  blinded: boolean;
  decisions: QualifiedReviewDecision[];
  count: number;
}

export interface QualifiedReviewDecideResponse {
  status: string;
  decision: QualifiedReviewDecision;
}

export type ClinicalSupportVerdict = "supported" | "unsupported" | "unclear";

export interface SemanticSupportReviewPacket {
  review_item_id: string;
  queue_position: number;
  letter_id: string;
  family: string;
  evidence_text: string;
  full_letter_text: string;
  selected_conclusion: {
    text?: string | null;
    normalized_concept?: string | null;
    assertion?: string | null;
    attributes?: Record<string, unknown>;
  };
  evidence_valid: boolean;
  has_decision: boolean;
  finding_id?: string;
  rationale?: string;
}

export interface SemanticSupportReviewDecision {
  review_item_id: string;
  reviewer_id: string;
  clinical_support: ClinicalSupportVerdict;
  review_notes?: string | null;
  timestamp?: string;
  revision?: number;
}

export interface SemanticSupportReviewPacketsResponse {
  protocol_version: string;
  blinded: boolean;
  reviewer_id?: string | null;
  total: number;
  decided: number;
  claim_boundary: string;
  families: string[];
  packets: SemanticSupportReviewPacket[];
}

export interface SemanticSupportReviewDecisionsResponse {
  reviewer_id: string;
  blinded: boolean;
  count: number;
  decisions: SemanticSupportReviewDecision[];
}

export interface SemanticSupportReviewDecideResponse {
  status: string;
  decision: SemanticSupportReviewDecision;
}

export interface SemanticSupportReviewExport {
  schema_version: string;
  protocol_version: string;
  reviewer_id: string;
  claim_boundary: string;
  completion: { decided: number; total: number };
  decisions: SemanticSupportReviewDecision[];
  revisions: SemanticSupportReviewDecision[];
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
  /** Production / ceiling / floor lane, derived from the entry's registry_roles. */
  lane?: LaneId;
}

// ── Gold noise (read-only gold-quality inspection) ──
//
// Companion to the gold-audit block above. The /gold-noise tab is read-only:
// it surfaces the per-item gold-vs-pred evidence the four ExECT ledgers and the
// Gan RQ10 audit already carry. No write-back.

export interface GoldNoiseItem {
  family: string;
  letter_id: string;
  row_id: string;
  disagreement_type: "missed" | "spurious" | string;
  match_key: string;
  mechanism: string;
  verdict: string;
  gold: Record<string, unknown> | null;
  pred: Record<string, unknown> | null;
  reason: string;
  run_id: string;
  source_letter_text?: string;
  source: string;
}

export interface GoldNoiseFamilySummary {
  family: string;
  total: number;
  /** verdict == "gold_right": the genuine-model-error ceiling (n/total). */
  gold_right: number;
  model_defensible: number;
  both_defensible: number;
  unadjudicated: number;
  by_verdict: Record<string, number>;
  by_mechanism: Record<string, number>;
  rows: GoldNoiseItem[];
}

export interface GoldNoiseLedgersResponse {
  families: GoldNoiseFamilySummary[];
}

export interface GoldNoiseGanAuditResponse {
  /** The full RQ10 audit JSON, or null when the file is absent. */
  audit: Record<string, unknown> | null;
  /** Always "rq10_class" — distinct from ExECT's Mechanism enum. */
  taxonomy: string;
  taxonomy_note: string;
}

export interface GoldNoiseIssuesResponse {
  count: number;
  issues: Record<string, unknown>[];
}

export interface GoldNoiseHypothesis {
  hypothesis_id: string;
  family: string;
  statement: string;
  predeclaration_doc: string;
  kill_criterion: string;
  verdict: string;
  date: string;
  owner: string;
  notes?: string;
}

export interface GoldNoiseHypothesesResponse {
  count: number;
  by_family: Record<string, GoldNoiseHypothesis[]>;
  entries: GoldNoiseHypothesis[];
}
