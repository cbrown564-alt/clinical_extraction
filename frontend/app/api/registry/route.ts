import { ganRegistry } from "../_mock";

export const dynamic = "force-static";

export function GET() {
  return Response.json(ganRegistry());
}
