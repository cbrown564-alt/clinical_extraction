"use client";

import { useCallback, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { fetchExectv2Runs } from "@/lib/api";
import { DATASET_PARAM } from "@/lib/datasets";
import type { Exectv2RunSummary } from "@/lib/types";

/** Order runs so dev140 controls lead and dev25 diagnostics follow. */
function decisionRank(run: Exectv2RunSummary): number {
  if (run.decision === "control") return 0;
  if (run.decision === "simplification") return 1;
  if (run.decision === "diagnostic") return 2;
  return 3;
}

export function useExectv2Runs() {
  const query = useQuery({
    queryKey: ["exectv2-runs"],
    queryFn: fetchExectv2Runs,
    staleTime: 5 * 60 * 1000,
  });

  const runs = useMemo(() => {
    const list = query.data?.runs ?? [];
    return [...list].sort((a, b) => decisionRank(a) - decisionRank(b));
  }, [query.data?.runs]);

  return { ...query, runs, sourceIndex: query.data?.source_index };
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

export function formatMetric(value: number | null | undefined, digits = 4): string {
  return typeof value === "number" ? value.toFixed(digits) : "—";
}

export function compactRunLabel(run: Exectv2RunSummary): string {
  return run.label.replace("dev140", "140").replace("dev25", "25");
}
