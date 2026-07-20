import type { ClinicalSupportVerdict, SemanticSupportReviewPacket } from "@/lib/types";

type SelectedConclusion = SemanticSupportReviewPacket["selected_conclusion"];

export interface PresentedConclusionField {
  label: string;
  value: string;
}

export interface StructuredConclusionFields {
  headline: PresentedConclusionField | null;
  metadata: PresentedConclusionField[];
}

const ATTRIBUTE_LABELS: Record<string, string> = {
  CT_Performed: "Performed",
  CT_Results: "Result",
  CUI: "Clinical code",
  CUIPhrase: "Standard concept",
};

function readableLabel(key: string): string {
  if (ATTRIBUTE_LABELS[key]) return ATTRIBUTE_LABELS[key];
  const words = key.replace(/_/g, " ").replace(/([a-z])([A-Z])/g, "$1 $2");
  return words.charAt(0).toUpperCase() + words.slice(1).toLowerCase();
}

function displayValue(value: unknown): string {
  if (Array.isArray(value)) return value.map(String).join(", ");
  if (value && typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export function presentConclusionFields(conclusion: SelectedConclusion): PresentedConclusionField[] {
  const attributes = conclusion.attributes ?? {};
  const hasInvestigationShape = "CT_Performed" in attributes || "CT_Results" in attributes;
  const fields: PresentedConclusionField[] = [];
  const finding = conclusion.text || conclusion.normalized_concept;

  if (finding) {
    fields.push({ label: hasInvestigationShape ? "Investigation" : "Finding", value: finding });
  }

  for (const [key, value] of Object.entries(attributes)) {
    if (value === null || value === undefined || key === "CUI" || key === "CUIPhrase") continue;
    fields.push({ label: readableLabel(key), value: displayValue(value) });
  }

  const cui = attributes.CUI ?? conclusion.normalized_concept;
  const cuiPhrase = attributes.CUIPhrase;
  if (cuiPhrase && cui) {
    fields.push({ label: "Standard concept", value: `${displayValue(cuiPhrase)} (${displayValue(cui)})` });
  } else if (cuiPhrase) {
    fields.push({ label: "Standard concept", value: displayValue(cuiPhrase) });
  } else if (cui && cui !== finding) {
    fields.push({ label: "Clinical code", value: displayValue(cui) });
  }

  fields.push({
    label: "Assertion and time",
    value: conclusion.assertion ? conclusion.assertion : "Not specified",
  });
  return fields;
}

export function clinicalSupportFromShortcut(key: string): ClinicalSupportVerdict | null {
  const shortcuts: Record<string, ClinicalSupportVerdict> = {
    s: "supported",
    d: "unsupported",
    a: "unclear",
  };
  return shortcuts[key.toLowerCase()] ?? null;
}

export function structureConclusionFields(
  fields: PresentedConclusionField[]
): StructuredConclusionFields {
  const [headline = null, ...metadata] = fields;
  return { headline, metadata };
}

export function shouldSaveReviewShortcut(key: string, targetTagName?: string): boolean {
  return key === "Enter" && !["INPUT", "SELECT"].includes(targetTagName ?? "");
}
