import type { IsoPoint, StationLayoutNode } from "./isometricTypes";

export const GAN_REPAIR_RULES = [
  { id: "selected_evidence", label: "1. Selected Evidence", stageId: "gan.llm_with_rules.repair.selected_evidence" },
  { id: "monthly_diary", label: "2. Monthly Diary", stageId: "gan.llm_with_rules.repair.monthly_diary" },
  { id: "usual_interval", label: "3. Usual Interval", stageId: "gan.llm_with_rules.repair.usual_interval" },
  { id: "typical_over_ytd", label: "4. Typical vs YTD ★", stageId: "gan.llm_with_rules.repair.typical_over_ytd" },
  { id: "breakthrough", label: "5. Breakthrough", stageId: "gan.llm_with_rules.repair.breakthrough" },
  { id: "non_epileptic", label: "6. Non-Epileptic", stageId: "gan.llm_with_rules.repair.non_epileptic" },
  { id: "residual_jerk", label: "7. Residual Jerks", stageId: "gan.llm_with_rules.repair.residual_jerk" },
  { id: "post_change_burst", label: "8. Post-Change Burst", stageId: "gan.llm_with_rules.repair.post_change_burst" },
  { id: "dated_sequence", label: "9. Dated Sequence", stageId: "gan.llm_with_rules.repair.dated_sequence" },
  { id: "elapsed_anchor", label: "10. Elapsed Anchor", stageId: "gan.llm_with_rules.repair.elapsed_anchor" },
];

export const GAN_STATIONS: StationLayoutNode[] = [
  {
    id: "gan_letterhead",
    label: "Clinical Letterhead",
    shortLabel: "Letterhead",
    gridX: -0.5,
    gridY: 0.2,
    elevation: 0,
    owner: "deterministic",
    effectClass: "transport_or_schema",
    stageIdPattern: "letterhead",
    visualType: "letterhead",
  },
  {
    id: "gan_prompt",
    label: "Prompt & Ingest Bay",
    shortLabel: "Ingest Bay",
    gridX: 2.5,
    gridY: 0.2,
    elevation: 0,
    owner: "deterministic",
    effectClass: "transport_or_schema",
    stageIdPattern: "build_prompt",
    visualType: "intake",
  },
  {
    id: "gan_model",
    label: "Model Structured Extractor",
    shortLabel: "Neural Core",
    gridX: 5.6,
    gridY: 0.2,
    elevation: 6,
    owner: "model",
    effectClass: "clinical_meaning",
    stageIdPattern: "model_call",
    visualType: "neural_core",
  },
  {
    id: "gan_schema",
    label: "Schema Repair & Retry Gate",
    shortLabel: "Schema Gate",
    gridX: 8.6,
    gridY: 0.6,
    elevation: 3,
    owner: "deterministic",
    effectClass: "transport_or_schema",
    stageIdPattern: "schema",
    visualType: "schema_gate",
    isGate: true,
  },
  {
    id: "gan_normalizer",
    label: "Event Normalizer & Resolver",
    shortLabel: "Resolver",
    gridX: 7.8,
    gridY: 3.2,
    elevation: 3,
    owner: "deterministic",
    effectClass: "representation",
    stageIdPattern: "normalize",
    visualType: "centrifuge",
  },
  {
    id: "gan_repair_bay",
    label: "10-Family Repair Bay",
    shortLabel: "Repair Bay",
    gridX: 4.4,
    gridY: 3.4,
    elevation: 7,
    owner: "deterministic",
    effectClass: "clinical_meaning",
    stageIdPattern: "repair",
    visualType: "repair_rack",
    isRepairRack: true,
    rackRules: GAN_REPAIR_RULES,
  },
  {
    id: "gan_evidence_gate",
    label: "Evidence Verbatim Gate",
    shortLabel: "Evidence Gate",
    gridX: 2.0,
    gridY: 5.2,
    elevation: 3,
    owner: "deterministic",
    effectClass: "validation_gate",
    stageIdPattern: "evidence",
    visualType: "evidence_gate",
    isGate: true,
  },
  {
    id: "gan_scorer",
    label: "Purist / Pragmatic Scorer",
    shortLabel: "Scoreboard",
    gridX: 5.6,
    gridY: 5.6,
    elevation: 5,
    owner: "scorer",
    effectClass: "benchmark_projection",
    stageIdPattern: "score",
    visualType: "scoreboard",
  },
];

export const EXECT_STATIONS: StationLayoutNode[] = [
  {
    id: "exect_letterhead",
    label: "Clinical Letterhead",
    shortLabel: "Letterhead",
    gridX: -0.5,
    gridY: 0.2,
    elevation: 0,
    owner: "deterministic",
    effectClass: "transport_or_schema",
    stageIdPattern: "letterhead",
    visualType: "letterhead",
  },
  {
    id: "exect_prompt",
    label: "4-Family Prompt Bay",
    shortLabel: "Ingest Bay",
    gridX: 2.2,
    gridY: 0.2,
    elevation: 0,
    owner: "deterministic",
    effectClass: "transport_or_schema",
    stageIdPattern: "build_prompt",
    visualType: "intake",
  },
  {
    id: "exect_model",
    label: "4-Family Structured LLM",
    shortLabel: "Neural Core",
    gridX: 5.0,
    gridY: 0.2,
    elevation: 6,
    owner: "model",
    effectClass: "clinical_meaning",
    stageIdPattern: "model_call",
    visualType: "neural_core",
  },
  {
    id: "exect_parse",
    label: "Parse & Local Format-Retry",
    shortLabel: "Parse Gate",
    gridX: 7.8,
    gridY: 0.6,
    elevation: 3,
    owner: "deterministic",
    effectClass: "transport_or_schema",
    stageIdPattern: "parse",
    visualType: "schema_gate",
    isGate: true,
  },
  {
    id: "exect_flatten_proj",
    label: "Mention Flattener & SF Proj",
    shortLabel: "Flattener",
    gridX: 7.2,
    gridY: 2.4,
    elevation: 3,
    owner: "deterministic",
    effectClass: "clinical_meaning",
    stageIdPattern: "flatten",
    visualType: "centrifuge",
  },
  {
    id: "exect_finding_store",
    label: "Finding Store (Commutator)",
    shortLabel: "Commutator",
    gridX: 5.0,
    gridY: 2.6,
    elevation: 6,
    owner: "deterministic",
    effectClass: "transport_or_schema",
    stageIdPattern: "finding_store",
    visualType: "commutator",
    isCommutator: true,
  },
  {
    id: "exect_lens_diagnosis",
    label: "Diagnosis Dictionary Lens",
    shortLabel: "Diagnosis Lens",
    gridX: 2.8,
    gridY: 2.2,
    elevation: 4,
    owner: "deterministic",
    effectClass: "clinical_meaning",
    stageIdPattern: "lens.diagnosis",
    visualType: "lens",
    lane: "diagnosis",
  },
  {
    id: "exect_lens_sf",
    label: "Seizure Frequency State Lens",
    shortLabel: "SF State Lens",
    gridX: 2.2,
    gridY: 3.6,
    elevation: 3,
    owner: "deterministic",
    effectClass: "representation",
    stageIdPattern: "lens.seizure_frequency",
    visualType: "lens",
    lane: "seizure_frequency",
  },
  {
    id: "exect_lens_rx",
    label: "Prescription Regimen Lens",
    shortLabel: "Prescription Lens",
    gridX: 2.6,
    gridY: 5.0,
    elevation: 4,
    owner: "deterministic",
    effectClass: "clinical_meaning",
    stageIdPattern: "lens.prescription",
    visualType: "lens",
    lane: "prescription",
  },
  {
    id: "exect_lens_investigations",
    label: "Investigations Adapter Lens",
    shortLabel: "Investigations",
    gridX: 4.4,
    gridY: 5.0,
    elevation: 2,
    owner: "deterministic",
    effectClass: "representation",
    stageIdPattern: "lens.investigations",
    visualType: "lens",
    lane: "investigations",
  },
  {
    id: "exect_evidence_gate",
    label: "Exact Evidence Gatekeeper",
    shortLabel: "Evidence Gate",
    gridX: 6.4,
    gridY: 4.4,
    elevation: 2,
    owner: "deterministic",
    effectClass: "validation_gate",
    stageIdPattern: "evidence",
    visualType: "evidence_gate",
    isGate: true,
  },
  {
    id: "exect_scorer",
    label: "Scoring Views & Fact Match",
    shortLabel: "Scoreboard",
    gridX: 7.8,
    gridY: 5.6,
    elevation: 5,
    owner: "scorer",
    effectClass: "benchmark_projection",
    stageIdPattern: "score",
    visualType: "scoreboard",
  },
];

/**
 * Camera settings and viewport bounds per pipeline mode
 */
export interface CameraSettings {
  viewBox: string;
  originX: number;
  originY: number;
  scale: number;
}

export function getCameraSettings(_isGan?: boolean): CameraSettings {
  return {
    viewBox: "0 0 1520 960",
    originX: 160,
    originY: 120,
    scale: 88,
  };
}

/**
 * Maps a stage ID to its precise isometric station node ID
 */
export function mapStageToStationId(stageId: string, isGan: boolean): string {
  if (isGan) {
    if (stageId.includes("letterhead") || stageId.includes("source_note")) return "gan_letterhead";
    if (stageId.includes("build_prompt") || stageId === "gan.rules.extract") return "gan_prompt";
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
      stageId.includes("select_and_render")
    ) {
      return "gan_normalizer";
    }
    if (stageId.includes(".repair.") || stageId.includes("selected_evidence_repair")) {
      return "gan_repair_bay";
    }
    if (
      stageId.includes("evidence_containment") ||
      stageId.includes("evidence_trace_check") ||
      stageId.includes("scorable_label_check")
    ) {
      return "gan_evidence_gate";
    }
    if (stageId.includes("score")) return "gan_scorer";
    return "gan_prompt";
  } else {
    if (stageId.includes("letterhead") || stageId.includes("source_note")) return "exect_letterhead";
    if (
      stageId.includes("build_prompt") ||
      stageId.includes("extract_seizure_frequency") ||
      stageId.includes("extract_entities")
    ) {
      return "exect_prompt";
    }
    if (stageId.includes("model_call")) return "exect_model";
    if (stageId.includes("parse")) return "exect_parse";
    if (
      stageId.includes("flatten") ||
      stageId.includes("project_and_gate") ||
      stageId.includes("sf_state_projection") ||
      stageId.includes("sf_unknown_suppression") ||
      stageId.includes("project_facts") ||
      stageId.includes("dedupe")
    ) {
      return "exect_flatten_proj";
    }
    if (stageId.includes("register_findings")) return "exect_finding_store";
    if (stageId.includes("lens.diagnosis")) return "exect_lens_diagnosis";
    if (stageId.includes("lens.seizure_frequency")) return "exect_lens_sf";
    if (stageId.includes("lens.prescription")) return "exect_lens_rx";
    if (stageId.includes("lens.investigations")) return "exect_lens_investigations";
    if (stageId.includes("evidence_requirement")) return "exect_evidence_gate";
    if (stageId.includes("materialize_views") || stageId.includes("score")) return "exect_scorer";
    return "exect_prompt";
  }
}

/**
 * Project (gridX, gridY, elevation) into 2D canvas coordinates
 */
export function projectIso(
  gridX: number,
  gridY: number,
  elevation: number = 0,
  scale: number = 105,
  originX: number = 210,
  originY: number = 130
): IsoPoint {
  const isoX = (gridX - gridY * 0.55) * scale;
  const isoY = (gridX * 0.40 + gridY * 0.70) * scale - elevation * 4;
  return {
    x: Math.round(originX + isoX),
    y: Math.round(originY + isoY),
  };
}

/**
 * Build an isometric cuboid / platform SVG path
 */
export function getPlatformTopPoints(
  center: IsoPoint,
  width: number = 65,
  length: number = 55
): string {
  const halfW = width / 2;
  const halfL = length / 2;
  const top = `${center.x},${center.y - halfL * 0.6}`;
  const right = `${center.x + halfW},${center.y}`;
  const bottom = `${center.x},${center.y + halfL * 0.6}`;
  const left = `${center.x - halfW},${center.y}`;
  return `${top} ${right} ${bottom} ${left}`;
}

export function getPlatformSideLeft(
  center: IsoPoint,
  depth: number = 14,
  width: number = 65,
  length: number = 55
): string {
  const halfW = width / 2;
  const halfL = length / 2;
  const topL = `${center.x - halfW},${center.y}`;
  const topB = `${center.x},${center.y + halfL * 0.6}`;
  const botB = `${center.x},${center.y + halfL * 0.6 + depth}`;
  const botL = `${center.x - halfW},${center.y + depth}`;
  return `${topL} ${topB} ${botB} ${botL}`;
}

export function getPlatformSideRight(
  center: IsoPoint,
  depth: number = 14,
  width: number = 65,
  length: number = 55
): string {
  const halfW = width / 2;
  const halfL = length / 2;
  const topB = `${center.x},${center.y + halfL * 0.6}`;
  const topR = `${center.x + halfW},${center.y}`;
  const botR = `${center.x + halfW},${center.y + depth}`;
  const botB = `${center.x},${center.y + halfL * 0.6 + depth}`;
  return `${topB} ${topR} ${botR} ${botB}`;
}
