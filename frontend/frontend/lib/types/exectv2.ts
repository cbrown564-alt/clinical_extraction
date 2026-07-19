import type { ClinicalTask } from "./shared";

// ── ExECTv2 frontend review data ──

export type Exectv2Entity =
  | "Diagnosis"
  | "SeizureFrequency"
  | "Prescription"
  | "Investigations";

export type Exectv2ComparisonMode =
  | "llm_plus_rules"
  | "llm_only"
  | "deterministic_only";

export interface Exectv2Mention {
  id: string;
  source: "gold" | "predicted";
  entity: Exectv2Entity | string;
  text: string;
  evidence: string;
  evidence_valid: boolean;
  component_owner: string;
  source_lane: string;
  source_model: string;
  confidence: string;
  assertion: string;
  attributes: Record<string, string>;
  status: string;
  /**
   * How the clinical-recovery headline treats this mention's scoring unit:
   * "deduplicated" — a Redundant-Convention Duplicate the headline collapses
   * (same unit as an earlier mention; the model is not charged for it);
   * "distinct_assertion" — a Distinct-Assertion Duplicate the headline counts
   * per occurrence (same concept repeated at distinct offsets); "" otherwise.
   */
  headline_status: "" | "deduplicated" | "distinct_assertion";
}

export interface Exectv2EvidenceSpan {
  start: number;
  end: number;
  text: string;
  entity: Exectv2Entity | string;
  kind: "gold" | "llm";
  label: string;
}

export interface Exectv2FamilyMetrics {
  f1: number | null;
  precision: number | null;
  recall: number | null;
  tp: number | null;
  fp: number | null;
  fn: number | null;
}

export interface Exectv2LetterRecord {
  letter_id: string;
  split: string;
  stage: string;
  letter_text: string;
  gold_mentions: Exectv2Mention[];
  predicted_mentions: Exectv2Mention[];
  family_counts: {
    gold: Record<Exectv2Entity, number>;
    predicted: Record<Exectv2Entity, number>;
  };
  evidence_spans: Exectv2EvidenceSpan[];
}

export interface Exectv2RunSummary {
  run_id: string;
  task: "exectv2";
  label: string;
  model: string;
  comparison_mode: Exectv2ComparisonMode;
  architecture_family: string;
  pipeline_family: string;
  split: string;
  row_count: number;
  date: string;
  decision: string;
  promotion_decision: string;
  claim_boundary: string;
  scorer_view: string;
  artifact_paths: string[];
  source_paths: string[];
  metrics: {
    overall_f1: number | null;
    precision: number | null;
    recall: number | null;
    families: Record<Exectv2Entity, Exectv2FamilyMetrics>;
  };
  operational: {
    call_failures: number;
    parse_schema_failures: number;
    evidence_invalid_dropped: number;
    exact_evidence_rate: number | null;
    by_family: Record<string, unknown>;
  };
  letters: Exectv2LetterRecord[];
}

export interface Exectv2RunsResponse {
  generated_on: string;
  source_index: string;
  runs: Exectv2RunSummary[];
}

export interface Exectv2SharedLetterRecord {
  letter_id: string;
  split: string;
  stage: string;
  letter_text: string;
  gold_mentions: Exectv2Mention[];
  gold_family_counts: Record<Exectv2Entity, number>;
  evidence_spans: Exectv2EvidenceSpan[];
}

export interface Exectv2RunLetterRecord {
  letter_id: string;
  split: string;
  stage: string;
  predicted_mentions: Exectv2Mention[];
  predicted_family_counts: Record<Exectv2Entity, number>;
  evidence_spans: Exectv2EvidenceSpan[];
}

export type Exectv2RunWireSummary = Omit<Exectv2RunSummary, "letters"> & {
  letters: Exectv2RunLetterRecord[];
};

export interface Exectv2RunsWireResponse {
  generated_on: string;
  source_index: string;
  shared_letters: Exectv2SharedLetterRecord[];
  runs: Exectv2RunWireSummary[];
}

export interface Exectv2RunWireResponse {
  generated_on: string;
  source_index: string;
  shared_letters: Exectv2SharedLetterRecord[];
  run: Exectv2RunWireSummary;
}

export interface Exectv2LayerScore {
  precision?: number;
  recall?: number;
  f1: number;
  tp?: number;
  fp?: number;
  fn?: number;
  pred_count?: number;
  gold_count?: number;
  precision_tp?: number;
  recall_tp?: number;
}

export interface Exectv2LayerScoreSet {
  overall: Exectv2LayerScore;
  families: Record<Exectv2Entity, Exectv2LayerScore>;
}

export interface Exectv2LayerDefinition {
  layer_id: string;
  label: string;
  component_type: string;
  score_source: string;
  surface_key: string;
  interpretation: string;
  /** Structurally inert stage (no score change on these single-lane runs); hidden from the ladder. */
  inert?: boolean;
}

export interface Exectv2LayerSnapshot {
  layer_id: string;
  label: string;
  component_type: string;
  surface_key: string;
  interpretation: string;
  /** Structurally inert stage (no score change on these single-lane runs); hidden from the ladder. */
  inert?: boolean;
  scores: Exectv2LayerScoreSet;
}

export interface Exectv2LayerImpact {
  artifact_kind: "exectv2_component_layer_impact";
  dataset: "exectv2";
  generated_on: string;
  run_id: string;
  layer_id: string;
  layer_label: string;
  component_type: string;
  previous_layer_id: string;
  previous_layer_label: string;
  overall_delta_from_previous: number;
  family_deltas: Record<Exectv2Entity, number>;
  current_score: Exectv2LayerScoreSet;
  previous_score: Exectv2LayerScoreSet | null;
  claim_boundary: string;
  row_inspection_policy: string;
}

export interface Exectv2ArchitectureLadder {
  artifact_kind: "exectv2_component_architecture_ladder";
  dataset: "exectv2";
  generated_on: string;
  run_id: string;
  label: string;
  model: string;
  decision: string;
  architecture_family: string;
  split: string;
  row_count: number;
  final_score: Exectv2LayerScoreSet;
  layers: Exectv2LayerSnapshot[];
  layer_impacts: Exectv2LayerImpact[];
  source_artifacts: string[];
  claim_boundary: string;
  row_inspection_policy: string;
}

export interface Exectv2ComponentAblationResponse {
  artifact_kind: "exectv2_component_ablation_set";
  dataset: "exectv2";
  generated_on: string;
  row_inspection_policy: string;
  allow_model_calls: boolean;
  allow_post_run_tuning: boolean;
  claim_boundary: string;
  provenance_policy: string;
  layers: Exectv2LayerDefinition[];
  architectures: Exectv2ArchitectureLadder[];
  ablations: Exectv2LayerImpact[];
}

// ── ExECTv2 per-letter stage-transition examples (illustrative, explanatory only) ──

export interface Exectv2TransitionMention {
  entity: string;
  text: string;
  concept: string;
  attributes: Record<string, string>;
  source_lane: string;
  evidence: string;
}

export interface Exectv2TransitionChange {
  before: Exectv2TransitionMention;
  after: Exectv2TransitionMention;
}

export interface Exectv2TransitionStage {
  stage_id: string;
  label: string;
  component_type: string;
  interpretation: string;
  has_transition: boolean;
  is_baseline: boolean;
  mention_count: number | null;
  added: Exectv2TransitionMention[];
  dropped: Exectv2TransitionMention[];
  changed: Exectv2TransitionChange[];
  kept: number;
  note?: string;
}

export interface Exectv2TransitionGoldMention {
  entity: string;
  text: string;
}

export interface Exectv2TransitionExample {
  letter_id: string;
  gold: Exectv2TransitionGoldMention[];
  gold_count: number;
  final_count: number | null;
  change_count: number;
  stages: Exectv2TransitionStage[];
}

export interface Exectv2TransitionArchitecture {
  run_id: string;
  label: string;
  model: string;
  decision: string;
  examples: Exectv2TransitionExample[];
}

export interface Exectv2ComponentTransitionsResponse {
  artifact_kind: "exectv2_component_transition_examples";
  dataset: "exectv2";
  generated_on: string;
  row_inspection_policy: string;
  allow_model_calls: boolean;
  allow_post_run_tuning: boolean;
  claim_boundary: string;
  examples_per_architecture: number;
  stage_order: string[];
  architectures: Exectv2TransitionArchitecture[];
}

export interface ReliabilityScorecardDimension {
  id: string;
  number?: number;
  dimension: string;
  coverage: number | null;
  coverage_max?: number | null;
  strength?: "strong" | "medium" | "weak" | "unknown";
  current_evidence: string;
  gap_to_close: string;
  artifact_path?: string;
}

export interface Exectv2ReliabilityEvidenceRow {
  role: string;
  candidate: string;
  surface: string;
  overall_f1: number | null;
  decision: string;
}

export interface Exectv2ReliabilityMetricStatus {
  metric: string;
  current_status: string;
}

export interface Exectv2ResidualRisk {
  family: string;
  current_strength: string;
  residual_risk: string;
}

export interface Exectv2UpgradePlanItem {
  dimension: string;
  next_metric_needed: string;
}

export interface Exectv2ComparisonRow {
  candidate: string;
  model: string;
  architecture_family: string;
  split_stage: string;
  call_failures: number | null;
  parse_schema_failures: number | null;
  exact_evidence_rate: number | null;
  overall_f1: number | null;
  diagnosis_f1: number | null;
  seizure_frequency_f1: number | null;
  prescription_f1: number | null;
  investigations_f1: number | null;
  companion_surface: string;
  decision: string;
  claim_boundary: string;
}

export interface Exectv2ReliabilityRunRef {
  candidate: string;
  model_label: string;
  rows_path: string;
  role: string;
  claim_boundary: string;
  summary_path?: string;
}

export interface Exectv2ReliabilityLatestSurface {
  surface_id: string;
  surface_label: string;
  /**
   * Latest-model run references for this surface, one per non-control model.
   * The backend derives these from the reliability catalog (catalog.yaml), so
   * adding a new model to the catalog surfaces a column here automatically —
   * no model-name hardcoding. Render one column per distinct `model_label`.
   */
  latest_runs: Exectv2ReliabilityRunRef[];
  replacement_policy: string;
  rationale: string;
}

export interface Exectv2ReliabilityMetricBin {
  bin: string;
  cells: number;
  confidence_range?: [number, number];
  avg_confidence_proxy: number;
  avg_calibrated_confidence?: number;
  accuracy: number;
  calibration_gap?: number;
  ece_contribution?: number;
  mean_cell_f1: number;
}

export interface Exectv2ReliabilityCalibrationFamily {
  family: string;
  cells: number;
  accuracy: number;
  mean_calibrated_confidence: number;
  expected_calibration_error: number;
  brier_score: number;
  constant_base_rate_brier_score: number;
  bin_count: number;
}

export interface Exectv2ReliabilityReviewFamily {
  family: string;
  eligible_cells: number;
  reviewed_cells?: number;
  caught_error_cells?: number;
  false_alarm_cells?: number;
  missed_error_cells?: number;
  total_error_cells?: number;
  review_burden: number;
  catch_rate: number;
}

export interface Exectv2ReliabilityReviewOperatingPoint {
  id: string;
  label: string;
  rules: string[];
  validation_status: string;
  eligible_cells: number;
  reviewed_cells: number;
  review_burden: number;
  total_error_cells: number;
  caught_error_cells: number;
  catch_rate: number;
  false_alarm_cells: number;
  false_alarm_rate: number;
  missed_error_cells: number;
  review_burden_delta_vs_high_recall: number;
  catch_rate_delta_vs_high_recall: number;
}

export interface Exectv2ReliabilityActiveReadout {
  candidate: string;
  model_label: string;
  rows_path: string;
  rows: number;
  surface: string;
  clinical_headline_f1: number;
  precision: number;
  recall: number;
  strict_benchmark_f1: number;
  evidence_validity: number;
  call_failures: number;
  parse_errors: number;
  family_f1: Record<string, number>;
  claim_boundary: string;
}

export interface Exectv2ComputedReliability {
  analysis_kind: string;
  claim_boundary: string;
  latest_run_check: {
    surfaces: Exectv2ReliabilityLatestSurface[];
  };
  cross_model_agreement: {
    overall: {
      pair_count: number;
      cell_count: number;
      exact_cell_agreement_rate: number;
      mean_pairwise_jaccard: number;
    };
  };
  calibration_proxy: {
    cell_count: number;
    bin_count: number;
    expected_calibration_error: number;
    brier_score?: number;
    constant_base_rate_brier_score?: number;
    brier_improvement_vs_base_rate?: number;
    mean_calibrated_confidence?: number;
    max_adjacent_bin_reversal?: number;
    model_type?: string;
    validation_status?: string;
    leakage_audit?: {
      group_key: string;
      fold_count: number;
      unique_groups: number;
      shared_letter_between_train_and_test: boolean;
      forbidden_validation_rows_loaded: boolean;
      forbidden_row_level_outputs_emitted: boolean;
      candidate_identity_used_as_feature: boolean;
      gold_or_failure_residual_used_as_feature: boolean;
    };
    bins: Exectv2ReliabilityMetricBin[];
    per_family?: Exectv2ReliabilityCalibrationFamily[];
  };
  review_routing: {
    eligible_cells: number;
    reviewed_cells: number;
    review_burden: number;
    total_error_cells: number;
    caught_error_cells: number;
    catch_rate: number;
    false_alarm_cells: number;
    missed_error_cells: number;
    operating_points: Exectv2ReliabilityReviewOperatingPoint[];
    by_family: Exectv2ReliabilityReviewFamily[];
  };
  active_llm_only_readout: Exectv2ReliabilityActiveReadout[];
}

export interface Exectv2ReliabilityScorecardResponse {
  dataset?: ClinicalTask;
  generated_on: string;
  source_scorecard: string;
  source_cross_model_report: string;
  evidence_set: Exectv2ReliabilityEvidenceRow[];
  dimensions: ReliabilityScorecardDimension[];
  weak_dimensions: ReliabilityScorecardDimension[];
  metrics_available_now: Exectv2ReliabilityMetricStatus[];
  residual_risks: Exectv2ResidualRisk[];
  upgrade_plan: Exectv2UpgradePlanItem[];
  comparison_rows: Exectv2ComparisonRow[];
  computed_reliability?: Exectv2ComputedReliability;
}

export type ReliabilityScorecardResponse = Exectv2ReliabilityScorecardResponse;

// ── SeizureFrequency gold-vs-prediction inspection ──
//
// Served by GET /exectv2/sf-inspection. The payload is scorer-faithful: the
// backend re-scores dev140 with the real score_frequency_state and aborts unless
// the scorecard reproduces the published F1s, so these numbers can be trusted.

export interface SfInspectionMetric {
  f1: number;
  precision: number;
  recall: number;
  tp: number;
  fp: number;
  fn: number;
}

/** component_name -> per-component metrics for the 11 FrequencyStateScores. */
export type SfInspectionScorecard = Record<string, SfInspectionMetric>;

export interface SfComponentMeta {
  name: string;
  info: string;
}

/** Per-mention row in one Layer B scoring component. */
export interface SfMentionRow {
  side: "gold" | "pred";
  phrase: string;
  counts: string;
  frequency_change: string;
  count_state: string;
  projected_state: string;
  key: string;
  status: "tp" | "fp" | "fn" | "skip";
}

export interface SfLayerBComponent {
  name: string;
  info: string;
  has_error: boolean;
  verdict: "clean" | "err";
  tp: number;
  fp: number;
  fn: number;
  rows: SfMentionRow[];
}

/** One attribute comparison row in a Layer A pair. */
export interface SfAttributeRow {
  key: string;
  gold: string;
  pred: string;
  validity: "ok" | "absent" | "illegal_value" | "illegal_attr" | "noise";
  canonical: string;
  match: "ok" | "bad" | "absent";
}

/** A dated, curated ``gold_data_issues.jsonl`` entry disputing this specific
 * value in gold -- distinct from an unadjudicated FP/FN. */
export interface SfGoldAdvisory {
  source: "gold_data_issues";
  gold_value: string;
  conflicting_evidence: string;
  resolution_status: string;
}

export interface SfLayerAPair {
  label: string;
  side: "pair" | "fn" | "fp";
  gold_phrase: string;
  gold_normalized: string;
  pred_phrase: string;
  pred_normalized: string;
  phrase_match: "ok" | "bad" | "absent";
  attributes: SfAttributeRow[];
  gold_advisory: SfGoldAdvisory | null;
}

/** A prior canonical adjudication for this letter, read-only and best-effort:
 * adjudicated against a different run than the one this payload scores, so it
 * is letter-level context, not a claim about one exact mention. */
export interface SfGoldCaseLedgerRow {
  disagreement_type: string;
  match_key: string;
  mechanism: string;
  verdict: "gold_right" | "model_defensible" | "both_defensible" | "unadjudicated";
  reason: string;
  run_id: string;
}

export interface SfLineageOverrideItem {
  applies_to: string;
  prior_frequency_change: string;
  assembled_magnitude: string;
  selection_mode: string;
  selected_candidate_id: string;
}

export interface SfLineageOverride {
  applied: boolean;
  /** Present when the LLM magnitude complement fired (applied === true). */
  items?: SfLineageOverrideItem[];
  /** Present when FrequencyChange differs from baseline but no ledger row exists. */
  baseline?: string[];
  complement?: string[];
}

export interface SfCandidateSpan {
  text_hint: string;
  candidate_type: string;
  source: string;
  evidence: string;
}

export interface SfLineage {
  candidate_spans: SfCandidateSpan[];
  override: SfLineageOverride | null;
}

export interface SfInspectionLetter {
  letter_id: string;
  has_activity: boolean;
  gold_count: number;
  pred_count: number;
  total_errors: number;
  direction_errors: { fp: number; fn: number };
  magnitude_errors: { fp: number; fn: number };
  layer_a: { pairs: SfLayerAPair[] };
  layer_b: { components: SfLayerBComponent[] };
  lineage: SfLineage;
  gold_case_ledger: SfGoldCaseLedgerRow[];
}

export interface SfInspectionResponse {
  generated_on: string;
  split: string;
  artifact: string;
  n_letters: number;
  n_with_errors: number;
  scorecard: SfInspectionScorecard;
  components: SfComponentMeta[];
  letters: SfInspectionLetter[];
}
