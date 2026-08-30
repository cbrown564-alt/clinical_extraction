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
  fetchHealth,
  fetchLetters,
  fetchLetter,
  fetchPipelineFamilies,
  fetchRegistry,
} from "./api";
import type { DatasetId } from "./datasets/types";
import type { RunNoteResponse, TraceStage } from "./types";
import { useArchitectStore } from "./stores";
import {
  isBareFamilyName,
  resolveFamilyDefaultRun,
} from "./registryResolver";
import { isGanRulesRunId } from "./ganPipelineOptions";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: false,
    refetchInterval: 30000,
  });
}

export function useLetters(dataset: DatasetId) {
  return useQuery({
    queryKey: ["letters", dataset],
    queryFn: () => fetchLetters(dataset),
    staleTime: 5 * 60 * 1000,
  });
}

export function useLetter(dataset: "gan2026", letterId: string | null) {
  return useQuery({
    queryKey: ["letter", dataset, letterId],
    queryFn: () => fetchLetter(dataset, letterId!),
    enabled: Boolean(letterId),
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

export function useArchitectUrlSync() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const skipInitialUrlSync = useRef(true);

  const {
    sourceRowIndex,
    selectedRunId,
    pipelineFamily,
    activeStage,
    setSourceRowIndex,
    setSelectedRunId,
    setActiveStage,
  } = useArchitectStore();

  const { data: registryData } = useQuery({
    queryKey: ["registry"],
    queryFn: fetchRegistry,
  });

  useEffect(() => {
    const rawParam = searchParams.get("run") ?? searchParams.get("pipeline");
    const rowParam = searchParams.get("row");
    const stageParam = searchParams.get("stage") as TraceStage | null;

    if (rawParam) {
      if (isGanRulesRunId(rawParam)) {
        setSelectedRunId("rules", "rules");
      } else {
        const runs = registryData?.runs ?? [];
        const resolved =
          isBareFamilyName(rawParam) && runs.length > 0
            ? resolveFamilyDefaultRun(runs, rawParam) ?? rawParam
            : rawParam;
        const family = isBareFamilyName(rawParam) ? rawParam : resolved;
        setSelectedRunId(resolved, family);
      }
    }
    if (rowParam) setSourceRowIndex(parseInt(rowParam, 10));
    if (stageParam && stageParam !== "repair") setActiveStage(stageParam);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const runs = registryData?.runs;
    if (!runs || runs.length === 0) return;
    const urlRun = searchParams.get("run") ?? searchParams.get("pipeline");
    if (urlRun && !isBareFamilyName(urlRun)) return;
    if (!isBareFamilyName(selectedRunId) && !isBareFamilyName(pipelineFamily)) return;
    const family = isBareFamilyName(pipelineFamily) ? pipelineFamily : selectedRunId;
    if (!family || !isBareFamilyName(family)) return;
    const resolved = resolveFamilyDefaultRun(runs, family);
    if (resolved && resolved !== selectedRunId) {
      setSelectedRunId(resolved, family);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [registryData?.runs]);

  useEffect(() => {
    if (skipInitialUrlSync.current) {
      skipInitialUrlSync.current = false;
      return;
    }
    const params = new URLSearchParams();
    preserveWorkbenchDataset(params, searchParams);
    if (selectedRunId && selectedRunId !== "rules") params.set("run", selectedRunId);
    if (sourceRowIndex !== null) params.set("row", String(sourceRowIndex));
    if (activeStage && activeStage !== "select") params.set("stage", activeStage);

    const newUrl = `${pathname}?${params.toString()}`;
    router.replace(newUrl, { scroll: false });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedRunId, sourceRowIndex, activeStage]);
}
