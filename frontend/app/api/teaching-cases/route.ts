import { readMockJson } from "../_mock";

export async function GET() {
  try {
    const data = readMockJson<Record<string, unknown>>("teaching-cases.json");
    return Response.json(data);
  } catch (error) {
    return Response.json(
      { detail: `Failed to load teaching cases: ${(error as Error).message}` },
      { status: 500 }
    );
  }
}
