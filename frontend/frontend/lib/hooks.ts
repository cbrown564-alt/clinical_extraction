"use client";

import { useEffect, useRef } from "react";
import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { preserveWorkbenchDataset } from "./architectUrl";
import {
  runNote,
  fetchRules,
  fetchHealth,
  fetchRecords,
  fetchRecord,
  fetchPipelineFamilies,
  fetchRegistry,
  runAblation,
  fetchPrompts,
} from "./api";
import type { RunNoteResponse, AblationConfigPayload, TraceStage } from "./types";
import { useArchitectStore } from "./stores";
import {
  isBareFamilyName,
  resolveFamilyDefaultRun,
} from "./registryResolver";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: false,
    refetchInterval: 30000,
  });
}

export function useRules() {
  return useQuery({
    queryKey: ["rules"],
    queryFn: fetchRules,
    staleTime: Infinity,
  });
}

export function useRecords(split: string | null) {
  return useQuery({
    queryKey: ["records", split],
    queryFn: () => fetchRecords(split!),
    enabled: !!split,
    staleTime: 5 * 60 * 1000,
  });
}

export function useRecord(split: string | null, sourceRowIndex: number | null) {
  return useQuery({
    queryKey: ["record", split, sourceRowIndex],
    queryFn: () => fetchRecord(split!, sourceRowIndex!),
    enabled: !!split && sourceRowIndex !== null,
    staleTime: 5 * 60 * 1000,
  });
}

export function useRunNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: runNote,
    onSuccess: (data: RunNoteResponse) => {
      queryClient.setQueryData(["lastRun"], data);
    },
  });
}

export function useLastRun() {
  const queryClient = useQueryClient();
  return queryClient.getQueryData<RunNoteResponse>(["lastRun"]);
}

export function usePipelineFamilies() {
  return useQuery({
    queryKey: ["pipelineFamilies"],
    queryFn: fetchPipelineFamilies,
    staleTime: Infinity,
  });
}

export function usePrompts() {
  return useQuery({
    queryKey: ["prompts"],
    queryFn: fetchPrompts,
    staleTime: Infinity,
  });
}

// ── Ablation simulation with deterministic caching ──

export function serializeAblation(config: AblationConfigPayload): string {
  const parts: string[] = [];
  if (config.enabled_groups?.length) {
    parts.push(`g:${config.enabled_groups.join(",")}`);
  }
  if (config.enabled_portability?.length) {
    parts.push(`p:${config.enabled_portability.join(",")}`);
  }
  if (config.disabled_rule_ids?.length) {
    parts.push(`d:${config.disabled_rule_ids.join(",")}`);
  }
  return parts.join("|");
}

export function deserializeAblation(raw: string): AblationConfigPayload {
  const config: AblationConfigPayload = {};
  for (const part of raw.split("|")) {
    if (part.startsWith("g:")) {
      config.enabled_groups = part.slice(2).split(",").filter(Boolean);
    } else if (part.startsWith("p:")) {
      config.enabled_portability = part.slice(2).split(",").filter(Boolean);
    } else if (part.startsWith("d:")) {
      config.disabled_rule_ids = part.slice(2).split(",").filter(Boolean);
    }
  }
  return config;
}

export function useRunAblation(
  split: string,
  limit: number | undefined,
  ablationConfig: AblationConfigPayload
) {
  const serialized = serializeAblation(ablationConfig);
  return useQuery({
    queryKey: ["ablation", split, limit ?? "all", serialized],
    queryFn: () =>
      runAblation({
        split,
        pipeline: "rules_only",
        limit,
        ablation_config: ablationConfig,
      }),
    enabled: false, // only runs when manually refetched
    staleTime: Infinity, // deterministic result never goes stale
    gcTime: 1000 * 60 * 60 * 24, // keep in cache for 24h
  });
}

export function useArchitectUrlSync() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const skipInitialUrlSync = useRef(true);

  const {
    split,
    sourceRowIndex,
    selectedRunId,
    pipelineFamily,
    ablationConfig,
    activeStage,
    replayRunId,
    replayRowIndex,
    setSplit,
    setSourceRowIndex,
    setSelectedRunId,
    setAblationConfig,
    setActiveStage,
    setReplayRunId,
    setReplayRowIndex,
  } = useArchitectStore();

  // Registry is the single source of run identity. Bare family names in the
  // URL (?pipeline=hybrid_structured_events) are resolved to the current
  // canonical run for that family once the registry is loaded.
  const { data: registryData } = useQuery({
    queryKey: ["registry"],
    queryFn: fetchRegistry,
  });

  // Restore from URL on mount
  useEffect(() => {
    const rawParam = searchParams.get("run") ?? searchParams.get("pipeline");
    const splitParam = searchParams.get("split");
    const rowParam = searchParams.get("row");
    const ablationParam = searchParams.get("ablation");
    const stageParam = searchParams.get("stage") as TraceStage | null;
    const replayRunIdParam = searchParams.get("replayRunId");
    const replayRowIndexParam = searchParams.get("replayRowIndex");

    if (rawParam) {
      // If the URL carries a bare family name, defer to the registry resolver;
      // it picks the production winner / test split. If the registry has not
      // loaded yet, fall back to the bare value (re-resolved in the effect
      // below once registryData arrives).
      const runs = registryData?.runs ?? [];
      const resolved =
        isBareFamilyName(rawParam) && runs.length > 0
          ? resolveFamilyDefaultRun(runs, rawParam) ?? rawParam
          : rawParam;
      const family = isBareFamilyName(rawParam) ? rawParam : resolved;
      setSelectedRunId(resolved, family);
    }
    if (splitParam) setSplit(splitParam);
    if (rowParam) setSourceRowIndex(parseInt(rowParam, 10));
    if (ablationParam) setAblationConfig(deserializeAblation(ablationParam));
    if (stageParam) setActiveStage(stageParam);
    if (replayRunIdParam) setReplayRunId(replayRunIdParam);
    if (replayRowIndexParam) setReplayRowIndex(parseInt(replayRowIndexParam, 10));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Once the registry loads, resolve any bare family name that the mount
  // effect had to leave unresolved (or that resolved to a fallback).
  useEffect(() => {
    const runs = registryData?.runs;
    if (!runs || runs.length === 0) return;
    const urlRun = searchParams.get("run") ?? searchParams.get("pipeline");
    if (urlRun && !isBareFamilyName(urlRun)) return;
    // Only the production winner should re-resolve the store default; explicit
    // full run ids in the URL are left as-is.
    if (!isBareFamilyName(selectedRunId) && !isBareFamilyName(pipelineFamily)) return;
    const family = isBareFamilyName(pipelineFamily) ? pipelineFamily : selectedRunId;
    if (!family || !isBareFamilyName(family)) return;
    const resolved = resolveFamilyDefaultRun(runs, family);
    if (resolved && resolved !== selectedRunId) {
      setSelectedRunId(resolved, family);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [registryData?.runs]);

  // Sync to URL when state changes
  useEffect(() => {
    if (skipInitialUrlSync.current) {
      skipInitialUrlSync.current = false;
      return;
    }
    const params = new URLSearchParams();
    preserveWorkbenchDataset(params, searchParams);
    if (selectedRunId && selectedRunId !== "rules_only") params.set("run", selectedRunId);
    if (split) params.set("split", split);
    if (sourceRowIndex !== null) params.set("row", String(sourceRowIndex));
    const ablationStr = serializeAblation(ablationConfig);
    if (ablationStr) params.set("ablation", ablationStr);
    if (activeStage && activeStage !== "extract") params.set("stage", activeStage);
    if (replayRunId) params.set("replayRunId", replayRunId);
    if (replayRowIndex !== null) params.set("replayRowIndex", String(replayRowIndex));

    const newUrl = `${pathname}?${params.toString()}`;
    router.replace(newUrl, { scroll: false });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    selectedRunId,
    split,
    sourceRowIndex,
    ablationConfig,
    activeStage,
    replayRunId,
    replayRowIndex,
  ]);
}

// ── URL sync for Observatory page ──
export function useObservatoryUrlSync<TTab extends string>(
  activeTab: TTab,
  setActiveTab: (tab: TTab) => void
) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  // Restore tab on mount
  useEffect(() => {
    const tabParam = searchParams.get("tab");
    if (tabParam) {
      setActiveTab(tabParam as TTab);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync tab state to URL
  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());
    if (activeTab && activeTab !== "ladder") {
      params.set("tab", activeTab);
    } else {
      params.delete("tab");
    }
    const newUrl = `${pathname}?${params.toString()}`;
    router.replace(newUrl, { scroll: false });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);
}

// ── URL sync for Gallery page ──
export function useGalleryUrlSync<TErrorFilter extends string, TSortKey extends string>(
  errorFilter: TErrorFilter,
  setErrorFilter: (f: TErrorFilter) => void,
  categoryFilter: string,
  setCategoryFilter: (c: string) => void,
  sortKey: TSortKey,
  setSortKey: (s: TSortKey) => void,
  compareRunId: string,
  setCompareRunId: (id: string) => void,
  expandedRowKey: string | null,
  setExpandedRowKey: (key: string | null) => void
) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  // Restore on mount
  useEffect(() => {
    const errorParam = searchParams.get("filter");
    const catParam = searchParams.get("category");
    const sortParam = searchParams.get("sort");
    const compareParam = searchParams.get("compare");
    const expandedParam = searchParams.get("expanded");

    if (errorParam) setErrorFilter(errorParam as TErrorFilter);
    if (catParam) setCategoryFilter(catParam);
    if (sortParam) setSortKey(sortParam as TSortKey);
    if (compareParam) setCompareRunId(compareParam);
    if (expandedParam) setExpandedRowKey(expandedParam);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync to URL when state changes
  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());

    if (errorFilter && errorFilter !== "all_errors") {
      params.set("filter", errorFilter);
    } else {
      params.delete("filter");
    }

    if (categoryFilter && categoryFilter !== "all") {
      params.set("category", categoryFilter);
    } else {
      params.delete("category");
    }

    if (sortKey && sortKey !== "severity") {
      params.set("sort", sortKey);
    } else {
      params.delete("sort");
    }

    if (compareRunId) {
      params.set("compare", compareRunId);
    } else {
      params.delete("compare");
    }

    if (expandedRowKey) {
      params.set("expanded", expandedRowKey);
    } else {
      params.delete("expanded");
    }

    const newUrl = `${pathname}?${params.toString()}`;
    router.replace(newUrl, { scroll: false });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [errorFilter, categoryFilter, sortKey, compareRunId, expandedRowKey]);
}

// ── URL sync for Laboratory page ──
export function useLaboratoryUrlSync(
  search: string,
  setSearch: (s: string) => void,
  groupFilter: string,
  setGroupFilter: (g: string) => void,
  portabilityFilter: string,
  setPortabilityFilter: (p: string) => void,
  simSplit: string,
  setSimSplit: (s: string) => void,
  simLimit: string,
  setSimLimit: (l: string) => void,
  ablationConfig: AblationConfigPayload,
  setAblationConfig: (config: AblationConfigPayload) => void
) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  // Restore on mount
  useEffect(() => {
    const searchParam = searchParams.get("search");
    const groupParam = searchParams.get("group");
    const portParam = searchParams.get("portability");
    const simSplitParam = searchParams.get("simSplit");
    const simLimitParam = searchParams.get("simLimit");
    const ablationParam = searchParams.get("ablation");

    if (searchParam) setSearch(decodeURIComponent(searchParam));
    if (groupParam) setGroupFilter(groupParam);
    if (portParam) setPortabilityFilter(portParam);
    if (simSplitParam) setSimSplit(simSplitParam);
    if (simLimitParam) setSimLimit(simLimitParam);
    if (ablationParam) setAblationConfig(deserializeAblation(ablationParam));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync to URL when state changes
  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());

    if (search) {
      params.set("search", encodeURIComponent(search));
    } else {
      params.delete("search");
    }

    if (groupFilter && groupFilter !== "all") {
      params.set("group", groupFilter);
    } else {
      params.delete("group");
    }

    if (portabilityFilter && portabilityFilter !== "all") {
      params.set("portability", portabilityFilter);
    } else {
      params.delete("portability");
    }

    if (simSplit && simSplit !== "validation") {
      params.set("simSplit", simSplit);
    } else {
      params.delete("simSplit");
    }

    if (simLimit) {
      params.set("simLimit", simLimit);
    } else {
      params.delete("simLimit");
    }

    const ablationStr = serializeAblation(ablationConfig);
    if (ablationStr) {
      params.set("ablation", ablationStr);
    } else {
      params.delete("ablation");
    }

    const newUrl = `${pathname}?${params.toString()}`;
    router.replace(newUrl, { scroll: false });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    search,
    groupFilter,
    portabilityFilter,
    simSplit,
    simLimit,
    ablationConfig,
  ]);
}

// ── URL sync for Review page ──
export function useReviewUrlSync<TTab extends string>(
  activeTab: TTab,
  setActiveTab: (tab: TTab) => void
) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  // Restore on mount
  useEffect(() => {
    const tabParam = searchParams.get("tab");
    if (tabParam) {
      setActiveTab(tabParam as TTab);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync tab state to URL
  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());
    if (activeTab && activeTab !== "comparison") {
      params.set("tab", activeTab);
    } else {
      params.delete("tab");
    }
    const newUrl = `${pathname}?${params.toString()}`;
    router.replace(newUrl, { scroll: false });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);
}

