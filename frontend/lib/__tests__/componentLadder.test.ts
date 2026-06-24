/**
 * Unit tests for the dataset-agnostic component-ladder view-model, focused on the
 * Gan 2026 adapter that renders the replay-only stage ladder through the same
 * shared surface as ExECTv2.
 */

import { readFileSync } from "fs";
import { join } from "path";

import {
  adaptExectv2Ladder,
  adaptGan2026Ladder,
  biggestMover,
} from "../componentLadder";
import type {
  Exectv2ComponentAblationResponse,
  Gan2026ComponentAblationResponse,
} from "../types";

const payload = JSON.parse(
  readFileSync(
    join(__dirname, "../../public/mock-data/gan2026/component-ablation.json"),
    "utf-8"
  )
) as Gan2026ComponentAblationResponse;

const exectv2Payload = JSON.parse(
  readFileSync(
    join(__dirname, "../../public/mock-data/exectv2/component-ablation.json"),
    "utf-8"
  )
) as Exectv2ComponentAblationResponse;

describe("adaptGan2026Ladder", () => {
  const ladder = adaptGan2026Ladder(payload);

  it("maps the payload onto the shared ComponentLadder shape", () => {
    expect(ladder.dataset).toBe("gan2026");
    expect(ladder.metricLabel).toBe("Purist accuracy");
    expect(ladder.architectures).toHaveLength(3);
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

  it("keeps the llm_only config as an honest two-stage label-repair ladder", () => {
    const arch = ladder.architectures.find((a) => a.id === "llm_only_canonical_pipeline")!;
    expect(arch.stages.map((s) => s.id)).toEqual(["model_label", "label_repair"]);
    expect(arch.stages[1].deltaFromPrevious).toBeGreaterThan(0.05);
  });
});

describe("adaptExectv2Ladder", () => {
  const ladder = adaptExectv2Ladder(exectv2Payload);
  const v08 = ladder.architectures.find(
    (a) => a.id === "exectv2_holistic_finding_assembly_v08_dev140"
  )!;

  it("hides the inert producer guards and the dropped final-assembly stage", () => {
    expect(ladder.dataset).toBe("exectv2");
    expect(ladder.metricLabel).toBe("Clinical F1");
    // source_scored + evidence_valid are inert (hidden); final_assembly is gone.
    expect(v08.stages.map((s) => s.id)).toEqual([
      "raw_lane_candidates",
      "dictionary_normalized",
      "residual_semantic_added",
      "headline_projection",
    ]);
  });

  it("recomputes visible-stage deltas so the waterfall closes exactly", () => {
    expect(v08.stages[0].isBaseline).toBe(true);
    expect(v08.stages[0].deltaFromPrevious).toBe(0);
    // Dictionary delta is measured against the raw baseline (0.8328 → 0.8697),
    // not the hidden evidence-valid surface, absorbing the tiny inert effect.
    const dictionary = v08.stages.find((s) => s.id === "dictionary_normalized")!;
    expect(dictionary.deltaFromPrevious).toBeCloseTo(0.0369, 4);
    // Deltas of the visible stages sum to final − baseline.
    const baseline = v08.stages[0].score;
    const summed = v08.stages
      .slice(1)
      .reduce((acc, s) => acc + s.deltaFromPrevious, 0);
    expect(baseline + summed).toBeCloseTo(v08.finalScore, 6);
    expect(biggestMover(v08)?.id).toBe("dictionary_normalized");
  });
});
