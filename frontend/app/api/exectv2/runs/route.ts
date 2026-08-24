import { exectv2Payload } from "../../_mock";
import { proxyPython } from "../../_upstream";

export const dynamic = "force-static";

export async function GET() {
  const upstream = await proxyPython("/exectv2/runs");
  if (upstream) return upstream;
  return Response.json(exectv2Payload());
}
