import type { SfAttributeRow, SfLayerAPair } from "@/lib/types";

/**
 * The SF schema is 20 flat attribute names, but it's really 5 groups. Pair
 * comparisons cluster columns by this grouping instead of listing 20 flat
 * rows. CUIPhrase is deliberately excluded from every group: it mirrors the
 * pair's phrase header (already shown above the card) and duplicating it
 * here would just be more text for no new signal.
 */
export interface SfSchemaGroup {
  id: string;
  label: string;
  keys: string[];
}

export const SF_SCHEMA_GROUPS: SfSchemaGroup[] = [
  { id: "identity", label: "Identity", keys: ["CUI", "Certainty", "Negation"] },
  { id: "count", label: "Count", keys: ["NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures"] },
  {
    id: "cadence",
    label: "Cadence",
    keys: ["NumberOfTimePeriods", "LowerNumberOfTimePeriods", "UpperNumberOfTimePeriods", "TimePeriod", "FrequencyChange"],
  },
  {
    id: "temporal",
    label: "Temporal anchor",
    keys: ["TimeSince_or_TimeOfEvent", "PointInTime", "DayDate", "MonthDate", "YearDate"],
  },
  { id: "demographics", label: "Demographics", keys: ["AgeLower", "AgeUpper", "AgeUnit"] },
];

/** Short slot labels for the compact card — the full key still shows on hover via the title attribute. */
export const SF_SLOT_SHORT_LABEL: Record<string, string> = {
  NumberOfSeizures: "count",
  LowerNumberOfSeizures: "lower",
  UpperNumberOfSeizures: "upper",
  NumberOfTimePeriods: "periods",
  LowerNumberOfTimePeriods: "lower",
  UpperNumberOfTimePeriods: "upper",
  TimePeriod: "unit",
  FrequencyChange: "FreqChg",
  TimeSince_or_TimeOfEvent: "since/event",
  PointInTime: "point-in-time",
  DayDate: "day",
  MonthDate: "month",
  YearDate: "year",
  AgeLower: "lower",
  AgeUpper: "upper",
  AgeUnit: "unit",
  CUI: "CUI",
  Certainty: "certainty",
  Negation: "negation",
};


// ── Always-visible gold/pred comparison table (Layer A) ──

export interface CompareColumn {
  key: string;
  groupId: string;
  groupLabel: string;
  label: string;
  gold: string;
  pred: string;
  state: "same" | "diverge";
}

/** One column per populated (gold or pred non-empty) attribute, in canonical group/key order — not raw payload order — so group clusters render contiguously. */
export function buildComparisonColumns(pair: SfLayerAPair): CompareColumn[] {
  const byKey = new Map(pair.attributes.map((a) => [a.key, a]));
  const columns: CompareColumn[] = [];
  for (const group of SF_SCHEMA_GROUPS) {
    for (const key of group.keys) {
      const attr = byKey.get(key);
      if (!attr || (!attr.gold && !attr.pred)) continue;
      columns.push({
        key,
        groupId: group.id,
        groupLabel: group.label,
        label: SF_SLOT_SHORT_LABEL[key] ?? key,
        gold: attr.gold,
        pred: attr.pred,
        state: attr.match === "ok" ? "same" : "diverge",
      });
    }
  }
  return columns;
}

// ── Plain-language divergence sentence (Layer A) ──
//
// Mechanical, not hand-written per letter: group each side's populated
// attributes into the same 5 schema groups (Identity excluded — already
// shown as matched via CUI). Different groups populated on each side means
// gold and pred disagree on what KIND of fact this is (a "structural"
// divergence — e.g. a rate vs. a dated event). Same groups populated but
// different values falls back to naming the specific attributes that
// disagree within an agreed-on shape.

export interface AttrValueChip {
  label: string;
  value: string;
}

export type PairDivergence =
  | { kind: "structural"; goldShape: string; goldChips: AttrValueChip[]; predShape: string; predChips: AttrValueChip[] }
  | { kind: "value"; shape: string; diffs: { label: string; gold: string; pred: string }[] }
  | null;

const NON_IDENTITY_GROUPS = SF_SCHEMA_GROUPS.filter((g) => g.id !== "identity");

const SHAPE_RULES: { groups: string[]; label: string }[] = [
  { groups: ["count", "cadence"], label: "a rate" },
  { groups: ["count", "temporal"], label: "a dated count" },
  { groups: ["temporal"], label: "a dated event" },
  { groups: ["count"], label: "a count" },
  { groups: ["cadence"], label: "a change in frequency" },
  { groups: ["demographics"], label: "a demographic detail" },
];

function shapeLabel(groupIds: Set<string>): string {
  for (const rule of SHAPE_RULES) {
    if (rule.groups.length === groupIds.size && rule.groups.every((g) => groupIds.has(g))) {
      return rule.label;
    }
  }
  if (groupIds.size === 0) return "a bare mention";
  return NON_IDENTITY_GROUPS.filter((g) => groupIds.has(g.id))
    .map((g) => g.label.toLowerCase())
    .join(" + ");
}

function sideChips(byKey: Map<string, SfAttributeRow>, groupIds: Set<string>, side: "gold" | "pred"): AttrValueChip[] {
  const chips: AttrValueChip[] = [];
  for (const group of NON_IDENTITY_GROUPS) {
    if (!groupIds.has(group.id)) continue;
    for (const key of group.keys) {
      const value = byKey.get(key)?.[side];
      if (value) chips.push({ label: SF_SLOT_SHORT_LABEL[key] ?? key, value });
    }
  }
  return chips;
}

export function describePairDivergence(pair: SfLayerAPair): PairDivergence {
  if (pair.side !== "pair") return null;
  const byKey = new Map(pair.attributes.map((a) => [a.key, a]));

  const goldGroups = new Set<string>();
  const predGroups = new Set<string>();
  for (const group of NON_IDENTITY_GROUPS) {
    for (const key of group.keys) {
      const attr = byKey.get(key);
      if (!attr) continue;
      if (attr.gold) goldGroups.add(group.id);
      if (attr.pred) predGroups.add(group.id);
    }
  }

  const sameGroups = goldGroups.size === predGroups.size && [...goldGroups].every((g) => predGroups.has(g));

  if (!sameGroups && (goldGroups.size > 0 || predGroups.size > 0)) {
    return {
      kind: "structural",
      goldShape: shapeLabel(goldGroups),
      goldChips: sideChips(byKey, goldGroups, "gold"),
      predShape: shapeLabel(predGroups),
      predChips: sideChips(byKey, predGroups, "pred"),
    };
  }

  const diffs = pair.attributes
    .filter((a) => a.key !== "CUIPhrase" && a.key !== "CUI" && a.match === "bad")
    .map((a) => ({ label: SF_SLOT_SHORT_LABEL[a.key] ?? a.key, gold: a.gold, pred: a.pred }));
  if (diffs.length === 0) return null;

  return { kind: "value", shape: shapeLabel(goldGroups), diffs };
}
