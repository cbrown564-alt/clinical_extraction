import { exectv2Payload, jsonError } from "../../../../_mock";
import { proxyPython } from "../../../../_upstream";

export const dynamic = "force-static";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ dataset: string; runId: string }> }
) {
  const { dataset, runId } = await params;
  const upstream = await proxyPython(
    `/datasets/${encodeURIComponent(dataset)}/runs/${encodeURIComponent(runId)}`
  );
  if (upstream) return upstream;
  if (dataset === "exectv2") {
    const payload = exectv2Payload() as {
      generated_on?: string;
      source_index?: string;
      runs: Array<Record<string, unknown>>;
      shared_letters: Array<Record<string, unknown>>;
    };
    const run = payload.runs.find((item) => String(item.run_id) === runId);
    return run
      ? Response.json({
          generated_on: payload.generated_on,
          source_index: payload.source_index,
          shared_letters: payload.shared_letters,
          run,
        })
      : jsonError(404, "Run not found");
  }
  return jsonError(404, "Unknown dataset");
}
