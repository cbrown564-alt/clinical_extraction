import { readFileSync } from "node:fs";
import { join } from "node:path";

export const dynamic = "force-static";

const METHODS = new Set([
  "exect_llm_only",
  "exect_llm_pre_post",
  "exect_llm_with_rules",
  "llm_extract",
  "llm_encode",
  "llm_select",
  "llm_schema", // sealed-artifact alias
  "llm_revise", // sealed-artifact alias
  "llm_format", // sealed-artifact alias
  "llm_post", // sealed-artifact alias
  "llm_pre_post",
]);

function normalizeMethod(method: string): string {
  if (method === "llm_format") return "llm_encode";
  if (method === "llm_schema") return "llm_extract";
  if (method === "llm_post" || method === "llm_revise") return "llm_select";
  return method;
}

function scoredPath(method: string, slug: string) {
  const root = join(process.cwd(), "..", "paper_experiments", "exect");
  const resolved = normalizeMethod(method);
  if (resolved === "exect_llm_with_rules" || resolved === "llm_pre_post") {
    return join(root, "exect_llm_pre_post", slug, "dev140", "scored.jsonl");
  }
  if (
    resolved === "llm_extract" ||
    resolved === "llm_encode" ||
    resolved === "llm_select"
  ) {
    return join(root, "rungs", slug, "dev140", "scored.jsonl");
  }
  return join(root, resolved, slug, "dev140", "scored.jsonl");
}

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ method: string; slug: string }> }
) {
  const { method, slug } = await params;
  if (!METHODS.has(method)) {
    return Response.json({ detail: "unknown ExECT paper method" }, { status: 404 });
  }
  const resolved = normalizeMethod(method);
  try {
    const rows = readFileSync(scoredPath(method, slug), "utf8")
      .split("\n")
      .filter((line) => line.trim())
      .map((line) => JSON.parse(line) as Record<string, unknown>);
    return Response.json({
      method: resolved,
      model_slug: slug,
      split: "dev140",
      count: rows.length,
      rows,
    });
  } catch {
    return Response.json({ detail: "scored rows are not on disk yet" }, { status: 404 });
  }
}
