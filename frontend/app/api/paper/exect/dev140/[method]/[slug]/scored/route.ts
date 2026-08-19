import { readFileSync } from "node:fs";
import { join } from "node:path";

export const dynamic = "force-static";

const METHODS = new Set(["exect_llm_only", "exect_llm_with_rules"]);

function scoredPath(method: string, slug: string) {
  return join(
    process.cwd(),
    "..",
    "paper_experiments",
    "exect",
    method,
    slug,
    "dev140",
    "scored.jsonl"
  );
}

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ method: string; slug: string }> }
) {
  const { method, slug } = await params;
  if (!METHODS.has(method)) {
    return Response.json({ detail: "unknown ExECT paper method" }, { status: 404 });
  }
  try {
    const rows = readFileSync(scoredPath(method, slug), "utf8")
      .split("\n")
      .filter((line) => line.trim())
      .map((line) => JSON.parse(line) as Record<string, unknown>);
    return Response.json({
      method,
      model_slug: slug,
      split: "dev140",
      count: rows.length,
      rows,
    });
  } catch {
    return Response.json({ detail: "scored rows are not on disk yet" }, { status: 404 });
  }
}
