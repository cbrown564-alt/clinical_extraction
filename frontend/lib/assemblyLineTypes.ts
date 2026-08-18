export type AssemblyBand = "propose" | "reshape" | "gate" | "leave";

export interface FactSpanData {
  start: number;
  end: number;
  text: string;
}

export interface FactGoldData {
  label: string;
  has_counterpart: boolean;
  note: string;
}

export interface FactTransformData {
  stage_id: string;
  stage_name: string;
  band: AssemblyBand;
  entered: string;
  left: string;
  idle: boolean;
  note: string;
}

export interface PredictedFactData {
  fact_id: string;
  label: string;
  span: FactSpanData | null;
  transforms: FactTransformData[];
  gold: FactGoldData;
}

export const ASSEMBLY_BANDS: { id: AssemblyBand; label: string }[] = [
  { id: "propose", label: "Propose" },
  { id: "reshape", label: "Reshape" },
  { id: "gate", label: "Gate" },
  { id: "leave", label: "Leave" },
];
