"use client";

import type { ComponentType } from "react";
import { useObservatoryData } from "@/components/observatory/useObservatoryData";
import Exectv2AggregatePerformance from "@/components/exectv2/Exectv2AggregatePerformance";
import Exectv2ComponentImpact from "@/components/exectv2/Exectv2ComponentImpact";
import Exectv2ErrorGallery from "@/components/exectv2/Exectv2ErrorGallery";
import Exectv2ExampleExplorer from "@/components/exectv2/Exectv2ExampleExplorer";
import { useExectv2Runs, useExectv2Selection } from "@/components/exectv2/useExectv2";
import GanComponentImpact from "@/components/laboratory/GanComponentImpact";
import ReportBuilder from "@/components/review/ReportBuilder";
import { GanErrorGallery } from "@/app/gallery/page";
import { GanExampleExplorer } from "@/app/workbench/page";
import type { Exectv2RunSummary, RegistryEntry } from "@/lib/types";
import type { DatasetId } from "./types";
import { useActiveDataset } from "./useDataset";

/** Lightweight run list for surface selectors. */
export interface RunCatalogState {
  runs: Array<RegistryEntry | Exectv2RunSummary>;
  isLoading: boolean;
  error: unknown;
}

/** Multi-run selection shared by observatory-style surfaces. */
export interface RunSelectionState {
  selectedRunIds: Set<string>;
  toggle: (runId: string) => void;
  setSelection: (runIds: string[]) => void;
  selectedIds?: Set<string>;
}

export interface DatasetSurfaceComponents {
  ErrorGallery: ComponentType;
  AggregatePerformance: ComponentType;
  ComponentImpact: ComponentType;
  ExampleExplorer: ComponentType;
}

export interface DatasetRuntimeAdapter {
  id: DatasetId;
  useRunCatalog: () => RunCatalogState;
  useRunSelection: () => RunSelectionState;
  surfaces: DatasetSurfaceComponents;
}

function useGan2026RunCatalog(): RunCatalogState {
  const { runs, registryLoading } = useObservatoryData();
  return { runs, isLoading: registryLoading, error: null };
}

function useGan2026RunSelection(): RunSelectionState {
  const { selectedRunIds, toggleRun, selectRuns } = useObservatoryData();
  return {
    selectedRunIds,
    toggle: toggleRun,
    setSelection: selectRuns,
  };
}

function useExectv2RunCatalog(): RunCatalogState {
  const { runs, isLoading, error } = useExectv2Runs();
  return { runs, isLoading, error };
}

function useExectv2RunSelection(): RunSelectionState {
  const { runs } = useExectv2Runs();
  const { selectedIds, selectedRunIds, toggle, setSelection } = useExectv2Selection(runs);
  return {
    selectedRunIds: new Set(selectedRunIds),
    selectedIds,
    toggle,
    setSelection,
  };
}

/** Dataset-agnostic run catalog; delegates to the active dataset hooks. */
export function useRunCatalog(): RunCatalogState {
  const dataset = useActiveDataset();
  const observatory = useObservatoryData();
  const exectv2 = useExectv2Runs();

  if (dataset === "exectv2") {
    return { runs: exectv2.runs, isLoading: exectv2.isLoading, error: exectv2.error };
  }
  return { runs: observatory.runs, isLoading: observatory.registryLoading, error: null };
}

/** Dataset-agnostic multi-run selection. */
export function useRunSelection(): RunSelectionState {
  const dataset = useActiveDataset();
  const observatory = useObservatoryData();
  const exectv2Runs = useExectv2Runs();
  const exectv2Selection = useExectv2Selection(exectv2Runs.runs);

  if (dataset === "exectv2") {
    return {
      selectedRunIds: new Set(exectv2Selection.selectedRunIds),
      selectedIds: exectv2Selection.selectedIds,
      toggle: exectv2Selection.toggle,
      setSelection: exectv2Selection.setSelection,
    };
  }
  return {
    selectedRunIds: observatory.selectedRunIds,
    toggle: observatory.toggleRun,
    setSelection: observatory.selectRuns,
  };
}

export const gan2026RuntimeAdapter: DatasetRuntimeAdapter = {
  id: "gan2026",
  useRunCatalog: useGan2026RunCatalog,
  useRunSelection: useGan2026RunSelection,
  surfaces: {
    ErrorGallery: GanErrorGallery,
    AggregatePerformance: ReportBuilder,
    ComponentImpact: GanComponentImpact,
    ExampleExplorer: GanExampleExplorer,
  },
};

export const exectv2RuntimeAdapter: DatasetRuntimeAdapter = {
  id: "exectv2",
  useRunCatalog: useExectv2RunCatalog,
  useRunSelection: useExectv2RunSelection,
  surfaces: {
    ErrorGallery: Exectv2ErrorGallery,
    AggregatePerformance: Exectv2AggregatePerformance,
    ComponentImpact: Exectv2ComponentImpact,
    ExampleExplorer: Exectv2ExampleExplorer,
  },
};

const RUNTIME_ADAPTERS: Record<DatasetId, DatasetRuntimeAdapter> = {
  gan2026: gan2026RuntimeAdapter,
  exectv2: exectv2RuntimeAdapter,
};

export function getRuntimeAdapter(datasetId: DatasetId): DatasetRuntimeAdapter {
  return RUNTIME_ADAPTERS[datasetId];
}
