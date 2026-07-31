// ── Gan 2026 component stage-ladder (replay-only cumulative purist ladder) ──

export interface Gan2026LadderCategory {
  id: string;
  label: string;
  short_label: string;
  tone: string;
}

export interface Gan2026LadderStage {
  stage_id: string;
  label: string;
  component_type: string;
  score: number;
  delta_from_previous: number;
  is_baseline: boolean;
  category_deltas: Record<string, number>;
  interpretation: string;
}

export interface Gan2026ArchitectureLadder {
  artifact_kind: "gan2026_component_architecture_ladder";
  dataset: "gan2026";
  generated_on: string;
  run_id: string;
  label: string;
  model: string;
  decision: string;
  split: string;
  row_count: number;
  final_score: number;
  stages: Gan2026LadderStage[];
  source_artifacts: string[];
  claim_boundary: string;
  row_inspection_policy: string;
}

export interface Gan2026ComponentAblationResponse {
  artifact_kind: "gan2026_component_stage_ladder_set";
  dataset: "gan2026";
  generated_on: string;
  metric: string;
  metric_label: string;
  method: string;
  method_note: string;
  split: string;
  row_inspection_policy: string;
  allow_model_calls: boolean;
  claim_boundary: string;
  categories: Gan2026LadderCategory[];
  architectures: Gan2026ArchitectureLadder[];
}

// ── Gan 2026 per-note stage label trajectories (illustrative, explanatory only) ──
//
// A Gan prediction is one seizure-frequency label, so its worked example is a
// label trajectory (not the mention add/drop/change diff ExECTv2 uses): each
// stage's predicted label, the purist boundary band it lands in, and whether that
// stage changed it. Explanatory only — never a scoring surface.

export interface Gan2026TransitionStage {
  stage_id: string;
  label: string;
  component_type: string;
  interpretation: string;
  is_baseline: boolean;
  predicted_label: string;
  band: string;
  band_label: string | null;
  evidence: string;
  changed: boolean;
  band_changed: boolean;
  previous_label: string | null;
  previous_band: string | null;
  previous_band_label: string | null;
  correct: boolean;
}

export interface Gan2026TransitionExample {
  row_id: number | null;
  row_label: string;
  gold_label: string;
  gold_band: string;
  gold_band_label: string | null;
  final_label: string;
  final_band: string;
  final_correct: boolean;
  change_count: number;
  band_change_count: number;
  stages: Gan2026TransitionStage[];
}

export interface Gan2026TransitionArchitecture {
  run_id: string;
  label: string;
  model: string;
  decision: string;
  examples: Gan2026TransitionExample[];
}

export interface Gan2026ComponentTransitionsResponse {
  artifact_kind: "gan2026_component_transition_examples";
  dataset: "gan2026";
  generated_on: string;
  row_inspection_policy: string;
  allow_model_calls: boolean;
  claim_boundary: string;
  metric_label: string;
  split: string;
  examples_per_architecture: number;
  categories: Gan2026LadderCategory[];
  architectures: Gan2026TransitionArchitecture[];
}