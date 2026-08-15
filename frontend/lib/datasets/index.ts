/** Dataset kernel public surface. */
export * from "./types";
export { gan2026Dataset } from "./gan2026";
export { exectv2Dataset, EXECTV2_FAMILIES } from "./exectv2";
export {
  DATASETS,
  DATASET_IDS,
  DEFAULT_DATASET,
  getDataset,
  datasetSupports,
} from "./registry";
export {
  DATASET_PARAM,
  DATASET_STORAGE_KEY,
  parseDatasetId,
  resolveDatasetId,
  surfaceHref,
} from "./url";
export { filterBrowsableLetters, isBrowsableSplit } from "./splits";
export { useActiveDataset, useDatasetNavigation } from "./useDataset";
export {
  exectv2RuntimeAdapter,
  gan2026RuntimeAdapter,
  getRuntimeAdapter,
} from "./runtime";
export type {
  DatasetRuntimeAdapter,
  DatasetSurfaceComponents,
} from "./runtime";
