const API_BASE = "/api";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export function runNote(params: {
  note_text: string;
  pipeline?: string;
  source_row_index?: number;
  gold_label?: string;
  gold_reference?: string;
  ablation_config?: import("./types").AblationConfigPayload;
}) {
  return fetchJson<import("./types").RunNoteResponse>("/run/note", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export function fetchRules() {
  return fetchJson<import("./types").RulesResponse>("/rules");
}

export function fetchHealth() {
  return fetchJson<{ status: string }>("/health");
}

export function fetchRecords(split: string) {
  return fetchJson<import("./types").SplitRecordsResponse>(`/records/${split}`);
}

export function fetchRecord(split: string, sourceRowIndex: number) {
  return fetchJson<import("./types").FullRecordResponse>(
    `/records/${split}/${sourceRowIndex}`
  );
}

export function fetchPipelineFamilies() {
  return fetchJson<import("./types").PipelineFamiliesResponse>(
    "/pipeline-families"
  );
}

export function fetchRegistry() {
  return fetchJson<import("./types").RegistryResponse>("/registry");
}

export function fetchArtifact(runId: string, artifactPath?: string, limit?: number) {
  const params = new URLSearchParams();
  if (artifactPath) params.set("artifact_path", artifactPath);
  if (limit !== undefined) params.set("limit", String(limit));
  const query = params.toString();
  return fetchJson<import("./types").ArtifactResponse>(
    `/artifacts/${runId}${query ? "?" + query : ""}`
  );
}

export function runAblation(params: {
  split: string;
  pipeline?: string;
  limit?: number;
  ablation_config?: import("./types").AblationConfigPayload;
}) {
  return fetchJson<import("./types").RunAblationResponse>("/run/ablation", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export function fetchPrompts() {
  return fetchJson<import("./types").PromptsResponse>("/prompts");
}
