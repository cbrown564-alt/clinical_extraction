/**
 * ExECTv2 component adapter.
 *
 * Summarises the prediction-bearing components of a run from the provenance
 * carried on each predicted mention (`component_owner`, `source_lane`). This is
 * the data source for the ExECTv2 Component Impact surface: it reports how much
 * each producer lane / dictionary / lens / assembler / verifier contributes,
 * which families it touches, and how clean its evidence is. It also classifies
 * each owner into one of the dataset's component types so formatting repairs are
 * distinguished from semantic add/drop/replace actions.
 */

import type { Exectv2RunSummary } from "../../types";

export type Exectv2ComponentTypeId =
  | "llm_producer"
  | "dictionary"
  | "semantic_lens"
  | "assembler"
  | "evidence_validation"
  | "deterministic_projection"
  | "scorer";

export interface Exectv2ComponentSummary {
  /** The raw `component_owner` provenance string. */
  owner: string;
  typeId: Exectv2ComponentTypeId;
  mentionCount: number;
  evidenceValidCount: number;
  evidenceValidRate: number;
  /** Mention count by family this component contributed to. */
  byFamily: Record<string, number>;
  /** Distinct source lanes observed under this owner. */
  lanes: string[];
  /** Whether this owner reflects a deterministic formatting/repair action. */
  deterministic: boolean;
}

/** Classifies a `component_owner` provenance string into a component type. */
export function classifyComponentOwner(owner: string): Exectv2ComponentTypeId {
  const o = owner.toLowerCase();
  if (o.includes("verifier")) return "evidence_validation";
  if (o.includes("arbitration") || o.includes("union") || o.includes("merge")) {
    return "assembler";
  }
  if (o.includes("projection") || o.includes("format") || o.includes("repair")) {
    return "deterministic_projection";
  }
  if (o.includes("dictionary") || o.includes("alias")) {
    return "dictionary";
  }
  if (o.includes("recovery") || o.includes("residual") || o.includes("reconciler")) {
    return "semantic_lens";
  }
  if (o.includes("route") || o.includes("llm") || o.includes("producer")) {
    return "llm_producer";
  }
  return "semantic_lens";
}

function isDeterministic(owner: string): boolean {
  const o = owner.toLowerCase();
  return (
    o.includes("deterministic") ||
    o.includes("projection") ||
    o.includes("format") ||
    o.includes("repair") ||
    o.includes("dictionary")
  );
}

/**
 * Builds one summary per `component_owner` in the run. A mention whose owner is
 * a compound (`a+b`) is attributed to each constituent so combined repair lanes
 * are visible.
 */
export function summarizeComponents(run: Exectv2RunSummary): Exectv2ComponentSummary[] {
  const acc = new Map<string, Exectv2ComponentSummary>();

  for (const letter of run.letters) {
    for (const mention of letter.predicted_mentions) {
      const owners = (mention.component_owner || "unattributed")
        .split("+")
        .map((s) => s.trim())
        .filter(Boolean);
      for (const owner of owners) {
        let entry = acc.get(owner);
        if (!entry) {
          entry = {
            owner,
            typeId: classifyComponentOwner(owner),
            mentionCount: 0,
            evidenceValidCount: 0,
            evidenceValidRate: 0,
            byFamily: {},
            lanes: [],
            deterministic: isDeterministic(owner),
          };
          acc.set(owner, entry);
        }
        entry.mentionCount += 1;
        if (mention.evidence_valid) entry.evidenceValidCount += 1;
        entry.byFamily[mention.entity] = (entry.byFamily[mention.entity] ?? 0) + 1;
        if (mention.source_lane && !entry.lanes.includes(mention.source_lane)) {
          entry.lanes.push(mention.source_lane);
        }
      }
    }
  }

  const summaries = Array.from(acc.values());
  for (const entry of summaries) {
    entry.evidenceValidRate =
      entry.mentionCount > 0 ? entry.evidenceValidCount / entry.mentionCount : 0;
  }
  summaries.sort((a, b) => b.mentionCount - a.mentionCount);
  return summaries;
}

export interface FamilyDelta {
  family: string;
  baseF1: number | null;
  variantF1: number | null;
  delta: number | null;
}

/**
 * Per-family F1 delta between a baseline run and a variant run (e.g. v08 vs the
 * v09 partial hybrid), so component impact can explain where simplification
 * trades headroom.
 */
export function familyDeltas(
  base: Exectv2RunSummary,
  variant: Exectv2RunSummary,
  families: string[]
): FamilyDelta[] {
  return families.map((family) => {
    const baseF1 = base.metrics.families[family as keyof typeof base.metrics.families]?.f1 ?? null;
    const variantF1 =
      variant.metrics.families[family as keyof typeof variant.metrics.families]?.f1 ?? null;
    const delta = baseF1 !== null && variantF1 !== null ? variantF1 - baseF1 : null;
    return { family, baseF1, variantF1, delta };
  });
}
