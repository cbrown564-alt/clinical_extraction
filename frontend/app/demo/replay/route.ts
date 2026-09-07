import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { resolve } from "node:path";
import { demoCases } from "@/lib/viva";

export const runtime = "nodejs";
const execute = promisify(execFile);

export async function POST(request: Request) {
  const origin = request.headers.get("origin");
  if (origin && origin !== new URL(request.url).origin) {
    return Response.json({ error: "Use the demo on this host." }, { status: 403 });
  }
  let id: unknown;
  try { ({ id } = await request.json()); }
  catch { return Response.json({ error: "Choose a saved case." }, { status: 400 }); }
  if (typeof id !== "number" || !demoCases.some(c => c.id === id)) {
    return Response.json({ error: "Choose a bundled development case." }, { status: 400 });
  }
  if (process.env.VERCEL === "1") {
    return Response.json({ error: "Live rules require the local Python environment. The saved decision is available." }, { status: 503 });
  }
  try {
    const root = resolve(process.cwd(), "..");
    const { stdout } = await execute(resolve(root, ".venv/bin/python"), [resolve(root, "scripts/viva_demo.py"), "--decide", String(id)], {
      cwd: root, timeout: 15000, maxBuffer: 1024 * 1024,
    });
    return Response.json(JSON.parse(stdout), { headers: { "Cache-Control": "no-store" } });
  } catch {
    return Response.json({ error: "The local rules could not run. Retry or use the saved decision." }, { status: 503 });
  }
}
