import type {
  SfInspectionLetter,
  SfInspectionScorecard,
  SfLayerBComponent,
  SfLineageOverrideItem,
  SfMentionRow,
} from "@/lib/types";

/**
 * The 11 FrequencyStateScores are not 11 peers — they're three families,
 * each a root lens plus child lenses that refine or filter the same
 * underlying mentions. This is the single source of truth for that
 * grouping, derived from the backend's own COMPONENT_ORDER + info strings
 * (see SfInspectionViews.tsx's COMPONENT_ORDER comment).
 */
export interface SfFamily {
  id: "headline" | "change" | "bench";
  label: string;
  accent: string;
  blurb: string;
  root: string;
  children: string[];
}

export const SF_FAMILIES: SfFamily[] = [
  {
    id: "headline",
    label: "Headline state",
    accent: "var(--color-deterministic)",
    blurb:
      "Convention-strict 3-way state (active-rate / seizure-free / unknown). Rules-owned — the deterministic SeizureFrequencyDictionaryLens fills every key here.",
    root: "clinical_headline",
    children: ["active_rate", "active_rate_fidelity", "seizure_free", "unknown"],
  },
  {
    id: "change",
    label: "Change state",
    accent: "var(--color-hybrid)",
    blurb:
      "4-way presence (seizure-free / active-rate / changed / unknown). Where FrequencyChange lives — and where an LLM magnitude-complement override can rewrite the deterministic read.",
    root: "state_profile",
    children: ["state_profile_directional", "state_profile_direction_deconf", "state_profile_magnitude"],
  },
  {
    id: "bench",
    label: "Strict benchmark",
    accent: "var(--color-muted)",
    blurb:
      "Full-attribute exact match. Legacy comparator, not part of the scored convention — low F1 is expected by construction. Worth opening only when the two families above also disagree.",
    root: "exact_semantic",
    children: ["benchmark_with_cui"],
  },
];

export function familyMembers(family: SfFamily): string[] {
  return [family.root, ...family.children];
}

/** component name -> owning family */
export function familyOf(componentName: string): SfFamily | undefined {
  return SF_FAMILIES.find((f) => familyMembers(f).includes(componentName));
}

export interface FamilyStatus {
  tp: number;
  fp: number;
  fn: number;
  clean: boolean;
  hasMentions: boolean;
}

/** Root-lens tp/fp/fn for one family on one letter — what the matrix cell shows. */
export function familyRootStatus(letter: SfInspectionLetter, family: SfFamily): FamilyStatus {
  const comp = letter.layer_b.components.find((c) => c.name === family.root);
  const tp = comp?.tp ?? 0;
  const fp = comp?.fp ?? 0;
  const fn = comp?.fn ?? 0;
  return { tp, fp, fn, clean: fp === 0 && fn === 0, hasMentions: comp ? comp.rows.length > 0 : false };
}

/**
 * Triage-facing family status: prefer the root lens, but if only a child is
 * dirty (e.g. active_rate_fidelity while clinical_headline is clean), surface
 * that child's fp/fn so the list doesn't contradict letterVerdict.
 */
export function familyTriageStatus(letter: SfInspectionLetter, family: SfFamily): FamilyStatus {
  const root = familyRootStatus(letter, family);
  if (root.fp + root.fn > 0 || !familyHasAnyError(letter, family)) return root;
  const primary = primaryErrorComponent(letter, family);
  if (!primary) return root;
  return {
    tp: primary.tp,
    fp: primary.fp,
    fn: primary.fn,
    clean: false,
    hasMentions: primary.rows.length > 0 || root.hasMentions,
  };
}

/** Whether ANY component in the family (root or child) has an error, for the family-tree rollup line. */
export function familyHasAnyError(letter: SfInspectionLetter, family: SfFamily): boolean {
  const members = new Set(familyMembers(family));
  return letter.layer_b.components.some((c) => members.has(c.name) && c.has_error);
}

export type CellSeverity = "clean" | "err1" | "err2" | "na";

/** 0 -> clean, 1-2 -> err1 (light), 3+ -> err2 (saturated), no mentions -> na. */
export function cellSeverity(status: Pick<FamilyStatus, "fp" | "fn">, letterHasActivity: boolean): CellSeverity {
  if (!letterHasActivity) return "na";
  const total = status.fp + status.fn;
  if (total === 0) return "clean";
  if (total <= 2) return "err1";
  return "err2";
}

export function rootF1(scorecard: SfInspectionScorecard, family: SfFamily) {
  return scorecard[family.root];
}

/**
 * The specific lens inside a family that's actually disagreeing — root first,
 * else the first erroring child. Naming one component (not summing the
 * family) avoids re-inflating the count across correlated child lenses.
 */
export function primaryErrorComponent(letter: SfInspectionLetter, family: SfFamily): SfLayerBComponent | null {
  const byName = new Map(letter.layer_b.components.map((c) => [c.name, c]));
  const root = byName.get(family.root);
  if (root?.has_error) return root;
  for (const childName of family.children) {
    const child = byName.get(childName);
    if (child?.has_error) return child;
  }
  return null;
}

export type VerdictSeverity = "no-activity" | "clean" | "change-only" | "headline";

export interface LetterVerdict {
  severity: VerdictSeverity;
  headlineErr: boolean;
  changeErr: boolean;
  benchErr: boolean;
  /** Family to auto-open in the Layer B tree; null when there's nothing actionable. */
  primaryFamilyId: SfFamily["id"] | null;
  primaryComponent: SfLayerBComponent | null;
}

/**
 * One-glance read on a letter: is there a genuine disagreement, and if so,
 * which family and which specific lens. Headline-state errors outrank
 * change-state errors (a wrong entity/state is a bigger deal than a right
 * state with the wrong direction); strict-benchmark is tracked but never
 * drives the verdict since it's expected to disagree by construction.
 */
export function letterVerdict(letter: SfInspectionLetter): LetterVerdict {
  if (!letter.has_activity) {
    return { severity: "no-activity", headlineErr: false, changeErr: false, benchErr: false, primaryFamilyId: null, primaryComponent: null };
  }
  const headline = SF_FAMILIES.find((f) => f.id === "headline")!;
  const change = SF_FAMILIES.find((f) => f.id === "change")!;
  const bench = SF_FAMILIES.find((f) => f.id === "bench")!;
  const headlineErr = familyHasAnyError(letter, headline);
  const changeErr = familyHasAnyError(letter, change);
  const benchErr = familyHasAnyError(letter, bench);

  if (headlineErr) {
    return { severity: "headline", headlineErr, changeErr, benchErr, primaryFamilyId: "headline", primaryComponent: primaryErrorComponent(letter, headline) };
  }
  if (changeErr) {
    return { severity: "change-only", headlineErr, changeErr, benchErr, primaryFamilyId: "change", primaryComponent: primaryErrorComponent(letter, change) };
  }
  return { severity: "clean", headlineErr, changeErr, benchErr, primaryFamilyId: null, primaryComponent: null };
}

/**
 * Triage filters for the overview letter list. "Actionable" is the default:
 * Headline or Change disagrees. Bench-only stays out of that bucket so the
 * matrix doesn't drown in expected exact-match noise.
 */
export type LetterTriageFilter =
  | "actionable"
  | "headline"
  | "change"
  | "bench"
  | "clean"
  | "all";

export const LETTER_TRIAGE_FILTERS: { id: LetterTriageFilter; label: string; hint: string }[] = [
  { id: "actionable", label: "Actionable", hint: "Headline or Change disagrees" },
  { id: "headline", label: "Headline", hint: "Headline-state family error" },
  { id: "change", label: "Change", hint: "Change-state family error" },
  { id: "bench", label: "Bench only", hint: "Strict-benchmark disagrees, scored families clean" },
  { id: "clean", label: "Clean", hint: "Headline and Change both clean" },
  { id: "all", label: "All", hint: "Every letter, original order" },
];

export function letterMatchesTriageFilter(letter: SfInspectionLetter, filter: LetterTriageFilter): boolean {
  if (filter === "all") return true;
  const v = letterVerdict(letter);
  switch (filter) {
    case "actionable":
      return v.severity === "headline" || v.severity === "change-only";
    case "headline":
      return v.severity === "headline";
    case "change":
      return v.changeErr;
    case "bench":
      return v.severity === "clean" && v.benchErr;
    case "clean":
      return v.severity === "clean" && !v.benchErr;
    default:
      return true;
  }
}

/** Headline errors first, then change-only, bench-only, clean, then inactive. */
export function triageRank(letter: SfInspectionLetter): number {
  const v = letterVerdict(letter);
  if (v.severity === "headline") return 0;
  if (v.severity === "change-only") return 1;
  if (v.severity === "clean" && v.benchErr) return 2;
  if (v.severity === "clean") return 3;
  return 4;
}

export function sortLettersForTriage(letters: SfInspectionLetter[]): SfInspectionLetter[] {
  return [...letters].sort((a, b) => {
    const d = triageRank(a) - triageRank(b);
    if (d !== 0) return d;
    return a.letter_id.localeCompare(b.letter_id);
  });
}

export function countLettersByTriage(letters: SfInspectionLetter[]): Record<LetterTriageFilter, number> {
  const counts: Record<LetterTriageFilter, number> = {
    actionable: 0,
    headline: 0,
    change: 0,
    bench: 0,
    clean: 0,
    all: letters.length,
  };
  for (const letter of letters) {
    for (const f of LETTER_TRIAGE_FILTERS) {
      if (f.id === "all") continue;
      if (letterMatchesTriageFilter(letter, f.id)) counts[f.id] += 1;
    }
  }
  return counts;
}

export function neighborLetterIds(
  letters: SfInspectionLetter[],
  selectedId: string | null
): { prevId: string | null; nextId: string | null; index: number } {
  if (!selectedId || letters.length === 0) return { prevId: null, nextId: null, index: -1 };
  const index = letters.findIndex((l) => l.letter_id === selectedId);
  if (index < 0) return { prevId: null, nextId: null, index: -1 };
  return {
    prevId: index > 0 ? letters[index - 1].letter_id : null,
    nextId: index < letters.length - 1 ? letters[index + 1].letter_id : null,
    index,
  };
}

/**
 * Which Layer B lenses register the given phrase(s) as an FP/FN — the
 * "consequence" of a Layer A attribute mismatch, so a disagreeing pair can
 * be tagged with what it actually breaks instead of leaving the reader to
 * cross-reference Layer A and Layer B by hand.
 */
export interface PhraseConsequence {
  component: string;
  status: "fp" | "fn";
  familyId: SfFamily["id"];
}

export function phraseConsequences(letter: SfInspectionLetter, phrases: string[]): PhraseConsequence[] {
  const targets = new Set(phrases.map((p) => p.trim().toLowerCase()).filter(Boolean));
  if (!targets.size) return [];
  const results: PhraseConsequence[] = [];
  for (const comp of letter.layer_b.components) {
    const family = familyOf(comp.name);
    if (!family) continue;
    const hit = comp.rows.find(
      (r) => (r.status === "fp" || r.status === "fn") && targets.has(r.phrase.trim().toLowerCase())
    );
    if (hit) results.push({ component: comp.name, status: hit.status as "fp" | "fn", familyId: family.id });
  }
  return results;
}

/**
 * Pairs a component's raw gold/pred mention rows into flows for the flow
 * chart: a matched TP pair, a phrase-linked FN/FP pair (same underlying
 * mention, disagreeing projection — e.g. "seizure" vs "seizures" landing on
 * different direction states), a gold-only miss, a pred-only extra, or a
 * filtered-out skip. This is a display-only heuristic layered on top of the
 * scorer's actual key-based TP/FP/FN verdicts, not a re-scoring — the
 * "linked" pairing only fires on an exact normalized-phrase match, so it
 * either finds an unambiguous link or falls back to two single-sided flows.
 */
export type MentionFlowKind = "matched" | "linked" | "miss" | "extra" | "skip";

export interface MentionFlow {
  kind: MentionFlowKind;
  gold?: SfMentionRow;
  pred?: SfMentionRow;
}

function normPhrase(s: string): string {
  return s
    .toLowerCase()
    .replace(/-/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/s$/, "");
}

export function buildMentionFlows(rows: SfMentionRow[]): MentionFlow[] {
  const golds = rows.filter((r) => r.side === "gold" && r.status !== "skip");
  const preds = rows.filter((r) => r.side === "pred" && r.status !== "skip");
  const skips = rows.filter((r) => r.status === "skip");
  const usedGold = new Set<number>();
  const usedPred = new Set<number>();

  const matched: MentionFlow[] = [];
  golds.forEach((g, gi) => {
    if (g.status !== "tp") return;
    const pi = preds.findIndex((p, i) => !usedPred.has(i) && p.status === "tp" && p.key === g.key);
    if (pi >= 0) {
      usedGold.add(gi);
      usedPred.add(pi);
      matched.push({ kind: "matched", gold: g, pred: preds[pi] });
    }
  });

  const linked: MentionFlow[] = [];
  golds.forEach((g, gi) => {
    if (usedGold.has(gi) || g.status !== "fn") return;
    const gp = normPhrase(g.phrase);
    const pi = preds.findIndex((p, i) => !usedPred.has(i) && p.status === "fp" && normPhrase(p.phrase) === gp);
    if (pi >= 0) {
      usedGold.add(gi);
      usedPred.add(pi);
      linked.push({ kind: "linked", gold: g, pred: preds[pi] });
    }
  });

  const miss: MentionFlow[] = golds
    .map((g, gi) => (usedGold.has(gi) ? null : ({ kind: "miss", gold: g } as MentionFlow)))
    .filter((f): f is MentionFlow => !!f);
  const extra: MentionFlow[] = preds
    .map((p, pi) => (usedPred.has(pi) ? null : ({ kind: "extra", pred: p } as MentionFlow)))
    .filter((f): f is MentionFlow => !!f);
  const skip: MentionFlow[] = skips.map((s) => ({
    kind: "skip",
    gold: s.side === "gold" ? s : undefined,
    pred: s.side === "pred" ? s : undefined,
  }));

  // Interesting flows first — matched pairs collapse to one line in the UI
  // anyway, so there's no reason to make the reader scroll past them.
  return [...linked, ...miss, ...extra, ...matched, ...skip];
}

/**
 * Best-effort link from an applied lineage override to the mention rows it
 * touched. Matches an override item's `applies_to` phrase against Layer B
 * mention phrases; a hit inside an errored, non-benchmark component is
 * treated as the likely cause of that error.
 */
export interface OverrideConnection {
  item: SfLineageOverrideItem;
  component: string;
  row: SfMentionRow;
}

export function connectOverridesToErrors(
  letter: SfInspectionLetter,
  overrideItems: SfLineageOverrideItem[] | undefined
): OverrideConnection[] {
  if (!overrideItems?.length) return [];
  const connections: OverrideConnection[] = [];
  const benchMembers = new Set(familyMembers(SF_FAMILIES.find((f) => f.id === "bench")!));

  for (const item of overrideItems) {
    const target = item.applies_to.trim().toLowerCase();
    if (!target) continue;
    for (const comp of letter.layer_b.components) {
      if (!comp.has_error || benchMembers.has(comp.name)) continue;
      const row = comp.rows.find(
        (r) => (r.status === "fp" || r.status === "fn") && r.phrase.trim().toLowerCase() === target
      );
      if (row) {
        connections.push({ item, component: comp.name, row });
        break;
      }
    }
  }
  return connections;
}
