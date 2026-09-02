"use client";

import { create } from "zustand";
import type { ActiveStage, AblationConfigPayload, PipelineFamily, PipelineTrace, TraceStage } from "./types";

interface UiState {
  activeStage: ActiveStage;
  goldOverlay: boolean;
  showDiff: boolean;
  setActiveStage: (stage: ActiveStage) => void;
  toggleGoldOverlay: () => void;
  toggleShowDiff: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  activeStage: "raw",
  goldOverlay: false,
  showDiff: false,
  setActiveStage: (stage) => set({ activeStage: stage }),
  toggleGoldOverlay: () => set((s) => ({ goldOverlay: !s.goldOverlay })),
  toggleShowDiff: () => set((s) => ({ showDiff: !s.showDiff })),
}));

// ── Architect store ──

interface ArchitectState {
  noteText: string;
  split: string | null;
  sourceRowIndex: number | null;
  selectedRunId: string;
  pipelineFamily: PipelineFamily;
  ablationConfig: AblationConfigPayload;
  activeStage: TraceStage;
  trace: PipelineTrace | null;
  isLoading: boolean;
  error: string | null;
  // For replay mode (LLM/hybrid)
  replayRunId: string | null;
  replayArtifactRows: unknown[] | null;
  replayRowIndex: number | null;
  workbenchView: "frequency" | "inventory";
  setNoteText: (t: string) => void;
  setSplit: (s: string | null) => void;
  setSourceRowIndex: (i: number | null) => void;
  setSelectedRunId: (runId: string, pipelineFamily: PipelineFamily) => void;
  setPipelineFamily: (p: PipelineFamily) => void;
  setAblationConfig: (a: AblationConfigPayload) => void;
  setActiveStage: (stage: TraceStage) => void;
  setTrace: (trace: PipelineTrace | null) => void;
  setIsLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setReplayRunId: (id: string | null) => void;
  setReplayArtifactRows: (rows: unknown[] | null) => void;
  setReplayRowIndex: (idx: number | null) => void;
  setWorkbenchView: (view: "frequency" | "inventory") => void;
  toggleRuleGroup: (group: string) => void;
  toggleRuleId: (ruleId: string) => void;
  reset: () => void;
}

// ── Laboratory store ──

interface LaboratoryState {
  ablationConfig: AblationConfigPayload;
  toggleRuleGroup: (group: string) => void;
  toggleRuleId: (ruleId: string) => void;
  setAblationConfig: (config: AblationConfigPayload) => void;
}

export const useLaboratoryStore = create<LaboratoryState>((set) => ({
  ablationConfig: {},
  toggleRuleGroup: (group) =>
    set((s) => {
      const current = new Set(s.ablationConfig.enabled_groups ?? []);
      if (current.has(group)) current.delete(group);
      else current.add(group);
      return { ablationConfig: { ...s.ablationConfig, enabled_groups: Array.from(current) } };
    }),
  toggleRuleId: (ruleId) =>
    set((s) => {
      const current = new Set(s.ablationConfig.disabled_rule_ids ?? []);
      if (current.has(ruleId)) current.delete(ruleId);
      else current.add(ruleId);
      return { ablationConfig: { ...s.ablationConfig, disabled_rule_ids: Array.from(current) } };
    }),
  setAblationConfig: (ablationConfig) => set({ ablationConfig }),
}));

export const useArchitectStore = create<ArchitectState>((set) => ({
  noteText: "",
  split: "validation",
  sourceRowIndex: 10,
  selectedRunId: "gan2026_validation750_gemini37flash_llm_extract",
  pipelineFamily: "llm_with_rules",
  ablationConfig: {},
  activeStage: "select",
  trace: null,
  isLoading: false,
  error: null,
  replayRunId: null,
  replayArtifactRows: null,
  replayRowIndex: null,
  workbenchView: "frequency",
  setNoteText: (noteText) => set({ noteText }),
  setSplit: (split) => set({ split, sourceRowIndex: null }),
  setSourceRowIndex: (sourceRowIndex) => set({ sourceRowIndex }),
  setSelectedRunId: (selectedRunId, pipelineFamily) =>
    set({
      selectedRunId,
      pipelineFamily,
      trace: null,
      replayArtifactRows: null,
      replayRowIndex: null,
    }),
  setPipelineFamily: (pipelineFamily) => set({ pipelineFamily, trace: null, replayArtifactRows: null, replayRowIndex: null }),
  setAblationConfig: (ablationConfig) => set({ ablationConfig }),
  setActiveStage: (activeStage) => set({ activeStage }),
  setTrace: (trace) => set({ trace }),
  setIsLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setReplayRunId: (replayRunId) => set({ replayRunId }),
  setReplayArtifactRows: (replayArtifactRows) => set({ replayArtifactRows }),
  setReplayRowIndex: (replayRowIndex) => set({ replayRowIndex }),
  setWorkbenchView: (workbenchView) => set({ workbenchView }),
  toggleRuleGroup: (group) =>
    set((s) => {
      const current = new Set(s.ablationConfig.enabled_groups ?? []);
      if (current.has(group)) current.delete(group);
      else current.add(group);
      return { ablationConfig: { ...s.ablationConfig, enabled_groups: Array.from(current) } };
    }),
  toggleRuleId: (ruleId) =>
    set((s) => {
      const current = new Set(s.ablationConfig.disabled_rule_ids ?? []);
      if (current.has(ruleId)) current.delete(ruleId);
      else current.add(ruleId);
      return { ablationConfig: { ...s.ablationConfig, disabled_rule_ids: Array.from(current) } };
    }),
  reset: () =>
    set({
      noteText: "",
      split: null,
      sourceRowIndex: null,
      selectedRunId: "gan2026_validation750_gemini37flash_llm_extract",
      pipelineFamily: "llm_with_rules",
      ablationConfig: {},
      activeStage: "select",
      trace: null,
      isLoading: false,
      error: null,
      replayRunId: null,
      replayArtifactRows: null,
      replayRowIndex: null,
      workbenchView: "frequency",
    }),
}));
