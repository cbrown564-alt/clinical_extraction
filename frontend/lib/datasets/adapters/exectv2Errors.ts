/**
 * ExECTv2 error adapter.
 *
 * Derives mention-level residual error rows from a run by matching gold and
 * predicted mentions within each family. This is the data source for the
 * ExECTv2 Error Gallery and feeds the aggregate family-weakness drill-down. It
 * works purely off the run's letters — no offsets required — using exact-quote
 * and CUI-aware matching.
 */

import type { Exectv2LetterRecord, Exectv2Mention, Exectv2RunSummary } from "../../types";

export type Exectv2ErrorClassId =
  | "false_positive"
  | "false_negative"
  | "attribute_mismatch"
  | "evidence_invalid";

export interface Exectv2ErrorRow {
  id: string;
  runId: string;
  letterId: string;
  split: string;
  family: string;
  errorClass: Exectv2ErrorClassId;
  goldText: string | null;
  predictedText: string | null;
  evidence: string;
  evidenceValid: boolean;
  componentOwner: string;
  sourceLane: string;
  /** Human-readable explanation, e.g. "CUI C0014547 → C0014548". */
  detail: string;
}

export interface Exectv2ErrorSummary {
  total: number;
  byClass: Record<Exectv2ErrorClassId, number>;
  byFamily: Record<string, number>;
}

function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function cuiOf(mention: Exectv2Mention): string | null {
  const cui = mention.attributes?.CUI;
  return cui ? String(cui).trim() : null;
}

/** Two mentions refer to the same finding when their text or CUI agree. */
function mentionsMatch(gold: Exectv2Mention, predicted: Exectv2Mention): boolean {
  const goldText = normalizeText(gold.text);
  const predText = normalizeText(predicted.text);
  if (goldText && goldText === predText) return true;
  const goldCui = cuiOf(gold);
  const predCui = cuiOf(predicted);
  return Boolean(goldCui && predCui && goldCui === predCui);
}

/** Builds a short description of how a matched pair's key attributes differ. */
function describeAttributeMismatch(
  gold: Exectv2Mention,
  predicted: Exectv2Mention
): string | null {
  const diffs: string[] = [];
  const goldCui = cuiOf(gold);
  const predCui = cuiOf(predicted);
  if (goldCui && predCui && goldCui !== predCui) {
    diffs.push(`CUI ${goldCui} → ${predCui}`);
  }
  const goldAssert = (gold.attributes?.Negation || gold.assertion || "").trim();
  const predAssert = (predicted.attributes?.Negation || predicted.assertion || "").trim();
  if (goldAssert && predAssert && goldAssert !== predAssert) {
    diffs.push(`assertion ${goldAssert} → ${predAssert}`);
  }
  return diffs.length > 0 ? diffs.join("; ") : null;
}

function familiesIn(letter: Exectv2LetterRecord): string[] {
  const set = new Set<string>();
  for (const m of letter.gold_mentions) set.add(m.entity);
  for (const m of letter.predicted_mentions) set.add(m.entity);
  return Array.from(set);
}

/** Derives all error rows for a single letter. */
export function deriveLetterErrors(
  runId: string,
  letter: Exectv2LetterRecord
): Exectv2ErrorRow[] {
  const rows: Exectv2ErrorRow[] = [];

  for (const family of familiesIn(letter)) {
    const gold = letter.gold_mentions.filter((m) => m.entity === family);
    const predicted = letter.predicted_mentions.filter((m) => m.entity === family);
    const usedGold = new Set<number>();

    predicted.forEach((pred, pi) => {
      const goldIdx = gold.findIndex((g, gi) => !usedGold.has(gi) && mentionsMatch(g, pred));
      if (goldIdx === -1) {
        rows.push({
          id: `${runId}:${letter.letter_id}:${family}:fp:${pi}`,
          runId,
          letterId: letter.letter_id,
          split: letter.stage || letter.split,
          family,
          errorClass: "false_positive",
          goldText: null,
          predictedText: pred.text,
          evidence: pred.evidence,
          evidenceValid: pred.evidence_valid,
          componentOwner: pred.component_owner,
          sourceLane: pred.source_lane,
          detail: "No matching gold mention",
        });
        return;
      }

      usedGold.add(goldIdx);
      const goldMention = gold[goldIdx];

      if (!pred.evidence_valid) {
        rows.push({
          id: `${runId}:${letter.letter_id}:${family}:ev:${pi}`,
          runId,
          letterId: letter.letter_id,
          split: letter.stage || letter.split,
          family,
          errorClass: "evidence_invalid",
          goldText: goldMention.text,
          predictedText: pred.text,
          evidence: pred.evidence,
          evidenceValid: false,
          componentOwner: pred.component_owner,
          sourceLane: pred.source_lane,
          detail: "Evidence quote is not an exact source match",
        });
        return;
      }

      const attrDiff = describeAttributeMismatch(goldMention, pred);
      if (attrDiff) {
        rows.push({
          id: `${runId}:${letter.letter_id}:${family}:attr:${pi}`,
          runId,
          letterId: letter.letter_id,
          split: letter.stage || letter.split,
          family,
          errorClass: "attribute_mismatch",
          goldText: goldMention.text,
          predictedText: pred.text,
          evidence: pred.evidence,
          evidenceValid: pred.evidence_valid,
          componentOwner: pred.component_owner,
          sourceLane: pred.source_lane,
          detail: attrDiff,
        });
      }
    });

    gold.forEach((goldMention, gi) => {
      if (usedGold.has(gi)) return;
      rows.push({
        id: `${runId}:${letter.letter_id}:${family}:fn:${gi}`,
        runId,
        letterId: letter.letter_id,
        split: letter.stage || letter.split,
        family,
        errorClass: "false_negative",
        goldText: goldMention.text,
        predictedText: null,
        evidence: goldMention.evidence,
        evidenceValid: goldMention.evidence_valid,
        componentOwner: "",
        sourceLane: "",
        detail: "Gold mention not predicted",
      });
    });
  }

  return rows;
}

/** Derives error rows for every letter in a run. */
export function deriveRunErrors(run: Exectv2RunSummary): Exectv2ErrorRow[] {
  return run.letters.flatMap((letter) => deriveLetterErrors(run.run_id, letter));
}

const EMPTY_CLASS_COUNTS: Record<Exectv2ErrorClassId, number> = {
  false_positive: 0,
  false_negative: 0,
  attribute_mismatch: 0,
  evidence_invalid: 0,
};

export function summarizeErrors(rows: Exectv2ErrorRow[]): Exectv2ErrorSummary {
  const byClass: Record<Exectv2ErrorClassId, number> = { ...EMPTY_CLASS_COUNTS };
  const byFamily: Record<string, number> = {};
  for (const row of rows) {
    byClass[row.errorClass] += 1;
    byFamily[row.family] = (byFamily[row.family] ?? 0) + 1;
  }
  return { total: rows.length, byClass, byFamily };
}
