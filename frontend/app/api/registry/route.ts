import { ganRegistry } from "../_mock";
import { proxyPython } from "../_upstream";

export const dynamic = "force-static";

export async function GET() {
  const upstream = await proxyPython("/registry");
  if (upstream) return upstream;
  return Response.json(ganRegistry());
}
