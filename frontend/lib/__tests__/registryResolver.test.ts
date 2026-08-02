import {
  isBareFamilyName,
  resolveFamilyDefaultRun,
} from "../registryResolver";
import type { RegistryEntry } from "../types";

function run(pipelineFamily: string, runId: string, rowCount: number): RegistryEntry {
  return {
    run_id: runId,
    pipeline_family: pipelineFamily,
    artifact_paths: [`experiments/${runId}.jsonl`],
    row_count: rowCount,
    split: "validation750",
  } as RegistryEntry;
}

describe("registry family aliases", () => {
  it("resolves active and legacy Gan LLM family names to the same active run", () => {
    const runs = [run("llm", "historical-immutable-run", 750)];

    expect(resolveFamilyDefaultRun(runs, "llm")).toBe("historical-immutable-run");
    expect(resolveFamilyDefaultRun(runs, "llm_only_canonical_pipeline")).toBe(
      "historical-immutable-run"
    );
  });

  it("does not select a stale legacy-family row or fall back", () => {
    const runs = [
      run("llm_only_canonical_pipeline", "stale-legacy-run", 9999),
      run("llm", "active-run", 750),
    ];

    expect(resolveFamilyDefaultRun(runs, "llm_only_canonical_pipeline")).toBe("active-run");
    expect(resolveFamilyDefaultRun(runs, "llm")).toBe("active-run");
    expect(resolveFamilyDefaultRun(runs, "unknown-family")).toBeNull();
  });

  it("keeps both LLM names as recognized bare families", () => {
    expect(isBareFamilyName("llm")).toBe(true);
    expect(isBareFamilyName("llm_only_canonical_pipeline")).toBe(true);
  });
});
