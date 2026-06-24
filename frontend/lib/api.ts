import type { GoldAuditDecision, GoldAuditRow } from "./types";

const API_BASE = "/api";
const STORAGE_DECISIONS_KEY = "mock-gold-audit-decisions";

type MockGoldAuditRow = Pick<GoldAuditRow, "source_row_index"> & {
  has_decision?: boolean | string;
};
type MockRowsPayload = {
  rows?: MockGoldAuditRow[];
  decided?: number;
  decisions?: GoldAuditDecision[];
};

async function fetchMockData<T>(path: string, init?: RequestInit): Promise<T> {
  // If it's a POST to decide, persist in localStorage and return success payload
  if (path === "/gold-audit/decide" && init?.method === "POST" && init.body) {
    const decision = JSON.parse(init.body as string) as GoldAuditDecision;
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem(STORAGE_DECISIONS_KEY);
      const list = saved ? (JSON.parse(saved) as GoldAuditDecision[]) : [];
      // Remove any existing decision for same index+split
      const filtered = list.filter(
        (d) =>
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

  // Handle /run/note (POST)
  if (path === "/run/note" && init?.method === "POST" && init.body) {
    const params = JSON.parse(init.body as string);
    const sri = params.source_row_index;
    
    // Check if we have precomputed run results for this source_row_index
    const precomputedIndices = [10, 40, 79, 103, 128, 156, 180, 182, 187, 190, 198, 212, 218, 243, 278];
    if (sri && precomputedIndices.includes(Number(sri))) {
      const runRes = await fetch(`/mock-data/run-note/validation/${sri}.json`);
      if (runRes.ok) {
        return await runRes.json() as T;
      }
    }
    
    // Fallback dynamic generation for run note
    const goldLabel = params.gold_label || "4 per day";
    const goldRef = params.gold_reference || "four per day";
    return {
      pipeline: params.pipeline || "rules_only",
      source_row_index: sri || 999,
      gold_label: goldLabel,
      result: {
        output: {
          final_value: goldLabel,
          rationale: "Selected the highest normalized current frequency candidate (Simulated).",
          evidence: goldRef
        },
        diagnostics: {
          candidate_events: [
            {
              event_id: "event_1",
              kind: "frequency_rate",
              raw_value: goldLabel,
              evidence: goldRef,
              start_char: 10,
              end_char: 25,
              rule_id: "rate.direct_count_per_period",
              rule_group: "portable_rate_expressions",
              portability: "seizure_frequency",
              match_groups: {
                count: "four",
                denominator: null,
                unit: "day"
              }
            }
          ],
          normalized_events: [
            {
              event_id: "event_1",
              normalized_label: goldLabel,
              semantic_kind: "frequency",
              monthly_frequency: 120.0,
              validation_errors: []
            }
          ],
          final_selection: {
            final_label: goldLabel,
            final_kind: "frequency",
            selected_event_ids: ["event_1"],
            rationale: "Selected the highest normalized current frequency candidate (Simulated).",
            evidence: goldRef,
            monthly_frequency: 120.0,
            validation_errors: []
          },
          evidence_valid: true
        }
      }
    } as unknown as T;
  }

  // Handle /run/ablation (POST)
  if (path === "/run/ablation" && init?.method === "POST" && init.body) {
    const params = JSON.parse(init.body as string);
    const split = params.split || "validation";
    const pipeline = params.pipeline || "rules_only";
    const config = params.ablation_config || {};
    const disabledCount = config.disabled_rule_ids?.length || 0;
    const accuracy = Math.max(0.6, 0.93 - disabledCount * 0.05);
    const mockIndices = [10, 40, 79, 103, 128, 156, 180, 182, 187, 190, 198, 212, 218, 243, 278];
    const commonLabels = ["4 per day", "1 per week", "2 to 3 per month", "seizure free for 6 month", "unknown"];
    
    const rows = mockIndices.map((sri, idx) => {
      const gold = commonLabels[idx % commonLabels.length];
      const isCorrect = idx % 10 !== 0 && (disabledCount === 0 || idx % 4 !== 0);
      const prediction = isCorrect ? gold : "unknown";
      return {
        source_row_index: sri,
        prediction_label: prediction,
        gold_label: gold,
        purist_predicted_category: isCorrect ? "seizure_freq_more1week_less1day" : "seizure_freq_unknown",
        purist_gold_category: "seizure_freq_more1week_less1day",
        pragmatic_predicted_category: isCorrect ? "seizure_frequent" : "seizure_freq_unknown",
        pragmatic_gold_category: "seizure_frequent",
        evidence_valid: true
      };
    });

    return {
      split,
      pipeline,
      row_count: rows.length,
      ablation_config: config,
      summary: {
        total: rows.length,
        purist: {
          accuracy,
          f1: accuracy,
          precision: accuracy,
          recall: accuracy,
          per_label: {}
        },
        pragmatic: {
          accuracy,
          f1: accuracy,
          precision: accuracy,
          recall: accuracy,
          per_label: {}
        }
      },
      rows
    } as unknown as T;
  }

  // Handle /gold-audit/next
  if (path.startsWith("/gold-audit/next")) {
    const rowsRes = await fetchMockData<import("./types").GoldAuditRowsResponse>("/gold-audit/rows", init);
    const nextRow = rowsRes.rows.find((r) => !r.has_decision) || null;
    return {
      split: "validation",
      row: nextRow,
      message: nextRow ? undefined : "All rows adjudicated!"
    } as unknown as T;
  }

  // Convert API path to static mock-data URL path
  let mockPath = "";
  if (path === "/registry") {
    mockPath = "/mock-data/registry.json";
  } else if (path === "/pipeline-families") {
    mockPath = "/mock-data/pipeline-families.json";
  } else if (path === "/rules") {
    mockPath = "/mock-data/rules.json";
  } else if (path === "/prompts") {
    mockPath = "/mock-data/prompts.json";
  } else if (path === "/exectv2/runs") {
    mockPath = "/mock-data/exectv2/runs.json";
  } else if (path === "/exectv2/component-ablation") {
    mockPath = "/mock-data/exectv2/component-ablation.json";
  } else if (path === "/exectv2/component-transitions") {
    mockPath = "/mock-data/exectv2/component-transitions.json";
  } else if (path === "/gan2026/component-ablation") {
    mockPath = "/mock-data/gan2026/component-ablation.json";
  } else if (path === "/gan2026/component-transitions") {
    mockPath = "/mock-data/gan2026/component-transitions.json";
  } else if (path === "/exectv2/reliability-scorecard") {
    mockPath = "/mock-data/exectv2/reliability-scorecard.json";
  } else if (path === "/gan2026/reliability-scorecard") {
    mockPath = "/mock-data/gan2026/reliability-scorecard.json";
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
    if (index === undefined) {
      mockPath = `/mock-data/records/${split}.json`;
    } else {
      mockPath = `/mock-data/records/${split}/${index}.json`;
    }
  } else if (path === "/hard-slices/definitions") {
    return {
      slices: [
        {
          slice_name: "candidate_generation_rescue",
          component_focus: "candidate generation",
          membership_rule: "Atlas row is Purist-wrong and first_failure_owner is candidate_generation.",
          primary_metric: "Candidate-recall rescue rate before final-label promotion; final policy keeps the deterministic safety floor unless a rescue is predeclared and ablated."
        },
        {
          slice_name: "candidate_generation_unknown_seizure_free_boundary",
          component_focus: "candidate generation",
          membership_rule: "Atlas row is Purist-wrong, first_failure_owner is candidate_generation, and hidden_families includes unknown_boundary or seizure_free_duration.",
          primary_metric: "Boundary-state recall without converting uncertain seizure-free language into a prediction-bearing deterministic repair."
        },
        {
          slice_name: "projection_arbitration",
          component_focus: "graph/final projection",
          membership_rule: "Atlas row is Purist-wrong and first_failure_owner is projection or final_projection.",
          primary_metric: "Projection-variant correction precision, mechanical-correct to projected-wrong regressions, and selected-evidence/source trace validity."
        },
        {
          slice_name: "projection_unknown_seizure_free_arbitration",
          component_focus: "graph/final projection",
          membership_rule: "Atlas row is Purist-wrong, first_failure_owner is projection or final_projection, and hidden_families includes unknown_boundary, seizure_free_duration, or current_vs_historical.",
          primary_metric: "Unknown/seizure-free/current-vs-historical arbitration precision with no broad validation retuning."
        }
      ]
    } as unknown as T;
  } else if (path === "/health") {
    return { status: "ok" } as unknown as T;
  } else {
    throw new Error(`No mock fallback defined for path: ${path}`);
  }

  const res = await fetch(mockPath);
  if (!res.ok) {
    throw new Error(`Failed to load mock data from ${mockPath}: ${res.statusText}`);
  }
  
  const data = (await res.json()) as MockRowsPayload;

  // Merge localStorage decisions for mock mode
  if (path.startsWith("/gold-audit/decisions") && typeof window !== "undefined") {
    const saved = localStorage.getItem(STORAGE_DECISIONS_KEY);
    const localDecisions = saved ? (JSON.parse(saved) as GoldAuditDecision[]) : [];
    const mergedDecisions = [...(data.decisions || []), ...localDecisions];
    return {
      decisions: mergedDecisions,
      count: mergedDecisions.length,
    } as unknown as T;
  }

  // Update rows in queue as decided based on localStorage decisions
  if (path.startsWith("/gold-audit/rows") && typeof window !== "undefined") {
    const saved = localStorage.getItem(STORAGE_DECISIONS_KEY);
    const localDecisions = saved ? (JSON.parse(saved) as GoldAuditDecision[]) : [];
    const localIndices = new Set(localDecisions.map((d) => Number(d.source_row_index)));
    
    if (data.rows) {
      data.rows = data.rows.map((row) => {
        const hasDecision = localIndices.has(Number(row.source_row_index));
        return {
          ...row,
          has_decision: hasDecision || row.has_decision,
        };
      });
      data.decided = data.rows.filter((r) => r.has_decision || r.has_decision === "true").length;
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

export function fetchExectv2Runs() {
  return fetchJson<import("./types").Exectv2RunsResponse>("/exectv2/runs");
}

export function fetchExectv2ReliabilityScorecard() {
  return fetchJson<import("./types").Exectv2ReliabilityScorecardResponse>(
    "/exectv2/reliability-scorecard"
  );
}

export function fetchExectv2ComponentAblation() {
  return fetchJson<import("./types").Exectv2ComponentAblationResponse>(
    "/exectv2/component-ablation"
  );
}

export function fetchExectv2ComponentTransitions() {
  return fetchJson<import("./types").Exectv2ComponentTransitionsResponse>(
    "/exectv2/component-transitions"
  );
}

export function fetchGan2026ComponentAblation() {
  return fetchJson<import("./types").Gan2026ComponentAblationResponse>(
    "/gan2026/component-ablation"
  );
}

export function fetchGan2026ComponentTransitions() {
  return fetchJson<import("./types").Gan2026ComponentTransitionsResponse>(
    "/gan2026/component-transitions"
  );
}

export function fetchReliabilityScorecard(dataset: import("./types").ClinicalTask) {
  const path =
    dataset === "exectv2"
      ? "/exectv2/reliability-scorecard"
      : "/gan2026/reliability-scorecard";
  return fetchJson<import("./types").ReliabilityScorecardResponse>(path);
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

export function fetchPromptTemplate(moduleName: string) {
  return fetchJson<import("./types").PromptTemplateResponse>(`/prompts/${moduleName}/template`);
}

export function tagError(params: {
  gold_category: string;
  predicted_category: string;
  purist_correct?: boolean;
  pragmatic_correct?: boolean;
}) {
  return fetchJson<import("./types").TagErrorResponse>("/tag-error", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export function fetchErrorTaxonomySchema() {
  return fetchJson<import("./types").ErrorTaxonomySchemaResponse>("/error-taxonomy/schema");
}

export function fetchHardSliceDefinitions() {
  return fetchJson<import("./types").HardSliceDefinitionsResponse>("/hard-slices/definitions");
}

export function fetchHardSliceMembership(rows: unknown[]) {
  return fetchJson<import("./types").HardSliceMembershipResponse>("/hard-slices/membership", {
    method: "POST",
    body: JSON.stringify({ rows }),
  });
}

export function fetchMeta() {
  return fetchJson<import("./types").MetaResponse>("/meta");
}
