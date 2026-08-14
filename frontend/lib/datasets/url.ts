import type { DatasetId, ExplorerSurface } from "./types";
import { DATASET_IDS, DEFAULT_DATASET } from "./registry";

/** The URL query key that carries the active dataset across surfaces. */
export const DATASET_PARAM = "dataset";

/** localStorage key for app-shell dataset persistence. */
export const DATASET_STORAGE_KEY = "explorer-active-dataset";

/** Parses a raw query value into a known dataset id, or null when unrecognised. */
export function parseDatasetId(raw: string | null | undefined): DatasetId | null {
  if (!raw) return null;
  return (DATASET_IDS as string[]).includes(raw) ? (raw as DatasetId) : null;
}

/** Resolves the active dataset from a URL value, falling back to the default. */
export function resolveDatasetId(raw: string | null | undefined): DatasetId {
  return parseDatasetId(raw) ?? DEFAULT_DATASET;
}

/** Route segment for each stable surface. */
const SURFACE_PATHS: Record<ExplorerSurface, string> = {
  workbench: "/workbench",
  "gold-audit": "/gold-audit",
};

/**
 * Builds a deep-link to a surface that preserves the active dataset plus any
 * extra params (e.g. run/letter/family). Used for cross-surface navigation so
 * the dataset is never dropped.
 */
export function surfaceHref(
  surface: ExplorerSurface,
  datasetId: DatasetId,
  extra: Record<string, string | number | undefined> = {}
): string {
  const params = new URLSearchParams();
  params.set(DATASET_PARAM, datasetId);
  for (const [key, value] of Object.entries(extra)) {
    if (value !== undefined && value !== "") params.set(key, String(value));
  }
  return `${SURFACE_PATHS[surface]}?${params.toString()}`;
}
