import { readFileSync } from "node:fs";
import { join } from "node:path";
import { ganFamiliesFromDev750Panel } from "@/lib/ganPipelineOptions";
import { readMockJson } from "../_mock";

export const dynamic = "force-static";

function panelPath() {
  return join(process.cwd(), "..", "paper_experiments", "gan", "dev750_panel.json");
}

export function GET() {
  try {
    const panel = JSON.parse(readFileSync(panelPath(), "utf8")) as {
      claim_boundary?: string;
      cells: Array<{
        model_slug: string;
        model: string;
        label: string;
        method:
          | "rules_only"
          | "llm_extract"
          | "llm_encode"
          | "llm_select"
          | "gan_llm_only"
          | "gan_llm_extract_raw";
        status: "present" | "pending";
        n: number;
        purist_correct?: number | null;
        purist_accuracy?: number | null;
      }>;
    };
    return Response.json({
      generated_on: "2026-08-19",
      source_artifact: "paper_experiments/gan/dev750_panel.json",
      claim_boundary: panel.claim_boundary,
      families: ganFamiliesFromDev750Panel(panel),
    });
  } catch {
    return Response.json(readMockJson("pipeline-families.json"));
  }
}
