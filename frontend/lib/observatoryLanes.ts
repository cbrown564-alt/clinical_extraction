/**
 * Observatory lane tagging.
 *
 * Runs can carry explicit `registry_roles` entries (declared in
 * `src/clinical_extraction/core/registry.py` and tagged in
 * `experiments/registry.jsonl`) that place them in a production / ceiling /
 * floor lane. The lane lets the observatory show the production winner next to
 * its ceiling and floor comparators rather than as an undifferentiated row.
 *
 * Lanes are gan2026-only today; exectv2 conveys control status through its own
 * `decision` field on the dedicated ExECTv2 surfaces, so no exectv2 run should
 * carry these roles.
 */

import type { LaneId, RegistryEntry } from "@/lib/types";

export type { LaneId };

export interface LaneMeta {
  id: LaneId;
  label: string;
  /** Sort weight — lower sorts first (production leads the ladder). */
  order: number;
  badgeClass: string;
  textClass: string;
  /** Card ring class (literal so Tailwind's scanner picks it up). */
  ringClass: string;
  title: string;
}

export const LANE_META: Record<LaneId, LaneMeta> = {
  production: {
    id: "production",
    label: "Production",
    order: 0,
    badgeClass: "bg-success/15 border-success/30",
    textClass: "text-success",
    ringClass: "ring-1 ring-success/40",
    title: "Promoted production architecture",
  },
  ceiling: {
    id: "ceiling",
    label: "Ceiling",
    order: 1,
    badgeClass: "bg-llm/15 border-llm/30",
    textClass: "text-llm",
    ringClass: "ring-1 ring-llm/40",
    title: "Ceiling comparator — not production",
  },
  floor: {
    id: "floor",
    label: "Floor",
    order: 2,
    badgeClass: "bg-deterministic/15 border-deterministic/30",
    textClass: "text-deterministic",
    ringClass: "ring-1 ring-deterministic/40",
    title: "Floor (rules-only) comparator",
  },
};

const ROLE_TO_LANE: Record<string, LaneId> = {
  production_winner: "production",
  ceiling_comparator: "ceiling",
  floor_comparator: "floor",
};

/**
 * Resolve the lane for a registry entry from its `registry_roles`, or `null`
 * if the entry carries no production/ceiling/floor role.
 */
export function laneForRun(entry: Pick<RegistryEntry, "registry_roles">): LaneId | null {
  const roles = entry.registry_roles;
  if (!roles || roles.length === 0) return null;
  for (const role of roles) {
    const lane = ROLE_TO_LANE[role];
    if (lane) return lane;
  }
  return null;
}

export function laneMetaForRun(entry: Pick<RegistryEntry, "registry_roles">): LaneMeta | null {
  const lane = laneForRun(entry);
  return lane ? LANE_META[lane] : null;
}

/** Sort comparator that puts lane-tagged runs first (production→ceiling→floor), then unlabeled. */
export function compareByLane<T extends Pick<RegistryEntry, "registry_roles">>(
  a: T,
  b: T
): number {
  const la = laneForRun(a);
  const lb = laneForRun(b);
  const oa = la ? LANE_META[la].order : Number.MAX_SAFE_INTEGER;
  const ob = lb ? LANE_META[lb].order : Number.MAX_SAFE_INTEGER;
  return oa - ob;
}
