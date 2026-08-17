import { exectv2Payload } from "../../_mock";

export const dynamic = "force-static";

export function GET() {
  return Response.json(exectv2Payload());
}
