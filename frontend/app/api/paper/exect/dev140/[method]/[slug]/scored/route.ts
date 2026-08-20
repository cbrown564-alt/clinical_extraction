import { readFileSync } from "node:fs";
import { join } from "node:path";

export const dynamic = "force-static";

const METHODS = new Set([
  "exect_llm_only",
  "exect_llm_pre_post",
  "exect_llm_with_rules",
  "llm_schema",
  "llm_format",
  "llm_post",
  "llm_pre_post",
]);

function scoredPath(method: string, slug: string) {
  const root = join(process.cwd(), "..", "paper_experiments", "exect");
  if (method === "exect_llm_with_rules" || method === "llm_pre_post") {
    return join(root, "exect_llm_pre_post", slug, "dev140", "scored.jsonl");
  }
  if (method === "llm_schema" || method === "llm_format" || method === "llm_post") {
    return join(root, "rungs", slug, "dev140", "scored.jsonl");
  }
  return join(root, method, slug, "dev140", "scored.jsonl");
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
