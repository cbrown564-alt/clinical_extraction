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

export type PipelineFamily =
  | "rules_only"
  | "deterministic_v1"
  | "llm_only_claim_table_selector"
  | "llm_only_direct_labeler"
  | "llm_only_structured_events"
  | "hybrid_rules_candidates_llm_adjudicator";

export type ActiveStage =
  | "raw"
  | "extract"
  | "normalise"
  | "select"
  | "score";

export interface HighlightSpan {
  start: number;
  end: number;
  kind: "deterministic" | "deterministic-alt" | "llm" | "repair" | "hybrid" | "success" | "gold";
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
