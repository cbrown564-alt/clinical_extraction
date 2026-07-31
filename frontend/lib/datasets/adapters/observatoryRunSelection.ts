/**
 * Observatory run-selection helpers.
 *
 * Parses run IDs for display and picks sensible default runs on first load.
 */

import type { RegistryEntry } from "@/lib/types";
import { laneForRun } from "@/lib/observatoryLanes";

/** Parse a run ID into a human-readable variant string. */
export function parseRunVariant(runId: string, family: string): string {
  let s = runId.replace(/_2026-\d{2}-\d{2}$/, "");

  const familyPattern = family.replace(/_/g, "[_-]");
  const m = s.match(
    new RegExp(`gan2026[_-]?(?:${familyPattern})[_-]?(.*?)_(?:validation|test|synthetic)`)
  );
  if (m && m[1]) return m[1];

  s = s.replace(/^gan2026_/, "");
  return s || runId;
}

/** Extract split size from run metadata for sorting. */
export function parseSplitSize(split: string): number {
  if (split.includes("test")) return 10000;
  if (split.includes("750")) return 750;
  if (split.includes("250")) return 250;
  if (split.includes("50")) return 50;
  if (split.includes("25")) return 25;
  if (split.includes("hard")) return 15;
  if (split.includes("synthetic")) return 5;
  return 0;
}

export function getDefaultSelections(runs: RegistryEntry[]): Set<string> {
  const selected = new Set<string>();

  // Lane-tagged runs (production winner, ceiling/floor comparators) are always
  // part of the default selection so the production architecture is shown in
  // context. They are exempt from the selection cap below.
  const laneRunIds = new Set<string>();
  for (const run of runs) {
    if (laneForRun(run) && run.artifact_paths.some((p) => p.endsWith(".jsonl"))) {
      selected.add(run.run_id);
      laneRunIds.add(run.run_id);
    }
  }

  for (const run of runs) {
    if (run.split?.includes("validation+test") || run.split?.includes("test")) {
      if (run.artifact_paths.some((p) => p.endsWith(".jsonl"))) {
        selected.add(run.run_id);
      }
    }
  }

  const byFamily = new Map<string, RegistryEntry[]>();
  for (const run of runs) {
    if (!run.artifact_paths.some((p) => p.endsWith(".jsonl"))) continue;
    const list = byFamily.get(run.pipeline_family) ?? [];
    list.push(run);
    byFamily.set(run.pipeline_family, list);
  }

  for (const [, familyRuns] of byFamily) {
    const validationRuns = familyRuns.filter(
      (r) => r.split === "validation" && !selected.has(r.run_id)
    );
    if (validationRuns.length > 0) {
      const best = validationRuns.reduce((a, b) => (a.row_count > b.row_count ? a : b));
      selected.add(best.run_id);
    }
  }

  // Cap non-lane selections at 6; lane-tagged runs are always retained.
  if (selected.size > 6) {
    const kept = new Set<string>(laneRunIds);
    for (const id of selected) {
      if (kept.size >= 6 && !laneRunIds.has(id)) continue;
      kept.add(id);
    }
    return kept;
  }

  return selected;
}
