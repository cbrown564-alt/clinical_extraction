import { activeMethodLabel } from "../plainLanguageLabels";
import {
  ganFamiliesFromDev750Panel,
  ganPaperRunId,
  ganPipelineOptionLabel,
  groupGanPipelineOptions,
  isGanAggregateRunId,
  resolveGanPipelineOption,
} from "../ganPipelineOptions";
import type { ActiveMethod, PipelineFamilyItem } from "../types";

const MODELS = [
  "xai/grok-4.6",
  "openai/gpt-5.6-luna",
  "gemini/gemini-3.7-flash",
  "deepseek/deepseek-v4-flash",
  "ollama_chat/qwen3.8:27b",
  "ollama_chat/gemma4:26b",
];

function option(
  method: ActiveMethod,
  model: string,
  index: number
): PipelineFamilyItem {
  return {
    value: `${method}-${index}`,
    run_id: `${method}-${index}`,
    label: `Model ${index}`,
    executable: method === "rules",
    kind: method,
    pipeline_family: method,
    model,
    availability:
      method === "llm_with_rules"
        ? "aggregate_only"
        : method === "llm"
          ? "not_retained"
          : "live",
    evidence_scope:
      method === "llm_with_rules"
        ? "test450_aggregate_only"
        : method === "llm"
          ? "not_measured"
          : "validation_rows",
    has_replay_artifact: false,
  };
}

describe("Gan architecture options", () => {
  it("uses method labels that distinguish otherwise identical model choices", () => {
    expect(activeMethodLabel("llm_with_rules")).toBe("LLM with rules");
    expect(activeMethodLabel("llm")).toBe("LLM only");
    expect(activeMethodLabel("rules")).toBe("Rules only");
  });

  it("removes execution-mode wording from picker option labels", () => {
    expect(ganPipelineOptionLabel("Grok 4.6 · replay")).toBe("Grok 4.6");
    expect(ganPipelineOptionLabel("Grok 4.6 · live")).toBe("Grok 4.6");
    expect(ganPipelineOptionLabel("Deterministic canonical")).toBe(
      "Deterministic rules"
    );
  });

  it("groups the six-model llm_with_rules, llm, and rules controls", () => {
    const options = [
      option("rules", "(model-independent)", 0),
      ...MODELS.flatMap((model, index) => [
        option("llm", model, index),
        option("llm_with_rules", model, index),
      ]),
    ];

    const groups = groupGanPipelineOptions(options);

    expect(groups.map((group) => group.method)).toEqual([
      "llm_with_rules",
      "llm",
      "rules",
    ]);
    expect(groups.map((group) => group.options.length)).toEqual([6, 6, 1]);
    expect(groups[0].label).toBe("LLM with rules");
    expect(groups[1].label).toBe("LLM only");
    expect(groups[2].label).toBe("Rules only");
    expect(groups[0].options.map((item) => item.model)).toEqual(MODELS);
    expect(groups[1].options.every((item) => item.availability === "not_retained")).toBe(true);
  });

  it("does not fall back when a legacy registry id is selected", () => {
    const options = [
      option("llm_with_rules", MODELS[0], 0),
      option("rules", "(model-independent)", 0),
    ];

    expect(resolveGanPipelineOption(options, "gan2026_rules_only_v1_baseline")).toBeUndefined();
  });

  it("resolves the active rules run by exact selectedRunId", () => {
    const options = [
      option("llm_with_rules", MODELS[0], 0),
      { ...option("rules", "(model-independent)", 0), run_id: "rules" },
    ];

    expect(resolveGanPipelineOption(options, "rules")?.run_id).toBe("rules");
  });

  it("builds living catalog rows from the Gan dev750 panel, Grok first", () => {
    const families = ganFamiliesFromDev750Panel({
      cells: [
        {
          model_slug: "gpt56luna",
          model: "openai/gpt-5.6-luna",
          label: "GPT-5.6 Luna",
          method: "llm_select",
          status: "present",
          n: 750,
          purist_correct: 663,
          purist_accuracy: 0.884,
        },
        {
          model_slug: "grok46",
          model: "xai/grok-4.6",
          label: "Grok 4.6",
          method: "llm_select",
          status: "present",
          n: 750,
          purist_correct: 675,
          purist_accuracy: 0.9,
        },
        {
          model_slug: "qwen38_27b",
          model: "ollama_chat/qwen3.8:27b",
          label: "Qwen 3.8 27B",
          method: "llm_select",
          status: "pending",
          n: 750,
        },
      ],
    });

    expect(ganPaperRunId("llm_select", "grok46")).toBe(
      "gan2026_validation750_grok46_llm_with_rules"
    );
    expect(families.map((item) => item.model)).toEqual([
      "openai/gpt-5.6-luna",
      "xai/grok-4.6",
      "ollama_chat/qwen3.8:27b",
      "(model-independent)",
    ]);
    const grouped = groupGanPipelineOptions(families);
    expect(grouped[0].options.map((item) => item.model)).toEqual([
      "xai/grok-4.6",
      "openai/gpt-5.6-luna",
      "ollama_chat/qwen3.8:27b",
    ]);
    expect(families.find((item) => item.model === "xai/grok-4.6")?.availability).toBe(
      "replay"
    );
    expect(
      families.find((item) => item.model === "ollama_chat/qwen3.8:27b")?.availability
    ).toBe("not_retained");
  });

  it("recognises only the sealed Gan winning-mode run ids as aggregate-only", () => {
    expect(
      isGanAggregateRunId("gan2026_winning_mode_qwen36_35b_llm_plus_rules_test450")
    ).toBe(true);
    expect(isGanAggregateRunId("rules_only")).toBe(false);
    expect(
      isGanAggregateRunId("gan2026_winning_mode_qwen36_35b_llm_only_test450")
    ).toBe(false);
  });
});
