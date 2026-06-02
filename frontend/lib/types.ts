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

export type PipelineFamily = "rules_only" | "deterministic_v1";

export type ActiveStage =
  | "raw"
  | "extract"
  | "normalise"
  | "select"
  | "score";

export interface HighlightSpan {
  start: number;
  end: number;
  kind: "deterministic" | "llm" | "repair" | "gold";
  label: string;
  ruleId?: string;
  ruleGroup?: string | null;
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
