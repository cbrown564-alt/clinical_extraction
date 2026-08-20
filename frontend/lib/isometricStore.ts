"use client";

import { create } from "zustand";
import type {
  TeachingCaseData,
  TeachingRunData,
  MethodManifestData,
  StageObservationData,
  ManifestStageData,
  MethodId,
} from "./isometricTypes";

export type MethodType = "rules" | "llm" | "llm_with_rules";

interface IsometricState {
  cases: TeachingCaseData[];
  manifests: MethodManifestData[];
  selectedCaseId: string;
  selectedMethod: MethodType;
  currentStepIndex: number;
  stepProgress: number;
  isPlaying: boolean;
  playbackSpeed: number;
  hoveredStageId: string | null;
  selectedStageId: string | null;
  expandedRack: boolean;
  letterheadOpen: boolean;
  zoom: number;
  pan: { x: number; y: number };
  isLoading: boolean;
  error: string | null;

  // Actions
  loadData: () => Promise<void>;
  setSelectedCaseId: (caseId: string) => void;
  setSelectedMethod: (method: MethodType) => void;
  setCurrentStepIndex: (index: number) => void;
  setStepProgress: (progress: number) => void;
  setIsPlaying: (playing: boolean) => void;
  togglePlay: () => void;
  setPlaybackSpeed: (speed: number) => void;
  stepForward: () => void;
  stepBackward: () => void;
  setHoveredStageId: (stageId: string | null) => void;
  setSelectedStageId: (stageId: string | null) => void;
  toggleExpandedRack: () => void;
  toggleLetterhead: () => void;
  setLetterheadOpen: (open: boolean) => void;
  setZoom: (zoom: number | ((prev: number) => number)) => void;
  setPan: (pan: { x: number; y: number } | ((prev: { x: number; y: number }) => { x: number; y: number })) => void;
  resetCamera: () => void;
  resetPlayback: () => void;
}

export function methodIdFor(task: "gan2026" | "exectv2", method: MethodType): MethodId {
  if (task === "gan2026") {
    if (method === "rules") return "gan_rules";
    if (method === "llm") return "gan_llm_only";
    return "gan_llm_with_rules";
  }
  if (method === "rules") return "exect_rules";
  if (method === "llm") return "exect_llm_only";
  return "exect_llm_pre_post";
}

export const useIsometricStore = create<IsometricState>((set, get) => ({
  cases: [],
  manifests: [],
  selectedCaseId: "gan2026_cluster_vs_quiet_interval",
  selectedMethod: "llm_with_rules",
  currentStepIndex: 0,
  stepProgress: 0,
  isPlaying: false,
  playbackSpeed: 1,
  hoveredStageId: null,
  selectedStageId: null,
  expandedRack: true,
  letterheadOpen: true,
  zoom: 1.0,
  pan: { x: 0, y: 0 },
  isLoading: false,
  error: null,

  loadData: async () => {
    if (get().cases.length > 0) return;
    set({ isLoading: true, error: null });
    try {
      const res = await fetch("/api/teaching-cases");
      if (!res.ok) throw new Error(`HTTP ${res.status} fetching teaching cases`);
      const payload = await res.json();
      set({
        cases: payload.cases || [],
        manifests: payload.manifests || [],
        isLoading: false,
      });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  setSelectedCaseId: (caseId) => {
    set({
      selectedCaseId: caseId,
      currentStepIndex: 0,
      stepProgress: 0,
      isPlaying: false,
      selectedStageId: null,
    });
  },

  setSelectedMethod: (method) => {
    set({
      selectedMethod: method,
      currentStepIndex: 0,
      stepProgress: 0,
      isPlaying: false,
      selectedStageId: null,
    });
  },

  setCurrentStepIndex: (index) => {
    set({ currentStepIndex: index, stepProgress: 0 });
  },

  setStepProgress: (progress) => {
    set({ stepProgress: progress });
  },

  setIsPlaying: (playing) => {
    set({ isPlaying: playing });
  },

  togglePlay: () => {
    const isPlaying = !get().isPlaying;
    set({ isPlaying });
  },

  setPlaybackSpeed: (speed) => {
    set({ playbackSpeed: speed });
  },

  stepForward: () => {
    const { cases, selectedCaseId, selectedMethod, currentStepIndex } = get();
    const activeCase = cases.find((c) => c.case_id === selectedCaseId);
    if (!activeCase) return;
    const activeMethodId = methodIdFor(activeCase.task, selectedMethod);
    const activeRun = activeCase.runs.find((r) => r.method_id === activeMethodId);
    const maxSteps = (activeRun?.observations.length ?? 1) - 1;

    if (currentStepIndex < maxSteps) {
      set({ currentStepIndex: currentStepIndex + 1, stepProgress: 0 });
    } else {
      set({ isPlaying: false, currentStepIndex: maxSteps, stepProgress: 1 });
    }
  },

  stepBackward: () => {
    const { currentStepIndex } = get();
    if (currentStepIndex > 0) {
      set({ currentStepIndex: currentStepIndex - 1, stepProgress: 0 });
    }
  },

  setHoveredStageId: (stageId) => set({ hoveredStageId: stageId }),
  setSelectedStageId: (stageId) => set({ selectedStageId: stageId }),
  toggleExpandedRack: () => set((s) => ({ expandedRack: !s.expandedRack })),
  toggleLetterhead: () => set((s) => ({ letterheadOpen: !s.letterheadOpen })),
  setLetterheadOpen: (open) => set({ letterheadOpen: open }),
  setZoom: (zoom) =>
    set((s) => ({
      zoom: Math.min(Math.max(typeof zoom === "function" ? zoom(s.zoom) : zoom, 0.65), 1.75),
    })),
  setPan: (pan) =>
    set((s) => ({
      pan: typeof pan === "function" ? pan(s.pan) : pan,
    })),
  resetCamera: () => set({ zoom: 1.0, pan: { x: 0, y: 0 } }),
  resetPlayback: () => set({ currentStepIndex: 0, stepProgress: 0, isPlaying: false }),
}));

// Helper selector functions
export function getActiveCase(state: IsometricState): TeachingCaseData | undefined {
  return state.cases.find((c) => c.case_id === state.selectedCaseId) || state.cases[0];
}

export function getActiveRun(state: IsometricState): TeachingRunData | undefined {
  const activeCase = getActiveCase(state);
  if (!activeCase) return undefined;
  const targetMethodId = methodIdFor(activeCase.task, state.selectedMethod);
  return activeCase.runs.find((r) => r.method_id === targetMethodId);
}

export function getActiveObservation(state: IsometricState): StageObservationData | undefined {
  const run = getActiveRun(state);
  if (!run || run.observations.length === 0) return undefined;
  const index = Math.min(state.currentStepIndex, run.observations.length - 1);
  return run.observations[index];
}

export function getActiveManifest(state: IsometricState): MethodManifestData | undefined {
  const activeCase = getActiveCase(state);
  if (!activeCase) return undefined;
  const targetMethodId = methodIdFor(activeCase.task, state.selectedMethod);
  return state.manifests.find((m) => m.method_id === targetMethodId);
}

export function getStageManifest(
  manifest: MethodManifestData | undefined,
  stageId: string
): ManifestStageData | undefined {
  return manifest?.stages.find((s) => s.stage_id === stageId);
}
