import { fetchJson } from "./client";
import { hydrateExectv2Run } from "@/lib/exectv2RunOptions";

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

export function fetchRules() {
  return request<import("../types").RulesResponse>("/rules");
}

export function fetchHealth() {
  return request<{ status: string }>("/health");
}

export function fetchRecords(split: string) {
  return request<import("../types").SplitRecordsResponse>(`/records/${split}`);
}

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

export function fetchArtifact(runId: string, artifactPath?: string, limit?: number) {
  const params = new URLSearchParams();
  if (artifactPath) params.set("artifact_path", artifactPath);
  if (limit !== undefined) params.set("limit", String(limit));
  const query = params.toString();
  return request<import("../types").ArtifactResponse>(
    `/artifacts/${runId}${query ? "?" + query : ""}`
  );
}

export function fetchExectv2Runs() {
  return request<import("../types").Exectv2RunsResponse>("/exectv2/runs");
}

export function fetchExectv2Run(runId: string) {
  return request<import("../types").Exectv2RunWireResponse>(
    `/exectv2/runs/${encodeURIComponent(runId)}`
  ).then(hydrateExectv2Run);
}

export function fetchExectv2SfInspection() {
  return request<import("../types").SfInspectionResponse>("/exectv2/sf-inspection");
}

export function fetchGan2026ComponentAblation() {
  return request<import("../types").Gan2026ComponentAblationResponse>(
    "/gan2026/component-ablation"
  );
}

export function fetchGan2026ComponentTransitions() {
  return request<import("../types").Gan2026ComponentTransitionsResponse>(
    "/gan2026/component-transitions"
  );
}

export function runAblation(params: {
  split: string;
  pipeline?: string;
  limit?: number;
  ablation_config?: import("../types").AblationConfigPayload;
}) {
  return request<import("../types").RunAblationResponse>("/run/ablation", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export function fetchPrompts() {
  return request<import("../types").PromptsResponse>("/prompts");
}

export function fetchGoldAuditRows(split: string = "validation", dataset: "gan2026" | "exectv2" = "gan2026") {
  return request<import("../types").GoldAuditRowsResponse>(
    `/gold-audit/rows?split=${encodeURIComponent(split)}&dataset=${dataset}`
  );
}

export function fetchGoldAuditDecisions(split?: string, dataset: "gan2026" | "exectv2" = "gan2026") {
  const params = new URLSearchParams({ dataset });
  if (split) params.set("split", split);
  return request<import("../types").GoldAuditDecisionsResponse>(`/gold-audit/decisions?${params}`);
}

export function postGoldAuditDecision(decision: import("../types").GoldAuditDecision) {
  return request<import("../types").GoldAuditDecisionResponse>("/gold-audit/decide", {
    method: "POST",
    body: JSON.stringify(decision),
  });
}

export function fetchGoldAuditNext(split: string = "validation", dataset: "gan2026" | "exectv2" = "gan2026") {
  return request<import("../types").GoldAuditNextResponse>(
    `/gold-audit/next?split=${encodeURIComponent(split)}&dataset=${dataset}`
  );
}

export function fetchQualifiedReviewPackets(reviewerId: string) {
  const params = new URLSearchParams({ reviewer_id: reviewerId });
  return request<import("../types").QualifiedReviewPacketsResponse>(
    `/qualified-review/packets?${params.toString()}`
  );
}

export function fetchQualifiedReviewDecisions(reviewerId: string) {
  const params = new URLSearchParams({ reviewer_id: reviewerId });
  return request<import("../types").QualifiedReviewDecisionsResponse>(
    `/qualified-review/decisions?${params.toString()}`
  );
}

export function postQualifiedReviewDecision(decision: import("../types").QualifiedReviewDecision) {
  return request<import("../types").QualifiedReviewDecideResponse>("/qualified-review/decide", {
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

// ── Gold noise (read-only inspection) ──

export function fetchGoldNoiseLedgers() {
  return request<import("../types").GoldNoiseLedgersResponse>("/gold-noise/ledgers");
}

export function fetchGoldNoiseGanAudit() {
  return request<import("../types").GoldNoiseGanAuditResponse>("/gold-noise/gan-audit");
}

export function fetchGoldNoiseIssues() {
  return request<import("../types").GoldNoiseIssuesResponse>("/gold-noise/issues");
}

export function fetchGoldNoiseRow(family: string, rowId: string) {
  const params = new URLSearchParams({ family, row_id: rowId });
  return request<import("../types").GoldNoiseItem>(
    `/gold-noise/row?${params.toString()}`
  );
}

export function fetchGoldNoiseHypotheses() {
  return request<import("../types").GoldNoiseHypothesesResponse>(
    "/gold-noise/hypotheses"
  );
}

export function fetchPromptTemplate(moduleName: string) {
  return request<import("../types").PromptTemplateResponse>(`/prompts/${moduleName}/template`);
}

export function tagError(params: {
  gold_category: string;
  predicted_category: string;
  purist_correct?: boolean;
  pragmatic_correct?: boolean;
}) {
  return request<import("../types").TagErrorResponse>("/tag-error", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export function fetchErrorTaxonomySchema() {
  return request<import("../types").ErrorTaxonomySchemaResponse>("/error-taxonomy/schema");
}

export function fetchHardSliceDefinitions() {
  return request<import("../types").HardSliceDefinitionsResponse>("/hard-slices/definitions");
}

export function fetchHardSliceMembership(rows: unknown[]) {
  return request<import("../types").HardSliceMembershipResponse>("/hard-slices/membership", {
    method: "POST",
    body: JSON.stringify({ rows }),
  });
}

export function fetchMeta() {
  return request<import("../types").MetaResponse>("/meta");
}
