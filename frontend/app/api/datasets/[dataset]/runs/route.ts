import { exectv2Payload, jsonError, readMockJson } from "../../../_mock";
import { proxyPython } from "../../../_upstream";

export const dynamic = "force-static";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ dataset: string }> }
) {
  const { dataset } = await params;
  const upstream = await proxyPython(`/datasets/${encodeURIComponent(dataset)}/runs`);
  if (upstream) return upstream;
  if (dataset === "exectv2") {
    return Response.json(exectv2Payload());
  }
  if (dataset === "gan2026") {
    const families = readMockJson<{ families: unknown[] }>("pipeline-families.json");
    return Response.json({
      dataset,
      split: "dev750",
      runs: families.families,
    });
  }
  return jsonError(404, "Unknown dataset");
}
