import type {
  PipelineTrace,
  EventsArtifactRow,
  FullRecordResponse,
  TraceItem,
} from "../types";
import { findEvidenceSpan, buildScoreFromComparison, buildScoreFromLayers, buildSchemaRepair } from "./utils";

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
      kind: evt.kind,
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
      ? normalizedEvents.map((n) => ({
          id: n.event_id,
          kind: n.semantic_kind,
          rawValue: n.normalized_label,
          normalizedValue: n.normalized_label,
          evidence: n.normalized_label,
          startChar: null,
          endChar: null,
          metadata: {
            monthly_frequency: n.monthly_frequency,
            validation_errors: n.validation_errors,
          },
        }))
      : events
          .filter((e) => e.model_normalized_clinical_label)
          .map((evt, idx) => ({
            id: evt.event_id || `event_${idx}`,
            kind: evt.kind,
            rawValue: evt.raw_phrase || evt.raw_value || evt.evidence,
            normalizedValue: evt.model_normalized_clinical_label,
            evidence: evt.evidence,
            startChar: null,
            endChar: null,
            metadata: {
              temporality: evt.temporality,
              assertion_status: evt.assertion_status,
            },
          }));

  // Select stage: from selection or final_answer
  const selectFinalLabel =
    selection?.final_label ??
    finalAnswer?.raw_llm_final_label ??
    "unknown";
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
    score: row.comparison
      ? buildScoreFromComparison(row.comparison, selectFinalLabel, row.reference.gold_label)
      : buildScoreFromLayers(row.score_layers, row.reference.gold_label),
  };
}
