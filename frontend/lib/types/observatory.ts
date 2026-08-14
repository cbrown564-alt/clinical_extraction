export interface GoldAuditRow {
  audit_id?: string;
  queue_position?: number;
  letter_id?: string;
  entity?: string;
  source_span?: string;
  source_row_index?: string;
  split: string;
  gold_label?: string;
  gold_label_kind?: string;
  gold_reference?: string;
  row_ok?: string;
  reference_found_in_note?: string;
  has_decision?: boolean;
}

export interface GoldAuditDecision {
  dataset?: "gan2026" | "exectv2";
  audit_id?: string | null;
  source_row_index?: number | null;
  split: string;
  simple_class?: "correct" | "ambiguous" | "wrong" | null;
  notes?: string;
  corrected_gold_label?: string | null;
  timestamp?: string;
  auditor?: string;
}

export interface GoldAuditRowsResponse {
  dataset?: "gan2026" | "exectv2";
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

export interface GoldAuditDecisionResponse {
  status: string;
  decision: GoldAuditDecision;
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
