/**
 * Dataset kernel — shared frontend contracts.
 *
 * The review instrument has stable surfaces (Example Explorer, Aggregate
 * Performance, Component Impact, Error Gallery, Reliability Scorecard) and swappable datasets. These
 * types are the shared language the surfaces speak so that components stop
 * importing Gan-only assumptions. Each dataset provides a {@link DatasetDescriptor}
 * that declares what it supports, which families/metrics/components/error
 * classes it owns, and how its specimens and runs are labelled.
 */

export type DatasetId = "gan2026" | "exectv2";

/** A stable review surface, keyed by its route segment. */
export type ExplorerSurface =
  | "workbench"
  | "observatory"
  | "laboratory"
  | "gallery"
  | "reliability";

/**
 * A colour tone from the design system. Drives tints/borders so each dataset
 * can map its families and components onto a consistent palette.
 */
export type DatasetTone =
  | "deterministic"
  | "deterministic-alt"
  | "llm"
  | "hybrid"
  | "success"
  | "error"
  | "muted";

/** Which surfaces a dataset can populate. */
export interface DatasetSurfaceSupport {
  workbench: boolean;
  observatory: boolean;
  laboratory: boolean;
  gallery: boolean;
  reliability: boolean;
}

/** A task family/sub-task within a dataset (e.g. a Gan category view or an ExECTv2 entity). */
export interface TaskFamilyDescriptor {
  id: string;
  label: string;
  shortLabel: string;
  tone: DatasetTone;
}

/** A quantitative result a dataset reports. */
export interface MetricDescriptor {
  id: string;
  label: string;
  shortLabel: string;
  kind: "headline" | "family" | "operational";
  /** Family id this metric belongs to, when kind === "family". */
  family?: string;
  format: "f1" | "rate" | "count";
  description?: string;
}

/** A prediction-bearing system part a dataset exposes for component impact. */
export interface ComponentTypeDescriptor {
  id: string;
  label: string;
  description: string;
  tone: DatasetTone;
}

/** A residual error class owned by the dataset's error taxonomy. */
export interface ErrorClassDescriptor {
  id: string;
  label: string;
  description: string;
  tone: DatasetTone;
}

/** How a run relates to the claim being made. */
export type RunDecision =
  | "control"
  | "simplification"
  | "diagnostic"
  | "pending"
  | "superseded";

export interface DatasetDescriptor {
  id: DatasetId;
  label: string;
  shortLabel: string;
  tagline: string;
  /** Singular noun for one reviewable source item, e.g. "note" or "letter". */
  specimenLabel: string;
  specimenLabelPlural: string;
  /** Noun for one model/pipeline/config result set. */
  runLabel: string;
  defaultSurface: ExplorerSurface;
  defaultSplit: string;
  splits: string[];
  supports: DatasetSurfaceSupport;
  families: TaskFamilyDescriptor[];
  metrics: MetricDescriptor[];
  componentTypes: ComponentTypeDescriptor[];
  errorClasses: ErrorClassDescriptor[];
  claimBoundaries: string[];
  tone: DatasetTone;
}

/** A URL-safe reference to one reviewable specimen, interpreted per dataset. */
export interface SpecimenRef {
  datasetId: DatasetId;
  split: string;
  /** Gan-style row reference. */
  sourceRowIndex?: number;
  /** ExECTv2-style letter reference. */
  letterId?: string;
}

/** Lightweight, dataset-agnostic run metadata used by selectors and tables. */
export interface RunDescriptor {
  datasetId: DatasetId;
  runId: string;
  label: string;
  model: string;
  architectureFamily: string;
  split: string;
  rowCount: number;
  claimBoundary: string;
  decision: RunDecision;
}

/** Maps a dataset tone to design-system utility classes for chips/cards. */
export const TONE_CLASSES: Record<DatasetTone, string> = {
  deterministic: "border-deterministic/25 bg-deterministic/10 text-deterministic",
  "deterministic-alt":
    "border-deterministic-alt/25 bg-deterministic-alt/10 text-deterministic-alt",
  llm: "border-llm/25 bg-llm/10 text-llm",
  hybrid: "border-hybrid/25 bg-hybrid/10 text-hybrid",
  success: "border-success/25 bg-success/10 text-success",
  error: "border-error/25 bg-error/10 text-error",
  muted: "border-muted/20 bg-muted/10 text-muted",
};

/** Classes for a decision badge; keeps control vs diagnostic visually distinct. */
export const DECISION_CLASSES: Record<RunDecision, string> = {
  control: "border-deterministic/25 bg-deterministic/10 text-deterministic",
  simplification: "border-success/25 bg-success/10 text-success",
  diagnostic: "border-llm/25 bg-llm/10 text-llm",
  pending: "border-muted/20 bg-muted/10 text-muted",
  superseded: "border-error/20 bg-error/8 text-error",
};
