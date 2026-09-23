import { readFileSync } from "node:fs";
import { join } from "node:path";

export const dynamic = "force-dynamic";

export function GET(request: Request) {
  if (process.env.VERCEL === "1") {
    return Response.json({ detail: "Local research artifact unavailable" }, { status: 404 });
  }
  try {
    const version = new URL(request.url).searchParams.get("version");
    const path = version === "v081"
      ? join(process.cwd(), "..", "runs", "seizure_finding_annotation_v0_8_1", "dev750_r8_saved", "review_bundle.json")
      : version === "v08"
        ? join(process.cwd(), "..", "runs", "seizure_finding_annotation_v0_8", "dev750_r8_saved", "review_bundle.json")
        : join(process.cwd(), "..", "runs", "one_shot_frequency_v2_measurements_r8", "dev750_rich_only", "review_bundle.json");
    return new Response(readFileSync(path), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "private, no-store" } });
  } catch {
    return Response.json({ detail: "Build the local bundle with .venv/bin/python scripts/benchmarks/retime_findings_v081.py, score_findings_v08.py, or build_r8_review.py" }, { status: 404 });
  }
}
