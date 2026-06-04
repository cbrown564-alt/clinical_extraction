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

export interface RegistryEntry {
  run_id: string;
  pipeline_family: string;
  date: string;
  row_count: number;
  artifact_paths: string[];
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
  rows: RowScore[];
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
// (llm_structured_events, llm_heavy_clinical_frequency_reasoner, llm_only_typed_adapter_reasoner)
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

// Group C: Operations-based families
// (llm_only_typed_operations_reasoner)
export interface OperationsArtifactRow {
  source_row_index: number;
  split: string;
  structured_record: {
    operations?: Array<{
      operation_id: string;
      operation_kind: string;
      operands?: Record<string, unknown>;
      raw_phrase?: string;
      evidence: string;
      evidence_id?: string;
      assertion_status?: string;
      certainty?: string;
      clinical_note?: string;
      temporality?: string;
      model_normalized_clinical_label?: string;
    }>;
    selection?: {
      selected_operation_ids?: string[];
      rejected_operation_ids?: string[];
      selected_evidence?: string;
      selected_evidence_id?: string;
      selection_strategy?: string;
      target_policy?: string;
      final_clinical_state?: string;
      rationale?: string;
      uncertainty_flags?: string[];
    };
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

// Group D: Selected-fact / state families
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

// (llm_only_simplified_selected_state_reasoner, llm_only_sparse_operands_selected_state_reasoner)
export interface SelectedStateArtifactRow {
  source_row_index: number;
  split: string;
  structured_record: {
    selected_state?: {
      final_kind?: string;
      raw_llm_final_label?: string;
      raw_source_phrase?: string;
      selected_evidence: string;
      selection_reason?: string;
      uncertainty_flags?: string[];
      operands?: Record<string, unknown>;
      selected_operation_kind?: string;
    };
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

// Group E: State-graph families
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

// Group F: Parallel hybrid
// (hybrid_parallel_state_candidate_reasoner)
export interface ParallelHybridArtifactRow {
  source_row_index: number;
  split: string;
  component_inputs?: {
    deterministic_candidates?: CandidateEvent[];
    deterministic_top?: {
      selected_event_ids?: string[];
      selected_decision?: string;
      selected_score?: number;
      selection_candidates?: unknown[];
    };
    state_graph_nodes?: Array<{
      semantic_kind?: string;
      node_normalized_label?: string;
      evidence?: string;
      rationale?: string;
    }>;
    state_graph_projection?: {
      final_label?: string;
      final_kind?: string;
      monthly_frequency?: number;
      rationale?: string;
      selected_node_ids?: string[];
      uncertainty_flags?: string[];
      evidence?: string;
    };
  };
  structured_adjudicator_record?: {
    final_label?: string;
    evidence?: string;
    rationale?: string;
    selected_event_ids?: string[];
    rejected_event_ids?: string[];
  } | null;
  structured_llm_candidate_record?: {
    final_label?: string;
    evidence?: string;
    rationale?: string;
  } | null;
  score_layers?: Record<string, unknown>;
  repair_changes?: unknown[];
  diagnostics?: Record<string, unknown>;
  reference: {
    gold_label: string;
  };
}

// Group G: Minimal evidence
// (llm_only_minimal_evidence_selector)
export interface MinimalEvidenceArtifactRow {
  source_row_index: number;
  split: string;
  minimal_record?: {
    final_label?: string;
    evidence?: string;
    rationale?: string;
    confidence?: string;
    selected_evidence?: string;
  };
  score_layers?: Record<string, unknown>;
  contract_diagnostics?: Record<string, unknown>;
  derived_diagnostics?: Record<string, unknown>;
  evidence_summary?: {
    selected_evidence?: string;
    selected_evidence_valid?: boolean;
  };
  repair_changes?: unknown[];
  reference: {
    gold_label: string;
  };
}

// Group H: Replacement postprocessing ablation
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
