"use client";

import { useCallback, useEffect, useSyncExternalStore } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import type { DatasetId } from "./types";
import { DEFAULT_DATASET, getDataset } from "./registry";
import {
  DATASET_PARAM,
  DATASET_STORAGE_KEY,
  parseDatasetId,
  resolveDatasetId,
} from "./url";

/** Same-tab notification channel for dataset persistence changes. */
const DATASET_EVENT = "explorer:dataset-changed";

function readStoredDataset(): DatasetId | null {
  if (typeof window === "undefined") return null;
  try {
    return parseDatasetId(window.localStorage.getItem(DATASET_STORAGE_KEY));
  } catch {
    return null;
  }
}

function writeStoredDataset(id: DatasetId): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(DATASET_STORAGE_KEY, id);
    window.dispatchEvent(new Event(DATASET_EVENT));
  } catch {
    // localStorage may be unavailable (private mode) — non-fatal.
  }
}

function subscribeStoredDataset(callback: () => void): () => void {
  if (typeof window === "undefined") return () => {};
  window.addEventListener("storage", callback);
  window.addEventListener(DATASET_EVENT, callback);
  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener(DATASET_EVENT, callback);
  };
}

/** Reads the persisted dataset reactively, defaulting on server/empty. */
function useStoredDataset(): DatasetId {
  return useSyncExternalStore(
    subscribeStoredDataset,
    () => readStoredDataset() ?? DEFAULT_DATASET,
    () => DEFAULT_DATASET
  );
}

/**
 * Resolves the active dataset for the current surface.
 *
 * Resolution order: an explicit `?dataset=` query value wins; otherwise fall
 * back to the last selection in localStorage; otherwise the default
 * ({@link DEFAULT_DATASET}). Bare Gan URLs therefore keep working. The stored
 * value is read through {@link useSyncExternalStore} so the server/initial render
 * uses the default and the client reconciles after hydration without a manual
 * effect-driven setState. A URL value is persisted so the shell remembers it.
 */
export function useActiveDataset(): DatasetId {
  const searchParams = useSearchParams();
  const urlDataset = parseDatasetId(searchParams.get(DATASET_PARAM));
  const storedDataset = useStoredDataset();

  useEffect(() => {
    if (urlDataset) writeStoredDataset(urlDataset);
  }, [urlDataset]);

  return urlDataset ?? storedDataset;
}

/**
 * Active dataset plus a setter for the app-shell switcher.
 *
 * Switching preserves the current surface (pathname) but resets incompatible
 * item selectors — Gan uses `pipeline`/`split`/`row`, ExECTv2 uses `run`/`letter`
 * — by replacing the query string with just `?dataset=`.
 */
export function useDatasetNavigation() {
  const datasetId = useActiveDataset();
  const router = useRouter();
  const pathname = usePathname();

  const setDataset = useCallback(
    (next: DatasetId) => {
      writeStoredDataset(next);
      const params = new URLSearchParams();
      params.set(DATASET_PARAM, next);
      router.push(`${pathname}?${params.toString()}`);
    },
    [pathname, router]
  );

  return { datasetId, descriptor: getDataset(datasetId), setDataset };
}

export { resolveDatasetId };
