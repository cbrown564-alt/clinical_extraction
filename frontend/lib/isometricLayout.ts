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

export const GAN_SCHEMA_CATALOG: CatalogItem[] = [
  { id: "json_schema_repair", label: "JSON shape", stageIdPattern: "json_schema_repair" },
  { id: "format_only_retry", label: "Format-only retry", stageIdPattern: "format_only_retry" },
  { id: "schema_validation", label: "Schema validation", stageIdPattern: "schema_validation" },
];

export const GAN_NORMALIZE_CATALOG: CatalogItem[] = [
  { id: "rules_extract", label: "Extract candidates", stageIdPattern: "gan.rules.extract" },
  { id: "normalize_events", label: "Normalize events", stageIdPattern: "normalize" },
  { id: "resolve_label", label: "Resolve label", stageIdPattern: "resolve_label" },
  { id: "select_and_render", label: "Select and render", stageIdPattern: "select_and_render" },
];

export const GAN_EVIDENCE_CATALOG: CatalogItem[] = [
  { id: "scorable", label: "Scorable label", stageIdPattern: "scorable_label_check" },
  { id: "containment", label: "Verbatim evidence", stageIdPattern: "evidence_containment" },
  { id: "trace", label: "Evidence trace", stageIdPattern: "evidence_trace_check" },
  { id: "selected_evidence_repair", label: "Selected-evidence repair", stageIdPattern: "selected_evidence_repair" },
];

export const EXECT_PARSE_CATALOG: CatalogItem[] = [
  { id: "parse", label: "Parse and retry", stageIdPattern: "parse" },
];

export const EXECT_FLATTEN_CATALOG: CatalogItem[] = [
  { id: "extract_sf", label: "Extract seizure frequency", stageIdPattern: "extract_seizure_frequency" },
  { id: "extract_entities", label: "Extract entities", stageIdPattern: "extract_entities" },
  { id: "flatten", label: "Map events", stageIdPattern: "map_events" },
  { id: "project_and_gate", label: "Project and gate", stageIdPattern: "project_and_gate" },
  { id: "sf_state", label: "Seizure-frequency state", stageIdPattern: "sf_state_projection" },
  { id: "sf_unknown", label: "Unknown suppression", stageIdPattern: "sf_unknown_suppression" },
  { id: "dedupe", label: "Dedupe", stageIdPattern: "dedupe" },
  { id: "raw_candidate", label: "Raw candidate", stageIdPattern: "raw_candidate" },
];

export const EXECT_SCORE_CATALOG: CatalogItem[] = [
  { id: "materialize", label: "Scoring views", stageIdPattern: "materialize_views" },
  { id: "score", label: "Emit units", stageIdPattern: "score" },
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
    catalog: GAN_SCHEMA_CATALOG,
  },
  {
    id: "gan_normalize",
    name: "Normalize",
    alwaysDoes: "Turn events into the scored representation.",
    kind: "normalize",
    catalog: GAN_NORMALIZE_CATALOG,
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
    catalog: GAN_EVIDENCE_CATALOG,
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
    catalog: EXECT_PARSE_CATALOG,
  },
  {
    id: "exect_flatten",
    name: "Flatten",
    alwaysDoes: "Turn mentions into findings and project seizure-frequency state.",
    kind: "flatten",
    catalog: EXECT_FLATTEN_CATALOG,
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
    alwaysDoes: "What left the line. Gold comparison lives on Workbench.",
    kind: "score",
    catalog: EXECT_SCORE_CATALOG,
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
    stageId.includes("map_events") ||
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

export function effectiveCatalog(
  station: StationLayoutNode,
  mapped: StageObservationData[]
): CatalogItem[] {
  if (station.catalog && station.catalog.length > 0) return station.catalog;
  return mapped.map((obs) => ({
    id: obs.stage_id,
    label: obs.stage_name,
    stageIdPattern: obs.stage_id,
  }));
}

export function stationActivation(
  station: StationLayoutNode,
  mapped: StageObservationData[]
): { activation: StationActivation; onCount: number; catalogSize: number } {
  if (station.kind === "source") {
    return { activation: "on", onCount: 1, catalogSize: 0 };
  }

  const catalog = effectiveCatalog(station, mapped);
  if (mapped.length === 0) {
    return { activation: "skipped", onCount: 0, catalogSize: catalog.length };
  }

  if (catalog.length > 1) {
    const onCount = catalog.filter((item) =>
      mapped.some((obs) => catalogMatches(item, obs) && obs.changed)
    ).length;
    return {
      activation: onCount > 0 ? "on" : "idle",
      onCount,
      catalogSize: catalog.length,
    };
  }

  return { activation: "on", onCount: mapped.length, catalogSize: catalog.length };
}

export interface StationPoint {
  x: number;
  y: number;
}

export const CANVAS_WIDTH = 960;
export const CANVAS_HEIGHT = 400;
export const ACCENT = "#0f4c4a";

export function layoutStationPoints(count: number): StationPoint[] {
  const topCount = Math.ceil(count / 2);
  const bottomCount = count - topCount;
  const left = 150;
  const right = CANVAS_WIDTH - 150;
  const topY = 108;
  const bottomY = 268;

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
      if (catalogSize > 1) return `on · ${onCount} of ${catalogSize}`;
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

export function clipLine(text: string, max = 88): string {
  const trimmed = text.trim();
  if (trimmed.length <= max) return trimmed;
  return `${trimmed.slice(0, max).trimEnd()}…`;
}

export function isPipelineFillerNote(note: string): boolean {
  return /^canonical (llm|rules)/i.test(note.trim());
}

export function usefulStageNote(note: string): string {
  const trimmed = note.trim();
  if (!trimmed || isPipelineFillerNote(trimmed)) return "";
  return trimmed;
}

export function lensThisCaseLine(item: CatalogItem, obs: StageObservationData | undefined): string {
  if (!obs) return `${item.label}: not in this method`;
  const note = usefulStageNote(obs.note);
  if (obs.changed && note) return `${item.label}: ${note}`;
  if (obs.changed) return item.label;
  return `${item.label}: assembled, no rewrite`;
}

export function lensRewriteLine(observations: StageObservationData[]): string {
  const notes = observations
    .filter((obs) => obs.changed)
    .map((obs) => usefulStageNote(obs.note))
    .filter((note) => note.length > 0);
  if (notes.length === 0) return "";
  return clipLine(notes[0], 88);
}

export function sourceLetterLine(
  noteText: string,
  goldReference: string,
  story = ""
): string {
  const gold = goldReference.trim();
  if (gold) return clipLine(gold);
  if (story.trim()) return clipLine(story);

  const lines = noteText
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
  const body =
    lines.find((line) => line.length > 24 && !/clinic letter/i.test(line)) ??
    lines[1] ??
    lines[0] ??
    "";
  return clipLine(body);
}
