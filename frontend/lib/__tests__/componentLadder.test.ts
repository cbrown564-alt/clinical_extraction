/**
 * Unit tests for the dataset-agnostic component-ladder view-model, focused on the
 * Gan 2026 adapter that renders the replay-only stage ladder through the same
 * shared surface as ExECTv2.
 */

import { readFileSync } from "fs";
import { join } from "path";

import { adaptGan2026Ladder, biggestMover } from "../componentLadder";
import type { Gan2026ComponentAblationResponse } from "../types";

const payload = JSON.parse(
  readFileSync(
    join(__dirname, "../../public/mock-data/gan2026/component-ablation.json"),
    "utf-8"
  )
) as Gan2026ComponentAblationResponse;

describe("adaptGan2026Ladder", () => {
  const ladder = adaptGan2026Ladder(payload);

  it("maps the payload onto the shared ComponentLadder shape", () => {
    expect(ladder.dataset).toBe("gan2026");
    expect(ladder.metricLabel).toBe("Purist accuracy");
    expect(ladder.architectures).toHaveLength(5);
    expect(ladder.categories.map((c) => c.shortLabel)).toContain("Wk");
  });

  it("renders hybrid_structured_events as a real four-stage ladder, not one bar", () => {
    const arch = ladder.architectures.find((a) => a.id === "hybrid_structured_events");
    expect(arch).toBeDefined();
    expect(arch!.stages).toHaveLength(4);
    expect(arch!.stages[0].isBaseline).toBe(true);
    expect(arch!.stages[0].deltaFromPrevious).toBe(0);
    expect(arch!.finalScore).toBeCloseTo(0.8893, 4);

    // Evidence projection is the biggest contributor and resolves a real tone
    // (not the muted fallback for an unknown component type).
    const mover = biggestMover(arch!);
    expect(mover?.id).toBe("evidence_projection");
    expect(mover?.tone).not.toBe("muted");
  });

  it("resolves Gan stage component types to descriptor tones", () => {
    const arch = ladder.architectures.find((a) => a.id === "hybrid_structured_events")!;
    const byType = Object.fromEntries(arch.stages.map((s) => [s.componentType, s.tone]));
    expect(byType["llm_assessment"]).toBe("llm");
    expect(byType["normalize"]).toBe("deterministic");
    expect(byType["projection"]).toBe("deterministic-alt");
    expect(byType["repair"]).toBe("hybrid");
  });

  it("keeps llm_only configs as honest two-stage label-repair ladders", () => {
    const arch = ladder.architectures.find((a) => a.id === "llm_only_direct_labeler")!;
    expect(arch.stages.map((s) => s.id)).toEqual(["model_label", "label_repair"]);
    expect(arch.stages[1].deltaFromPrevious).toBeGreaterThan(0.05);
  });
});
