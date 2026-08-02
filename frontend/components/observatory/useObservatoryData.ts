"use client";

import { useState, useCallback, useMemo, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchArtifact, fetchRegistry } from "@/lib/api";
import { computeMetrics, computeSummary } from "@/lib/datasets/adapters/observatoryMetrics";
import { getDefaultSelections } from "@/lib/datasets/adapters/observatoryRunSelection";
import { extractRowScore } from "@/lib/datasets/adapters/observatoryRowScore";
import { isActivePipelineFamily } from "@/lib/pipelineFamilies";
import { hasReplayableArtifact } from "@/lib/registryArtifacts";
import type { RowScore, RunSummary } from "@/lib/types";
import { useSearchParams } from "next/navigation";

export { parseRunVariant } from "@/lib/datasets/adapters/observatoryRunSelection";

const STORAGE_KEY = "observatory-selected-runs";

export function useObservatoryData() {
  const searchParams = useSearchParams();

  const { data: registryData, isLoading: registryLoading } = useQuery({
    queryKey: ["registry"],
    queryFn: fetchRegistry,
  });

  const runs = useMemo(
    () =>
      (registryData?.runs ?? []).filter(
        (run) =>
          (run.task ?? "gan2026") === "gan2026" && isActivePipelineFamily(run.pipeline_family)
      ),
    [registryData?.runs]
  );

  const [selectedRunIds, setSelectedRunIds] = useState<Set<string>>(new Set());
  const [summaries, setSummaries] = useState<Map<string, RunSummary>>(new Map());
  const [detailRows, setDetailRows] = useState<Map<string, RowScore[]>>(new Map());
  const [loadingRuns, setLoadingRuns] = useState<Set<string>>(new Set());
  const [runErrors, setRunErrors] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    if (runs.length === 0) return;

    const runsParam = searchParams.get("runs");
    if (runsParam) {
      const ids = runsParam.split(",").filter(Boolean);
      setSelectedRunIds(new Set(ids));
      return;
    }

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

    setSelectedRunIds(getDefaultSelections(runs));
  }, [runs, searchParams]);

  useEffect(() => {
    if (typeof window !== "undefined" && selectedRunIds.size > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(selectedRunIds)));
    }
  }, [selectedRunIds]);

  const fetchArtifactWithTimeout = useCallback(async (runId: string, path?: string) => {
    return fetchArtifact(runId, path);
  }, []);

  useEffect(() => {
    for (const runId of selectedRunIds) {
      if (summaries.has(runId) || loadingRuns.has(runId)) continue;
      const entry = runs.find((r) => r.run_id === runId);
      if (!entry) continue;
      if (!hasReplayableArtifact(entry.artifact_paths)) {
        setRunErrors((prev) => new Map(prev).set(runId, "No replay artifact"));
        continue;
      }

      setLoadingRuns((prev) => {
        if (prev.has(runId)) return prev;
        const next = new Set(prev);
        next.add(runId);
        return next;
      });
      setRunErrors((prev) => {
        if (!prev.has(runId)) return prev;
        const next = new Map(prev);
        next.delete(runId);
        return next;
      });

      fetchArtifactWithTimeout(runId)
        .then((artifact) => {
          const summary = computeMetrics(entry, artifact.content);
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
  }, [selectedRunIds, runs, fetchArtifactWithTimeout]);

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

      if (!summaries.has(runId) && !loadingRuns.has(runId)) {
        const entry = runs.find((r) => r.run_id === runId);
        if (!entry) return;

        if (!hasReplayableArtifact(entry.artifact_paths)) {
          setRunErrors((prev) => new Map(prev).set(runId, "No replay artifact"));
          return;
        }

        setLoadingRuns((prev) => new Set(prev).add(runId));
        setRunErrors((prev) => {
          if (!prev.has(runId)) return prev;
          const next = new Map(prev);
          next.delete(runId);
          return next;
        });
        try {
          const artifact = await fetchArtifactWithTimeout(runId);
          const summary = computeMetrics(entry, artifact.content);
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
    [runs, summaries, loadingRuns, fetchArtifactWithTimeout]
  );

  const selectRuns = useCallback(
    (runIds: string[]) => {
      setSelectedRunIds(new Set(runIds));
      for (const runId of runIds) {
        if (!summaries.has(runId) && !loadingRuns.has(runId)) {
          const entry = runs.find((r) => r.run_id === runId);
          if (!entry) continue;
          if (!hasReplayableArtifact(entry.artifact_paths)) continue;
          setLoadingRuns((prev) => new Set(prev).add(runId));
          setRunErrors((prev) => {
            if (!prev.has(runId)) return prev;
            const next = new Map(prev);
            next.delete(runId);
            return next;
          });
          fetchArtifactWithTimeout(runId)
            .then((artifact) => {
              const summary = computeMetrics(entry, artifact.content);
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
    [runs, summaries, loadingRuns, fetchArtifactWithTimeout]
  );

  const loadRunDetail = useCallback(
    async (runId: string) => {
      if (detailRows.has(runId) || loadingRuns.has(runId)) return;
      const entry = runs.find((r) => r.run_id === runId);
      if (!entry) return;
      if (!hasReplayableArtifact(entry.artifact_paths)) return;

      setLoadingRuns((prev) => new Set(prev).add(runId));
      setRunErrors((prev) => {
        if (!prev.has(runId)) return prev;
        const next = new Map(prev);
        next.delete(runId);
        return next;
      });
      try {
        const artifact = await fetchArtifactWithTimeout(runId);
        const allRows = artifact.content;
        const scores = allRows
          .map((row, index) => extractRowScore(row, index))
          .filter((s): s is RowScore => s !== null);
        setDetailRows((prev) => new Map(prev).set(runId, scores));
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
    },
    [runs, detailRows, loadingRuns, fetchArtifactWithTimeout]
  );

  const selectedSummaries = useMemo(() => {
    const result: RunSummary[] = [];
    for (const runId of selectedRunIds) {
      const s = summaries.get(runId);
      if (!s) continue;
      const rows = detailRows.get(runId);
      if (rows) {
        result.push({ ...s, rows });
      } else {
        result.push(s);
      }
    }
    return result;
  }, [selectedRunIds, summaries, detailRows]);

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
    loadRunDetail,
    hasTestData,
    runs,
  };
}
