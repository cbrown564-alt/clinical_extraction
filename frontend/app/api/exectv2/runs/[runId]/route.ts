import { exectv2Payload, jsonError } from "../../../_mock";
import { proxyPython } from "../../../_upstream";

export const dynamic = "force-static";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ runId: string }> }
) {
  const { runId } = await params;
  const upstream = await proxyPython(`/exectv2/runs/${encodeURIComponent(runId)}`);
  if (upstream) return upstream;
  const payload = exectv2Payload() as {
    runs: Array<Record<string, unknown>>;
    shared_letters: Array<Record<string, unknown>>;
  };
  const run = payload.runs.find((item) => String(item.run_id) === runId);
  return run
    ? Response.json({ run, shared_letters: payload.shared_letters })
    : jsonError(404, "Run not found");
}
