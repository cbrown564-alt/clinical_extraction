"use client";

import { useState, useCallback, useMemo, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchRegistry, fetchArtifact } from "@/lib/api";
import type { RegistryEntry, RowScore, RunSummary, CategoryMetrics } from "@/lib/types";

const STORAGE_KEY = "observatory-selected-runs";

function normalizeCategory(cat: string): string {
  if (!cat || cat === "unknown" || cat === "None") return "seizure_freq_unknown";
  return cat;
}

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
        predictedCategory: normalizeCategory(String(adjudicator.predicted_purist_category)),
        goldCategory: normalizeCategory(String(adjudicator.gold_purist_category)),
        puristCorrect: Boolean(adjudicator.purist_correct),
        pragmaticCorrect: Boolean(adjudicator.pragmatic_correct),
        predictedLabel: String(adjudicator.final_label ?? "unknown"),
        goldLabel: String(ref?.gold_label ?? "unknown"),
        split: String(r.split ?? ""),
      };
    }
  }

  // LLM format (claim table / direct labeler / structured events)
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
      };
    }
  }

  // Ablation / deterministic format
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
    };
  }

  // Replacement post-processing ablation format (flat schema)
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

/** Parse a run ID into a human-readable variant string. */
export function parseRunVariant(runId: string, family: string): string {
  // Remove date suffix
  let s = runId.replace(/_2026-\d{2}-\d{2}$/, "");
  
  // Try to extract the part between family and split/date
  const familyPattern = family.replace(/_/g, "[_-]");
  const m = s.match(new RegExp(`gan2026[_-]?(?:${familyPattern})[_-]?(.*?)_(?:validation|test|synthetic)`));
  if (m && m[1]) return m[1];
  
  // Fallback: remove prefix
  s = s.replace(/^gan2026_/, "");
  return s || runId;
}

/** Extract split size from run metadata for sorting. */
export function parseSplitSize(split: string): number {
  if (split.includes("test")) return 10000;
  if (split.includes("750")) return 750;
  if (split.includes("250")) return 250;
  if (split.includes("50")) return 50;
  if (split.includes("25")) return 25;
  if (split.includes("hard")) return 15;
  if (split.includes("synthetic")) return 5;
  return 0;
}

function getDefaultSelections(runs: RegistryEntry[]): Set<string> {
  // Prefer: validation+test runs, then largest validation runs per family
  const selected = new Set<string>();
  
  // 1. Select all validation+test runs
  for (const run of runs) {
    if (run.split?.includes("validation+test") || run.split?.includes("test")) {
      if (run.artifact_paths.some((p) => p.endsWith(".jsonl"))) {
        selected.add(run.run_id);
      }
    }
  }
  
  // 2. For each family, select the largest pure validation run
  const byFamily = new Map<string, RegistryEntry[]>();
  for (const run of runs) {
    if (!run.artifact_paths.some((p) => p.endsWith(".jsonl"))) continue;
    const list = byFamily.get(run.pipeline_family) ?? [];
    list.push(run);
    byFamily.set(run.pipeline_family, list);
  }
  
  for (const [, familyRuns] of byFamily) {
    const validationRuns = familyRuns.filter(
      (r) => r.split === "validation" && !selected.has(r.run_id)
    );
    if (validationRuns.length > 0) {
      // Pick largest by row count
      const best = validationRuns.reduce((a, b) => (a.row_count > b.row_count ? a : b));
      selected.add(best.run_id);
    }
  }
  
  // Cap at 6 to avoid overwhelming the UI
  if (selected.size > 6) {
    const arr = Array.from(selected);
    return new Set(arr.slice(0, 6));
  }
  
  return selected;
}

export function useObservatoryData() {
  const { data: registryData, isLoading: registryLoading } = useQuery({
    queryKey: ["registry"],
    queryFn: fetchRegistry,
  });

  const runs = registryData?.runs ?? [];

  const [selectedRunIds, setSelectedRunIds] = useState<Set<string>>(new Set());
  const [summaries, setSummaries] = useState<Map<string, RunSummary>>(new Map());
  const [loadingRuns, setLoadingRuns] = useState<Set<string>>(new Set());
  const [runErrors, setRunErrors] = useState<Map<string, string>>(new Map());

  // Auto-select defaults on first load
  useEffect(() => {
    if (runs.length === 0) return;
    const saved = typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
    if (saved) {
      try {
        const ids = JSON.parse(saved) as string[];
        setSelectedRunIds(new Set(ids));
        return;
      } catch {
        // ignore
      }
    }
    const defaults = getDefaultSelections(runs);
    setSelectedRunIds(defaults);
  }, [runs.length > 0]);

  // Persist selections
  useEffect(() => {
    if (typeof window !== "undefined" && selectedRunIds.size > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(selectedRunIds)));
    }
  }, [selectedRunIds]);

  // Auto-fetch artifacts for selected runs that aren't loaded yet
  useEffect(() => {
    for (const runId of selectedRunIds) {
      if (summaries.has(runId) || loadingRuns.has(runId)) continue;
      const entry = runs.find((r) => r.run_id === runId);
      if (!entry) continue;
      const jsonlPaths = entry.artifact_paths.filter((p) => p.endsWith(".jsonl"));
      if (jsonlPaths.length === 0) {
        setRunErrors((prev) => new Map(prev).set(runId, "No JSONL artifact"));
        continue;
      }

      setLoadingRuns((prev) => {
        if (prev.has(runId)) return prev;
        const next = new Set(prev);
        next.add(runId);
        return next;
      });

      Promise.all(jsonlPaths.map((path) => fetch(`/api/artifacts/${runId}?artifact_path=${encodeURIComponent(path)}`).then(r => r.json())))
        .then((artifacts) => {
          const allRows = (artifacts as Array<{content: unknown[]}>).flatMap((a) => a.content);
          const summary = computeSummary(entry, allRows);
          setSummaries((prev) => new Map(prev).set(runId, summary));
        })
        .catch((err) => {
          setRunErrors((prev) => new Map(prev).set(runId, String(err)));
        })
        .finally(() => {
          setLoadingRuns((prev) => {
            const next = new Set(prev);
            next.delete(runId);
            return next;
          });
        });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedRunIds, runs]);

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

      // If not already loaded, fetch all JSONL artifacts
      if (!summaries.has(runId) && !loadingRuns.has(runId)) {
        const entry = runs.find((r) => r.run_id === runId);
        if (!entry) return;

        const jsonlPaths = entry.artifact_paths.filter((p) => p.endsWith(".jsonl"));
        if (jsonlPaths.length === 0) {
          setRunErrors((prev) => new Map(prev).set(runId, "No JSONL artifact"));
          return;
        }

        setLoadingRuns((prev) => new Set(prev).add(runId));
        try {
          const artifacts = await Promise.all(jsonlPaths.map((path) => fetch(`/api/artifacts/${runId}?artifact_path=${encodeURIComponent(path)}`).then(r => r.json())));
          const allRows = (artifacts as Array<{content: unknown[]}>).flatMap((a) => a.content);
          const summary = computeSummary(entry, allRows);
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
    [runs, summaries, loadingRuns]
  );

  const selectRuns = useCallback(
    (runIds: string[]) => {
      setSelectedRunIds(new Set(runIds));
      for (const runId of runIds) {
        if (!summaries.has(runId) && !loadingRuns.has(runId)) {
          const entry = runs.find((r) => r.run_id === runId);
          if (!entry) continue;
          const jsonlPaths = entry.artifact_paths.filter((p) => p.endsWith(".jsonl"));
          if (jsonlPaths.length === 0) continue;
          setLoadingRuns((prev) => new Set(prev).add(runId));
          Promise.all(jsonlPaths.map((path) => fetch(`/api/artifacts/${runId}?artifact_path=${encodeURIComponent(path)}`).then(r => r.json())))
            .then((artifacts) => {
              const allRows = (artifacts as Array<{content: unknown[]}>).flatMap((a) => a.content);
              const summary = computeSummary(entry, allRows);
              setSummaries((prev) => new Map(prev).set(runId, summary));
            })
            .catch((err) => {
              setRunErrors((prev) => new Map(prev).set(runId, String(err)));
            })
            .finally(() => {
              setLoadingRuns((prev) => {
                const next = new Set(prev);
                next.delete(runId);
                return next;
              });
            });
        }
      }
    },
    [runs, summaries, loadingRuns]
  );

  const selectedSummaries = useMemo(() => {
    const result: RunSummary[] = [];
    for (const runId of selectedRunIds) {
      const s = summaries.get(runId);
      if (s) result.push(s);
    }
    return result;
  }, [selectedRunIds, summaries]);

  const hasTestData = useMemo(() => {
    return selectedSummaries.some((s) => s.testMetrics);
  }, [selectedSummaries]);

  return {
    registry: registryData,
    registryLoading,
    selectedRunIds,
    selectedSummaries,
    loadingRuns,
    runErrors,
    toggleRun,
    selectRuns,
    hasTestData,
    runs,
  };
}
