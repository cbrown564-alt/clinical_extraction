# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `test` / `gan2026_split_v1`
- Rows: 100
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `validation50_signal_result`

## Smoke Summary

- Structured LLM candidates: 99/100
- Structured adjudicator records: 100/100
- Parse/schema failures: 1
- Selected evidence exact: 100/100
- Selected source ids valid: 100/100
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 2
- deterministic-correct regressions: 0
- adapter-changed rows: 0

## Score Layers

- `deterministic_top_candidate`: scorable 100, Purist 86/100 (0.8600), Pragmatic 86/100 (0.8600)
- `state_graph_projection`: scorable 100, Purist 85/100 (0.8500), Pragmatic 85/100 (0.8500)
- `llm_candidate_selector_raw`: scorable 24, Purist 23/100 (0.2300), Pragmatic 23/100 (0.2300)
- `hybrid_adjudicator_raw`: scorable 100, Purist 86/100 (0.8600), Pragmatic 86/100 (0.8600)
- `hybrid_adjudicator_with_adapters`: scorable 100, Purist 86/100 (0.8600), Pragmatic 86/100 (0.8600)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 100, Purist 86/100 (0.8600), Pragmatic 86/100 (0.8600)

## Provenance

- `deterministic_candidate`: 96
- `llm_candidate`: 64
- `state_graph_node`: 70

## Row Review

- 750: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 2978: gold `seizure free for 9 month`; deterministic `seizure free for 9 month`; adapted `seizure free for 9 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
