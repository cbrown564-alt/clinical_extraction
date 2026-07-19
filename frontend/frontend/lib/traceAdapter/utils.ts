import type { TraceItem, StageScore, StageRepair } from "../types";

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
