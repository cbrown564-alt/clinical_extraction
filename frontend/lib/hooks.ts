"use client";

import { useEffect, useCallback } from "react";
import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { runNote, fetchRules, fetchHealth, fetchRecords, fetchRecord, fetchPipelineFamilies } from "./api";
import type { RunNoteResponse, PipelineFamily, AblationConfigPayload } from "./types";
import { useConfigStore, useUiStore } from "./stores";

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
  return useQuery<RunNoteResponse | undefined>({
    queryKey: ["lastRun"],
    enabled: false,
  });
}

export function usePipelineFamilies() {
  return useQuery({
    queryKey: ["pipelineFamilies"],
    queryFn: fetchPipelineFamilies,
    staleTime: Infinity,
  });
}

function serializeAblation(config: AblationConfigPayload): string {
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

function deserializeAblation(raw: string): AblationConfigPayload {
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
    if (activeStage && activeStage !== "raw") params.set("stage", activeStage);
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
