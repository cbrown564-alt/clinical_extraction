import { readSavedJson } from "@/lib/server/fixture-store";
import { join } from "node:path";

export const dynamic = "force-static";

function panelPath() {
  return join("results/letter-benchmarks", "exect", "dev140_panel.json");
}

export function GET() {
  try {
    const payload = readSavedJson(panelPath()) as Record<string, unknown>;
    return Response.json(payload);
  } catch {
    return Response.json({ detail: "ExECT dev140 panel is not on disk yet" }, { status: 404 });
  }
}
