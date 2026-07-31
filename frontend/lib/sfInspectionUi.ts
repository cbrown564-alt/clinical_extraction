import type { SfFamily } from "@/lib/sfFamilies";

/** Must match backend COMPONENT_ORDER — see sf_inspection.py. */
export const COMPONENT_ORDER = [
  "clinical_headline",
  "state_profile",
  "state_profile_directional",
  "state_profile_direction_deconf",
  "state_profile_magnitude",
  "active_rate",
  "active_rate_fidelity",
  "seizure_free",
  "unknown",
  "exact_semantic",
  "benchmark_with_cui",
] as const;

export const FAMILY_TONE: Record<
  SfFamily["id"],
  { text: string; bg: string; border: string; dot: string; topBorder: string; leftBorder: string }
> = {
  headline: {
    text: "text-deterministic",
    bg: "bg-deterministic/10",
    border: "border-deterministic/30",
    dot: "bg-deterministic",
    topBorder: "border-t-deterministic",
    leftBorder: "border-l-deterministic",
  },
  change: {
    text: "text-hybrid",
    bg: "bg-hybrid/10",
    border: "border-hybrid/30",
    dot: "bg-hybrid",
    topBorder: "border-t-hybrid",
    leftBorder: "border-l-hybrid",
  },
  bench: {
    text: "text-muted",
    bg: "bg-surface-raised",
    border: "border-border",
    dot: "bg-muted",
    topBorder: "border-t-border",
    leftBorder: "border-l-border",
  },
};
