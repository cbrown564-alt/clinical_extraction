export interface EvidenceSpan {
  text: string;
  start_char: number | null;
  end_char: number | null;
}

export interface CandidateEvent {
  event_id: string;
  kind: string;
  raw_value: string | null;
  evidence: string;
  start_char: number | null;
  end_char: number | null;
  rule_id: string;
  rule_group: string | null;
  portability: string | null;
  match_groups: Record<string, string | null>;
}

export interface NormalizedEvent {
  event_id: string;
  normalized_label: string;
  semantic_kind: string;
  monthly_frequency: number;
  validation_errors: string[];
}

export interface FinalSelection {
  final_label: string;
  rationale: string;
  evidence: string;
  start_char?: number | null;
  end_char?: number | null;
  final_kind?: string;
  selected_event_ids?: string[];
  monthly_frequency?: number;
}

export interface PipelineDiagnostics {
  candidate_events: CandidateEvent[];
  normalized_events: NormalizedEvent[];
  final_selection: FinalSelection;
  evidence_valid: boolean;
}

export interface PipelineResult {
  output: {
    final_value: string;
    rationale: string;
    evidence: string;
  };
  diagnostics: PipelineDiagnostics;
}

export interface RunNoteResponse {
  pipeline: string;
  source_row_index: number;
  gold_label: string;
  result: PipelineResult;
}

export interface RulePayload {
  rule_id: string;
  group: string;
  portability: string;
  description: string;
  regex_preview: string;
  provenance: string | null;
  examples: Array<{
    text: string;
    expected_label: string | null;
    expected_evidence: string | null;
    anti_example: boolean;
    note: string | null;
  }>;
  has_exclusions: boolean;
}

export interface RulesResponse {
  groups: string[];
  portability: string[];
  rules: RulePayload[];
}

export interface AblationConfigPayload {
  enabled_groups?: string[] | null;
  enabled_portability?: string[] | null;
  disabled_rule_ids?: string[];
}

export type PipelineFamily = string;

export type ActiveStage =
  | "raw"
  | "extract"
  | "normalise"
  | "select"
  | "score";

export interface HighlightSpan {
  start: number;
  end: number;
  kind: "deterministic" | "deterministic-alt" | "llm" | "repair" | "hybrid" | "success" | "gold" | "no-reference";
  label: string;
  ruleId?: string;
  ruleGroup?: string | null;
  portability?: string | null;
  tooltip?: string;
}

export interface SplitRecord {
  source_row_index: number;
  gold_label: string;
  gold_reference: string;
  row_ok: boolean;
  note_preview: string;
}

export interface SplitRecordsResponse {
  split: string;
  count: number;
  records: SplitRecord[];
}

export interface FullRecordResponse {
  split: string;
  source_row_index: number;
  gold_label: string;
  gold_reference: string;
  row_ok: boolean;
  note_text: string;
  labels_match_all_categories: boolean;
  quotes_ok_all_categories: boolean;
}

export interface PipelineFamilyItem {
  value: PipelineFamily;
  label: string;
  executable: boolean;
  kind: "rules_only" | "llm_only" | "hybrid";
  has_replay_artifact: boolean;
  run_count?: number;
}

export interface PipelineFamiliesResponse {
  families: PipelineFamilyItem[];
}

// ── Architect (Phase 2) ──

export type TraceStage = "extract" | "normalise" | "select" | "repair" | "score";

export interface TraceItem {
  id: string;
  kind: string;
  rawValue: string;
  normalizedValue?: string;
  evidence: string;
  startChar: number | null;
  endChar: number | null;
  ruleId?: string;
  ruleGroup?: string | null;
  portability?: string | null;
  metadata?: Record<string, unknown>;
}

export interface StageExtract {
  items: TraceItem[];
}

export interface StageNormalise {
  items: TraceItem[];
}

export interface StageSelect {
  finalLabel: string;
  rationale: string;
  evidence: string;
  monthlyFrequency?: number;
  selectedIds?: string[];
  rejectedIds?: string[];
}

export interface StageRepair {
  changes: string[];
  beforeLabel?: string;
  afterLabel?: string;
}

export interface StageScore {
  predictedLabel: string;
  goldLabel: string;
  match: boolean;
  evidenceValid: boolean;
}

export interface PipelineTrace {
  pipelineFamily: PipelineFamily;
  noteText: string;
  goldLabel: string;
  sourceRowIndex: number;
  split: string;
  extract: StageExtract;
  normalise: StageNormalise;
  select: StageSelect;
  repair?: StageRepair;
  score: StageScore;
}

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

// ── Artifact / Registry ──

export type ClinicalTask = "gan2026" | "exectv2";

export interface RegistryEntry {
  task?: ClinicalTask;
  run_id: string;
  pipeline_family: string;
  date: string;
  row_count: number;
  artifact_paths: string[];
  architecture_family?: string;
  claim_boundary?: string;
  scorer_view?: string;
  mode?: string;
  model?: string;
  model_role?: string;
  split?: string;
  decision?: string;
}

export interface RegistryResponse {
  registry_path: string;
  runs: RegistryEntry[];
}

export interface ArtifactResponse {
  run_id: string;
  artifact_path: string;
  artifact_type: string;
  content: unknown[];
}

// ── ExECTv2 frontend review data ──

export type Exectv2Entity =
  | "Diagnosis"
  | "SeizureFrequency"
  | "Prescription"
  | "Investigations";

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

export interface ReliabilityScorecardDimension {
  id: string;
  dimension: string;
  coverage: number;
  current_evidence: string;
  gap_to_close: string;
  artifact_path?: string;
}

// ── Hybrid artifact row ──

export interface HybridArtifactRow {
  source_row_index: number;
  split: string;
  deterministic_diagnostics: {
    candidate_events: CandidateEvent[];
    normalized_events: NormalizedEvent[];
    final_selection: FinalSelection;
    evidence_valid: boolean;
  };
  decision_record: {
    final_label: string;
    rationale: string;
    evidence: string;
    accepted_event_ids: string[];
    rejected_event_ids: string[];
    temporality: string;
    uncertainty: string;
    normalized_rate: string;
  };
  reference: {
    gold_label: string;
  };
  scores?: Record<string, unknown>;
}

// ── LLM artifact row ──

export interface LLMClaim {
  claim_id: string;
  claim_type: string;
  evidence: string;
  raw_frequency: string | null;
  temporality: string;
  assertion_status: string;
  uncertainty: string;
  anchor_text: string;
  section: string | null;
  semiology: string | null;
}

export interface LLMFinalQuery {
  final_label: string | null;
  answer_kind: string;
  evidence: string;
  rationale: string;
  confidence: string;
  conversion_note: string | null;
  raw_selected_frequency: string | null;
  selected_claim_ids: string;
}

export interface LLMArtifactRow {
  source_row_index: number;
  split: string;
  structured_record: {
    claims: LLMClaim[];
    final_query: LLMFinalQuery;
  };
  repair_changes: string[];
  evidence_summary: {
    selected_evidence: string;
    selected_evidence_valid: boolean;
  };
  score_layers: Record<string, {
    final_label: string;
    purist_correct?: boolean;
    pragmatic_correct?: boolean;
    scorable?: boolean;
  }>;
  reference: {
    gold_label: string;
  };
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

export interface CategoryMetrics {
  tp: number;
  fp: number;
  fn: number;
  precision: number;
  recall: number;
  f1: number;
  support: number;
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

// ── Laboratory (Phase 4) ──

export interface RunAblationResponse {
  split: string;
  pipeline: string;
  row_count: number;
  ablation_config: AblationConfigPayload;
  summary: {
    total: number;
    purist: {
      accuracy: number;
      f1: number;
      precision: number;
      recall: number;
      per_label: Record<string, CategoryMetrics>;
    };
    pragmatic: {
      accuracy: number;
      f1: number;
      precision: number;
      recall: number;
      per_label: Record<string, CategoryMetrics>;
    };
  };
  rows: Array<{
    source_row_index: number;
    prediction_label: string;
    gold_label: string;
    purist_predicted_category: string;
    purist_gold_category: string;
    pragmatic_predicted_category: string;
    pragmatic_gold_category: string;
    evidence_valid: boolean;
  }>;
}

export interface PromptPolicy {
  policy_id: string;
  controlled_variable: string;
  portability: string;
  status: string;
  description: string;
}

export interface PromptPayload {
  module: string;
  prompt_version: string;
  policy_taxonomy: PromptPolicy[];
  policy_ids: string[];
}

export interface PromptsResponse {
  prompts: PromptPayload[];
}

export interface PromptTemplateResponse {
  module: string;
  prompt_version: string;
  system_hint: string | null;
  user_hint: string | null;
  output_schema_hint: string | null;
  build_prompt_signature: string | null;
  policy_taxonomy: PromptPolicy[];
}

// ── Error taxonomy ──

export interface TagErrorResponse {
  error_type: "correct" | "false_negative" | "false_positive" | "over_estimate" | "under_estimate" | "near_miss";
  severity: number;
  severity_level: "none" | "near" | "moderate" | "significant" | "severe";
}

export interface ErrorTaxonomySchemaResponse {
  error_types: Array<{ id: string; description: string }>;
  severity: { description: string; levels: string[] };
}

// ── Hard slices ──

export interface HardSliceDefinition {
  slice_name: string;
  component_focus: string;
  membership_rule: string;
  primary_metric: string;
}

export interface HardSliceDefinitionsResponse {
  slices: HardSliceDefinition[];
}

export interface HardSliceMembershipResponse {
  rows: Array<{ source_row_index: number | null; hidden_families: string[] }>;
}

// ── Meta / git ──

export interface MetaResponse {
  git: {
    branch: string | null;
    commit: string | null;
    dirty: boolean;
    remote_url: string | null;
  };
  observatory_version: string;
  timestamp: string;
}

// ── Artifact rows for additional pipeline families ──

// Group A: Decision-record-only families
// (llm_first_direct_extractor, dspy_final_selection_adjudicator)
export interface DecisionRecordArtifactRow {
  source_row_index: number;
  split: string;
  decision_record: {
    final_label: string;
    evidence: string;
    rationale: string;
    answer_kind?: string;
    confidence?: string;
    temporality?: string;
    uncertainty?: string;
    selected_event_ids?: string[];
    rejected_event_ids?: string[];
  } | null;
  comparison: {
    purist_correct?: boolean;
    pragmatic_correct?: boolean;
    predicted_purist_category?: string;
    gold_purist_category?: string;
    predicted_monthly_frequency?: number;
    gold_monthly_frequency?: number;
  } | null;
  reference: {
    gold_label: string;
  };
  evidence_valid?: boolean;
  parse_errors?: string[];
  repair_changes?: unknown[];
  score_layers?: Record<string, unknown>;
}

// Group B: Events-based families
// (llm_structured_events, hybrid_structured_events, llm_heavy_clinical_frequency_reasoner)
export interface EventsArtifactRow {
  source_row_index: number;
  split: string;
  structured_record: {
    events?: Array<{
      event_id: string;
      kind: string;
      applies_to?: string | null;
      assertion_status?: string;
      evidence: string;
      raw_phrase?: string;
      raw_value?: string;
      model_normalized_clinical_label?: string;
      temporality?: string;
      notes?: string;
      certainty?: string;
      clinical_quantity?: Record<string, unknown>;
    }>;
    selection?: {
      selected_event_ids?: string[];
      rejected_event_ids?: string[];
      final_label?: string;
      final_kind?: string;
      evidence?: string;
      rationale?: string;
      confidence?: string;
      aggregation_strategy?: string;
      uncertainty_flags?: string[];
    };
    final_answer?: {
      raw_llm_final_label?: string;
      raw_llm_final_kind?: string;
      raw_llm_monthly_frequency?: number | null;
      selected_evidence?: string;
      final_rationale?: string;
      selected_event_ids?: string;
      rendering_operands?: Record<string, unknown>;
    };
  };
  normalized_events?: NormalizedEvent[];
  comparison?: {
    purist_correct?: boolean;
    pragmatic_correct?: boolean;
  };
  score_layers?: Record<string, unknown>;
  repair_changes?: unknown[];
  evidence_summary?: {
    selected_evidence?: string;
    selected_evidence_valid?: boolean;
  };
  reference: {
    gold_label: string;
  };
}

// Group C: Selected-fact families
// (llm_heavy_evidence_selection_with_deterministic_adapters)
export interface SelectedFactArtifactRow {
  source_row_index: number;
  split: string;
  structured_record: {
    selected_fact?: {
      fact_id?: string;
      clinical_kind?: string;
      raw_value?: string;
      evidence: string;
      rationale?: string;
      assertion_status?: string;
      temporality?: string;
      applies_to?: string;
      benchmark_caveat_flags?: string[];
      competing_fact_summary?: string;
    };
    raw_model_answer?: {
      selected_evidence?: string;
    };
    operands?: Record<string, unknown>;
  };
  mechanical_adapter?: {
    final_label?: string;
    error?: string | null;
    adapter_families?: string[];
    operand_complete?: boolean;
  };
  score_layers?: Record<string, unknown>;
  repair_changes?: unknown[];
  evidence_summary?: {
    selected_fact_evidence?: string;
    selected_evidence?: string;
    selected_evidence_valid?: boolean;
  };
  reference: {
    gold_label: string;
  };
}

// Group D: State-graph families
// (hybrid_clinical_frequency_state_graph)
export interface StateGraphArtifactRow {
  source_row_index: number;
  split: string;
  structured_record: {
    nodes?: Array<{
      semantic_kind?: string;
      node_normalized_label?: string;
      evidence: string;
      rationale?: string;
      assertion_status?: string;
      certainty?: string;
      temporality?: string;
    }>;
    no_reference_vs_unknown_rationale?: string;
  };
  representability_gain_candidate?: boolean;
  surface_role?: string;
  evidence_summary?: {
    exact_evidence_total?: number;
    exact_evidence_valid?: number;
    selected_evidence?: string;
    selected_evidence_valid?: boolean;
  };
  repair_changes?: unknown[];
  reference: {
    gold_label: string;
  };
}

// Group E: Replacement postprocessing ablation
// (llm_replacement_postprocessing_ablation)
export interface ReplacementAblationArtifactRow {
  source_row_index: number;
  split: string;
  final_label: string;
  raw_label: string;
  gold_label: string;
  repair_mode: string;
  replacement_target: string;
  condition?: string;
  changed_from_comparator?: boolean;
  changed_from_raw?: boolean;
  purist_correct?: boolean;
  pragmatic_correct?: boolean;
  scorable?: boolean;
  purist_category_transition?: string;
  pragmatic_category_transition?: string;
  semantic_kind_transition?: string;
  transition_reason?: string;
  prediction_owner?: string;
  projection_owner?: string;
  node_source?: string;
  hard_slice_tags?: string[];
}
