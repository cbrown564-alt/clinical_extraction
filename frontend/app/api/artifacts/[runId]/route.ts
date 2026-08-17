import { ganArtifact, jsonError } from "../../_mock";

export const dynamic = "force-static";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ runId: string }> }
) {
  const { runId } = await params;
  const letterId = new URL(request.url).searchParams.get("letter_id") ?? undefined;
  const artifact = ganArtifact(runId, letterId);
  return artifact ? Response.json(artifact) : jsonError(404, "Artifact not found");
}
