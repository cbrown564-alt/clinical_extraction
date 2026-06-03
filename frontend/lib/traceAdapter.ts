import type {
  CandidateEvent,
  NormalizedEvent,
  PipelineTrace,
  TraceItem,
  RunNoteResponse,
  HybridArtifactRow,
  LLMArtifactRow,
  FullRecordResponse,
} from "./types";

function candidateToTraceItem(c: CandidateEvent): TraceItem {
  return {
    id: c.event_id,
    kind: c.kind,
    rawValue: c.raw_value ?? c.evidence,
    evidence: c.evidence,
    startChar: c.start_char,
    endChar: c.end_char,
    ruleId: c.rule_id,
    ruleGroup: c.rule_group,
    portability: c.portability,
    metadata: c.match_groups,
  };
}

function normalisedToTraceItem(n: NormalizedEvent, candidates: CandidateEvent[]): TraceItem {
  const candidate = candidates.find((c) => c.event_id === n.event_id);
  return {
    id: n.event_id,
    kind: n.semantic_kind,
    rawValue: candidate?.evidence ?? n.normalized_label,
    normalizedValue: n.normalized_label,
    evidence: candidate?.evidence ?? n.normalized_label,
    startChar: candidate?.start_char ?? null,
    endChar: candidate?.end_char ?? null,
    ruleId: candidate?.rule_id,
    ruleGroup: candidate?.rule_group,
    portability: candidate?.portability,
    metadata: {
      monthly_frequency: n.monthly_frequency,
      validation_errors: n.validation_errors,
    },
  };
}

export function adaptDeterministicTrace(
  response: RunNoteResponse,
  noteText: string,
  sourceRowIndex: number,
  split: string
): PipelineTrace {
  const d = response.result.diagnostics;
  return {
    pipelineFamily: response.pipeline as PipelineTrace["pipelineFamily"],
    noteText,
    goldLabel: response.gold_label,
    sourceRowIndex,
    split,
    extract: {
      items: d.candidate_events.map(candidateToTraceItem),
    },
    normalise: {
      items: d.normalized_events.map((n) => normalisedToTraceItem(n, d.candidate_events)),
    },
    select: {
      finalLabel: d.final_selection.final_label,
      rationale: d.final_selection.rationale,
      evidence: d.final_selection.evidence,
      monthlyFrequency: d.final_selection.monthly_frequency,
      selectedIds: d.final_selection.selected_event_ids,
    },
    score: {
      predictedLabel: response.result.output.final_value,
      goldLabel: response.gold_label,
      match: response.result.output.final_value === response.gold_label,
      evidenceValid: d.evidence_valid,
    },
  };
}

export function adaptHybridTrace(
  row: HybridArtifactRow,
  record: FullRecordResponse
): PipelineTrace {
  const dd = row.deterministic_diagnostics;
  const dr = row.decision_record;
  return {
    pipelineFamily: "hybrid_rules_candidates_llm_adjudicator",
    noteText: record.note_text,
    goldLabel: row.reference.gold_label,
    sourceRowIndex: row.source_row_index,
    split: row.split,
    extract: {
      items: dd.candidate_events.map(candidateToTraceItem),
    },
    normalise: {
      items: dd.normalized_events.map((n) => normalisedToTraceItem(n, dd.candidate_events)),
    },
    select: {
      finalLabel: dr.final_label,
      rationale: dr.rationale,
      evidence: dr.evidence,
      monthlyFrequency: undefined, // Could compute from normalized_rate
      selectedIds: dr.accepted_event_ids,
      rejectedIds: dr.rejected_event_ids,
    },
    score: {
      predictedLabel: dr.final_label,
      goldLabel: row.reference.gold_label,
      match: dr.final_label === row.reference.gold_label,
      evidenceValid: dd.evidence_valid,
    },
  };
}

function findEvidenceSpan(noteText: string, evidence: string): { start: number; end: number } | null {
  if (!evidence || !noteText) return null;
  // Exact match first
  const exactPos = noteText.indexOf(evidence);
  if (exactPos >= 0) {
    return { start: exactPos, end: exactPos + evidence.length };
  }
  // Case-insensitive fallback
  const lowerNote = noteText.toLowerCase();
  const lowerEvidence = evidence.toLowerCase();
  const ciPos = lowerNote.indexOf(lowerEvidence);
  if (ciPos >= 0) {
    return { start: ciPos, end: ciPos + evidence.length };
  }
  return null;
}

export function adaptLLMTrace(
  row: LLMArtifactRow,
  record: FullRecordResponse
): PipelineTrace {
  const claims = row.structured_record.claims;
  const fq = row.structured_record.final_query;

  // Build evidence spans by searching for claim evidence in note text
  const claimItems: TraceItem[] = claims.map((claim, idx) => {
    const evidence = claim.evidence;
    let startChar: number | null = null;
    let endChar: number | null = null;
    const span = evidence ? findEvidenceSpan(record.note_text, evidence) : null;
    if (span) {
      startChar = span.start;
      endChar = span.end;
    }
    return {
      id: claim.claim_id || `claim_${idx}`,
      kind: claim.claim_type,
      rawValue: claim.raw_frequency || claim.anchor_text,
      normalizedValue: claim.raw_frequency || undefined,
      evidence: claim.evidence,
      startChar,
      endChar,
      metadata: {
        temporality: claim.temporality,
        assertion_status: claim.assertion_status,
        uncertainty: claim.uncertainty,
        section: claim.section,
        semiology: claim.semiology,
      },
    };
  });

  // Build a single "normalised" item from the final query
  const normalisedItems: TraceItem[] = [];
  if (fq.final_label) {
    normalisedItems.push({
      id: "final_query",
      kind: fq.answer_kind,
      rawValue: fq.raw_selected_frequency || fq.final_label,
      normalizedValue: fq.final_label,
      evidence: fq.evidence,
      startChar: null,
      endChar: null,
      metadata: {
        confidence: fq.confidence,
        conversion_note: fq.conversion_note,
      },
    });
  }

  return {
    pipelineFamily: "llm_only_claim_table_selector",
    noteText: record.note_text,
    goldLabel: row.reference.gold_label,
    sourceRowIndex: row.source_row_index,
    split: row.split,
    extract: { items: claimItems },
    normalise: { items: normalisedItems },
    select: {
      finalLabel: fq.final_label || fq.answer_kind,
      rationale: fq.rationale,
      evidence: fq.evidence,
      selectedIds: fq.selected_claim_ids ? [fq.selected_claim_ids] : undefined,
    },
    repair: row.repair_changes.length > 0
      ? { changes: row.repair_changes }
      : undefined,
    score: {
      predictedLabel: fq.final_label || fq.answer_kind,
      goldLabel: row.reference.gold_label,
      match: (fq.final_label || fq.answer_kind) === row.reference.gold_label,
      evidenceValid: row.evidence_summary.selected_evidence_valid,
    },
  };
}
