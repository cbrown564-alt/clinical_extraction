import {
  groupExectv2Runs,
  hydrateExectv2Run,
  hydrateExectv2Runs,
  resolveExectv2RunId,
} from "../exectv2RunOptions";
import type {
  Exectv2ComparisonMode,
  Exectv2RunSummary,
} from "../types";

const MODELS = [
  "openai/gpt-4.1-mini",
  "openai/gpt-5.6-luna",
  "openai/gpt-5.6-sol",
  "deepseek/deepseek-v4-flash",
  "ollama_chat/qwen3.6:35b",
  "ollama_chat/gemma4:26b",
];

function run(
  comparisonMode: Exectv2ComparisonMode,
  model: string,
  index: number
): Exectv2RunSummary {
  return {
    run_id: `${comparisonMode}-${index}`,
    comparison_mode: comparisonMode,
    model,
    label: `Model ${index}`,
  } as Exectv2RunSummary;
}

describe("ExECTv2 architecture options", () => {
  it("resolves retained aliases exactly and rejects unknown or colliding aliases", () => {
    const rules = {
      ...run("deterministic_only", "rules", 0),
      run_id: "rules",
      saved_run_id: "exectv2_deterministic_all9_dev140",
      retained_evidence_id: "exectv2_deterministic_all9_dev_20260714",
      legacy_run_ids: [
        "rules_only",
        "exectv2_rules_only",
        "exectv2_deterministic_all9_dev140",
      ],
    };
    const other = run("llm_only", MODELS[0], 1);
    const collision = {
      ...run("llm_plus_rules", MODELS[1], 2),
      saved_run_id: "same-alias",
    };
    const collision2 = {
      ...run("llm_plus_rules", MODELS[2], 3),
      saved_run_id: "same-alias",
    };

    expect(resolveExectv2RunId([rules, other], "rules")).toBe("rules");
    expect(resolveExectv2RunId([rules, other], "rules_only")).toBe("rules");
    expect(resolveExectv2RunId([rules, other], "exectv2_rules_only")).toBe("rules");
    expect(
      resolveExectv2RunId([rules, other], "exectv2_deterministic_all9_dev140")
    ).toBe("rules");
    expect(
      resolveExectv2RunId([rules, other], "exectv2_deterministic_all9_dev_20260714")
    ).toBe("rules");
    expect(resolveExectv2RunId([rules, other], "missing")).toBeNull();
    expect(resolveExectv2RunId([rules, other], "deterministic_all9")).toBeNull();
    expect(resolveExectv2RunId([rules, other], "exectv2_deterministic_all9")).toBeNull();
    expect(resolveExectv2RunId([collision, collision2], "same-alias")).toBeNull();
  });

  it("groups the winning mode first, then its raw and no-call comparators", () => {
    const runs = [
      run("deterministic_only", "(model-independent)", 0),
      ...MODELS.flatMap((model, index) => [
        run("llm_only", model, index),
        run("llm_plus_rules", model, index),
      ]),
    ];

    const groups = groupExectv2Runs(runs);

    expect(groups.map((group) => group.mode)).toEqual([
      "llm_plus_rules",
      "llm_only",
      "deterministic_only",
    ]);
    expect(groups.map((group) => group.runs.length)).toEqual([6, 6, 1]);
    expect(groups[0].label).toBe("Winning mode · LLM + rules");
    expect(groups[1].label).toBe("LLM only · raw one-call output");
    expect(groups[2].label).toBe("Deterministic only · no model");
    expect(groups[0].runs.map((item) => item.model)).toEqual(MODELS);
  });

  it("hydrates shared letter text and gold annotations into every run", () => {
    const wire = {
      generated_on: "2026-07-18",
      source_index: "protocol.md",
      shared_letters: [
        {
          letter_id: "EA0002",
          split: "dev",
          stage: "dev140",
          letter_text: "Diagnosis: focal epilepsy",
          gold_mentions: [],
          gold_family_counts: {
            Diagnosis: 1,
            SeizureFrequency: 0,
            Prescription: 0,
            Investigations: 0,
          },
          evidence_spans: [],
        },
      ],
      runs: [
        {
          ...run("llm_plus_rules", MODELS[0], 0),
          letters: [
            {
              letter_id: "EA0002",
              split: "dev",
              stage: "dev140",
              predicted_mentions: [],
              predicted_family_counts: {
                Diagnosis: 1,
                SeizureFrequency: 0,
                Prescription: 0,
                Investigations: 0,
              },
              evidence_spans: [],
            },
          ],
        },
      ],
    };
    const hydrated = hydrateExectv2Runs(wire);
    const hydratedSingle = hydrateExectv2Run({
      generated_on: wire.generated_on,
      source_index: wire.source_index,
      shared_letters: wire.shared_letters,
      run: wire.runs[0],
    });

    expect(hydrated.runs[0].letters[0]).toMatchObject({
      letter_id: "EA0002",
      letter_text: "Diagnosis: focal epilepsy",
      family_counts: {
        gold: { Diagnosis: 1 },
        predicted: { Diagnosis: 1 },
      },
    });
    expect(hydratedSingle.letters[0]).toEqual(hydrated.runs[0].letters[0]);
  });
});
