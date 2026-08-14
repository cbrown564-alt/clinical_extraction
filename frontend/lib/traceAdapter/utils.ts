import type { TraceItem, StageScore, StageRepair } from "../types";

/**
 * Canonical semantic kind mapping across all model and deterministic pipelines.
 * Standardizes 'rate', 'frequency', 'frequency_rate' -> 'frequency_rate',
 * 'seizure_free' -> 'seizure_free', 'unknown' -> 'unknown_frequency', etc.
 */
export function canonicalSemanticKind(kind: string | null | undefined, label?: string | null): string {
  const k = (kind ?? "").toLowerCase().trim();
  const l = (label ?? "").toLowerCase().trim();

  if (k === "frequency_rate" || k === "rate" || k === "frequency") return "frequency_rate";
  if (k === "cluster_frequency" || k === "cluster") return "cluster_frequency";
  if (k === "seizure_free" || l.startsWith("seizure free")) return "seizure_free";
  if (k === "unknown_frequency" || k === "unknown" || l === "unknown") return "unknown_frequency";
  if (k === "no_reference" || k === "no_seizure_frequency_reference" || l.includes("no seizure") || l.includes("no reference")) return "no_reference";
  if (k === "unresolved_multiple") return "unresolved_multiple";
  if (k === "last_event_only") return "last_event_only";

  if (l.includes("per day") || l.includes("per week") || l.includes("per month") || l.includes("per year")) return "frequency_rate";
  if (l.startsWith("seizure free")) return "seizure_free";
  if (l === "unknown") return "unknown_frequency";
  if (l.includes("no seizure") || l.includes("no reference")) return "no_reference";

  return k || "frequency_rate";
}

/**
 * Find the character span of an evidence string within a note text.
 * Returns exact match first, then case-insensitive fallback.
 */
export function findEvidenceSpan(
  noteText: string,
  evidence: string
): { start: number; end: number } | null {
  if (!evidence || !noteText) return null;
  const exactPos = noteText.indexOf(evidence);
  if (exactPos >= 0) {
    return { start: exactPos, end: exactPos + evidence.length };
  }
  const lowerNote = noteText.toLowerCase();
  const lowerEvidence = evidence.toLowerCase();
  const ciPos = lowerNote.indexOf(lowerEvidence);
  if (ciPos >= 0) {
    return { start: ciPos, end: ciPos + evidence.length };
  }
  return null;
}

/**
 * Build a TraceItem from an evidence string and optional metadata.
 */
export function evidenceToTraceItem(
  id: string,
  kind: string,
  rawValue: string,
  evidence: string,
  noteText: string,
  metadata?: Record<string, unknown>
): TraceItem {
  const span = evidence ? findEvidenceSpan(noteText, evidence) : null;
  return {
    id,
    kind,
    rawValue,
    evidence,
    startChar: span?.start ?? null,
    endChar: span?.end ?? null,
    metadata,
  };
}

/**
 * Build a StageScore from a comparison object (used by direct extractor, DSPY adjudicator, etc.).
 */
export function buildScoreFromComparison(
  comparison: {
    purist_correct?: boolean;
    pragmatic_correct?: boolean;
    predicted_purist_category?: string;
    gold_purist_category?: string;
  } | undefined,
  predictedLabel: string,
  goldLabel: string
): StageScore {
  return {
    predictedLabel,
    goldLabel,
    match: predictedLabel === goldLabel,
    evidenceValid: comparison?.purist_correct ?? false,
  };
}

/**
 * Build a StageScore from score_layers, following the canonical preference order.
 */
export function buildScoreFromLayers(
  scoreLayers: Record<string, unknown> | undefined,
  goldLabel: string
): StageScore {
  const layerOrder = [
    "clean_scorer_facing",
    "benchmark_aligned",
    "format_only",
    "strict_format",
    "raw_llm",
  ];

  for (const key of layerOrder) {
    const layer = scoreLayers?.[key] as
      | {
          final_label?: string;
          purist_correct?: boolean;
          pragmatic_correct?: boolean;
          scorable?: boolean;
        }
      | undefined;
    if (layer?.final_label) {
      return {
        predictedLabel: layer.final_label,
        goldLabel,
        match: layer.final_label === goldLabel,
        evidenceValid: layer.purist_correct ?? false,
      };
    }
  }

  return {
    predictedLabel: "unknown",
    goldLabel,
    match: false,
    evidenceValid: false,
  };
}

/**
 * Build StageRepair from repair_changes array.
 */
export function buildRepair(
  repairChanges: unknown[] | undefined
): StageRepair | undefined {
  if (!repairChanges || repairChanges.length === 0) return undefined;

  const changes: string[] = [];
  let beforeLabel: string | undefined;
  let afterLabel: string | undefined;

  for (const change of repairChanges) {
    if (typeof change === "string") {
      changes.push(change);
    } else if (change && typeof change === "object") {
      const c = change as Record<string, unknown>;
      const layer = c.layer ?? c.repair_mode ?? "repair";
      const before = c.before;
      const after = c.after;
      if (typeof before === "string" && typeof after === "string") {
        changes.push(`${layer}: "${before}" → "${after}"`);
        beforeLabel = before;
        afterLabel = after;
      } else {
        changes.push(JSON.stringify(change));
      }
    }
  }

  if (changes.length === 0) return undefined;
  return { changes, beforeLabel, afterLabel };
}

function schemaRepairType(events: string[], schemaPayloadChanged: boolean): string {
  const prefixes = new Set(events.map((event) => event.split(":", 1)[0]));
  const types: string[] = [];
  if (prefixes.has("json_dialect_repaired")) types.push("JSON dialect repair");
  if (prefixes.has("invalid_json")) types.push("JSON parsing failure");
  if (prefixes.has("schema_validation_error")) types.push("Schema validation failure");
  if (prefixes.has("format_retry_rejected")) types.push("Format retry rejected");
  if (prefixes.has("not_run")) types.push("Schema repair not run");
  if (schemaPayloadChanged) types.push("Schema payload repair");
  return types.length > 0 ? Array.from(new Set(types)).join(" · ") : "Schema repair";
}

/** Build the stage-4 schema repair view from the retained row trace. */
export function buildSchemaRepair(
  formatRepair: { schema_payload_changed?: boolean; events?: string[] } | undefined,
  rawOutput: string | undefined,
  repairedValue: unknown,
  fallbackChanges?: unknown[]
): StageRepair | undefined {
  const events = (formatRepair?.events ?? []).map(String);
  const schemaPayloadChanged = formatRepair?.schema_payload_changed === true;
  if (events.length === 0 && !schemaPayloadChanged) return buildRepair(fallbackChanges);

  return {
    changes: events.length > 0 ? events : ["Schema payload changed"],
    repairType: schemaRepairType(events, schemaPayloadChanged),
    beforeValue: rawOutput ?? "Raw model output unavailable",
    afterValue:
      repairedValue == null
        ? "No valid structured value produced"
        : JSON.stringify(repairedValue, null, 2),
  };
}
