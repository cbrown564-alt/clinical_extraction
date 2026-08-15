import type { Exectv2Mention } from "./types";

export interface MentionPair {
  type: "matched";
  gold: Exectv2Mention;
  predicted: Exectv2Mention;
}
export interface UnmatchedGold {
  type: "missed_gold";
  gold: Exectv2Mention;
}
export interface UnmatchedPred {
  type: "extra_predicted";
  predicted: Exectv2Mention;
}
export type ComparisonGroup = MentionPair | UnmatchedGold | UnmatchedPred;

export function normalizeConceptString(str?: string): string {
  if (!str) return "";
  return str
    .toLowerCase()
    .replace(/[-_]+/g, " ")
    .replace(/[^\w\s]/g, "")
    .trim()
    .replace(/\s+/g, " ");
}

export function attributeValuesMatch(key: string, gold?: string, predicted?: string): boolean {
  if (gold === undefined || predicted === undefined) return false;
  if (gold === predicted) return true;
  if (gold.toLowerCase() === predicted.toLowerCase()) return true;
  if (key === "CUIPhrase") {
    return normalizeConceptString(gold) === normalizeConceptString(predicted);
  }
  return false;
}

export function mentionIdentityKeys(m: Exectv2Mention) {
  return {
    cui: m.attributes["CUI"]?.trim(),
    cuiPhrase: normalizeConceptString(m.attributes["CUIPhrase"]),
    text: normalizeConceptString(m.text),
    answer: normalizeConceptString(m.attributes["DrugName"] || m.attributes["CUIPhrase"] || m.text),
  };
}

/** Count non-empty attribute values. Used to prefer the richer of two concept twins. */
export function filledAttributeCount(m: Exectv2Mention): number {
  return Object.values(m.attributes).filter((value) => String(value ?? "").trim() !== "").length;
}

/** How many gold attributes have a matching predicted value. */
export function matchingAttributeCount(gold: Exectv2Mention, predicted: Exectv2Mention): number {
  return Object.entries(gold.attributes).filter(([key, goldValue]) =>
    attributeValuesMatch(key, goldValue, predicted.attributes[key])
  ).length;
}

/**
 * Among candidates that share CUI / CUIPhrase / answer identity, prefer the
 * mention with the most filled attributes. Ties break on gold-attribute overlap,
 * then earlier pool order.
 */
export function pickBestPredictedIndex(
  gold: Exectv2Mention,
  predPool: Exectv2Mention[],
  isCandidate: (predicted: Exectv2Mention) => boolean
): number {
  let bestIdx = -1;
  let bestFilled = -1;
  let bestOverlap = -1;

  predPool.forEach((predicted, idx) => {
    if (!isCandidate(predicted)) return;
    const filled = filledAttributeCount(predicted);
    const overlap = matchingAttributeCount(gold, predicted);
    if (
      filled > bestFilled ||
      (filled === bestFilled && overlap > bestOverlap)
    ) {
      bestFilled = filled;
      bestOverlap = overlap;
      bestIdx = idx;
    }
  });

  return bestIdx;
}

/**
 * Alignment matching logic between gold and predicted mentions for a family.
 * Computes exact/semantic true positives (paired), false negatives (gold misses),
 * and false positives (extra predictions / duplicates).
 *
 * When several predictions share the same CUI, CUIPhrase, and answer, the
 * richest mention (most filled attributes) is paired with gold.
 */
export function alignFamilyMentions(
  gold: Exectv2Mention[],
  predicted: Exectv2Mention[]
): ComparisonGroup[] {
  const goldPool = [...gold];
  const predPool = [...predicted];
  const groups: ComparisonGroup[] = [];

  const takeMatch = (goldIdx: number, predIdx: number) => {
    const [matchedPred] = predPool.splice(predIdx, 1);
    const [matchedGold] = goldPool.splice(goldIdx, 1);
    groups.push({
      type: "matched",
      gold: matchedGold,
      predicted: matchedPred,
    });
  };

  // 1. Match by CUI (exact UMLS concept match)
  for (let i = goldPool.length - 1; i >= 0; i--) {
    const g = goldPool[i];
    const gKeys = mentionIdentityKeys(g);
    if (!gKeys.cui) continue;

    const predIdx = pickBestPredictedIndex(g, predPool, (p) => {
      const pKeys = mentionIdentityKeys(p);
      return Boolean(pKeys.cui && pKeys.cui === gKeys.cui);
    });

    if (predIdx !== -1) takeMatch(i, predIdx);
  }

  // 2. Match by CUIPhrase or Normalized Text exact match
  for (let i = goldPool.length - 1; i >= 0; i--) {
    const g = goldPool[i];
    const gKeys = mentionIdentityKeys(g);

    const predIdx = pickBestPredictedIndex(g, predPool, (p) => {
      const pKeys = mentionIdentityKeys(p);
      if (gKeys.cuiPhrase && pKeys.cuiPhrase && gKeys.cuiPhrase === pKeys.cuiPhrase) return true;
      if (gKeys.text && pKeys.text && gKeys.text === pKeys.text) return true;
      if (gKeys.cuiPhrase && pKeys.text && gKeys.cuiPhrase === pKeys.text) return true;
      if (gKeys.text && pKeys.cuiPhrase && gKeys.text === pKeys.cuiPhrase) return true;
      return false;
    });

    if (predIdx !== -1) takeMatch(i, predIdx);
  }

  // 3. Partial/Fuzzy overlap match on remaining
  for (let i = goldPool.length - 1; i >= 0; i--) {
    const g = goldPool[i];
    const gKeys = mentionIdentityKeys(g);
    const gTarget = gKeys.cuiPhrase || gKeys.text;

    const predIdx = pickBestPredictedIndex(g, predPool, (p) => {
      const pKeys = mentionIdentityKeys(p);
      const pTarget = pKeys.cuiPhrase || pKeys.text;
      if (!gTarget || !pTarget || gTarget.length < 4 || pTarget.length < 4) return false;
      return pTarget.includes(gTarget) || gTarget.includes(pTarget);
    });

    if (predIdx !== -1) takeMatch(i, predIdx);
  }

  for (const leftoverGold of goldPool) {
    groups.push({ type: "missed_gold", gold: leftoverGold });
  }

  for (const leftoverPred of predPool) {
    groups.push({ type: "extra_predicted", predicted: leftoverPred });
  }

  return groups;
}
