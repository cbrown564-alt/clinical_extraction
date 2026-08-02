import type { DatasetDescriptor, DatasetTone } from "@/lib/datasets";
import { gan2026Dataset } from "@/lib/datasets";
import type { Gan2026ComponentAblationResponse } from "@/lib/types";

/**
 * Dataset-agnostic "component ladder" view-model.
 *
 * Both datasets answer the same question — *how much does each component
 * contribute to the final score?* — by decomposing a pipeline into an ordered
 * stack of named, typed stages and reading the cumulative score at each stage's
 * output. The marginal step at each stage is its contribution. This shape is the
 * single contract the shared waterfall surface renders.
 */
export interface LadderCategory {
  id: string;
  label: string;
  shortLabel: string;
  tone: DatasetTone;
}

export interface LadderStage {
  id: string;
  label: string;
  /** Raw component-type id (llm_producer, dictionary, prompt, …). */
  componentType: string;
  /** Human label for the component type, from the dataset descriptor. */
  componentTypeLabel: string;
  tone: DatasetTone;
  /** Cumulative score at this stage's output, in [0, 1]. */
  score: number;
  /** Score gained (or lost) versus the previous stage; 0 for the baseline. */
  deltaFromPrevious: number;
  /** True for the first stage — the floor the ladder builds up from. */
  isBaseline: boolean;
  /** Per-category deltas for this stage versus the previous one. */
  categoryDeltas: Record<string, number>;
  precision?: number;
  recall?: number;
  interpretation?: string;
}

export interface LadderArchitecture {
  id: string;
  label: string;
  model: string;
  decision: string;
  finalScore: number;
  rowCount: number;
  stages: LadderStage[];
}

export interface ComponentLadder {
  dataset: "gan2026";
  /** Short human name for how contribution was measured. */
  method: string;
  /** Provenance line shown under the method (split, replay policy, …). */
  methodNote: string;
  /** The metric the ladder scores ("Clinical F1", "Strict label match"). */
  metricLabel: string;
  claimBoundary: string;
  generatedOn: string;
  categories: LadderCategory[];
  architectures: LadderArchitecture[];
}

/** Resolve a stage's component-type label + tone from the dataset descriptor. */
function resolveComponentType(
  descriptor: DatasetDescriptor,
  componentType: string
): { label: string; tone: DatasetTone } {
  const match = descriptor.componentTypes.find((c) => c.id === componentType);
  return {
    label: match?.label ?? componentType.replace(/_/g, " "),
    tone: match?.tone ?? "muted",
  };
}

/**
 * Adapt the Gan 2026 component stage-ladder payload onto the shared view-model.
 *
 * The Gan payload is already a cumulative purist-accuracy ladder produced by the
 * replay-only builder (one StageLadderProvider per architecture). This renames its
 * snake_case fields into the dataset-agnostic stage vocabulary and resolves each
 * stage's component-type tone from the Gan descriptor, so the Gan and ExECTv2
 * ladders render through the identical `ComponentLadderSurface`.
 */
export function adaptGan2026Ladder(
  payload: Gan2026ComponentAblationResponse
): ComponentLadder {
  const categories: LadderCategory[] = payload.categories.map((category) => ({
    id: category.id,
    label: category.label,
    shortLabel: category.short_label,
    tone: category.tone as DatasetTone,
  }));

  const architectures: LadderArchitecture[] = payload.architectures.map((arch) => {
    const stages: LadderStage[] = arch.stages.map((stage, index) => {
      const { label: componentTypeLabel, tone } = resolveComponentType(
        gan2026Dataset,
        stage.component_type
      );
      return {
        id: stage.stage_id,
        label: stage.label,
        componentType: stage.component_type,
        componentTypeLabel,
        tone,
        score: stage.score,
        deltaFromPrevious: index === 0 ? 0 : stage.delta_from_previous,
        isBaseline: stage.is_baseline,
        categoryDeltas: stage.category_deltas,
        interpretation: stage.interpretation,
      };
    });
    return {
      id: arch.run_id,
      label: arch.label,
      model: arch.model,
      decision: arch.decision,
      finalScore: arch.final_score,
      rowCount: arch.row_count,
      stages,
    };
  });

  return {
    dataset: "gan2026",
    method: payload.method,
    methodNote: payload.method_note,
    metricLabel: payload.metric_label,
    claimBoundary: payload.claim_boundary,
    generatedOn: payload.generated_on,
    categories,
    architectures,
  };
}

/** The stage with the largest absolute contribution (excludes the baseline). */
export function biggestMover(arch: LadderArchitecture): LadderStage | undefined {
  let best: LadderStage | undefined;
  for (const stage of arch.stages) {
    if (stage.isBaseline) continue;
    if (!best || Math.abs(stage.deltaFromPrevious) > Math.abs(best.deltaFromPrevious)) {
      best = stage;
    }
  }
  return best;
}

/** Shared y-axis floor for a set of stages, anchored to 1.0 at the top. */
export function ladderDomain(stages: LadderStage[]): { min: number; max: number } {
  const scores = stages.map((s) => s.score).filter((s) => Number.isFinite(s));
  if (scores.length === 0) return { min: 0, max: 1 };
  const lo = Math.min(...scores);
  const min = Math.max(0, Math.floor((lo - 0.05) * 20) / 20);
  return { min, max: 1 };
}
