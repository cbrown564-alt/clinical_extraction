import type {
  PipelineTrace,
  EventsArtifactRow,
  FullRecordResponse,
  TraceItem,
} from "../types";
import { findEvidenceSpan, buildScoreFromComparison, buildSchemaRepair, canonicalSemanticKind } from "./utils";

export function adaptEventsTrace(
  row: EventsArtifactRow,
  record: FullRecordResponse,
  family: string
): PipelineTrace {
  const events = row.structured_record?.events ?? [];
  const selection = row.structured_record?.selection;
  const finalAnswer = row.structured_record?.final_answer;
  const normalizedEvents = row.normalized_events ?? [];

  // Extract stage: events as candidate items
  const extractItems: TraceItem[] = events.map((evt, idx) => {
    const span = evt.evidence ? findEvidenceSpan(record.note_text, evt.evidence) : null;
    return {
      id: evt.event_id || `event_${idx}`,
      kind: canonicalSemanticKind(evt.kind, evt.raw_phrase || evt.raw_value || evt.evidence),
      rawValue: evt.raw_phrase || evt.raw_value || evt.evidence,
      normalizedValue: evt.model_normalized_clinical_label || undefined,
      evidence: evt.evidence,
      startChar: span?.start ?? null,
      endChar: span?.end ?? null,
      metadata: {
        temporality: evt.temporality,
        assertion_status: evt.assertion_status,
        certainty: evt.certainty,
        notes: evt.notes,
        clinical_quantity: evt.clinical_quantity,
      },
    };
  });

  // Normalise stage: use normalized_events if available, otherwise fall back to events
  const normaliseItems: TraceItem[] =
    normalizedEvents.length > 0
      ? normalizedEvents.map((n) => {
          const matchingEvt = events.find((e) => e.event_id === n.event_id);
          const rawStr =
            matchingEvt?.raw_phrase ??
            matchingEvt?.raw_value ??
            matchingEvt?.evidence ??
            n.normalized_label;
          const evText = matchingEvt?.evidence ?? matchingEvt?.raw_phrase ?? matchingEvt?.raw_value ?? n.normalized_label;
          const span = evText ? findEvidenceSpan(record.note_text, evText) : null;
          return {
            id: n.event_id,
            kind: canonicalSemanticKind(matchingEvt?.kind ?? n.semantic_kind, n.normalized_label),
            rawValue: rawStr,
            normalizedValue: n.normalized_label,
            evidence: evText,
            startChar: span?.start ?? null,
            endChar: span?.end ?? null,
            ruleId: matchingEvt?.kind ? `normalize_${matchingEvt.kind}` : "normalize_frequency_label",
            ruleGroup: matchingEvt?.kind,
            metadata: {
              original_label: rawStr,
              monthly_frequency: Math.round(n.monthly_frequency),
              ...(n.validation_errors && n.validation_errors.length > 0
                ? { validation_errors: n.validation_errors }
                : {}),
            },
          };
        })
      : events.map((evt, idx) => {
          const rawStr =
            evt.raw_phrase ??
            evt.raw_value ??
            evt.evidence ??
            evt.model_normalized_clinical_label;
          const normStr =
            evt.model_normalized_clinical_label ??
            (typeof evt.clinical_quantity === "string" ? evt.clinical_quantity : undefined) ??
            evt.kind;
          const evText = evt.evidence ?? evt.raw_phrase ?? evt.raw_value ?? "";
          const span = evText ? findEvidenceSpan(record.note_text, evText) : null;
          return {
            id: evt.event_id || `event_${idx}`,
            kind: canonicalSemanticKind(evt.kind, typeof normStr === "string" ? normStr : undefined),
            rawValue: typeof rawStr === "string" ? rawStr : String(rawStr ?? ""),
            normalizedValue: typeof normStr === "string" ? normStr : String(normStr ?? ""),
            evidence: evText,
            startChar: span?.start ?? null,
            endChar: span?.end ?? null,
            ruleId: evt.kind ? `normalize_${evt.kind}` : "normalize_frequency_label",
            ruleGroup: evt.kind,
            metadata: {
              original_label: typeof rawStr === "string" ? rawStr : String(rawStr ?? ""),
              monthly_frequency: 0,
            },
          };
        });

  // Select stage: from selection or final_answer
  const selectFinalLabel = selection?.final_label ?? "unknown";
  const selectEvidence =
    selection?.evidence ??
    finalAnswer?.selected_evidence ??
    row.evidence_summary?.selected_evidence ??
    "";
  const selectRationale =
    selection?.rationale ??
    finalAnswer?.final_rationale ??
    "";

  return {
    pipelineFamily: family,
    noteText: record.note_text,
    goldLabel: row.reference.gold_label,
    sourceRowIndex: row.source_row_index,
    split: row.split,
    extract: { items: extractItems },
    normalise: { items: normaliseItems },
    select: {
      finalLabel: selectFinalLabel,
      rationale: selectRationale,
      evidence: selectEvidence,
      selectedIds: selection?.selected_event_ids,
      rejectedIds: selection?.rejected_event_ids,
    },
    repair: buildSchemaRepair(
      row.row_trace?.format_repair,
      row.raw_output,
      row.row_trace?.model_prediction?.record ?? row.structured_record,
      row.repair_changes
    ),
    score: buildScoreFromComparison(
      row.comparison,
      selectFinalLabel,
      row.reference.gold_label
    ),
  };
}
