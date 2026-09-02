import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { proxyPython } from "../../../_upstream";

export const dynamic = "force-static";

const CLAIM_BOUNDARY =
  "Descriptive output on 100 Gan dev750 letters. No inventory gold. Not scored. Not ExECT benchmark performance.";

function artifactDir(): string | null {
  const root = join(process.cwd(), "..");
  const candidates = [
    join(root, "experiments", "gan_inventory_feasibility_dev750_n100_20260828"),
    join(root, "paper_experiments", "gan", "inventory_feasibility_dev750_n100"),
  ];
  return (
    candidates.find(
      (dir) => existsSync(join(dir, "summary.json")) && existsSync(join(dir, "rows.jsonl"))
    ) ?? null
  );
}

function loadFromDisk(): Record<string, unknown> {
  const directory = artifactDir();
  if (!directory) {
    throw new Error("missing");
  }
  const summary = JSON.parse(readFileSync(join(directory, "summary.json"), "utf8")) as {
    schema_version?: string;
    study?: string;
    split?: string;
    sample_size?: number;
    sample_seed?: number;
    selected_source_row_indices?: number[];
    illustration_source_row_indices?: number[];
    program_entry?: string;
    program_config?: string;
    scorer?: null;
    family_summaries?: Record<string, unknown>;
  };
  if (summary.split !== "dev750") {
    throw new Error("locked");
  }
  const selected = new Set(
    (summary.selected_source_row_indices ?? []).map((index) => Number(index))
  );
  const letters = readFileSync(join(directory, "rows.jsonl"), "utf8")
    .split("\n")
    .filter((line) => line.trim())
    .map((line) => JSON.parse(line) as { source_row_index: number; mentions: unknown[] })
    .map((row) => {
      const index = Number(row.source_row_index);
      if (!selected.has(index)) {
        throw new Error("unsampled");
      }
      return { source_row_index: index, mentions: row.mentions ?? [] };
    })
    .sort((left, right) => left.source_row_index - right.source_row_index);
  return {
    schema_version: summary.schema_version ?? "gan_inventory_feasibility.v1",
    study: summary.study,
    split: "dev750",
    sample_size: summary.sample_size ?? letters.length,
    sample_seed: summary.sample_seed ?? 20260828,
    selected_source_row_indices: letters.map((letter) => letter.source_row_index),
    illustration_source_row_indices: summary.illustration_source_row_indices ?? [],
    program_entry: summary.program_entry ?? "run_letter",
    program_config: summary.program_config ?? "ACCEPTED_THREE_STAGE_CONFIG",
    scorer: summary.scorer ?? null,
    claim_boundary: CLAIM_BOUNDARY,
    family_summaries: summary.family_summaries ?? {},
    letters,
  };
}

export async function GET() {
  const upstream = await proxyPython("/paper/gan/inventory");
  if (upstream) return upstream;
  try {
    return Response.json(loadFromDisk());
  } catch {
    return Response.json(
      { detail: "Gan inventory feasibility artifact is not on disk yet" },
      { status: 404 }
    );
  }
}
