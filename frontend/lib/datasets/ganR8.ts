import type { DatasetDescriptor } from "./types";

/** Saved R8 rich output compared with the reviewed v0.7 Gan dev750 reference. */
export const ganR8Dataset: DatasetDescriptor = {
  id: "ganR8",
  label: "Gan R8 review",
  shortLabel: "R8",
  tagline: "Saved R8 findings versus reviewed gold",
  specimenLabel: "letter",
  specimenLabelPlural: "letters",
  runLabel: "saved run",
  defaultSurface: "workbench",
  defaultSplit: "dev750",
  splits: ["dev750"],
  supports: { workbench: true },
  tone: "llm",
  families: [{ id: "SeizureFrequency", label: "Seizure Frequency", shortLabel: "SF", tone: "llm" }],
  metrics: [
    { id: "finding_precision", label: "Finding precision", shortLabel: "Precision", kind: "headline", format: "rate" },
    { id: "finding_recall", label: "Finding recall", shortLabel: "Recall", kind: "headline", format: "rate" },
  ],
  componentTypes: [],
  errorClasses: [],
  claimBoundaries: ["Synthetic Gan dev750 only", "No holdout letters"],
};
