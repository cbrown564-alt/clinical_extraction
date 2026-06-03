import type { PipelineTrace, FullRecordResponse } from "../types";
import { adaptDeterministicTrace } from "./deterministic";
import { adaptHybridTrace } from "./hybrid";
import { adaptClaimTableTrace } from "./claimTable";
import { adaptDecisionRecordTrace } from "./decisionRecord";
import { adaptEventsTrace } from "./events";
import { adaptOperationsTrace } from "./operations";
import { adaptSelectedFactTrace, adaptSelectedStateTrace } from "./selectedFact";
import { adaptStateGraphTrace } from "./stateGraph";
import { adaptParallelHybridTrace } from "./parallelHybrid";
import { adaptMinimalEvidenceTrace } from "./minimal";
import { adaptAblationTrace } from "./ablation";

// Re-export existing deterministic adapter for live runs
export { adaptDeterministicTrace };

function isDeterministicFamily(family: string): boolean {
  return family === "rules_only" || family.includes("deterministic");
}

function isHybridFamily(family: string): boolean {
  return family === "hybrid_rules_candidates_llm_adjudicator";
}

function isClaimTableFamily(family: string): boolean {
  return family === "llm_only_claim_table_selector" || family === "llm_only_direct_labeler";
}

function isDecisionRecordFamily(family: string): boolean {
  return (
    family === "llm_first_direct_extractor" ||
    family === "dspy_final_selection_adjudicator"
  );
}

function isEventsFamily(family: string): boolean {
  return (
    family === "llm_structured_events" ||
    family === "llm_heavy_clinical_frequency_reasoner" ||
    family === "llm_only_typed_adapter_reasoner"
  );
}

function isOperationsFamily(family: string): boolean {
  return family === "llm_only_typed_operations_reasoner";
}

function isSelectedFactFamily(family: string): boolean {
  return family === "llm_heavy_evidence_selection_with_deterministic_adapters";
}

function isSelectedStateFamily(family: string): boolean {
  return (
    family === "llm_only_simplified_selected_state_reasoner" ||
    family === "llm_only_sparse_operands_selected_state_reasoner"
  );
}

function isStateGraphFamily(family: string): boolean {
  return family === "hybrid_clinical_frequency_state_graph";
}

function isParallelHybridFamily(family: string): boolean {
  return family === "hybrid_parallel_state_candidate_reasoner";
}

function isMinimalEvidenceFamily(family: string): boolean {
  return family === "llm_only_minimal_evidence_selector";
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
  if (isHybridFamily(family)) {
    return adaptHybridTrace(row as Parameters<typeof adaptHybridTrace>[0], record);
  }
  if (isClaimTableFamily(family)) {
    return adaptClaimTableTrace(row as Parameters<typeof adaptClaimTableTrace>[0], record);
  }
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
  if (isOperationsFamily(family)) {
    return adaptOperationsTrace(row as Parameters<typeof adaptOperationsTrace>[0], record, family);
  }
  if (isSelectedFactFamily(family)) {
    return adaptSelectedFactTrace(row as Parameters<typeof adaptSelectedFactTrace>[0], record, family);
  }
  if (isSelectedStateFamily(family)) {
    return adaptSelectedStateTrace(row as Parameters<typeof adaptSelectedStateTrace>[0], record, family);
  }
  if (isStateGraphFamily(family)) {
    return adaptStateGraphTrace(row as Parameters<typeof adaptStateGraphTrace>[0], record, family);
  }
  if (isParallelHybridFamily(family)) {
    return adaptParallelHybridTrace(row as Parameters<typeof adaptParallelHybridTrace>[0], record, family);
  }
  if (isMinimalEvidenceFamily(family)) {
    return adaptMinimalEvidenceTrace(row as Parameters<typeof adaptMinimalEvidenceTrace>[0], record, family);
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
    isHybridFamily(family) ||
    isClaimTableFamily(family) ||
    isDecisionRecordFamily(family) ||
    isEventsFamily(family) ||
    isOperationsFamily(family) ||
    isSelectedFactFamily(family) ||
    isSelectedStateFamily(family) ||
    isStateGraphFamily(family) ||
    isParallelHybridFamily(family) ||
    isMinimalEvidenceFamily(family) ||
    isAblationFamily(family)
  );
}
