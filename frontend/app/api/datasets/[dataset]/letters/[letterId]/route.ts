import { exectv2Payload, ganRecord, jsonError } from "../../../../_mock";
import { proxyPython } from "../../../../_upstream";

export const dynamic = "force-static";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ dataset: string; letterId: string }> }
) {
  const { dataset, letterId } = await params;
  const upstream = await proxyPython(
    `/datasets/${encodeURIComponent(dataset)}/letters/${encodeURIComponent(letterId)}`
  );
  if (upstream) return upstream;
  if (dataset === "gan2026") {
    const record = ganRecord(letterId);
    return record ? Response.json(record) : jsonError(404, "Letter not found");
  }
  if (dataset === "exectv2") {
    const payload = exectv2Payload() as {
      shared_letters: Array<Record<string, unknown>>;
    };
    const record = payload.shared_letters.find(
      (letter) => String(letter.letter_id) === letterId
    );
    return record ? Response.json(record) : jsonError(404, "Letter not found");
  }
  return jsonError(404, "Unknown dataset");
}
