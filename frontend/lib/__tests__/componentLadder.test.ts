/**
 * Unit tests for the dataset-agnostic component-ladder view-model, focused on the
 * Gan 2026 adapter that renders the replay-only stage ladder through the shared
 * surface.
 */

import { readFileSync } from "fs";
import { join } from "path";

import {
  adaptGan2026Ladder,
  biggestMover,
  isGanRulesArchitecture,
} from "../componentLadder";
import type { Gan2026ComponentAblationResponse } from "../types";

const payload = JSON.parse(
  readFileSync(
    join(__dirname, "../../public/mock-data/gan2026/component-ablation.json"),
    "utf-8"
  )
) as Gan2026ComponentAblationResponse;

const GAN_LLM_WITH_RULES_GPT41_RUN =
  "gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07";
const GAN_LLM_ONLY_GPT41_RUN =
  "gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07";

describe("adaptGan2026Ladder", () => {
  const ladder = adaptGan2026Ladder(payload);

  it("maps the payload onto the shared ComponentLadder shape", () => {
    expect(ladder.dataset).toBe("gan2026");
    expect(ladder.metricLabel).toBe("Strict label match");
    // One rules ladder plus three model runs per selected active method.
    expect(ladder.architectures).toHaveLength(7);
    expect(ladder.architectures.filter((a) => a.id.includes("hybrid_structured_events"))).toHaveLength(
      3
    );
    expect(
      ladder.architectures.filter((a) => a.id.includes("llm_only_canonical_pipeline"))
    ).toHaveLength(3);
    expect(ladder.categories.map((c) => c.shortLabel)).toContain("Wk");
  });

  it("uses active-method labels and tags for the three-way comparison columns", () => {
    const rules = ladder.architectures.find((a) => a.id === "deterministic_canonical_pipeline");
    const llmWithRules = ladder.architectures.find((a) => a.id === GAN_LLM_WITH_RULES_GPT41_RUN);
    const llmOnly = ladder.architectures.find((a) => a.id === GAN_LLM_ONLY_GPT41_RUN);

    expect(rules?.label).toBe("Rules only");
    expect(rules && isGanRulesArchitecture(rules)).toBe(true);
    expect(rules?.decision).toBe("method");
    expect(llmWithRules?.label).toBe("LLM with rules · GPT-4.1-mini");
    expect(llmWithRules?.decision).toBe("method");
    expect(llmOnly?.label).toBe("LLM only · GPT-4.1-mini");
    expect(llmOnly?.decision).toBe("method");
    expect(llmOnly && isGanRulesArchitecture(llmOnly)).toBe(false);
  });

  it("renders llm_with_rules as a real four-stage ladder, not one bar", () => {
    const arch = ladder.architectures.find((a) => a.id === GAN_LLM_WITH_RULES_GPT41_RUN);
    expect(arch).toBeDefined();
    expect(arch!.stages).toHaveLength(4);
    expect(arch!.stages[0].isBaseline).toBe(true);
    expect(arch!.stages[0].deltaFromPrevious).toBe(0);
    expect(arch!.finalScore).toBeCloseTo(0.8893, 4);

    const mover = biggestMover(arch!);
    expect(mover?.id).toBe("evidence_projection");
    expect(mover?.tone).not.toBe("muted");
  });

  it("resolves Gan stage component types to descriptor tones", () => {
    const arch = ladder.architectures.find((a) => a.id === GAN_LLM_WITH_RULES_GPT41_RUN)!;
    const byType = Object.fromEntries(arch.stages.map((s) => [s.componentType, s.tone]));
    expect(byType["llm_assessment"]).toBe("llm");
    expect(byType["normalize"]).toBe("deterministic");
    expect(byType["projection"]).toBe("deterministic-alt");
    expect(byType["repair"]).toBe("hybrid");
  });

  it("keeps the llm_only config as an honest two-stage label-repair ladder", () => {
    const arch = ladder.architectures.find((a) => a.id === GAN_LLM_ONLY_GPT41_RUN)!;
    expect(arch.stages.map((s) => s.id)).toEqual(["model_label", "label_repair"]);
    expect(arch.stages[1].deltaFromPrevious).toBeGreaterThan(0.05);
  });
});
