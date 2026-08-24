import type { ActiveMethod } from "./shared";

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
  /**
   * How the clinical-recovery headline treats this mention's scoring unit:
   * "deduplicated" — a Redundant-Convention Duplicate the headline collapses
   * (same unit as an earlier mention; the model is not charged for it);
   * "distinct_assertion" — a Distinct-Assertion Duplicate the headline counts
   * per occurrence (same concept repeated at distinct offsets); "" otherwise.
   */
  headline_status: "" | "deduplicated" | "distinct_assertion";
  /**
   * Last assembly action that changed this mention away from the model
   * baseline. Empty when the finding is still the producer's unchanged fact.
   */
  last_rule_action?: string;
  /** Plain sentence for that action, including before/after when recorded. */
  last_rule_label?: string;
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
  active_method?: string;
  method_id?: string;
  saved_run_id?: string;
  retained_evidence_id?: string;
  legacy_run_ids?: string[];
  task: "exectv2";
  label: string;
  model: string;
  kind?: ActiveMethod;
  paper_cell?: import("../paperCells").PaperCellId;
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
