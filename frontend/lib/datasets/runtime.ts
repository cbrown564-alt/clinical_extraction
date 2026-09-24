"use client";

import type { ComponentType } from "react";
import Exectv2ExampleExplorer from "@/components/exectv2/Exectv2ExampleExplorer";
import { GanExampleExplorer } from "@/components/gan2026/GanExampleExplorer";
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

const RUNTIME_ADAPTERS: Record<DatasetId, DatasetRuntimeAdapter> = {
  gan2026: gan2026RuntimeAdapter,
  exectv2: exectv2RuntimeAdapter,
};

export function getRuntimeAdapter(datasetId: DatasetId): DatasetRuntimeAdapter {
  return RUNTIME_ADAPTERS[datasetId];
}
