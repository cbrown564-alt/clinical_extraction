# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `test` / `gan2026_split_v1`
- Rows: 240
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `validation50_signal_result`

## Smoke Summary

- Structured LLM candidates: 238/240
- Structured adjudicator records: 240/240
- Parse/schema failures: 2
- Selected evidence exact: 240/240
- Selected source ids valid: 240/240
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 3
- deterministic-correct regressions: 0
- adapter-changed rows: 1

## Score Layers

- `deterministic_top_candidate`: scorable 240, Purist 179/240 (0.7458), Pragmatic 182/240 (0.7583)
- `state_graph_projection`: scorable 240, Purist 177/240 (0.7375), Pragmatic 181/240 (0.7542)
- `llm_candidate_selector_raw`: scorable 57, Purist 52/240 (0.2167), Pragmatic 53/240 (0.2208)
- `hybrid_adjudicator_raw`: scorable 240, Purist 178/240 (0.7417), Pragmatic 181/240 (0.7542)
- `hybrid_adjudicator_with_adapters`: scorable 240, Purist 179/240 (0.7458), Pragmatic 182/240 (0.7583)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 240, Purist 179/240 (0.7458), Pragmatic 182/240 (0.7583)

## Provenance

- `deterministic_candidate`: 210
- `llm_candidate`: 162
- `state_graph_node`: 146

## Row Review

- 750: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 2978: gold `seizure free for 9 month`; deterministic `seizure free for 9 month`; adapted `seizure free for 9 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 4076: gold `1 per 2 to 3 week`; deterministic `1 per 2 to 3 week`; adapted `1 per 2 to 3 week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
