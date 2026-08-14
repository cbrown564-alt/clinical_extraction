import { fetchJson } from "./client";
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
  return request<import("../types").LetterCatalogResponse>(`/datasets/${dataset}/letters`);
}

export function fetchLetter(dataset: DatasetId, letterId: string) {
  return request<import("../types").FullRecordResponse | import("../types").Exectv2SharedLetterRecord>(
    `/datasets/${dataset}/letters/${encodeURIComponent(letterId)}`
  );
}

export function fetchRuns(dataset: DatasetId) {
  if (dataset === "exectv2") {
    return request<import("../types").Exectv2RunsResponse>("/datasets/exectv2/runs");
  }
  return request<import("../types").DatasetRunsResponse>(`/datasets/${dataset}/runs`);
}

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

/** @deprecated Use fetchLetters("gan2026") */
export function fetchRecords(split: string) {
  return request<import("../types").SplitRecordsResponse>(`/records/${split}`);
}

/** @deprecated Use fetchLetter("gan2026", id) */
export function fetchRecord(split: string, sourceRowIndex: number) {
  return request<import("../types").FullRecordResponse>(
    `/records/${split}/${sourceRowIndex}`
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

/** @deprecated Use fetchRuns("exectv2") */
export function fetchExectv2Runs() {
  return fetchRuns("exectv2") as Promise<import("../types").Exectv2RunsResponse>;
}

/** @deprecated Use fetchRun("exectv2", runId) */
export function fetchExectv2Run(runId: string) {
  return fetchRun("exectv2", runId) as Promise<import("../types").Exectv2RunSummary>;
}

export function fetchGoldAuditRows(dataset: DatasetId = "gan2026") {
  return request<import("../types").GoldAuditRowsResponse>(
    `/gold-audit/rows?dataset=${dataset}`
  );
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

export function fetchGoldAuditNext(dataset: DatasetId = "gan2026") {
  return request<import("../types").GoldAuditNextResponse>(
    `/gold-audit/next?dataset=${dataset}`
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

export function fetchMeta() {
  return request<import("../types").MetaResponse>("/meta");
}
