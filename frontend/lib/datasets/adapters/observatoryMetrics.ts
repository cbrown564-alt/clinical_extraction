/**
 * Observatory run-summary adapter.
 *
 * Aggregates RowScore rows into confusion matrices, per-category F1, and
 * validation/test split metrics for the Observatory run ladder.
 */

import type { CategoryMetrics, RegistryEntry, RowScore, RunSummary } from "@/lib/types";
import { extractRowScore, PURIST_CATEGORIES } from "./observatoryRowScore";

export function computeMetrics(entry: RegistryEntry, rows: unknown[]): RunSummary {
  const scores = rows
    .map((row, index) => extractRowScore(row, index))
    .filter((s): s is RowScore => s !== null);

  const total = scores.length;
  const puristCorrect = scores.filter((s) => s.puristCorrect).length;
  const pragmaticCorrect = scores.filter((s) => s.pragmaticCorrect).length;

  const confusionMatrix = new Map<string, Map<string, number>>();
  for (const cat of PURIST_CATEGORIES) {
    confusionMatrix.set(cat, new Map<string, number>());
  }

  for (const s of scores) {
    const goldRow = confusionMatrix.get(s.goldCategory) ?? new Map<string, number>();
    goldRow.set(s.predictedCategory, (goldRow.get(s.predictedCategory) ?? 0) + 1);
    confusionMatrix.set(s.goldCategory, goldRow);
  }

  const perCategoryMetrics: Record<string, CategoryMetrics> = {};
  for (const cat of PURIST_CATEGORIES) {
    const tp = scores.filter((s) => s.goldCategory === cat && s.predictedCategory === cat).length;
    const fp = scores.filter((s) => s.goldCategory !== cat && s.predictedCategory === cat).length;
    const fn = scores.filter((s) => s.goldCategory === cat && s.predictedCategory !== cat).length;
    const precision = tp + fp > 0 ? tp / (tp + fp) : 0;
    const recall = tp + fn > 0 ? tp / (tp + fn) : 0;
    const f1 = precision + recall > 0 ? (2 * precision * recall) / (precision + recall) : 0;
    perCategoryMetrics[cat] = { tp, fp, fn, precision, recall, f1, support: tp + fn };
  }

  const totalTP = Object.values(perCategoryMetrics).reduce((sum, m) => sum + m.tp, 0);
  const totalFP = Object.values(perCategoryMetrics).reduce((sum, m) => sum + m.fp, 0);
  const totalFN = Object.values(perCategoryMetrics).reduce((sum, m) => sum + m.fn, 0);
  const microF1 =
    totalTP + totalFP + totalFN > 0 ? (2 * totalTP) / (2 * totalTP + totalFP + totalFN) : 0;

  const validationRows = scores.filter((s) => s.split === "validation");
  const testRows = scores.filter((s) => s.split === "test");

  const summary: RunSummary = {
    runId: entry.run_id,
    pipelineFamily: entry.pipeline_family,
    split: entry.split ?? "unknown",
    rowCount: total,
    date: entry.date,
    decision: entry.decision ?? "unknown",
    puristAccuracy: total > 0 ? puristCorrect / total : 0,
    pragmaticAccuracy: total > 0 ? pragmaticCorrect / total : 0,
    puristF1: microF1,
    pragmaticF1: microF1,
    confusionMatrix,
    perCategoryMetrics,
  };

  if (validationRows.length > 0) {
    summary.validationMetrics = {
      puristAccuracy: validationRows.filter((s) => s.puristCorrect).length / validationRows.length,
      pragmaticAccuracy:
        validationRows.filter((s) => s.pragmaticCorrect).length / validationRows.length,
      rowCount: validationRows.length,
    };
  }

  if (testRows.length > 0) {
    summary.testMetrics = {
      puristAccuracy: testRows.filter((s) => s.puristCorrect).length / testRows.length,
      pragmaticAccuracy: testRows.filter((s) => s.pragmaticCorrect).length / testRows.length,
      rowCount: testRows.length,
    };
  }

  return summary;
}

export function computeSummary(entry: RegistryEntry, rows: unknown[]): RunSummary {
  const metrics = computeMetrics(entry, rows);
  const scores = rows
    .map((row, index) => extractRowScore(row, index))
    .filter((s): s is RowScore => s !== null);
  return { ...metrics, rows: scores };
}
