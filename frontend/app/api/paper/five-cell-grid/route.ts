import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import {
  COMPARISON_KEY_TO_CELL,
  PAPER_CELLS,
  paperCellById,
  type PaperCellId,
} from "@/lib/paperCells";

export const dynamic = "force-dynamic";

type ComparisonCell = {
  extract_role?: string;
  encode_role?: string;
  select_role?: string;
  select?: number;
  ablation?: { extract?: number; encode?: number };
};

type ComparisonFile = {
  claim_boundary?: string;
  split?: string;
  n?: number;
  headline?: string;
  model?: string;
  cells?: Record<string, ComparisonCell>;
};

function gridPath(task: "gan" | "exect", slug: string): { path: string; split: string } | null {
  const repoRoot = join(process.cwd(), "..");
  if (task === "gan") {
    const path = join(
      repoRoot,
      "paper_experiments",
      "gan",
      "five_cell_grid",
      slug,
      "test450",
      "comparison.json"
    );
    return existsSync(path) ? { path, split: "test450" } : null;
  }
  const test60 = join(
    repoRoot,
    "paper_experiments",
    "exect",
    "five_cell_grid",
    slug,
    "test60",
    "comparison.json"
  );
  if (existsSync(test60)) return { path: test60, split: "test60" };
  const test450 = join(
    repoRoot,
    "paper_experiments",
    "exect",
    "five_cell_grid",
    slug,
    "test450",
    "comparison.json"
  );
  if (existsSync(test450)) return { path: test450, split: "test450" };
  return null;
}

function mapCells(raw: Record<string, ComparisonCell> | undefined) {
  const byId = new Map<PaperCellId, ComparisonCell>();
  for (const [key, value] of Object.entries(raw ?? {})) {
    const id = COMPARISON_KEY_TO_CELL[key];
    if (id) byId.set(id, value);
  }
  return PAPER_CELLS.map((cell) => {
    const row = byId.get(cell.id);
    const meta = paperCellById(cell.id);
    return {
      id: cell.id,
      order: cell.order,
      display_name: meta.displayName,
      short_label: meta.shortLabel,
      extract: row?.extract_role ?? meta.extract,
      encode: row?.encode_role ?? meta.encode,
      select: row?.select_role ?? meta.select,
      select_stop: row?.select ?? null,
      extract_ablation: row?.ablation?.extract ?? null,
      encode_ablation: row?.ablation?.encode ?? null,
      headline: meta.headline,
    };
  });
}

export function GET(request: Request) {
  const url = new URL(request.url);
  const taskParam = url.searchParams.get("task") === "exect" ? "exect" : "gan";
  const slug = url.searchParams.get("model") || "gemini37flash";
  const found = gridPath(taskParam, slug);
  if (!found) {
    return Response.json(
      { detail: `five_cell_grid comparison.json not found for ${taskParam}/${slug}` },
      { status: 404 }
    );
  }
  const payload = JSON.parse(readFileSync(found.path, "utf8")) as ComparisonFile;
  const rel = found.path.split("paper_experiments/")[1];
  return Response.json({
    task: taskParam,
    model: payload.model ?? slug,
    split: payload.split ?? found.split,
    n: payload.n ?? null,
    headline: payload.headline ?? "select",
    claim_boundary: payload.claim_boundary ?? null,
    source: `paper_experiments/${rel}`,
    cells: mapCells(payload.cells),
  });
}
