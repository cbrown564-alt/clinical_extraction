import { exectv2Payload, ganLetters, jsonError } from "../../../_mock";

export const dynamic = "force-static";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ dataset: string }> }
) {
  const { dataset } = await params;
  if (dataset === "gan2026") {
    const letters = ganLetters();
    return Response.json({ dataset, split: "dev750", count: letters.length, letters });
  }
  if (dataset === "exectv2") {
    const payload = exectv2Payload() as {
      shared_letters: Array<Record<string, unknown>>;
    };
    const letters = payload.shared_letters.map((letter) => ({
      id: String(letter.letter_id),
      dataset: "exectv2",
      split: String(letter.split ?? "dev"),
      label: "",
      preview: String(letter.letter_text ?? "").replace(/\s+/g, " ").trim().slice(0, 180),
      gold_summary: "",
      has_gold_reference: false,
    }));
    return Response.json({ dataset, split: "dev140", count: letters.length, letters });
  }
  return jsonError(404, "Unknown dataset");
}
