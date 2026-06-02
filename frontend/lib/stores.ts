"use client";

import { create } from "zustand";
import type { ActiveStage, AblationConfigPayload, PipelineFamily } from "./types";

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
