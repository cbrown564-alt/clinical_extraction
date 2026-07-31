import type { DatasetDescriptor, DatasetId, ExplorerSurface } from "./types";
import { gan2026Dataset } from "./gan2026";
import { exectv2Dataset } from "./exectv2";

/** The dataset that bare URLs (no `?dataset=`) resolve to, for Gan back-compat. */
export const DEFAULT_DATASET: DatasetId = "gan2026";

/** All datasets, in app-shell display order. */
export const DATASETS: DatasetDescriptor[] = [gan2026Dataset, exectv2Dataset];

export const DATASET_IDS: DatasetId[] = DATASETS.map((d) => d.id);

const BY_ID: Record<DatasetId, DatasetDescriptor> = {
  gan2026: gan2026Dataset,
  exectv2: exectv2Dataset,
};

/** Returns the descriptor for a dataset id, falling back to the default. */
export function getDataset(id: DatasetId): DatasetDescriptor {
  return BY_ID[id] ?? BY_ID[DEFAULT_DATASET];
}

/** Whether a dataset declares support for a given surface. */
export function datasetSupports(id: DatasetId, surface: ExplorerSurface): boolean {
  return getDataset(id).supports[surface];
}
