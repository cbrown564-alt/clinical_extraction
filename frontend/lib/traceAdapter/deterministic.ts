import type {
  CandidateEvent,
  NormalizedEvent,
  PipelineTrace,
  TraceItem,
  RunNoteResponse,
} from "../types";
import { canonicalSemanticKind, monthlyFrequencyFromLabel } from "./utils";

export function candidateToTraceItem(c: CandidateEvent): TraceItem {
  return {
    id: c.event_id,
    kind: canonicalSemanticKind(c.kind, c.raw_value ?? c.evidence),
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

export function normalisedToTraceItem(
  n: NormalizedEvent,
  candidates: CandidateEvent[]
): TraceItem {
  const candidate = candidates.find((c) => c.event_id === n.event_id);
  const originalLabel = candidate?.raw_value ?? candidate?.evidence ?? n.normalized_label;
  return {
    id: n.event_id,
    kind: canonicalSemanticKind(candidate?.kind ?? n.semantic_kind, n.normalized_label),
    rawValue: originalLabel,
    normalizedValue: n.normalized_label,
    evidence: candidate?.evidence ?? n.normalized_label,
    startChar: candidate?.start_char ?? null,
    endChar: candidate?.end_char ?? null,
    ruleId: candidate?.rule_id ?? "normalize_frequency_label",
    ruleGroup: candidate?.rule_group,
    portability: candidate?.portability,
    metadata: {
      original_label: originalLabel,
      monthly_frequency:
        monthlyFrequencyFromLabel(n.normalized_label) ?? n.monthly_frequency,
      ...(n.validation_errors && n.validation_errors.length > 0
        ? { validation_errors: n.validation_errors }
        : {}),
      ...(candidate?.match_groups && Object.keys(candidate.match_groups).length > 0
        ? { match_groups: candidate.match_groups }
        : {}),
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
    pipelineFamily: response.pipeline,
    noteText,
    goldLabel: response.gold_label,
    sourceRowIndex,
    split,
    extract: {
      items: d.candidate_events.map(candidateToTraceItem),
    },
    normalise: {
      items: d.normalized_events.map((n) =>
        normalisedToTraceItem(n, d.candidate_events)
      ),
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
