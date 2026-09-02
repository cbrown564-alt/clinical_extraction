import type { FamilyHighlightSpan } from "./letterHighlights";

export const GAN_INVENTORY_VIEW = "inventory";
export const WORKBENCH_VIEW_PARAM = "view";

export type GanInventoryFamily =
  | "Diagnosis"
  | "Prescription"
  | "Investigations"
  | "SeizureFrequency";

/** Inventory workbench omits SeizureFrequency; Gan already owns that label. */
export const INVENTORY_DISPLAY_FAMILIES = [
  "Diagnosis",
  "Prescription",
  "Investigations",
] as const satisfies readonly GanInventoryFamily[];

export type GanInventoryDisplayFamily = (typeof INVENTORY_DISPLAY_FAMILIES)[number];

export function isInventoryDisplayFamily(
  entity: string
): entity is GanInventoryDisplayFamily {
  return (INVENTORY_DISPLAY_FAMILIES as readonly string[]).includes(entity);
}

export type GanInventoryMention = {
  entity: GanInventoryFamily | string;
  text: string;
  subtype: string;
  attributes: Record<string, string>;
  evidence: string;
};

export type GanInventoryLetter = {
  source_row_index: number;
  mentions: GanInventoryMention[];
};

export type GanInventoryPanel = {
  schema_version: string;
  study: string;
  split: "dev750";
  sample_size: number;
  sample_seed: number;
  selected_source_row_indices: number[];
  illustration_source_row_indices: number[];
  program_entry: string;
  program_config: string;
  scorer: null;
  claim_boundary: string;
  family_summaries: Record<string, unknown>;
  letters: GanInventoryLetter[];
};

export function isGanInventoryView(raw: string | null | undefined): boolean {
  return raw === GAN_INVENTORY_VIEW;
}

export function resolveInventoryRow(
  current: number | null,
  sampled: readonly number[],
  fallback: number
): number {
  if (current !== null && sampled.includes(current)) return current;
  if (sampled.includes(fallback)) return fallback;
  return sampled[0] ?? fallback;
}

export type CompactInventoryFact = {
  identity: string;
  clinical: string | null;
  evidence: string;
};

function filled(value: string | undefined): string | null {
  const trimmed = value?.trim();
  return trimmed ? trimmed : null;
}

function seizureClinical(attributes: Record<string, string>): string | null {
  const change = filled(attributes.FrequencyChange);
  if (change) return change;
  const lower = filled(attributes.LowerNumberOfSeizures);
  const upper = filled(attributes.UpperNumberOfSeizures);
  if (lower && upper) return `${lower}–${upper}`;
  return filled(attributes.NumberOfSeizures);
}

function prescriptionFrequency(value: string): string {
  return /^\d+$/.test(value)
    ? `${value} ${value === "1" ? "dose" : "doses"}`
    : value;
}

function prescriptionClinical(attributes: Record<string, string>): string | null {
  const dose = filled(attributes.DrugDose);
  const unit = filled(attributes.DoseUnit);
  const amount = dose && unit ? `${dose}${unit}` : dose;
  const frequency = filled(attributes.Frequency);
  const parts = [
    amount,
    frequency ? prescriptionFrequency(frequency) : null,
  ].flatMap((value) => (value ? [value] : []));
  return parts.length > 0 ? parts.join(", ") : null;
}

export function compactInventoryFact(
  mention: GanInventoryMention
): CompactInventoryFact {
  const identity =
    filled(mention.attributes.CUIPhrase) ??
    filled(mention.text) ??
    filled(mention.subtype) ??
    "Blank mention";
  let clinical: string | null = null;
  if (mention.entity === "SeizureFrequency") {
    clinical = seizureClinical(mention.attributes);
  } else if (mention.entity === "Prescription") {
    clinical = prescriptionClinical(mention.attributes);
  }
  return {
    identity,
    clinical,
    evidence: filled(mention.evidence) ?? "No evidence text",
  };
}

export function inventoryEvidenceSpans(
  mentions: readonly GanInventoryMention[],
  noteText: string
): FamilyHighlightSpan[] {
  const spans: FamilyHighlightSpan[] = [];
  for (const mention of mentions) {
    const quote = mention.evidence?.trim();
    if (!quote) continue;
    const start = noteText.indexOf(quote);
    if (start < 0) continue;
    spans.push({
      start,
      end: start + quote.length,
      entity: mention.entity,
      label: mention.entity,
    });
  }
  return spans;
}
