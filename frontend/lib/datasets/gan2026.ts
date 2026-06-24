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
  defaultSplit: "validation",
  splits: ["validation", "test", "synthetic"],
  supports: {
    workbench: true,
    observatory: true,
    laboratory: true,
    gallery: true,
    reliability: true,
  },
  tone: "llm",
  families: [
    { id: "seizure_frequency", label: "Seizure Frequency", shortLabel: "SF", tone: "llm" },
  ],
  metrics: [
    {
      id: "purist_accuracy",
      label: "Purist Accuracy",
      shortLabel: "Purist",
      kind: "headline",
      format: "rate",
      description: "Exact seizure-frequency category match.",
    },
    {
      id: "pragmatic_accuracy",
      label: "Pragmatic Accuracy",
      shortLabel: "Pragmatic",
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
      id: "deterministic_rule",
      label: "Deterministic rule",
      description: "Regex/candidate-generation rule families.",
      tone: "deterministic",
    },
    {
      id: "repair",
      label: "Repair",
      description: "Post-processing label repair.",
      tone: "hybrid",
    },
    {
      id: "scorer",
      label: "Scorer",
      description: "Purist/Pragmatic scoring surface.",
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
  claimBoundaries: ["validation", "test450 holdout"],
};
