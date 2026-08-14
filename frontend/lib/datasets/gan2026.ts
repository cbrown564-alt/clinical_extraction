import type { DatasetDescriptor } from "./types";

/**
 * Gan 2026 — seizure-frequency extraction and reliability analysis.
 *
 * The descriptor exists so the app shell can reason about Gan generically; the
 * Gan surfaces themselves continue to use their existing, battle-tested
 * components. Nothing here changes Gan rendering — it only declares labels and
 * the taxonomy so the dataset switcher and shared chrome have stable language.
 */
export const gan2026Dataset: DatasetDescriptor = {
  id: "gan2026",
  label: "Gan 2026",
  shortLabel: "Gan",
  tagline: "Seizure-frequency extraction & reliability",
  specimenLabel: "note",
  specimenLabelPlural: "notes",
  runLabel: "pipeline run",
  defaultSurface: "workbench",
  defaultSplit: "dev750",
  splits: ["dev750"],
  supports: {
    workbench: true,
    "gold-audit": true,
  },
  tone: "llm",
  families: [
    { id: "seizure_frequency", label: "Seizure Frequency", shortLabel: "SF", tone: "llm" },
  ],
  metrics: [
    {
      id: "purist_accuracy",
      label: "Strict label match",
      shortLabel: "Strict",
      kind: "headline",
      format: "rate",
      description: "Exact seizure-frequency category match.",
    },
    {
      id: "pragmatic_accuracy",
      label: "Lenient label match",
      shortLabel: "Lenient",
      kind: "headline",
      format: "rate",
      description: "Clinically-adjacent category match.",
    },
    {
      id: "micro_f1",
      label: "Micro F1",
      shortLabel: "F1",
      kind: "headline",
      format: "f1",
    },
  ],
  componentTypes: [
    {
      id: "prompt",
      label: "Prompt policy",
      description: "LLM prompt-controlled extraction behaviour.",
      tone: "llm",
    },
    {
      id: "llm_assessment",
      label: "LLM producer",
      description: "The LLM's selection/label, the producer floor every stage builds on.",
      tone: "llm",
    },
    {
      id: "deterministic_rule",
      label: "Deterministic rule",
      description: "Regex/candidate-generation rule families.",
      tone: "deterministic",
    },
    {
      id: "normalize",
      label: "Normalize",
      description: "Deterministic frequency/label normalization.",
      tone: "deterministic",
    },
    {
      id: "projection",
      label: "Projection",
      description: "Evidence-grounded projection of the label onto a Gan category.",
      tone: "deterministic-alt",
    },
    {
      id: "repair",
      label: "Repair",
      description: "Post-processing label repair.",
      tone: "hybrid",
    },
    {
      id: "verify_route",
      label: "Verify / route",
      description: "Routing of ambiguous rows for review; affects disposition, not category.",
      tone: "muted",
    },
    {
      id: "scorer",
      label: "Scorer",
      description: "Strict / lenient label-match scoring surface.",
      tone: "muted",
    },
  ],
  errorClasses: [
    { id: "false_negative", label: "False negative", description: "Missed a real frequency.", tone: "error" },
    { id: "false_positive", label: "False positive", description: "Invented a frequency.", tone: "hybrid" },
    { id: "over_estimate", label: "Over-estimate", description: "Predicted higher than gold.", tone: "error" },
    { id: "under_estimate", label: "Under-estimate", description: "Predicted lower than gold.", tone: "deterministic-alt" },
    { id: "near_miss", label: "Near miss", description: "Off by one category bucket.", tone: "muted" },
  ],
  claimBoundaries: ["Gan validation (750)", "Gan holdout (450)"],
};
