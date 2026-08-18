import { readFileSync } from "node:fs";
import { join } from "node:path";

export const dynamic = "force-static";

function panelPath() {
  return join(process.cwd(), "..", "paper_experiments", "gan", "dev750_panel.json");
}

export function GET() {
  try {
    const payload = JSON.parse(readFileSync(panelPath(), "utf8")) as Record<string, unknown>;
    return Response.json(payload);
  } catch {
    return Response.json({ detail: "Gan dev750 panel is not on disk yet" }, { status: 404 });
  }
}
