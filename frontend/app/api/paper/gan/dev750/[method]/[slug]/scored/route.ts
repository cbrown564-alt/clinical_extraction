import { readFileSync } from "node:fs";
import { join } from "node:path";

export const dynamic = "force-static";

function scoredPath(method: string, slug: string) {
  return join(
    process.cwd(),
    "..",
    "paper_experiments",
    "gan",
    method,
    slug,
    "dev750",
    "scored.jsonl"
  );
}

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ method: string; slug: string }> }
) {
  const { method, slug } = await params;
  try {
    const rows = readFileSync(scoredPath(method, slug), "utf8")
      .split("\n")
      .filter((line) => line.trim())
      .map((line) => JSON.parse(line) as Record<string, unknown>);
    return Response.json({
      method,
      model_slug: slug,
      split: "dev750",
      count: rows.length,
      rows,
    });
  } catch {
    return Response.json({ detail: "scored rows are not on disk yet" }, { status: 404 });
  }
}
