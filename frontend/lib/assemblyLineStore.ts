import { create } from "zustand";
import type { TeachingCaseData, TeachingRunData } from "./isometricTypes";
import { methodIdFor, type MethodType } from "./isometricStore";
import { resolvePaperCellId } from "./paperCells";

interface AssemblyLineState {
  cases: TeachingCaseData[];
  selectedCaseId: string;
  selectedMethod: MethodType;
  selectedFactId: string | null;
  isLoading: boolean;
  error: string | null;
  loadData: () => Promise<void>;
  setSelectedCaseId: (caseId: string) => void;
  setSelectedMethod: (method: MethodType) => void;
  setSelectedFactId: (factId: string | null) => void;
}

export const useAssemblyLineStore = create<AssemblyLineState>((set, get) => ({
  cases: [],
  selectedCaseId: "exectv2_epileptic_vs_dissociative",
  selectedMethod: "llm_extract",
  selectedFactId: null,
  isLoading: false,
  error: null,

  loadData: async () => {
    const firstLoad = get().cases.length === 0;
    if (firstLoad) set({ isLoading: true, error: null });
    try {
      const res = await fetch("/api/teaching-cases", { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status} fetching teaching cases`);
      const payload = await res.json();
      set({
        cases: payload.cases || [],
        isLoading: false,
        error: null,
      });
    } catch (err) {
      set({ error: (err as Error).message, isLoading: false });
    }
  },

  setSelectedCaseId: (caseId) => {
    set({ selectedCaseId: caseId, selectedFactId: null });
  },

  setSelectedMethod: (method) => {
    set({ selectedMethod: resolvePaperCellId(method), selectedFactId: null });
  },

  setSelectedFactId: (factId) => {
    set({ selectedFactId: factId });
  },
}));

export function getActiveAssemblyCase(state: AssemblyLineState): TeachingCaseData | undefined {
  return state.cases.find((item) => item.case_id === state.selectedCaseId) || state.cases[0];
}

export function getActiveAssemblyRun(state: AssemblyLineState): TeachingRunData | undefined {
  const activeCase = getActiveAssemblyCase(state);
  if (!activeCase) return undefined;
  return activeCase.runs.find(
    (run) => run.method_id === methodIdFor(activeCase.task, state.selectedMethod)
  );
}
