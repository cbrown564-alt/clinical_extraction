# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments/gan2026_h10_fresh_live_variability_validation25_run_b_2026-06-05.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 20
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `promote_to_50`

## Smoke Summary

- Structured LLM candidates: 20/20
- Structured adjudicator records: 20/20
- Parse/schema failures: 0
- Selected evidence exact: 20/20
- Selected source ids valid: 20/20
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 1
- deterministic-correct regressions: 0
- adapter-changed rows: 2

## Score Layers

- `deterministic_top_candidate`: scorable 20, Purist 20/20 (1.0000), Pragmatic 20/20 (1.0000)
- `state_graph_projection`: scorable 20, Purist 19/20 (0.9500), Pragmatic 19/20 (0.9500)
- `llm_candidate_selector_raw`: scorable 1, Purist 1/20 (0.0500), Pragmatic 1/20 (0.0500)
- `hybrid_adjudicator_raw`: scorable 20, Purist 18/20 (0.9000), Pragmatic 18/20 (0.9000)
- `hybrid_adjudicator_with_adapters`: scorable 20, Purist 20/20 (1.0000), Pragmatic 20/20 (1.0000)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 20, Purist 20/20 (1.0000), Pragmatic 20/20 (1.0000)

## Provenance

- `deterministic_candidate`: 17
- `llm_candidate`: 15
- `state_graph_node`: 16

## Row Review

- 278: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
