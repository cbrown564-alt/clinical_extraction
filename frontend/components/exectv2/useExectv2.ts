"use client";

import { useCallback, useMemo } from "react";
import { useQueries, useQuery } from "@tanstack/react-query";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { fetchRun, fetchRuns } from "@/lib/api";
import { DATASET_PARAM } from "@/lib/datasets";
import { isDemoSurface, lockDemoExectRuns } from "@/lib/demoSurface";
import { exectv2RunActiveMethod, resolveExectv2RunId, sortExectv2Runs } from "@/lib/exectv2RunOptions";
import type { Exectv2RunSummary } from "@/lib/types";

export function useExectv2Runs() {
  const query = useQuery({
    queryKey: ["runs", "exectv2"],
    queryFn: () => fetchRuns("exectv2"),
    staleTime: 5 * 60 * 1000,
  });

  const runs = useMemo(() => {
    const list = query.data?.runs ?? [];
    const sorted = sortExectv2Runs(list);
    return isDemoSurface() ? lockDemoExectRuns(sorted) : sorted;
  }, [query.data?.runs]);

  return { ...query, runs, sourceIndex: query.data?.source_index };
}

export function useExectv2Run(runId: string | undefined) {
  return useQuery({
    queryKey: ["run", "exectv2", runId],
    queryFn: () => fetchRun("exectv2", runId as string),
    enabled: Boolean(runId),
    staleTime: 5 * 60 * 1000,
  });
}

export function useExectv2RunDetails(runIds: string[]) {
  const queries = useQueries({
    queries: runIds.map((runId) => ({
      queryKey: ["run", "exectv2", runId],
      queryFn: () => fetchRun("exectv2", runId),
      staleTime: 5 * 60 * 1000,
    })),
  });
  return {
    runs: queries.flatMap((query) => (query.data ? [query.data] : [])),
    isLoading: queries.some((query) => query.isLoading),
    error: queries.find((query) => query.error)?.error,
  };
}

export type Exectv2UrlKey = "run" | "letter" | "family" | "errorClass" | "component";

/**
 * Reads and writes ExECTv2 selection params (`run`, `letter`, `family`, …) while
 * always preserving `dataset=exectv2`. Shared by all four ExECTv2 surfaces so
 * deep-links and cross-surface navigation keep the active dataset and selection.
 */
export function useExectv2UrlState() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const get = useCallback(
    (key: Exectv2UrlKey) => searchParams.get(key) ?? undefined,
    [searchParams]
  );

  const set = useCallback(
    (updates: Partial<Record<Exectv2UrlKey, string | undefined>>) => {
      const params = new URLSearchParams(searchParams.toString());
      params.set(DATASET_PARAM, "exectv2");
      for (const [key, value] of Object.entries(updates)) {
        if (value === undefined || value === "") params.delete(key);
        else params.set(key, value);
      }
      router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    },
    [pathname, router, searchParams]
  );

  return { get, set };
}

export function compactRunLabel(run: Exectv2RunSummary): string {
  return run.label.replace("dev140", "140").replace("dev25", "25");
}

const SELECTION_STORAGE_KEY = "exectv2-selected-runs";

/** Default selection: all six models under the winning assembled mode. */
function defaultSelection(runs: Exectv2RunSummary[]): string[] {
  const winningMode = runs.filter((run) => exectv2RunActiveMethod(run) === "llm_with_rules");
  return (winningMode.length > 0 ? winningMode : runs).map((run) => run.run_id);
}

/**
 * Multi-select run set for ExECTv2, mirroring Gan's observatory selection.
 *
 * The selected architectures live in the `runs` URL param (comma-separated) with
 * a localStorage fallback, so a set assembled in Aggregate Performance flows into
 * the Error Gallery exactly the way Gan's selected runs do. Single-focus surfaces
 * (Example Explorer, Component Impact) keep using the `run` param; this is the
 * set, not the focus.
 */
export function useExectv2Selection(runs: Exectv2RunSummary[]) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const runsParam = searchParams.get("runs");

  const selectedIds = useMemo<Set<string>>(() => {
    const valid = new Set(runs.map((r) => r.run_id));
    if (runsParam !== null) {
      return new Set(
        runsParam
          .split(",")
          .map((id) => resolveExectv2RunId(runs, id))
          .filter((id): id is string => id !== null && valid.has(id))
      );
    }
    if (typeof window !== "undefined") {
      try {
        const saved = window.localStorage.getItem(SELECTION_STORAGE_KEY);
        if (saved) {
          const ids = (JSON.parse(saved) as string[])
            .map((id) => resolveExectv2RunId(runs, id))
            .filter((id): id is string => id !== null && valid.has(id));
          if (ids.length > 0) return new Set(ids);
        }
      } catch {
        // ignore unavailable localStorage
      }
    }
    return new Set(runs.length > 0 ? defaultSelection(runs) : []);
  }, [runsParam, runs]);

  const setSelection = useCallback(
    (ids: string[]) => {
      const params = new URLSearchParams(searchParams.toString());
      params.set(DATASET_PARAM, "exectv2");
      if (ids.length > 0) params.set("runs", ids.join(","));
      else params.delete("runs");
      router.replace(`${pathname}?${params.toString()}`, { scroll: false });
      if (typeof window !== "undefined") {
        try {
          window.localStorage.setItem(SELECTION_STORAGE_KEY, JSON.stringify(ids));
        } catch {
          // ignore
        }
      }
    },
    [pathname, router, searchParams]
  );

  const toggle = useCallback(
    (id: string) => {
      const next = new Set(selectedIds);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      setSelection([...next]);
    },
    [selectedIds, setSelection]
  );

  return {
    selectedIds,
    selectedRunIds: [...selectedIds],
    setSelection,
    toggle,
    isSelected: useCallback((id: string) => selectedIds.has(id), [selectedIds]),
  };
}
