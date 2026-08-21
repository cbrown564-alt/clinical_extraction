import { fetchJson } from "./client";
import { filterBrowsableLetters } from "@/lib/datasets/splits";
import { hydrateExectv2Run } from "@/lib/exectv2RunOptions";
import type { DatasetId } from "@/lib/datasets/types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  return fetchJson<T>(path, init);
}

export function runNote(params: {
  note_text: string;
  pipeline?: string;
  source_row_index?: number;
  gold_label?: string;
  gold_reference?: string;
  ablation_config?: import("../types").AblationConfigPayload;
}) {
  return request<import("../types").RunNoteResponse>("/run/note", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export function fetchHealth() {
  return request<{ status: string }>("/health");
}

export function fetchLetters(dataset: DatasetId) {
  return request<import("../types").LetterCatalogResponse>(
    `/datasets/${dataset}/letters`
  ).then((payload) => {
    const letters = filterBrowsableLetters(payload.letters);
    return { ...payload, letters, count: letters.length };
  });
}

export function fetchLetter(dataset: "gan2026", letterId: string): Promise<import("../types").FullRecordResponse>;
export function fetchLetter(dataset: "exectv2", letterId: string): Promise<import("../types").Exectv2SharedLetterRecord>;
export function fetchLetter(dataset: DatasetId, letterId: string) {
  return request(
    `/datasets/${dataset}/letters/${encodeURIComponent(letterId)}`
  );
}

export function fetchRuns(dataset: "exectv2"): Promise<import("../types").Exectv2RunsResponse>;
export function fetchRuns(dataset: "gan2026"): Promise<import("../types").DatasetRunsResponse>;
export function fetchRuns(dataset: DatasetId) {
  return request(`/datasets/${dataset}/runs`);
}

export function fetchRun(dataset: "exectv2", runId: string): Promise<import("../types").Exectv2RunSummary>;
export function fetchRun(dataset: "gan2026", runId: string): Promise<import("../types").DatasetRunResponse>;
export function fetchRun(dataset: DatasetId, runId: string) {
  if (dataset === "exectv2") {
    return request<import("../types").Exectv2RunWireResponse>(
      `/datasets/exectv2/runs/${encodeURIComponent(runId)}`
    ).then(hydrateExectv2Run);
  }
  return request<import("../types").DatasetRunResponse>(
    `/datasets/${dataset}/runs/${encodeURIComponent(runId)}`
  );
}

export function fetchPipelineFamilies() {
  return request<import("../types").PipelineFamiliesResponse>("/pipeline-families");
}

export function fetchRegistry() {
  return request<import("../types").RegistryResponse>("/registry");
}

export type GanDev750Method = "gan_llm_only" | "gan_llm_with_rules";

export type GanDev750PanelCell = {
  model_slug: string;
  model: string;
  label: string;
  method: GanDev750Method;
  status: "present" | "pending";
  path: string;
  n: number;
  rows?: string;
  scored?: string | null;
  comparison?: string;
  purist_correct?: number | null;
  purist_accuracy?: number | null;
  living_effort?: string | null;
};

export type GanDev750Panel = {
  schema_version: string;
  split: "dev750";
  methods: GanDev750Method[];
  models: string[];
  method_identity: string;
  living_effort: {
    hosted_reasoning: string;
    deepseek: string;
    local: string;
  };
  notes_source: {
    split_machine: string;
    frontend: string;
  };
  cells: GanDev750PanelCell[];
};

export type GanDev750ScoredRow = {
  source_row_index: number;
  letter_id: string;
  method: GanDev750Method;
  predicted_label: string | null;
  purist_correct: boolean | null;
  pragmatic_correct: boolean | null;
  parse_ok: boolean;
};

export function fetchGanDev750Panel() {
  return request<GanDev750Panel>("/paper/gan/dev750");
}

export function fetchGanDev750Scored(method: GanDev750Method, slug: string) {
  return request<{
    method: GanDev750Method;
    model_slug: string;
    split: "dev750";
    count: number;
    rows: GanDev750ScoredRow[];
  }>(`/paper/gan/dev750/${method}/${encodeURIComponent(slug)}/scored`);
}

export type ExectDev140Method =
  | "exect_llm_only"
  | "exect_llm_pre_post"
  | "exect_llm_with_rules"
  | "exect_rules"
  | "llm_schema"
  | "llm_encode"
  | "llm_revise"
  | "llm_format" // sealed-artifact alias
  | "llm_post" // sealed-artifact alias
  | "llm_pre_post";

export type ExectDev140PanelCell = {
  model_slug: string;
  model: string;
  label: string;
  method: ExectDev140Method;
  status: "present" | "pending";
  path: string;
  n: number;
  rows?: string;
  scored?: string | null;
  comparison?: string;
  raw_headline_f1?: number | null;
  hybrid_headline_f1?: number | null;
  living_effort?: string | null;
};

export type ExectDev140Panel = {
  schema_version: string;
  split: "dev140";
  methods: ExectDev140Method[];
  models: string[];
  method_identity: string;
  living_effort: {
    hosted_reasoning: string;
    deepseek: string;
    local: string;
  };
  notes_source: {
    split_machine: string;
    frontend: string;
  };
  cells: ExectDev140PanelCell[];
};

export type ExectDev140ScoredRow = {
  letter_id: string;
  method: ExectDev140Method;
  raw_headline_f1: number | null;
  hybrid_headline_f1?: number | null;
  raw_four_family_letter_exact: boolean | null;
  hybrid_four_family_letter_exact?: boolean | null;
  parse_ok: boolean;
};

export function fetchExectDev140Panel() {
  return request<ExectDev140Panel>("/paper/exect/dev140");
}

export function fetchExectDev140Scored(method: ExectDev140Method, slug: string) {
  return request<{
    method: ExectDev140Method;
    model_slug: string;
    split: "dev140";
    count: number;
    rows: ExectDev140ScoredRow[];
  }>(`/paper/exect/dev140/${method}/${encodeURIComponent(slug)}/scored`);
}

export function fetchArtifact(
  runId: string,
  artifactPath?: string,
  limit?: number,
  letterId?: string
) {
  const params = new URLSearchParams();
  if (artifactPath) params.set("artifact_path", artifactPath);
  if (limit !== undefined) params.set("limit", String(limit));
  if (letterId) params.set("letter_id", letterId);
  const query = params.toString();
  return request<import("../types").ArtifactResponse>(
    `/artifacts/${runId}${query ? "?" + query : ""}`
  );
}


export function fetchSemanticSupportReviewPackets(reviewerId: string) {
  const params = new URLSearchParams({ reviewer_id: reviewerId });
  return request<import("../types").SemanticSupportReviewPacketsResponse>(
    `/semantic-support-review/packets?${params.toString()}`
  );
}

export function fetchSemanticSupportReviewDecisions(reviewerId: string) {
  const params = new URLSearchParams({ reviewer_id: reviewerId });
  return request<import("../types").SemanticSupportReviewDecisionsResponse>(
    `/semantic-support-review/decisions?${params.toString()}`
  );
}

export function postSemanticSupportReviewDecision(
  decision: import("../types").SemanticSupportReviewDecision
) {
  return request<import("../types").SemanticSupportReviewDecideResponse>(
    "/semantic-support-review/decide",
    { method: "POST", body: JSON.stringify(decision) }
  );
}

export function fetchSemanticSupportReviewExport(reviewerId: string) {
  const params = new URLSearchParams({ reviewer_id: reviewerId });
  return request<import("../types").SemanticSupportReviewExport>(
    `/semantic-support-review/export?${params.toString()}`
  );
}


