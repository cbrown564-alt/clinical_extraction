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
