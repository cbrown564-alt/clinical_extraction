# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments\gan2026_hybrid_parallel_state_candidate_reasoner_validation1_qwen36_35b_paired_gate_v0_live_2026-06-03.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 1
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `revise`

## Smoke Summary

- Structured LLM candidates: 1/1
- Structured adjudicator records: 1/1
- Parse/schema failures: 0
- Selected evidence exact: 1/1
- Selected source ids valid: 1/1
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 0
- deterministic-correct regressions: 0
- adapter-changed rows: 0

## Score Layers

- `deterministic_top_candidate`: scorable 1, Purist 1/1 (1.0000), Pragmatic 1/1 (1.0000)
- `state_graph_projection`: scorable 1, Purist 1/1 (1.0000), Pragmatic 1/1 (1.0000)
- `llm_candidate_selector_raw`: scorable 0, Purist 0/1 (0.0000), Pragmatic 0/1 (0.0000)
- `hybrid_adjudicator_raw`: scorable 1, Purist 1/1 (1.0000), Pragmatic 1/1 (1.0000)
- `hybrid_adjudicator_with_adapters`: scorable 1, Purist 1/1 (1.0000), Pragmatic 1/1 (1.0000)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 1, Purist 1/1 (1.0000), Pragmatic 1/1 (1.0000)

## Provenance

- `deterministic_candidate`: 1
- `state_graph_node`: 1

## Row Review

- No rescue or regression rows on this surface.
