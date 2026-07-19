import type { SfAttributeRow, SfMentionRow } from "@/lib/types";

/**
 * Shared presentation tokens for SF inspection — split out from the view
 * components so SfMentionFlow / SfAttributeSchema / SfInspectionViews can
 * all reference them without importing each other's components.
 */

export const STATUS_META: Record<SfMentionRow["status"], { label: string; tone: string }> = {
  tp: { label: "TP", tone: "text-success" },
  fp: { label: "FP", tone: "text-error" },
  fn: { label: "FN", tone: "text-error" },
  skip: { label: "—", tone: "text-muted" },
};

export const MATCH_META: Record<SfAttributeRow["match"], { symbol: string; tone: string }> = {
  ok: { symbol: "✓", tone: "text-success" },
  bad: { symbol: "✗", tone: "text-error" },
  absent: { symbol: "—", tone: "text-muted" },
};

export const VALIDITY_LABEL: Record<SfAttributeRow["validity"], string> = {
  ok: "ok",
  absent: "—",
  illegal_value: "OUT OF VOCAB",
  illegal_attr: "ILLEGAL ATTR",
  noise: "noise attr",
};

export const VALIDITY_TONE: Record<SfAttributeRow["validity"], string> = {
  ok: "text-success",
  absent: "text-muted",
  illegal_value: "text-error font-semibold",
  illegal_attr: "text-error font-semibold",
  noise: "text-muted",
};

export function fmtVal(v: string): string {
  return v === "" ? "—" : v;
}

/**
 * Display-side phrase normalization: hyphens, case, spacing, trailing plural-s.
 * Used to decide whether a scorer phrase_match=bad is a real mismatch or just
 * surface spelling noise (e.g. "focal-…-seizure" vs "Focal … seizures").
 */
export function displayPhraseNorm(s: string): string {
  return s
    .toLowerCase()
    .replace(/-/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/s$/, "");
}

export type PhraseSurfaceKind = "identical" | "surface" | "substantive";

export function phraseSurfaceKind(gold: string, pred: string): PhraseSurfaceKind {
  if (gold.trim() === pred.trim()) return "identical";
  if (displayPhraseNorm(gold) === displayPhraseNorm(pred)) return "surface";
  return "substantive";
}

/** Short human label for a FrequencyStateScores component name. */
export const COMPONENT_SHORT_LABEL: Record<string, string> = {
  clinical_headline: "Headline (3-way state)",
  state_profile: "Change profile (4-way)",
  state_profile_directional: "Directional change",
  state_profile_direction_deconf: "Direction deconflicted",
  state_profile_magnitude: "Magnitude axis",
  active_rate: "Active-rate filter",
  active_rate_fidelity: "Active-rate fidelity",
  seizure_free: "Seizure-free filter",
  unknown: "Unknown filter",
  exact_semantic: "Exact semantic match",
  benchmark_with_cui: "Benchmark with CUI",
};

export function componentShortLabel(name: string): string {
  return COMPONENT_SHORT_LABEL[name] ?? name.replace(/_/g, " ");
}

/** Plain-English component stats for the scorer breakdown header. */
export function componentStatsLabel(tp: number, fp: number, fn: number): string {
  if (fp === 0 && fn === 0) {
    return tp === 1 ? "1 match" : `${tp} matches`;
  }
  const parts: string[] = [];
  if (fp > 0) parts.push(`${fp} extra pred${fp === 1 ? "" : "s"}`);
  if (fn > 0) parts.push(`${fn} missed gold${fn === 1 ? "" : "s"}`);
  if (tp > 0) parts.push(`${tp} match${tp === 1 ? "" : "es"}`);
  return parts.join(" · ");
}

/**
 * Turn scorer-internal count keys (NS=/L=/U=) into readable text.
 * NS = point count, L/U = range bounds used in the fidelity lens.
 */
export function formatScorerCounts(raw: string): string {
  if (!raw || raw === "(no counts)") return "no count attributes";
  const m = raw.match(/^NS=([^/]*)\/L=([^/]*)\/U=(.*)$/);
  if (!m) return raw;
  const [, ns, lower, upper] = m;
  const parts: string[] = [];
  if (ns) parts.push(`exact count ${ns}`);
  if (lower || upper) {
    const lo = lower || "?";
    const hi = upper || "?";
    parts.push(lo === hi ? `range ${lo} (lower=upper)` : `range ${lo}–${hi}`);
  }
  return parts.length > 0 ? parts.join(" · ") : "no count attributes";
}

export function formatScorerFreqChg(raw: string): string | null {
  const v = raw.trim();
  if (!v) return null;
  return `change: ${v}`;
}

export function formatScorerState(raw: string): string | null {
  const v = raw.trim();
  if (!v) return null;
  return `projected state: ${v}`;
}
