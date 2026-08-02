import type { DatasetDescriptor, TaskFamilyDescriptor } from "./types";

/** The four ExECTv2 key-finding families, in canonical order. */
export const EXECTV2_FAMILIES: TaskFamilyDescriptor[] = [
  { id: "Diagnosis", label: "Diagnosis", shortLabel: "Dx", tone: "hybrid" },
  { id: "SeizureFrequency", label: "Seizure Frequency", shortLabel: "SF", tone: "llm" },
  { id: "Prescription", label: "Prescription", shortLabel: "Rx", tone: "success" },
  { id: "Investigations", label: "Investigations", shortLabel: "Inv", tone: "deterministic-alt" },
];

/**
 * ExECTv2 — four-family key clinical finding extraction.
 *
 * Diagnosis, SeizureFrequency, Prescription, and Investigations across epilepsy
 * letters. This descriptor owns the family/metric/component/error-class language
 * so ExECTv2 never gets coerced into Gan seizure-frequency category concepts.
 */
export const exectv2Dataset: DatasetDescriptor = {
  id: "exectv2",
  label: "ExECTv2",
  shortLabel: "ExECTv2",
  tagline: "Four-family key clinical finding extraction",
  specimenLabel: "letter",
  specimenLabelPlural: "letters",
  runLabel: "architecture",
  defaultSurface: "workbench",
  defaultSplit: "dev140",
  splits: ["dev140", "dev25"],
  supports: {
    workbench: true,
    observatory: true,
    laboratory: false,
    gallery: true,
    reliability: true,
  },
  tone: "deterministic",
  families: EXECTV2_FAMILIES,
  metrics: [
    {
      id: "overall_f1",
      label: "Overall clinical F1",
      shortLabel: "Overall",
      kind: "headline",
      format: "f1",
      description: "Headline clinical mention F1 across all four families.",
    },
    {
      id: "f1_Diagnosis",
      label: "Diagnosis F1",
      shortLabel: "Dx",
      kind: "family",
      family: "Diagnosis",
      format: "f1",
    },
    {
      id: "f1_SeizureFrequency",
      label: "Seizure Frequency F1",
      shortLabel: "SF",
      kind: "family",
      family: "SeizureFrequency",
      format: "f1",
    },
    {
      id: "f1_Prescription",
      label: "Prescription F1",
      shortLabel: "Rx",
      kind: "family",
      family: "Prescription",
      format: "f1",
    },
    {
      id: "f1_Investigations",
      label: "Investigations F1",
      shortLabel: "Inv",
      kind: "family",
      family: "Investigations",
      format: "f1",
    },
    {
      id: "exact_evidence_rate",
      label: "Exact evidence rate",
      shortLabel: "Evidence",
      kind: "operational",
      format: "rate",
      description: "Fraction of mentions whose evidence quote matches the source exactly.",
    },
    {
      id: "call_failures",
      label: "Call failures",
      shortLabel: "Calls",
      kind: "operational",
      format: "count",
    },
    {
      id: "parse_schema_failures",
      label: "Parse / schema failures",
      shortLabel: "Parse",
      kind: "operational",
      format: "count",
    },
  ],
  componentTypes: [
    {
      id: "llm_producer",
      label: "LLM producer lane",
      description: "Focused LLM producer that proposes candidate mentions.",
      tone: "llm",
    },
    {
      id: "dictionary",
      label: "Deterministic dictionary",
      description: "Standard-dictionary normalization and projection.",
      tone: "deterministic",
    },
    {
      id: "semantic_lens",
      label: "Semantic lens",
      description: "Lens that reshapes or reconciles candidates.",
      tone: "hybrid",
    },
    {
      id: "assembler",
      label: "Assembly / merge",
      description: "Union/arbitration logic that merges lanes into the final set.",
      tone: "deterministic-alt",
    },
    {
      id: "evidence_validation",
      label: "Evidence validation",
      description: "Verifier that checks evidence quotes against the source.",
      tone: "success",
    },
    {
      id: "deterministic_projection",
      label: "Deterministic projection",
      description: "Format-only projection and benchmark repair kept separate from semantic recovery.",
      tone: "deterministic",
    },
    {
      id: "scorer",
      label: "Scorer",
      description: "Clinical mention scoring surface.",
      tone: "muted",
    },
  ],
  errorClasses: [
    {
      id: "false_positive",
      label: "False positive mention",
      description: "Predicted a mention with no matching gold mention.",
      tone: "hybrid",
    },
    {
      id: "false_negative",
      label: "False negative mention",
      description: "Gold mention with no matching prediction.",
      tone: "error",
    },
    {
      id: "attribute_mismatch",
      label: "Attribute mismatch",
      description: "Matched mention but a key attribute (CUI, assertion, status) differs.",
      tone: "deterministic-alt",
    },
    {
      id: "evidence_invalid",
      label: "Invalid / weak evidence",
      description: "Matched mention but the evidence quote is not exact.",
      tone: "llm",
    },
  ],
  claimBoundaries: [
    "ExECT dev (25) diagnostic",
    "ExECT dev (140) control",
    "ExECT full (200) — not authorized here",
    "Holdout — not authorized here",
  ],
};
