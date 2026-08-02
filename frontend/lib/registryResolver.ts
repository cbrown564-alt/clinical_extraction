/**
 * Registry-driven default-run resolution.
 *
 * Replaces the former hardcoded `LEGACY_FAMILY_DEFAULT_RUN` map, which pointed
 * at frozen validation750 comparator rows. The architect page accepts a bare
 * family name in the URL (`?pipeline=hybrid_structured_events`); this module
 * resolves that family name to the registry's best run for that family —
 * preferring the promoted production winner, then a test split, then the
 * highest-row validation run — so the URL always points at the current
 * canonical run rather than a frozen date-stamped row.
 */

import type { RegistryEntry } from "@/lib/types";
import { laneForRun } from "@/lib/observatoryLanes";

/** Bare family names historically accepted by the architect URL (?pipeline=…). */
export const KNOWN_PIPELINE_FAMILIES = new Set<string>([
  "rules",
  "rules_only",
  "hybrid_structured_events",
  "llm",
  "llm_only_canonical_pipeline",
]);

/**
 * Resolve a family name (or pass through a full run id) against a registry.
 * Returns the chosen `RegistryEntry`'s `run_id`, or `null` if no match.
 *
 * Selection precedence within a family:
 *   1. lane-tagged production winner
 *   2. a `test` (locked-test) split run with a scoreable artifact
 *   3. the highest-`row_count` run with a scoreable artifact
 */
export function resolveFamilyDefaultRun(
  runs: RegistryEntry[],
  family: string
): string | null {
  const inFamily = runs.filter(
    (r) => r.pipeline_family === family && r.artifact_paths.some((p) => p.endsWith(".jsonl"))
  );
  if (inFamily.length === 0) return null;

  const production = inFamily.find((r) => laneForRun(r) === "production");
  if (production) return production.run_id;

  const test = inFamily.find((r) => (r.split ?? "").includes("test"));
  if (test) return test.run_id;

  return inFamily.reduce((a, b) => (a.row_count > b.row_count ? a : b)).run_id;
}

/**
 * True if `value` is a bare family name that should be resolved against the
 * registry rather than treated as a concrete run id.
 */
export function isBareFamilyName(value: string): boolean {
  return KNOWN_PIPELINE_FAMILIES.has(value);
}
