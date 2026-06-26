# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments/gan2026_parallel_reasoner_gpt41_prediction_bearing_hardslice40_validation_2026-06-05.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 40
- Model: `openai/gpt-4.1`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `promote_to_50`

## Smoke Summary

- Structured LLM candidates: 39/40
- Structured adjudicator records: 40/40
- Parse/schema failures: 1
- Selected evidence exact: 40/40
- Selected source ids valid: 40/40
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 1
- deterministic-correct regressions: 0
- adapter-changed rows: 8

## Score Layers

- `deterministic_top_candidate`: scorable 40, Purist 20/40 (0.5000), Pragmatic 21/40 (0.5250)
- `state_graph_projection`: scorable 40, Purist 19/40 (0.4750), Pragmatic 20/40 (0.5000)
- `llm_candidate_selector_raw`: scorable 6, Purist 5/40 (0.1250), Pragmatic 5/40 (0.1250)
- `hybrid_adjudicator_raw`: scorable 40, Purist 13/40 (0.3250), Pragmatic 14/40 (0.3500)
- `hybrid_adjudicator_with_adapters`: scorable 40, Purist 20/40 (0.5000), Pragmatic 21/40 (0.5250)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 40, Purist 20/40 (0.5000), Pragmatic 21/40 (0.5250)

## Provenance

- `deterministic_candidate`: 29
- `llm_candidate`: 21
- `state_graph_node`: 13

## Row Review

- 278: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
