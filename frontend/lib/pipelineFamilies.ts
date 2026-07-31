const RETIRED_PIPELINE_FAMILIES = new Set([
  "hybrid_parallel_state_candidate_reasoner",
  "hybrid_rules_candidates_llm_adjudicator",
  "llm_only_claim_table_selector",
  "llm_only_minimal_evidence_selector",
  "llm_only_simplified_selected_state_reasoner",
  "llm_only_sparse_operands_selected_state_reasoner",
  "llm_only_typed_adapter_reasoner",
  "llm_only_typed_operations_reasoner",
]);

export function isRetiredPipelineFamily(family: string): boolean {
  return RETIRED_PIPELINE_FAMILIES.has(family);
}

export function isActivePipelineFamily(family: string): boolean {
  return !isRetiredPipelineFamily(family);
}
