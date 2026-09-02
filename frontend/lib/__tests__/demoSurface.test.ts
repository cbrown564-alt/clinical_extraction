import {
  DEMO_GAN_RUN_ID,
  DEMO_MODEL,
  DEMO_PAPER_CELL,
  demoMethodLabel,
  lockDemoExectRuns,
  lockDemoGanFamilies,
} from "../demoSurface";
import { ganFamiliesFromDev750Panel } from "../ganPipelineOptions";
import type { Exectv2RunSummary } from "../types";

describe("demo surface lock", () => {
  it("keeps only Gemini cell-3 extract on Gan", () => {
    const families = ganFamiliesFromDev750Panel({
      cells: [
        {
          model_slug: "grok46",
          model: "xai/grok-4.6",
          label: "Grok 4.6",
          method: "llm_extract",
          status: "present",
          n: 750,
          purist_accuracy: 0.8,
        },
        {
          model_slug: "gemini37flash",
          model: DEMO_MODEL,
          label: "Gemini 3.7 Flash",
          method: "llm_extract",
          status: "present",
          n: 750,
          purist_accuracy: 0.88,
        },
        {
          model_slug: "gemini37flash",
          model: DEMO_MODEL,
          label: "Gemini 3.7 Flash",
          method: "llm_encode",
          status: "present",
          n: 750,
          purist_accuracy: 0.81,
        },
        {
          model_slug: "gemini37flash",
          model: DEMO_MODEL,
          label: "Gemini 3.7 Flash",
          method: "rules_only",
          status: "present",
          n: 750,
          purist_accuracy: 0.72,
        },
      ],
    });

    const locked = lockDemoGanFamilies(families);
    expect(locked).toHaveLength(1);
    expect(locked[0]).toMatchObject({
      run_id: DEMO_GAN_RUN_ID,
      paper_cell: DEMO_PAPER_CELL,
      model: DEMO_MODEL,
    });
    expect(demoMethodLabel()).toBe(
      "LLM extract, rules encode, rules select"
    );
  });

  it("leaves a catalog unchanged when the living cell is missing", () => {
    const families = ganFamiliesFromDev750Panel({
      cells: [
        {
          model_slug: "grok46",
          model: "xai/grok-4.6",
          label: "Grok 4.6",
          method: "llm_encode",
          status: "present",
          n: 750,
        },
      ],
    });
    expect(lockDemoGanFamilies(families)).toEqual(families);
  });

  it("keeps only Gemini cell-3 extract on ExECT when it is present", () => {
    const runs = [
      { run_id: "rules", paper_cell: "rules_only", model: "(model-independent)" },
      {
        run_id: "exectv2_dev140_grok46_llm_extract",
        paper_cell: "llm_extract",
        model: "xai/grok-4.6",
      },
      {
        run_id: "exectv2_dev140_gemini37flash_llm_extract",
        paper_cell: "llm_extract",
        model: DEMO_MODEL,
      },
    ] as Exectv2RunSummary[];

    expect(lockDemoExectRuns(runs).map((run) => run.run_id)).toEqual([
      "exectv2_dev140_gemini37flash_llm_extract",
    ]);
  });
});
