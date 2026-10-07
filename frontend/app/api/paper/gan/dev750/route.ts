import { readSavedJson } from "@/lib/server/fixture-store";
import { join } from "node:path";

export const dynamic = "force-static";

function panelPath() {
  return join("results/letter-benchmarks", "gan", "dev750_panel.json");
}

export function GET() {
  try {
    const payload = readSavedJson(panelPath()) as Record<string, unknown>;
    return Response.json(payload);
  } catch {
    return Response.json({ detail: "Gan dev750 panel is not on disk yet" }, { status: 404 });
  }
}
