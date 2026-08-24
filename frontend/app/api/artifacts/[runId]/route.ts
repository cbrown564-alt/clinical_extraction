import { ganArtifact, jsonError } from "../../_mock";
import { proxyPython } from "../../_upstream";

export const dynamic = "force-static";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ runId: string }> }
) {
  const { runId } = await params;
  const query = new URL(request.url).search;
  const upstream = await proxyPython(`/artifacts/${encodeURIComponent(runId)}${query}`);
  if (upstream) return upstream;
  const letterId = new URL(request.url).searchParams.get("letter_id") ?? undefined;
  const artifact = ganArtifact(runId, letterId);
  return artifact ? Response.json(artifact) : jsonError(404, "Artifact not found");
}
