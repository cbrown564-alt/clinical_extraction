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

interface ConfigState {
  pipeline: PipelineFamily;
  noteText: string;
  ablationConfig: AblationConfigPayload;
  split: string | null;
  sourceRowIndex: number | null;
  comparePipeline: PipelineFamily;
  compareAblationConfig: AblationConfigPayload;
  setPipeline: (p: PipelineFamily) => void;
  setNoteText: (t: string) => void;
  setAblationConfig: (a: AblationConfigPayload) => void;
  setSplit: (s: string | null) => void;
  setSourceRowIndex: (i: number | null) => void;
  setComparePipeline: (p: PipelineFamily) => void;
  setCompareAblationConfig: (a: AblationConfigPayload) => void;
  toggleRuleGroup: (group: string, target?: "a" | "b") => void;
  toggleRuleId: (ruleId: string, target?: "a" | "b") => void;
}

function toggleRuleGroupInConfig(
  config: AblationConfigPayload,
  group: string
): AblationConfigPayload {
  const current = new Set(config.enabled_groups ?? []);
  if (current.has(group)) {
    current.delete(group);
  } else {
    current.add(group);
  }
  return {
    ...config,
    enabled_groups: Array.from(current),
  };
}

function toggleRuleIdInConfig(
  config: AblationConfigPayload,
  ruleId: string
): AblationConfigPayload {
  const current = new Set(config.disabled_rule_ids ?? []);
  if (current.has(ruleId)) {
    current.delete(ruleId);
  } else {
    current.add(ruleId);
  }
  return {
    ...config,
    disabled_rule_ids: Array.from(current),
  };
}

export const useConfigStore = create<ConfigState>((set) => ({
  pipeline: "rules_only",
  noteText: "",
  ablationConfig: {},
  split: null,
  sourceRowIndex: null,
  comparePipeline: "rules_only",
  compareAblationConfig: {},
  setPipeline: (pipeline) => set({ pipeline }),
  setNoteText: (noteText) => set({ noteText }),
  setAblationConfig: (ablationConfig) => set({ ablationConfig }),
  setSplit: (split) => set({ split, sourceRowIndex: null }),
  setSourceRowIndex: (sourceRowIndex) => set({ sourceRowIndex }),
  setComparePipeline: (comparePipeline) => set({ comparePipeline }),
  setCompareAblationConfig: (compareAblationConfig) =>
    set({ compareAblationConfig }),
  toggleRuleGroup: (group, target = "a") =>
    set((s) =>
      target === "b"
        ? {
            compareAblationConfig: toggleRuleGroupInConfig(
              s.compareAblationConfig,
              group
            ),
          }
        : {
            ablationConfig: toggleRuleGroupInConfig(s.ablationConfig, group),
          }
    ),
  toggleRuleId: (ruleId, target = "a") =>
    set((s) =>
      target === "b"
        ? {
            compareAblationConfig: toggleRuleIdInConfig(
              s.compareAblationConfig,
              ruleId
            ),
          }
        : {
            ablationConfig: toggleRuleIdInConfig(s.ablationConfig, ruleId),
          }
    ),
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
  selectedRunId: "rules_only",
  pipelineFamily: "rules_only",
  ablationConfig: {},
  activeStage: "extract",
  trace: null,
  isLoading: false,
  error: null,
  replayRunId: null,
  replayArtifactRows: null,
  replayRowIndex: null,
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
      selectedRunId: "rules_only",
      pipelineFamily: "rules_only",
      ablationConfig: {},
      activeStage: "extract",
      trace: null,
      isLoading: false,
      error: null,
      replayRunId: null,
      replayArtifactRows: null,
      replayRowIndex: null,
    }),
}));
