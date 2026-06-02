"use client";

import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { runNote, fetchRules, fetchHealth, fetchRecords, fetchRecord } from "./api";
import type { RunNoteResponse } from "./types";

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
