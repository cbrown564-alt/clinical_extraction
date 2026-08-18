import { readFileSync } from "node:fs";
import { join } from "node:path";

export const dynamic = "force-static";

function scoredPath(slug: string) {
  return join(
    process.cwd(),
    "..",
    "paper_experiments",
    "exect",
    "exect_llm_with_rules",
    slug,
    "dev140",
    "scored.jsonl"
  );
}

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;
  try {
    const rows = readFileSync(scoredPath(slug), "utf8")
      .split("\n")
      .filter((line) => line.trim())
      .map((line) => JSON.parse(line) as Record<string, unknown>);
    return Response.json({
      method: "exect_llm_with_rules",
      model_slug: slug,
      split: "dev140",
      count: rows.length,
      rows,
    });
  } catch {
    return Response.json({ detail: "scored rows are not on disk yet" }, { status: 404 });
  }
}
