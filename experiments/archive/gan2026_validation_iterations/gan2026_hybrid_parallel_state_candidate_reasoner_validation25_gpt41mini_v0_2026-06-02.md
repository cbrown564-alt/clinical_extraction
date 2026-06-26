# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation25_gpt41mini_v0_2026-06-02.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `test` / `gan2026_split_v1`
- Rows: 5
- Model: `openai/gpt-4.1-mini`
- Mode: `prompt-only`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `reject`

## Smoke Summary

- Structured LLM candidates: 0/5
- Structured adjudicator records: 0/5
- Parse/schema failures: 5
- Selected evidence exact: 0/5
- Selected source ids valid: 0/5
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 0
- deterministic-correct regressions: 5
- adapter-changed rows: 0

## Score Layers

- `deterministic_top_candidate`: scorable 5, Purist 5/5 (1.0000), Pragmatic 5/5 (1.0000)
- `state_graph_projection`: scorable 5, Purist 5/5 (1.0000), Pragmatic 5/5 (1.0000)
- `llm_candidate_selector_raw`: scorable 0, Purist 0/5 (0.0000), Pragmatic 0/5 (0.0000)
- `hybrid_adjudicator_raw`: scorable 0, Purist 0/5 (0.0000), Pragmatic 0/5 (0.0000)
- `hybrid_adjudicator_with_adapters`: scorable 0, Purist 0/5 (0.0000), Pragmatic 0/5 (0.0000)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 0, Purist 0/5 (0.0000), Pragmatic 0/5 (0.0000)

## Provenance


## Row Review

- 31: gold `4 per day`; deterministic `4 per day`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 51: gold `5 per week`; deterministic `5 per week`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 61: gold `4 per week`; deterministic `4 per week`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 115: gold `7 to 8 per month`; deterministic `7 to 8 per month`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 136: gold `6 to 7 per month`; deterministic `6 to 7 per month`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
