import { readFileSync } from "node:fs";
import { join } from "node:path";

export const dynamic = "force-dynamic";

export function GET(request: Request) {
  if (process.env.VERCEL === "1") {
    return Response.json({ detail: "Local research artifact unavailable" }, { status: 404 });
  }
  try {
    const version = new URL(request.url).searchParams.get("version");
    const path = version === "v083"
      ? join(process.cwd(), "..", "runs", "seizure_finding_annotation_v0_8_3", "dev750_r8_saved", "review_bundle.json")
      : version === "v082"
      ? join(process.cwd(), "..", "runs", "seizure_finding_annotation_v0_8_2", "dev750_r8_saved", "review_bundle.json")
      : version === "v081"
      ? join(process.cwd(), "..", "runs", "seizure_finding_annotation_v0_8_1", "dev750_r8_saved", "review_bundle.json")
      : version === "v08"
        ? join(process.cwd(), "..", "runs", "seizure_finding_annotation_v0_8", "dev750_r8_saved", "review_bundle.json")
        : join(process.cwd(), "..", "runs", "one_shot_frequency_v2_measurements_r8", "dev750_rich_only", "review_bundle.json");
    if (version === "v081") {
      const bundle = JSON.parse(readFileSync(path, "utf8"));
      const components = JSON.parse(readFileSync(join(process.cwd(), "..", "results", "letter-benchmarks", "gan", "seizure_finding_annotation_v0_8_1", "dev750_r8_saved", "component_score.json"), "utf8"));
      const byLetter = new Map<number, unknown>(components.rows.map((row: { source_row_index: number }) => [row.source_row_index, row]));
      bundle.rows = bundle.rows.map((row: { source_row_index: number }) => ({ ...row, component_score: byLetter.get(row.source_row_index) }));
      bundle.component_aggregate = components.aggregate;
      return Response.json(bundle, { headers: { "cache-control": "private, no-store" } });
    }
    return new Response(readFileSync(path), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "private, no-store" } });
  } catch {
    return Response.json({ detail: "Build the local bundle with .venv/bin/python scripts/benchmarks/revise_findings_v083.py, revise_findings_v082.py, retime_findings_v081.py, score_findings_v08.py, or build_r8_review.py" }, { status: 404 });
  }
}
