# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments\gan2026_hybrid_multi_component_staged_assembly_v1_qwen36_35b_ollama_test450_live_source_2026-06-05.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `test` / `gan2026_split_v1`
- Rows: 40
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `locked_test_generalization_audit_result`

## Smoke Summary

- Structured LLM candidates: 40/40
- Structured adjudicator records: 40/40
- Parse/schema failures: 0
- Selected evidence exact: 40/40
- Selected source ids valid: 40/40
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 1
- deterministic-correct regressions: 0
- adapter-changed rows: 2

## Score Layers

- `deterministic_top_candidate`: scorable 40, Purist 32/40 (0.8000), Pragmatic 32/40 (0.8000)
- `state_graph_projection`: scorable 40, Purist 31/40 (0.7750), Pragmatic 31/40 (0.7750)
- `llm_candidate_selector_raw`: scorable 9, Purist 4/40 (0.1000), Pragmatic 4/40 (0.1000)
- `hybrid_adjudicator_raw`: scorable 40, Purist 30/40 (0.7500), Pragmatic 30/40 (0.7500)
- `hybrid_adjudicator_with_adapters`: scorable 40, Purist 32/40 (0.8000), Pragmatic 32/40 (0.8000)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 40, Purist 32/40 (0.8000), Pragmatic 32/40 (0.8000)

## Provenance

- `deterministic_candidate`: 36
- `llm_candidate`: 13
- `state_graph_node`: 13

## Row Review

- 750: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
