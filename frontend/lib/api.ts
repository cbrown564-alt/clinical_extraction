const API_BASE = "/api";
const STORAGE_DECISIONS_KEY = "mock-gold-audit-decisions";

async function fetchMockData<T>(path: string, init?: RequestInit): Promise<T> {
  // If it's a POST to decide, persist in localStorage and return success payload
  if (path === "/gold-audit/decide" && init?.method === "POST" && init.body) {
    const decision = JSON.parse(init.body as string);
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem(STORAGE_DECISIONS_KEY);
      const list = saved ? JSON.parse(saved) : [];
      // Remove any existing decision for same index+split
      const filtered = list.filter(
        (d: any) =>
          !(d.source_row_index === decision.source_row_index && d.split === decision.split)
      );
      filtered.push({
        ...decision,
        timestamp: new Date().toISOString(),
        auditor: "demo-user",
      });
      localStorage.setItem(STORAGE_DECISIONS_KEY, JSON.stringify(filtered));
    }
    return { status: "saved", decision } as unknown as T;
  }

  // Convert API path to static mock-data URL path
  let mockPath = "";
  if (path === "/registry") {
    mockPath = "/mock-data/registry.json";
  } else if (path.startsWith("/artifacts/")) {
    const runId = path.split("/")[2].split("?")[0];
    mockPath = `/mock-data/artifacts/${runId}.json`;
  } else if (path.startsWith("/gold-audit/rows")) {
    mockPath = "/mock-data/gold-audit/rows.json";
  } else if (path.startsWith("/gold-audit/decisions")) {
    mockPath = "/mock-data/gold-audit/decisions.json";
  } else if (path.startsWith("/records/")) {
    const parts = path.split("/");
    const split = parts[2];
    const index = parts[3];
    mockPath = `/mock-data/records/${split}/${index}.json`;
  } else if (path === "/health") {
    return { status: "ok" } as unknown as T;
  } else {
    throw new Error(`No mock fallback defined for path: ${path}`);
  }

  const res = await fetch(mockPath);
  if (!res.ok) {
    throw new Error(`Failed to load mock data from ${mockPath}: ${res.statusText}`);
  }
  
  const data = await res.json();

  // Merge localStorage decisions for mock mode
  if (path.startsWith("/gold-audit/decisions") && typeof window !== "undefined") {
    const saved = localStorage.getItem(STORAGE_DECISIONS_KEY);
    const localDecisions = saved ? JSON.parse(saved) : [];
    const mergedDecisions = [...(data.decisions || []), ...localDecisions];
    return {
      decisions: mergedDecisions,
      count: mergedDecisions.length,
    } as unknown as T;
  }

  // Update rows in queue as decided based on localStorage decisions
  if (path.startsWith("/gold-audit/rows") && typeof window !== "undefined") {
    const saved = localStorage.getItem(STORAGE_DECISIONS_KEY);
    const localDecisions = saved ? JSON.parse(saved) : [];
    const localIndices = new Set(localDecisions.map((d: any) => Number(d.source_row_index)));
    
    if (data.rows) {
      data.rows = data.rows.map((row: any) => {
        const hasDecision = localIndices.has(Number(row.source_row_index));
        return {
          ...row,
          has_decision: hasDecision || row.has_decision,
        };
      });
      data.decided = data.rows.filter((r: any) => r.has_decision || r.has_decision === "true").length;
    }
  }

  return data as T;
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
    if (!res.ok) {
      const text = await res.text().catch(() => "Unknown error");
      throw new Error(`HTTP ${res.status}: ${text}`);
    }
    return await res.json() as Promise<T>;
  } catch (error) {
    console.warn(`API request to ${path} failed:`, error, `. Falling back to mock data...`);
    return await fetchMockData<T>(path, init);
  }
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

export function fetchGoldAuditRows(split: string = "validation") {
  return fetchJson<import("./types").GoldAuditRowsResponse>(
    `/gold-audit/rows?split=${encodeURIComponent(split)}`
  );
}

export function fetchGoldAuditDecisions(split?: string) {
  const qs = split ? `?split=${encodeURIComponent(split)}` : "";
  return fetchJson<import("./types").GoldAuditDecisionsResponse>(`/gold-audit/decisions${qs}`);
}

export function postGoldAuditDecision(decision: import("./types").GoldAuditDecision) {
  return fetchJson<import("./types").GoldAuditDecisionResponse>("/gold-audit/decide", {
    method: "POST",
    body: JSON.stringify(decision),
  });
}

export function fetchGoldAuditNext(split: string = "validation") {
  return fetchJson<import("./types").GoldAuditNextResponse>(
    `/gold-audit/next?split=${encodeURIComponent(split)}`
  );
}
