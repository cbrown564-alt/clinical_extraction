# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation25_gpt41mini_v0_live_contractfix_2026-06-03.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 25
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Smoke outcome: `promote_to_50`

## Smoke Summary

- Structured LLM candidates: 23/25
- Structured adjudicator records: 25/25
- Parse/schema failures: 2
- Selected evidence exact: 25/25
- Selected source ids valid: 25/25
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 1
- deterministic-correct regressions: 0
- adapter-changed rows: 1

## Score Layers

- `deterministic_top_candidate`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)
- `state_graph_projection`: scorable 25, Purist 24/25 (0.9600), Pragmatic 24/25 (0.9600)
- `llm_candidate_selector_raw`: scorable 3, Purist 3/25 (0.1200), Pragmatic 3/25 (0.1200)
- `hybrid_adjudicator_raw`: scorable 25, Purist 24/25 (0.9600), Pragmatic 24/25 (0.9600)
- `hybrid_adjudicator_with_adapters`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)

## Provenance

- `deterministic_candidate`: 23
- `llm_candidate`: 25
- `state_graph_node`: 23

## Row Review

- 278: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
