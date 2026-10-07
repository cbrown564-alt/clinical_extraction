import { readSavedJson } from "@/lib/server/fixture-store";
import { join } from "node:path";
import { isDemoSurface, lockDemoGanFamilies } from "@/lib/demoSurface";
import { ganFamiliesFromDev750Panel } from "@/lib/ganPipelineOptions";
import { readMockJson } from "../_mock";
import { proxyPython } from "../_upstream";

export const dynamic = "force-static";

function panelPath() {
  return join("results/letter-benchmarks", "gan", "dev750_panel.json");
}

export async function GET() {
  const upstream = await proxyPython("/pipeline-families");
  if (upstream) return upstream;
  try {
    const panel = readSavedJson(panelPath()) as {
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
    const families = ganFamiliesFromDev750Panel(panel);
    return Response.json({
      generated_on: "2026-08-19",
      source_artifact: "results/letter-benchmarks/gan/dev750_panel.json",
      claim_boundary: panel.claim_boundary,
      families: isDemoSurface() ? lockDemoGanFamilies(families) : families,
    });
  } catch {
    const fallback = readMockJson<{ families: ReturnType<typeof ganFamiliesFromDev750Panel> }>(
      "pipeline-families.json"
    );
    return Response.json({
      ...fallback,
      families: isDemoSurface()
        ? lockDemoGanFamilies(fallback.families)
        : fallback.families,
    });
  }
}
