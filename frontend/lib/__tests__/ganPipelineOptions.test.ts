import {
  ganPipelineModeLabel,
  ganPipelineOptionLabel,
  groupGanPipelineOptions,
  isGanAggregateRunId,
  resolveGanPipelineOption,
} from "../ganPipelineOptions";
import type { PipelineFamilyItem } from "../types";

const MODELS = [
  "openai/gpt-4.1-mini",
  "openai/gpt-5.6-luna",
  "openai/gpt-5.6-sol",
  "deepseek/deepseek-v4-flash",
  "ollama_chat/qwen3.6:35b",
  "ollama_chat/gemma4:26b",
];

function option(
  comparisonMode: PipelineFamilyItem["comparison_mode"],
  model: string,
  index: number
): PipelineFamilyItem {
  return {
    value: `${comparisonMode}-${index}`,
    run_id: `${comparisonMode}-${index}`,
    label: `Model ${index}`,
    executable: comparisonMode === "deterministic_only",
    kind: comparisonMode === "deterministic_only" ? "rules_only" : "hybrid",
    pipeline_family:
      comparisonMode === "deterministic_only" ? "rules_only" : "hybrid_structured_events",
    model,
    comparison_mode: comparisonMode,
    availability:
      comparisonMode === "llm_plus_rules"
        ? "aggregate_only"
        : comparisonMode === "llm_only"
          ? "not_retained"
          : "live",
    evidence_scope:
      comparisonMode === "llm_plus_rules"
        ? "test450_aggregate_only"
        : comparisonMode === "llm_only"
          ? "not_measured"
          : "validation_rows",
    has_replay_artifact: false,
  };
}

describe("Gan architecture options", () => {
  it("uses method labels that distinguish otherwise identical model choices", () => {
    expect(ganPipelineModeLabel("llm_plus_rules")).toBe("LLM + Rules");
    expect(ganPipelineModeLabel("llm_only")).toBe("LLM Only");
    expect(ganPipelineModeLabel("deterministic_only")).toBe("Rules Only");
  });

  it("removes execution-mode wording from picker option labels", () => {
    expect(ganPipelineOptionLabel("GPT-5.6 Sol · replay")).toBe("GPT-5.6 Sol");
    expect(ganPipelineOptionLabel("GPT-5.6 Sol · live")).toBe("GPT-5.6 Sol");
    expect(ganPipelineOptionLabel("Deterministic canonical")).toBe(
      "Deterministic canonical"
    );
  });

  it("groups the six-model winning mode, LLM-only variants, and deterministic control", () => {
    const options = [
      option("deterministic_only", "(model-independent)", 0),
      ...MODELS.flatMap((model, index) => [
        option("llm_only", model, index),
        option("llm_plus_rules", model, index),
      ]),
    ];

    const groups = groupGanPipelineOptions(options);

    expect(groups.map((group) => group.mode)).toEqual([
      "llm_plus_rules",
      "llm_only",
      "deterministic_only",
    ]);
    expect(groups.map((group) => group.options.length)).toEqual([6, 6, 1]);
    expect(groups[0].label).toBe("Winning mode · LLM + rules");
    expect(groups[1].label).toBe("LLM only · raw one-call output");
    expect(groups[2].label).toBe("Deterministic only · no model");
    expect(groups[0].options.map((item) => item.model)).toEqual(MODELS);
    expect(groups[1].options.every((item) => item.availability === "not_retained")).toBe(true);
  });

  it("does not fall back when a legacy registry id is selected", () => {
    const options = [
      option("llm_plus_rules", MODELS[0], 0),
      option("deterministic_only", "(model-independent)", 0),
    ];

    expect(resolveGanPipelineOption(options, "gan2026_rules_only_v1_baseline")).toBeUndefined();
  });

  it("resolves the active rules run by exact selectedRunId", () => {
    const options = [
      option("llm_plus_rules", MODELS[0], 0),
      { ...option("deterministic_only", "(model-independent)", 0), run_id: "rules" },
    ];

    expect(resolveGanPipelineOption(options, "rules")?.run_id).toBe("rules");
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
