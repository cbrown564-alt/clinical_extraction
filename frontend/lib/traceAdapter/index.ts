import type { PipelineTrace, FullRecordResponse } from "../types";
import { adaptDeterministicTrace } from "./deterministic";
import { adaptDecisionRecordTrace } from "./decisionRecord";
import { adaptEventsTrace } from "./events";
import { adaptSelectedFactTrace } from "./selectedFact";
import { adaptStateGraphTrace } from "./stateGraph";
import { adaptAblationTrace } from "./ablation";

// Re-export existing deterministic adapter for live runs
export { adaptDeterministicTrace };

function isDecisionRecordFamily(family: string): boolean {
  return (
    family === "llm_first_direct_extractor" ||
    family === "dspy_final_selection_adjudicator" ||
    family === "llm_only_direct_labeler" ||
    family === "llm" || family === "llm_only_canonical_pipeline"
  );
}

function isEventsFamily(family: string): boolean {
  return (
    family === "llm_structured_events" ||
    family === "hybrid_structured_events" ||
    family === "llm_with_rules" ||
    family === "llm_heavy_clinical_frequency_reasoner"
  );
}

function isSelectedFactFamily(family: string): boolean {
  return family === "llm_heavy_evidence_selection_with_deterministic_adapters";
}

function isStateGraphFamily(family: string): boolean {
  return family === "hybrid_clinical_frequency_state_graph";
}

function isAblationFamily(family: string): boolean {
  return family === "llm_replacement_postprocessing_ablation";
}

/**
 * Unified trace adapter dispatch.
 * Routes a raw artifact row to the correct adapter based on pipeline family.
 */
export function adaptTrace(
  row: unknown,
  family: string,
  record: FullRecordResponse
): PipelineTrace {
  if (isDecisionRecordFamily(family)) {
    return adaptDecisionRecordTrace(
      row as Parameters<typeof adaptDecisionRecordTrace>[0],
      record,
      family
    );
  }
  if (isEventsFamily(family)) {
    return adaptEventsTrace(row as Parameters<typeof adaptEventsTrace>[0], record, family);
  }
  if (isSelectedFactFamily(family)) {
    return adaptSelectedFactTrace(row as Parameters<typeof adaptSelectedFactTrace>[0], record, family);
  }
  if (isStateGraphFamily(family)) {
    return adaptStateGraphTrace(row as Parameters<typeof adaptStateGraphTrace>[0], record, family);
  }
  if (isAblationFamily(family)) {
    return adaptAblationTrace(row as Parameters<typeof adaptAblationTrace>[0], record, family);
  }

  throw new Error(`No trace adapter available for pipeline family: ${family}`);
}

/**
 * Check whether a pipeline family has replay support (i.e. an adapter exists).
 */
export function isReplaySupported(family: string): boolean {
  return (
    isDecisionRecordFamily(family) ||
    isEventsFamily(family) ||
    isSelectedFactFamily(family) ||
    isStateGraphFamily(family) ||
    isAblationFamily(family)
  );
}
