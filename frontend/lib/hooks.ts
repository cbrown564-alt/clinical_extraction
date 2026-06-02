"use client";

import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { runNote, fetchRules, fetchHealth } from "./api";
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
