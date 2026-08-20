import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

export const MOCK_ROOT = join(process.cwd(), "public", "mock-data");

export function readMockJson<T>(relativePath: string): T {
  return JSON.parse(readFileSync(join(MOCK_ROOT, relativePath), "utf8")) as T;
}

export function jsonError(status: number, message: string) {
  return Response.json({ detail: message }, { status });
}

export function ganRecordIds(): number[] {
  return readdirSync(join(MOCK_ROOT, "records", "validation"))
    .filter((name) => /^\d+\.json$/.test(name))
    .map((name) => Number(name.slice(0, -5)))
    .sort((a, b) => a - b);
}

export function ganRecord(sourceRowIndex: string) {
  if (!/^\d+$/.test(sourceRowIndex)) return null;
  try {
    return readMockJson<Record<string, unknown>>(
      `records/validation/${sourceRowIndex}.json`
    );
  } catch {
    return null;
  }
}

export function ganLetters() {
  return ganRecordIds().flatMap((id) => {
    const record = ganRecord(String(id));
    if (!record) return [];
    const note = String(record.note_text ?? "");
    return [
      {
        id: String(id),
        dataset: "gan2026" as const,
        split: String(record.split ?? "validation"),
        label: String(record.gold_label ?? "unknown"),
        preview: note.replace(/\s+/g, " ").trim().slice(0, 180),
        gold_summary: String(record.gold_label ?? "unknown"),
        gold_reference: String(record.gold_reference ?? ""),
        has_gold_reference: Boolean(record.gold_reference),
        row_ok: Boolean(record.row_ok ?? true),
      },
    ];
  });
}

type GanFamily = {
  run_id: string;
  kind: string;
  pipeline_family?: string;
  [key: string]: unknown;
};

const GAN_ARTIFACTS = {
  llm_with_rules:
    "frontend/public/mock-data/artifacts/gan2026_hybrid_multi_component_staged_assembly_v1_validation750_2026-06-05.json",
  llm: "frontend/public/mock-data/artifacts/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_gpt41mini_v02_live_2026-06-01.json",
  rules:
    "frontend/public/mock-data/artifacts/gan2026_rules_only_v1_baseline_2026-05-31.json",
} as const;

export function ganRegistry() {
  const registry = readMockJson<{ runs: Array<Record<string, unknown>> }>(
    "registry.json"
  );
  const familyCatalog = readMockJson<{ families: GanFamily[] }>(
    "pipeline-families.json"
  );
  const existing = new Set(registry.runs.map((run) => String(run.run_id)));
  const synthetic = familyCatalog.families
    .filter((family) => !existing.has(family.run_id))
    .map((family) => ({
      run_id: family.run_id,
      pipeline_family: family.pipeline_family ?? family.kind,
      artifact_paths: [
        GAN_ARTIFACTS[family.kind as keyof typeof GAN_ARTIFACTS] ??
          GAN_ARTIFACTS.rules,
      ],
      row_count: 750,
      split: "validation750",
      registry_roles: [],
    }));
  return { ...registry, runs: [...registry.runs, ...synthetic] };
}

export function ganArtifact(runId: string, letterId?: string) {
  const familyCatalog = readMockJson<{ families: GanFamily[] }>(
    "pipeline-families.json"
  );
  const family = familyCatalog.families.find((item) => item.run_id === runId);
  const file =
    GAN_ARTIFACTS[family?.kind as keyof typeof GAN_ARTIFACTS] ??
    (runId === "gan2026_rules_only_v1_baseline_2026-05-31"
      ? GAN_ARTIFACTS.rules
      : undefined);
  if (!file) return null;
  const payload = readMockJson<{ content: Array<Record<string, unknown>> }>(
    file.replace("frontend/public/mock-data/", "")
  );
  const content = letterId
    ? payload.content.filter(
        (row) => String(row.source_row_index) === String(letterId)
      )
    : payload.content;
  return {
    run_id: runId,
    artifact_path: file,
    artifact_type: "json",
    content,
  };
}

export function exectv2Payload() {
  const payload = readMockJson<{
    generated_on?: string;
    source_index?: string;
    shared_letters?: unknown[];
    runs?: Array<Record<string, unknown>>;
  }>("exectv2/runs.json");
  const runs = (payload.runs ?? []).filter(
    (run) => run.kind === "rules" || run.run_id === "rules"
  );
  return { ...payload, runs };
}
