"use client";

import { create } from "zustand";
import type { ActiveStage, AblationConfigPayload, ArchitectNodeConfig, ArchitectEdgeConfig, PipelineFamily, SavedArchitecture } from "./types";

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

const DEFAULT_NODES: ArchitectNodeConfig[] = [
  { id: "extract", type: "extractor", label: "Extract", family: "rules_only", pipelineFamily: "rules_only", x: 100, y: 200 },
  { id: "normalise", type: "normaliser", label: "Normalise", family: "rules_only", pipelineFamily: "rules_only", x: 300, y: 200 },
  { id: "select", type: "selector", label: "Select", family: "rules_only", pipelineFamily: "rules_only", x: 500, y: 200 },
  { id: "repair", type: "repair", label: "Repair", family: "rules_only", pipelineFamily: "rules_only", x: 700, y: 200 },
  { id: "score", type: "scorer", label: "Score", family: "rules_only", pipelineFamily: "rules_only", x: 900, y: 200 },
];

const DEFAULT_EDGES: ArchitectEdgeConfig[] = [
  { id: "e1", source: "extract", target: "normalise" },
  { id: "e2", source: "normalise", target: "select" },
  { id: "e3", source: "select", target: "repair" },
  { id: "e4", source: "repair", target: "score" },
];

interface ArchitectState {
  nodes: ArchitectNodeConfig[];
  edges: ArchitectEdgeConfig[];
  selectedNodeId: string | null;
  compareMode: boolean;
  configA: SavedArchitecture | null;
  configB: SavedArchitecture | null;
  activeConfigLabel: "a" | "b";
  setNodes: (nodes: ArchitectNodeConfig[]) => void;
  setEdges: (edges: ArchitectEdgeConfig[]) => void;
  updateNode: (id: string, patch: Partial<ArchitectNodeConfig>) => void;
  setSelectedNodeId: (id: string | null) => void;
  toggleCompareMode: () => void;
  saveConfig: (label: "a" | "b", name: string, pipelineFamily: PipelineFamily, ablation: AblationConfigPayload) => void;
  loadConfig: (label: "a" | "b") => void;
  setActiveConfigLabel: (label: "a" | "b") => void;
  resetCanvas: () => void;
}

export const useArchitectStore = create<ArchitectState>((set, get) => ({
  nodes: DEFAULT_NODES,
  edges: DEFAULT_EDGES,
  selectedNodeId: null,
  compareMode: false,
  configA: null,
  configB: null,
  activeConfigLabel: "a",
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  updateNode: (id, patch) =>
    set((s) => ({
      nodes: s.nodes.map((n) => (n.id === id ? { ...n, ...patch } : n)),
    })),
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),
  toggleCompareMode: () => set((s) => ({ compareMode: !s.compareMode })),
  saveConfig: (label, name, pipelineFamily, ablation) =>
    set((s) => {
      const saved: SavedArchitecture = {
        name,
        pipelineFamily,
        nodes: s.nodes.map((n) => ({ ...n })),
        ablationConfig: ablation,
      };
      return label === "a" ? { configA: saved } : { configB: saved };
    }),
  loadConfig: (label) => {
    const cfg = label === "a" ? get().configA : get().configB;
    if (cfg) {
      set({ nodes: cfg.nodes.map((n) => ({ ...n })) });
    }
  },
  setActiveConfigLabel: (label) => set({ activeConfigLabel: label }),
  resetCanvas: () => set({ nodes: DEFAULT_NODES.map((n) => ({ ...n })), edges: DEFAULT_EDGES.map((e) => ({ ...e })) }),
}));
