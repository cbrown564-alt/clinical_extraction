import type {
  CatalogItem,
  StageObservationData,
  StationActivation,
  StationLayoutNode,
} from "./isometricTypes";

export const GAN_REPAIR_CATALOG: CatalogItem[] = [
  { id: "selected_evidence", label: "Selected evidence", stageIdPattern: "repair.selected_evidence" },
  { id: "monthly_diary", label: "Monthly diary", stageIdPattern: "repair.monthly_diary" },
  { id: "usual_interval", label: "Usual interval", stageIdPattern: "repair.usual_interval" },
  { id: "typical_over_ytd", label: "Typical vs year-to-date", stageIdPattern: "repair.typical_over_ytd" },
  { id: "breakthrough", label: "Breakthrough", stageIdPattern: "repair.breakthrough" },
  { id: "non_epileptic", label: "Non-epileptic", stageIdPattern: "repair.non_epileptic" },
  { id: "residual_jerk", label: "Residual jerks", stageIdPattern: "repair.residual_jerk" },
  { id: "post_change_burst", label: "Post-change burst", stageIdPattern: "repair.post_change_burst" },
  { id: "dated_sequence", label: "Dated sequence", stageIdPattern: "repair.dated_sequence" },
  { id: "elapsed_anchor", label: "Elapsed since anchor", stageIdPattern: "repair.elapsed_anchor" },
];

export const EXECT_LENS_CATALOG: CatalogItem[] = [
  { id: "diagnosis", label: "Diagnosis", stageIdPattern: "lens.diagnosis" },
  { id: "seizure_frequency", label: "Seizure frequency", stageIdPattern: "lens.seizure_frequency" },
  { id: "prescription", label: "Prescription", stageIdPattern: "lens.prescription" },
  { id: "investigations", label: "Investigations", stageIdPattern: "lens.investigations" },
];

export const GAN_STATIONS: StationLayoutNode[] = [
  {
    id: "gan_source",
    name: "Source",
    alwaysDoes: "The letter this run is about.",
    kind: "source",
  },
  {
    id: "gan_prompt",
    name: "Prompt",
    alwaysDoes: "Combine the letter with the task instructions and examples for the model.",
    kind: "prompt",
  },
  {
    id: "gan_model",
    name: "Model",
    alwaysDoes: "Propose structured candidates.",
    kind: "model",
  },
  {
    id: "gan_schema",
    name: "Schema",
    alwaysDoes: "Make the output parseable. No clinical rewrite.",
    kind: "schema",
  },
  {
    id: "gan_normalize",
    name: "Normalize",
    alwaysDoes: "Turn events into the scored representation.",
    kind: "normalize",
  },
  {
    id: "gan_repair",
    name: "Repair",
    alwaysDoes: "The ten-family ruleset that may change meaning.",
    kind: "repair",
    catalog: GAN_REPAIR_CATALOG,
  },
  {
    id: "gan_evidence",
    name: "Evidence",
    alwaysDoes: "Require a verbatim span. Drop or fail if it is missing.",
    kind: "evidence",
  },
  {
    id: "gan_score",
    name: "Score",
    alwaysDoes: "Project onto Purist and Pragmatic.",
    kind: "score",
  },
];

export const EXECT_STATIONS: StationLayoutNode[] = [
  {
    id: "exect_source",
    name: "Source",
    alwaysDoes: "The letter this run is about.",
    kind: "source",
  },
  {
    id: "exect_prompt",
    name: "Prompt",
    alwaysDoes: "Combine the letter with the four-family instructions and examples.",
    kind: "prompt",
  },
  {
    id: "exect_model",
    name: "Model",
    alwaysDoes: "Propose structured mentions and facts.",
    kind: "model",
  },
  {
    id: "exect_parse",
    name: "Parse",
    alwaysDoes: "Make the model output parseable. No clinical rewrite.",
    kind: "schema",
  },
  {
    id: "exect_flatten",
    name: "Flatten",
    alwaysDoes: "Turn mentions into findings and project seizure-frequency state.",
    kind: "flatten",
  },
  {
    id: "exect_store",
    name: "Store",
    alwaysDoes: "Hold the findings the lenses read.",
    kind: "store",
  },
  {
    id: "exect_lenses",
    name: "Lenses",
    alwaysDoes: "Four adapters: diagnosis, seizure frequency, prescription, investigations.",
    kind: "lenses",
    catalog: EXECT_LENS_CATALOG,
  },
  {
    id: "exect_evidence",
    name: "Evidence",
    alwaysDoes: "Require exact evidence where the method demands it.",
    kind: "evidence",
  },
  {
    id: "exect_score",
    name: "Score",
    alwaysDoes: "Materialize scoring views and fact-match.",
    kind: "score",
  },
];

export function mapStageToStationId(stageId: string, isGan: boolean): string | null {
  if (isGan) {
    if (stageId.includes("letterhead") || stageId.includes("source_note")) return "gan_source";
    if (stageId.includes("build_prompt")) return "gan_prompt";
    if (stageId.includes("model_call")) return "gan_model";
    if (
      stageId.includes("json_schema_repair") ||
      stageId.includes("format_only_retry") ||
      stageId.includes("schema_validation")
    ) {
      return "gan_schema";
    }
    if (
      stageId.includes("normalize") ||
      stageId.includes("resolve_label") ||
      stageId.includes("select_and_render") ||
      stageId.includes("gan.rules.extract")
    ) {
      return "gan_normalize";
    }
    if (stageId.includes(".repair.")) return "gan_repair";
    if (
      stageId.includes("evidence_containment") ||
      stageId.includes("evidence_trace_check") ||
      stageId.includes("scorable_label_check") ||
      stageId.includes("selected_evidence_repair")
    ) {
      return "gan_evidence";
    }
    if (stageId.includes("score")) return "gan_score";
    return null;
  }

  if (stageId.includes("letterhead") || stageId.includes("source_note")) return "exect_source";
  if (stageId.includes("build_prompt")) return "exect_prompt";
  if (stageId.includes("model_call")) return "exect_model";
  if (stageId.includes("parse")) return "exect_parse";
  if (
    stageId.includes("flatten") ||
    stageId.includes("project_and_gate") ||
    stageId.includes("sf_state_projection") ||
    stageId.includes("sf_unknown_suppression") ||
    stageId.includes("project_facts") ||
    stageId.includes("dedupe") ||
    stageId.includes("extract_seizure_frequency") ||
    stageId.includes("extract_entities") ||
    stageId.includes("raw_candidate")
  ) {
    return "exect_flatten";
  }
  if (stageId.includes("register_findings")) return "exect_store";
  if (stageId.includes("lens.")) return "exect_lenses";
  if (stageId.includes("evidence_requirement")) return "exect_evidence";
  if (stageId.includes("materialize_views") || stageId.includes("score")) return "exect_score";
  return null;
}

export function observationsForStation(
  observations: StageObservationData[],
  stationId: string,
  isGan: boolean
): StageObservationData[] {
  return observations.filter((obs) => mapStageToStationId(obs.stage_id, isGan) === stationId);
}

export function catalogMatches(item: CatalogItem, obs: StageObservationData): boolean {
  return obs.stage_id.includes(item.stageIdPattern);
}

export function stationActivation(
  station: StationLayoutNode,
  mapped: StageObservationData[]
): { activation: StationActivation; onCount: number; catalogSize: number } {
  if (station.kind === "source") {
    return { activation: "on", onCount: 1, catalogSize: 0 };
  }

  if (mapped.length === 0) {
    return { activation: "skipped", onCount: 0, catalogSize: station.catalog?.length ?? 0 };
  }

  if (station.catalog && station.catalog.length > 0) {
    const onCount = station.catalog.filter((item) =>
      mapped.some((obs) => catalogMatches(item, obs) && obs.changed)
    ).length;
    return {
      activation: onCount > 0 ? "on" : "idle",
      onCount,
      catalogSize: station.catalog.length,
    };
  }

  return { activation: "on", onCount: mapped.length, catalogSize: 0 };
}

export interface StationPoint {
  x: number;
  y: number;
}

export const CANVAS_WIDTH = 960;
export const CANVAS_HEIGHT = 520;

export function layoutStationPoints(count: number): StationPoint[] {
  const topCount = Math.ceil(count / 2);
  const bottomCount = count - topCount;
  const left = 90;
  const right = CANVAS_WIDTH - 90;
  const topY = 150;
  const bottomY = 370;

  const row = (n: number, y: number): StationPoint[] => {
    if (n === 1) return [{ x: (left + right) / 2, y }];
    const span = right - left;
    return Array.from({ length: n }, (_, i) => ({
      x: left + (span * i) / (n - 1),
      y,
    }));
  };

  return [...row(topCount, topY), ...row(bottomCount, bottomY)];
}

export function activationLabel(
  activation: StationActivation,
  onCount: number,
  catalogSize: number
): string {
  switch (activation) {
    case "on":
      if (catalogSize > 0) return `on · ${onCount} of ${catalogSize}`;
      return "on";
    case "idle":
      return "idle";
    case "skipped":
      return "not in this method";
    default: {
      const _exhaustive: never = activation;
      return _exhaustive;
    }
  }
}
