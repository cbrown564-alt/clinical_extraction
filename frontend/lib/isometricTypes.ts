import type { FactGoldData, PredictedFactData } from "./assemblyLineTypes";

export type EffectClass =
  | "transport_or_schema"
  | "representation"
  | "clinical_meaning"
  | "validation_gate"
  | "benchmark_projection";

export type StageOwner = "model" | "deterministic" | "scorer";

export type MethodId =
  | "gan_rules"
  | "gan_llm_only"
  | "gan_llm_with_rules"
  | "exect_rules"
  | "exect_llm_only"
  | "exect_llm_pre_post";

export interface StageObservationData {
  stage_id: string;
  stage_name: string;
  owner: StageOwner;
  effect_class: EffectClass;
  input: string;
  output: string;
  changed: boolean;
  note: string;
}

export interface TeachingRunData {
  method_id: MethodId;
  method_label: string;
  one_sentence: string;
  prediction_owner: string;
  final_answer: string;
  correct: boolean | null;
  correctness_note: string;
  observations: StageObservationData[];
  facts?: PredictedFactData[];
  gold_unit?: FactGoldData;
}

export interface TeachingCaseData {
  case_id: string;
  task: "gan2026" | "exectv2";
  task_label: string;
  letter_id: string;
  note_text: string;
  gold: string;
  gold_note: string;
  fixture_note: string;
  story: string;
  gold_reference: string;
  card_why: {
    rules?: string;
    llm?: string;
    llm_with_rules?: string;
  };
  mechanism_title: string;
  mechanism: string;
  runs: TeachingRunData[];
}

export interface ManifestStageData {
  stage_id: string;
  name: string;
  operation: string;
  owner: StageOwner;
  effect_class: EffectClass;
  may_change_clinical_meaning: boolean;
  input_type: string;
  input_example: string;
  output_type: string;
  output_example: string;
  implementation: {
    path: string;
    symbol: string;
  };
  governing_test: string;
  trace_fields: string[];
  paper_wording: string;
  rule_category?: string;
  notes?: string;
}

export interface MethodManifestData {
  method_id: MethodId;
  task: string;
  task_label: string;
  method: string;
  method_label: string;
  role: string;
  entry_point: {
    path: string;
    symbol: string;
  };
  one_sentence: string;
  sixty_second: string;
  prediction_owner: string;
  scored_representation: string;
  stages: ManifestStageData[];
}

export interface TeachingCasesPayload {
  cases: TeachingCaseData[];
  manifests: MethodManifestData[];
}

export type StationKind =
  | "source"
  | "prompt"
  | "model"
  | "schema"
  | "normalize"
  | "repair"
  | "evidence"
  | "score"
  | "flatten"
  | "store"
  | "lenses";

export interface CatalogItem {
  id: string;
  label: string;
  stageIdPattern: string;
}

export interface StationLayoutNode {
  id: string;
  name: string;
  alwaysDoes: string;
  kind: StationKind;
  catalog?: CatalogItem[];
}

export type StationActivation = "on" | "idle" | "skipped";
