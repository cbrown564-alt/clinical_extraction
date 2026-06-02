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
  setPipeline: (p: PipelineFamily) => void;
  setNoteText: (t: string) => void;
  setAblationConfig: (a: AblationConfigPayload) => void;
  toggleRuleGroup: (group: string) => void;
  toggleRuleId: (ruleId: string) => void;
}

export const useConfigStore = create<ConfigState>((set) => ({
  pipeline: "rules_only",
  noteText: "",
  ablationConfig: {},
  setPipeline: (pipeline) => set({ pipeline }),
  setNoteText: (noteText) => set({ noteText }),
  setAblationConfig: (ablationConfig) => set({ ablationConfig }),
  toggleRuleGroup: (group) =>
    set((s) => {
      const current = new Set(s.ablationConfig.enabled_groups ?? []);
      if (current.has(group)) {
        current.delete(group);
      } else {
        current.add(group);
      }
      return {
        ablationConfig: {
          ...s.ablationConfig,
          enabled_groups: Array.from(current),
        },
      };
    }),
  toggleRuleId: (ruleId) =>
    set((s) => {
      const current = new Set(s.ablationConfig.disabled_rule_ids ?? []);
      if (current.has(ruleId)) {
        current.delete(ruleId);
      } else {
        current.add(ruleId);
      }
      return {
        ablationConfig: {
          ...s.ablationConfig,
          disabled_rule_ids: Array.from(current),
        },
      };
    }),
}));
