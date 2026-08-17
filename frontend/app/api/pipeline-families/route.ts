import { readMockJson } from "../_mock";

export const dynamic = "force-static";

export function GET() {
  return Response.json(readMockJson("pipeline-families.json"));
}
