import { EXECTV2_FAMILIES } from "./datasets/exectv2";
import {
  ASSEMBLY_BANDS,
  type AssemblyBand,
  type PredictedFactData,
} from "./assemblyLineTypes";

export type AssemblyHighlightTone =
  | "deterministic"
  | "deterministic-alt"
  | "llm"
  | "hybrid"
  | "success"
  | "no-reference";

export function clickableFacts(facts: PredictedFactData[]): PredictedFactData[] {
  return facts.filter((fact) => fact.span !== null && fact.span.end > fact.span.start);
}

export function factById(
  facts: PredictedFactData[],
  factId: string | null
): PredictedFactData | undefined {
  if (!factId) return undefined;
  return facts.find((fact) => fact.fact_id === factId);
}

export function bandHasSteps(fact: PredictedFactData | undefined, band: AssemblyBand): boolean {
  if (!fact) return false;
  return fact.transforms.some((step) => step.band === band);
}

export function stepsForBand(fact: PredictedFactData, band: AssemblyBand) {
  return fact.transforms.filter((step) => step.band === band);
}

export function bandIdsTouched(fact: PredictedFactData | undefined): AssemblyBand[] {
  return ASSEMBLY_BANDS.map((band) => band.id).filter((band) => bandHasSteps(fact, band));
}

const EMPTY_IN = new Set(["", "(none)", "(letter)"]);

export function isEmptyPayload(raw: string): boolean {
  return EMPTY_IN.has(raw.trim());
}

export function displayPayload(raw: string): string {
  const text = raw.trim();
  if (text === "(none)" || text === "") return "";
  if (text === "(letter)") return "(letter)";
  try {
    return JSON.stringify(JSON.parse(text), null, 2);
  } catch {
    return text;
  }
}

export function sameOutgoing(previous: string | undefined, current: string): boolean {
  if (previous === undefined) return false;
  const left = displayPayload(previous);
  const right = displayPayload(current);
  return left.length > 0 && left === right;
}

export type StationFactView =
  | {
      kind: "structured";
      family: string;
      phrase: string;
      attributes: Record<string, string>;
      evidence: string;
      confidence: string;
      rationale: string;
    }
  | { kind: "prose"; text: string };

function asRecord(value: unknown): Record<string, unknown> | null {
  if (value !== null && typeof value === "object" && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  return null;
}

function stringMap(value: unknown): Record<string, string> {
  const record = asRecord(value);
  if (!record) return {};
  const out: Record<string, string> = {};
  for (const [key, item] of Object.entries(record)) {
    if (item == null || item === "") continue;
    if (typeof item === "object") continue;
    out[key] = String(item);
  }
  return out;
}

function entityFromFamily(family: string): string {
  switch (family) {
    case "diagnosis":
      return "Diagnosis";
    case "medication":
      return "Prescription";
    case "seizure_frequency":
      return "SeizureFrequency";
    case "investigation":
      return "Investigations";
    case "Diagnosis":
    case "Prescription":
    case "SeizureFrequency":
    case "Investigations":
      return family;
    default:
      return family;
  }
}

export function parseStationFact(raw: string): StationFactView {
  const text = raw.trim();
  if (isEmptyPayload(text)) {
    return { kind: "prose", text: "" };
  }
  try {
    const data = asRecord(JSON.parse(text));
    if (!data) {
      return { kind: "prose", text };
    }
    const mentions = Array.isArray(data.mentions) ? data.mentions : [];
    const firstMention = mentions.length > 0 ? asRecord(mentions[0]) : null;
    const mentionAttrs = firstMention ? stringMap(firstMention.attributes) : {};
    const attributes =
      Object.keys(mentionAttrs).length > 0 ? mentionAttrs : stringMap(data.attributes);
    const entity = String(data.entity ?? firstMention?.entity ?? "");
    const family = entityFromFamily(entity || String(data.family ?? ""));
    const phrase = String(
      data.text ?? data.fact ?? data.anchor_text ?? firstMention?.text ?? data.label ?? ""
    ).trim();
    const evidence = String(data.evidence ?? "").trim();
    if (!phrase && Object.keys(attributes).length === 0) {
      return { kind: "prose", text: displayPayload(text) };
    }
    return {
      kind: "structured",
      family,
      phrase: phrase || family,
      attributes,
      evidence,
      confidence: String(data.confidence ?? ""),
      rationale: String(data.rationale ?? ""),
    };
  } catch {
    return { kind: "prose", text };
  }
}

export function isShapeCompareStage(stageId: string): boolean {
  const tail = stageId.split(".").pop() ?? "";
  return tail === "flatten_events" || stageId.includes(".lens.");
}

function isAssemblyHighlightTone(tone: string): tone is AssemblyHighlightTone {
  switch (tone) {
    case "deterministic":
    case "deterministic-alt":
    case "llm":
    case "hybrid":
    case "success":
    case "no-reference":
      return true;
    default:
      return false;
  }
}

export function highlightToneForFact(fact: PredictedFactData): AssemblyHighlightTone {
  const prefix = fact.fact_id.split(":")[0] ?? "";
  const fromId = EXECTV2_FAMILIES.find((family) => family.id === prefix);
  if (fromId && isAssemblyHighlightTone(fromId.tone)) {
    return fromId.tone;
  }
  const first = fact.transforms[0]?.left;
  if (first) {
    const view = parseStationFact(first);
    if (view.kind === "structured") {
      const fromPayload = EXECTV2_FAMILIES.find((family) => family.id === view.family);
      if (fromPayload && isAssemblyHighlightTone(fromPayload.tone)) {
        return fromPayload.tone;
      }
    }
  }
  return "deterministic";
}

export function hasMentionList(raw: string): boolean {
  try {
    const parsed: unknown = JSON.parse(raw);
    if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed)) {
      return false;
    }
    return Array.isArray((parsed as { mentions?: unknown }).mentions);
  } catch {
    return false;
  }
}
