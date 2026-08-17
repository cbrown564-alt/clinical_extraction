import { exectv2Payload, jsonError } from "../../../_mock";

export const dynamic = "force-static";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ runId: string }> }
) {
  const { runId } = await params;
  const payload = exectv2Payload() as {
    runs: Array<Record<string, unknown>>;
    shared_letters: Array<Record<string, unknown>>;
  };
  const run = payload.runs.find((item) => String(item.run_id) === runId);
  return run
    ? Response.json({ run, shared_letters: payload.shared_letters })
    : jsonError(404, "Run not found");
}
