"use client";

import { useState, useCallback, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchRegistry, fetchArtifact } from "@/lib/api";
import type { RegistryEntry, RowScore, RunSummary, CategoryMetrics } from "@/lib/types";

const PURIST_CATEGORIES = [
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
];

function extractRowScore(row: unknown): RowScore | null {
  const r = row as Record<string, unknown>;

  // Hybrid format
  const scores = r.scores as Record<string, unknown> | undefined;
  if (scores) {
    const adjudicator = scores.adjudicator as Record<string, unknown> | undefined;
    if (adjudicator) {
      const ref = r.reference as Record<string, unknown> | undefined;
      return {
        predictedCategory: String(adjudicator.predicted_purist_category ?? "unknown"),
        goldCategory: String(adjudicator.gold_purist_category ?? "unknown"),
        puristCorrect: Boolean(adjudicator.purist_correct),
        pragmaticCorrect: Boolean(adjudicator.pragmatic_correct),
        predictedLabel: String(adjudicator.final_label ?? "unknown"),
        goldLabel: String(ref?.gold_label ?? "unknown"),
        split: String(r.split ?? ""),
      };
    }
  }

  // LLM format
  const scoreLayers = r.score_layers as Record<string, unknown> | undefined;
  if (scoreLayers) {
    const layer =
      (scoreLayers.clean_scorer_facing as Record<string, unknown> | undefined) ||
      (scoreLayers.strict_format as Record<string, unknown> | undefined);
    if (layer) {
      const ref = r.reference as Record<string, unknown> | undefined;
      return {
        predictedCategory: String(layer.predicted_purist_category ?? "unknown"),
        goldCategory: String(layer.gold_purist_category ?? "unknown"),
        puristCorrect: Boolean(layer.purist_correct),
        pragmaticCorrect: Boolean(layer.pragmatic_correct),
        predictedLabel: String(layer.final_label ?? "unknown"),
        goldLabel: String(ref?.gold_label ?? "unknown"),
        split: String(r.split ?? ""),
      };
    }
  }

  // Ablation / deterministic format
  const puristPredicted = r.purist_predicted_category as string | undefined;
  const puristGold = r.purist_gold_category as string | undefined;
  if (puristPredicted && puristGold) {
    return {
      predictedCategory: puristPredicted,
      goldCategory: puristGold,
      puristCorrect: puristPredicted === puristGold,
      pragmaticCorrect:
        (r.pragmatic_predicted_category as string | undefined) ===
        (r.pragmatic_gold_category as string | undefined),
      predictedLabel: String(r.prediction_label ?? "unknown"),
      goldLabel: String(r.gold_label ?? "unknown"),
      split: String(r.split ?? ""),
    };
  }

  return null;
}

function computeSummary(entry: RegistryEntry, rows: unknown[]): RunSummary {
  const scores = rows.map(extractRowScore).filter((s): s is RowScore => s !== null);

  const total = scores.length;
  const puristCorrect = scores.filter((s) => s.puristCorrect).length;
  const pragmaticCorrect = scores.filter((s) => s.pragmaticCorrect).length;

  // Confusion matrix
  const confusionMatrix = new Map<string, Map<string, number>>();
  for (const cat of PURIST_CATEGORIES) {
    confusionMatrix.set(cat, new Map<string, number>());
  }

  for (const s of scores) {
    const goldRow = confusionMatrix.get(s.goldCategory) ?? new Map<string, number>();
    goldRow.set(s.predictedCategory, (goldRow.get(s.predictedCategory) ?? 0) + 1);
    confusionMatrix.set(s.goldCategory, goldRow);
  }

  // Per-category metrics
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

  // Micro F1
  const totalTP = Object.values(perCategoryMetrics).reduce((sum, m) => sum + m.tp, 0);
  const totalFP = Object.values(perCategoryMetrics).reduce((sum, m) => sum + m.fp, 0);
  const totalFN = Object.values(perCategoryMetrics).reduce((sum, m) => sum + m.fn, 0);
  const microF1 =
    totalTP + totalFP + totalFN > 0
      ? (2 * totalTP) / (2 * totalTP + totalFP + totalFN)
      : 0;

  // Validation / test split
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
    rows: scores,
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

export function useObservatoryData() {
  const { data: registryData, isLoading: registryLoading } = useQuery({
    queryKey: ["registry"],
    queryFn: fetchRegistry,
  });

  const [selectedRunIds, setSelectedRunIds] = useState<Set<string>>(new Set());
  const [summaries, setSummaries] = useState<Map<string, RunSummary>>(new Map());
  const [loadingRuns, setLoadingRuns] = useState<Set<string>>(new Set());
  const [runErrors, setRunErrors] = useState<Map<string, string>>(new Map());

  const toggleRun = useCallback(
    async (runId: string) => {
      setSelectedRunIds((prev) => {
        const next = new Set(prev);
        if (next.has(runId)) {
          next.delete(runId);
          return next;
        }
        next.add(runId);
        return next;
      });

      // If not already loaded, fetch it
      if (!summaries.has(runId) && !loadingRuns.has(runId)) {
        const entry = registryData?.runs.find((r) => r.run_id === runId);
        if (!entry) return;

        // Find JSONL artifact path
        const jsonlPath = entry.artifact_paths.find((p) => p.endsWith(".jsonl"));
        if (!jsonlPath) {
          setRunErrors((prev) => new Map(prev).set(runId, "No JSONL artifact found"));
          return;
        }

        setLoadingRuns((prev) => new Set(prev).add(runId));
        try {
          const artifact = await fetchArtifact(runId, jsonlPath);
          const summary = computeSummary(entry, artifact.content as unknown[]);
          setSummaries((prev) => new Map(prev).set(runId, summary));
        } catch (err) {
          setRunErrors((prev) => new Map(prev).set(runId, String(err)));
        } finally {
          setLoadingRuns((prev) => {
            const next = new Set(prev);
            next.delete(runId);
            return next;
          });
        }
      }
    },
    [registryData, summaries, loadingRuns]
  );

  const selectedSummaries = useMemo(() => {
    const result: RunSummary[] = [];
    for (const runId of selectedRunIds) {
      const s = summaries.get(runId);
      if (s) result.push(s);
    }
    return result;
  }, [selectedRunIds, summaries]);

  return {
    registry: registryData,
    registryLoading,
    selectedRunIds,
    selectedSummaries,
    loadingRuns,
    runErrors,
    toggleRun,
  };
}
