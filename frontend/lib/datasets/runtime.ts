"use client";

import type { ComponentType } from "react";
import Exectv2ExampleExplorer from "@/components/exectv2/Exectv2ExampleExplorer";
import { GanExampleExplorer } from "@/components/gan2026/GanExampleExplorer";
import R8WorkbenchExplorer from "@/components/gan2026/R8WorkbenchExplorer";
import type { DatasetId } from "./types";

export interface DatasetSurfaceComponents {
  ExampleExplorer: ComponentType;
}

export interface DatasetRuntimeAdapter {
  id: DatasetId;
  surfaces: DatasetSurfaceComponents;
}

export const gan2026RuntimeAdapter: DatasetRuntimeAdapter = {
  id: "gan2026",
  surfaces: {
    ExampleExplorer: GanExampleExplorer,
  },
};

export const exectv2RuntimeAdapter: DatasetRuntimeAdapter = {
  id: "exectv2",
  surfaces: {
    ExampleExplorer: Exectv2ExampleExplorer,
  },
};

export const ganR8RuntimeAdapter: DatasetRuntimeAdapter = {
  id: "ganR8",
  surfaces: { ExampleExplorer: R8WorkbenchExplorer },
};

const RUNTIME_ADAPTERS: Record<DatasetId, DatasetRuntimeAdapter> = {
  gan2026: gan2026RuntimeAdapter,
  exectv2: exectv2RuntimeAdapter,
  ganR8: ganR8RuntimeAdapter,
};

export function getRuntimeAdapter(datasetId: DatasetId): DatasetRuntimeAdapter {
  return RUNTIME_ADAPTERS[datasetId];
}
