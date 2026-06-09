"use client";

import { useEffect, useCallback } from "react";
import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import {
  runNote,
  fetchRules,
  fetchHealth,
  fetchRecords,
  fetchRecord,
  fetchPipelineFamilies,
  runAblation,
  fetchPrompts,
} from "./api";
import type { RunNoteResponse, PipelineFamily, AblationConfigPayload, TraceStage, ActiveStage } from "./types";
import { useConfigStore, useUiStore, useArchitectStore } from "./stores";

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

// ── URL sync for the old workbench (ConfigStore) ──

export function useWorkbenchUrlSync() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const {
    pipeline,
    noteText,
    split,
    sourceRowIndex,
    ablationConfig,
    comparePipeline,
    compareAblationConfig,
    setPipeline,
    setNoteText,
    setSplit,
    setSourceRowIndex,
    setAblationConfig,
    setComparePipeline,
    setCompareAblationConfig,
  } = useConfigStore();
  const { activeStage, goldOverlay, showDiff, setActiveStage, toggleGoldOverlay, toggleShowDiff } =
    useUiStore();

  // Restore from URL on mount
  useEffect(() => {
    const p = searchParams.get("pipeline") as PipelineFamily | null;
    const cp = searchParams.get("comparePipeline") as PipelineFamily | null;
    const splitParam = searchParams.get("split");
    const rowParam = searchParams.get("row");
    const noteParam = searchParams.get("note");
    const ablationParam = searchParams.get("ablation");
    const compareAblationParam = searchParams.get("compareAblation");
    const stageParam = searchParams.get("stage") as ActiveStage | null;
    const goldParam = searchParams.get("gold");
    const diffParam = searchParams.get("diff");

    if (p) setPipeline(p);
    if (cp) setComparePipeline(cp);
    if (splitParam) setSplit(splitParam);
    if (rowParam) setSourceRowIndex(parseInt(rowParam, 10));
    if (noteParam) setNoteText(decodeURIComponent(noteParam));
    if (ablationParam) setAblationConfig(deserializeAblation(ablationParam));
    if (compareAblationParam)
      setCompareAblationConfig(deserializeAblation(compareAblationParam));
    if (stageParam) setActiveStage(stageParam);
    if (goldParam === "1") toggleGoldOverlay();
    if (diffParam === "1") toggleShowDiff();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync to URL when state changes
  useEffect(() => {
    const params = new URLSearchParams();
    if (pipeline && pipeline !== "rules_only") params.set("pipeline", pipeline);
    if (comparePipeline && comparePipeline !== "rules_only")
      params.set("comparePipeline", comparePipeline);
    if (split) params.set("split", split);
    if (sourceRowIndex !== null) params.set("row", String(sourceRowIndex));
    if (noteText) params.set("note", encodeURIComponent(noteText));
    const ablationStr = serializeAblation(ablationConfig);
    if (ablationStr) params.set("ablation", ablationStr);
    const compareAblationStr = serializeAblation(compareAblationConfig);
    if (compareAblationStr) params.set("compareAblation", compareAblationStr);
    if (activeStage && activeStage !== "extract") params.set("stage", activeStage);
    if (goldOverlay) params.set("gold", "1");
    if (showDiff) params.set("diff", "1");

    const newUrl = `${pathname}?${params.toString()}`;
    router.replace(newUrl, { scroll: false });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    pipeline,
    comparePipeline,
    split,
    sourceRowIndex,
    noteText,
    ablationConfig,
    compareAblationConfig,
    activeStage,
    goldOverlay,
    showDiff,
  ]);
}

// ── URL sync for the Architect store (Workbench / Trace viewer) ──

export function useArchitectUrlSync() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const {
    split,
    sourceRowIndex,
    pipelineFamily,
    ablationConfig,
    activeStage,
    replayRunId,
    replayRowIndex,
    setSplit,
    setSourceRowIndex,
    setPipelineFamily,
    setAblationConfig,
    setActiveStage,
    setReplayRunId,
    setReplayRowIndex,
  } = useArchitectStore();

  // Restore from URL on mount
  useEffect(() => {
    const pipelineParam = searchParams.get("pipeline");
    const splitParam = searchParams.get("split");
    const rowParam = searchParams.get("row");
    const ablationParam = searchParams.get("ablation");
    const stageParam = searchParams.get("stage") as TraceStage | null;
    const replayRunIdParam = searchParams.get("replayRunId");
    const replayRowIndexParam = searchParams.get("replayRowIndex");

    if (pipelineParam) setPipelineFamily(pipelineParam);
    if (splitParam) setSplit(splitParam);
    if (rowParam) setSourceRowIndex(parseInt(rowParam, 10));
    if (ablationParam) setAblationConfig(deserializeAblation(ablationParam));
    if (stageParam) setActiveStage(stageParam);
    if (replayRunIdParam) setReplayRunId(replayRunIdParam);
    if (replayRowIndexParam) setReplayRowIndex(parseInt(replayRowIndexParam, 10));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync to URL when state changes
  useEffect(() => {
    const params = new URLSearchParams();
    if (pipelineFamily && pipelineFamily !== "rules_only")
      params.set("pipeline", pipelineFamily);
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
    pipelineFamily,
    split,
    sourceRowIndex,
    ablationConfig,
    activeStage,
    replayRunId,
    replayRowIndex,
  ]);
}

// ── URL sync for Observatory page ──
export function useObservatoryUrlSync(
  activeTab: string,
  setActiveTab: (tab: any) => void
) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  // Restore tab on mount
  useEffect(() => {
    const tabParam = searchParams.get("tab");
    if (tabParam) {
      setActiveTab(tabParam);
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
export function useGalleryUrlSync(
  errorFilter: string,
  setErrorFilter: (f: any) => void,
  categoryFilter: string,
  setCategoryFilter: (c: string) => void,
  sortKey: string,
  setSortKey: (s: any) => void,
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

    if (errorParam) setErrorFilter(errorParam);
    if (catParam) setCategoryFilter(catParam);
    if (sortParam) setSortKey(sortParam);
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
  activeTab: string,
  setActiveTab: (tab: any) => void,
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
    const tabParam = searchParams.get("tab");
    const searchParam = searchParams.get("search");
    const groupParam = searchParams.get("group");
    const portParam = searchParams.get("portability");
    const simSplitParam = searchParams.get("simSplit");
    const simLimitParam = searchParams.get("simLimit");
    const ablationParam = searchParams.get("ablation");

    if (tabParam) setActiveTab(tabParam);
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

    if (activeTab && activeTab !== "inventory") {
      params.set("tab", activeTab);
    } else {
      params.delete("tab");
    }

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
    activeTab,
    search,
    groupFilter,
    portabilityFilter,
    simSplit,
    simLimit,
    ablationConfig,
  ]);
}

// ── URL sync for Review page ──
export function useReviewUrlSync(
  activeTab: string,
  setActiveTab: (tab: any) => void
) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  // Restore on mount
  useEffect(() => {
    const tabParam = searchParams.get("tab");
    if (tabParam) {
      setActiveTab(tabParam);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync tab state to URL
  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());
    if (activeTab && activeTab !== "assembly") {
      params.set("tab", activeTab);
    } else {
      params.delete("tab");
    }
    const newUrl = `${pathname}?${params.toString()}`;
    router.replace(newUrl, { scroll: false });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);
}

