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

export function fetchGoldAuditRows(dataset: DatasetId = "gan2026") {
  return request<import("../types").GoldAuditRowsResponse>(
    `/gold-audit/rows?dataset=${dataset}`
  ).then((payload) => {
    const rows = filterBrowsableLetters(payload.rows ?? []);
    return { ...payload, rows, total: rows.length };
  });
}

export function fetchGoldAuditDecisions(dataset: DatasetId = "gan2026") {
  return request<import("../types").GoldAuditDecisionsResponse>(
    `/gold-audit/decisions?dataset=${dataset}`
  );
}

export function postGoldAuditDecision(decision: import("../types").GoldAuditDecision) {
  return request<import("../types").GoldAuditDecisionResponse>("/gold-audit/decide", {
    method: "POST",
    body: JSON.stringify(decision),
  });
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


