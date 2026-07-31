/**
 * Observatory row-score adapter.
 *
 * Normalises artifact JSONL rows from heterogeneous Gan2026 pipeline families
 * into a uniform RowScore for confusion matrices, run ladders, and error galleries.
 */

import type { RowScore } from "@/lib/types";

export const PURIST_CATEGORIES = [
  "currently_no_seizure",
  "seizure_freq_unknown",
  "seizure_freq_1_per_yr",
  "seizure_freq_1_per_6mon",
  "seizure_freq_more1per6mon_less1mon",
  "seizure_freq_1_per_mon",
  "seizure_freq_more1mon_less1week",
  "seizure_freq_1_per_week",
  "seizure_freq_more1week_less1day",
  "seizure_freq_1ormore_daily",
  "seizure_infrequent",
  "seizure_frequent",
] as const;

export function normalizeCategory(cat: string): string {
  if (!cat || cat === "unknown" || cat === "None") return "seizure_freq_unknown";
  return cat;
}

function extractEvidence(r: Record<string, unknown>): string | undefined {
  const decision = r.decision_record as Record<string, unknown> | undefined;
  if (decision?.evidence) return String(decision.evidence);

  const diag = r.deterministic_diagnostics as Record<string, unknown> | undefined;
  const finalSel = diag?.final_selection as Record<string, unknown> | undefined;
  if (finalSel?.evidence) return String(finalSel.evidence);

  const sr = r.structured_record as Record<string, unknown> | undefined;
  const fq = sr?.final_query as Record<string, unknown> | undefined;
  if (fq?.evidence) return String(fq.evidence);

  const evSum = r.evidence_summary as Record<string, unknown> | undefined;
  if (evSum?.selected_evidence) return String(evSum.selected_evidence);

  if (r.selected_evidence) return String(r.selected_evidence);
  if (r.evidence) return String(r.evidence);

  return undefined;
}

function extractRationale(r: Record<string, unknown>): string | undefined {
  const decision = r.decision_record as Record<string, unknown> | undefined;
  if (decision?.rationale) return String(decision.rationale);

  const sr = r.structured_record as Record<string, unknown> | undefined;
  const fq = sr?.final_query as Record<string, unknown> | undefined;
  if (fq?.rationale) return String(fq.rationale);

  const diag = r.deterministic_diagnostics as Record<string, unknown> | undefined;
  const finalSel = diag?.final_selection as Record<string, unknown> | undefined;
  if (finalSel?.rationale) return String(finalSel.rationale);

  if (r.rationale) return String(r.rationale);

  return undefined;
}

/** Maps one artifact JSONL row to a uniform RowScore, or null when unrecognised. */
export function extractRowScore(row: unknown, fallbackIndex: number): RowScore | null {
  const r = row as Record<string, unknown>;
  const evidence = extractEvidence(r);
  const rationale = extractRationale(r);

  const sourceRowIndex =
    typeof r.source_row_index === "number"
      ? r.source_row_index
      : typeof r.source_row_index === "string"
        ? parseInt(r.source_row_index, 10)
        : fallbackIndex;

  const evSummary = r.evidence_summary as Record<string, unknown> | undefined;
  const detDiag = r.deterministic_diagnostics as Record<string, unknown> | undefined;

  const rawEvValid = r.evidence_valid ?? evSummary?.selected_evidence_valid ?? detDiag?.evidence_valid;
  const evidenceValid =
    rawEvValid !== undefined
      ? Boolean(rawEvValid)
      : typeof evSummary?.exact_evidence_valid === "number"
        ? evSummary.exact_evidence_valid > 0
        : undefined;

  const repairChanges = r.repair_changes as unknown[] | undefined;
  const repairChangesCount = Array.isArray(repairChanges) ? repairChanges.length : undefined;

  const scores = r.scores as Record<string, unknown> | undefined;
  if (scores) {
    const adjudicator = scores.adjudicator as Record<string, unknown> | undefined;
    if (adjudicator) {
      const ref = r.reference as Record<string, unknown> | undefined;
      return {
        predictedCategory: normalizeCategory(String(adjudicator.predicted_purist_category)),
        goldCategory: normalizeCategory(String(adjudicator.gold_purist_category)),
        puristCorrect: Boolean(adjudicator.purist_correct),
        pragmaticCorrect: Boolean(adjudicator.pragmatic_correct),
        predictedLabel: String(adjudicator.final_label ?? "unknown"),
        goldLabel: String(ref?.gold_label ?? "unknown"),
        split: String(r.split ?? ""),
        evidence,
        rationale,
        sourceRowIndex,
        evidenceValid,
        repairChangesCount,
      };
    }
  }

  const scoreLayers = r.score_layers as Record<string, unknown> | undefined;
  if (scoreLayers) {
    const layer =
      (scoreLayers.clean_scorer_facing as Record<string, unknown> | undefined) ||
      (scoreLayers.strict_format as Record<string, unknown> | undefined) ||
      (scoreLayers.benchmark_aligned as Record<string, unknown> | undefined) ||
      (scoreLayers.format_only as Record<string, unknown> | undefined) ||
      (scoreLayers.raw_llm as Record<string, unknown> | undefined);
    if (layer) {
      const ref = r.reference as Record<string, unknown> | undefined;
      return {
        predictedCategory: normalizeCategory(String(layer.predicted_purist_category)),
        goldCategory: normalizeCategory(String(layer.gold_purist_category)),
        puristCorrect: Boolean(layer.purist_correct),
        pragmaticCorrect: Boolean(layer.pragmatic_correct),
        predictedLabel: String(layer.final_label ?? "unknown"),
        goldLabel: String(ref?.gold_label ?? "unknown"),
        split: String(r.split ?? ""),
        evidence,
        rationale,
        sourceRowIndex,
        evidenceValid,
        repairChangesCount,
      };
    }
  }

  const comparison = r.comparison as Record<string, unknown> | undefined;
  if (comparison) {
    const decision = r.decision_record as Record<string, unknown> | undefined;
    const ref = r.reference as Record<string, unknown> | undefined;
    return {
      predictedCategory: normalizeCategory(String(comparison.predicted_purist_category)),
      goldCategory: normalizeCategory(String(comparison.gold_purist_category)),
      puristCorrect: Boolean(comparison.purist_correct),
      pragmaticCorrect: Boolean(comparison.pragmatic_correct),
      predictedLabel: String(decision?.final_label ?? "unknown"),
      goldLabel: String(ref?.gold_label ?? "unknown"),
      split: String(r.split ?? ""),
      evidence,
      rationale,
      sourceRowIndex,
      evidenceValid,
      repairChangesCount,
    };
  }

  const puristPredicted = r.purist_predicted_category as string | undefined;
  const puristGold = r.purist_gold_category as string | undefined;
  if (puristPredicted && puristGold) {
    return {
      predictedCategory: normalizeCategory(puristPredicted),
      goldCategory: normalizeCategory(puristGold),
      puristCorrect: puristPredicted === puristGold,
      pragmaticCorrect:
        (r.pragmatic_predicted_category as string | undefined) ===
        (r.pragmatic_gold_category as string | undefined),
      predictedLabel: String(r.prediction_label ?? "unknown"),
      goldLabel: String(r.gold_label ?? "unknown"),
      split: String(r.split ?? ""),
      evidence,
      rationale,
      sourceRowIndex,
      evidenceValid,
      repairChangesCount,
    };
  }

  const flatPuristCorrect = r.purist_correct as boolean | undefined;
  const flatPragmaticCorrect = r.pragmatic_correct as boolean | undefined;
  const flatFinalLabel = r.final_label as string | undefined;
  const flatGoldLabel = r.gold_label as string | undefined;
  const flatPuristTransition = r.purist_category_transition as string | undefined;
  if (flatPuristCorrect !== undefined && flatFinalLabel !== undefined && flatGoldLabel !== undefined) {
    let predictedCategory = "unknown";
    let goldCategory = "unknown";
    if (flatPuristTransition && flatPuristTransition.includes("->")) {
      const [from, to] = flatPuristTransition.split("->");
      goldCategory = from === "None" ? "unknown" : from;
      predictedCategory = to === "None" ? "unknown" : to;
    }
    return {
      predictedCategory: normalizeCategory(predictedCategory),
      goldCategory: normalizeCategory(goldCategory),
      puristCorrect: Boolean(flatPuristCorrect),
      pragmaticCorrect: Boolean(flatPragmaticCorrect),
      predictedLabel: flatFinalLabel,
      goldLabel: flatGoldLabel,
      split: String(r.split ?? ""),
      evidence,
      rationale,
      sourceRowIndex,
      evidenceValid,
      repairChangesCount,
    };
  }

  return null;
}
