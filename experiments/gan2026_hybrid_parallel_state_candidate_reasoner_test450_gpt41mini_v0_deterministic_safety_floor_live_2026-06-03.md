# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `test` / `gan2026_split_v1`
- Rows: 380
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `validation250_development_result`

## Smoke Summary

- Structured LLM candidates: 374/380
- Structured adjudicator records: 380/380
- Parse/schema failures: 6
- Selected evidence exact: 380/380
- Selected source ids valid: 380/380
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 11
- deterministic-correct regressions: 0
- adapter-changed rows: 1

## Score Layers

- `deterministic_top_candidate`: scorable 380, Purist 283/380 (0.7447), Pragmatic 292/380 (0.7684)
- `state_graph_projection`: scorable 380, Purist 273/380 (0.7184), Pragmatic 283/380 (0.7447)
- `llm_candidate_selector_raw`: scorable 80, Purist 66/380 (0.1737), Pragmatic 69/380 (0.1816)
- `hybrid_adjudicator_raw`: scorable 380, Purist 282/380 (0.7421), Pragmatic 291/380 (0.7658)
- `hybrid_adjudicator_with_adapters`: scorable 380, Purist 283/380 (0.7447), Pragmatic 292/380 (0.7684)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 380, Purist 283/380 (0.7447), Pragmatic 292/380 (0.7684)

## Provenance

- `deterministic_candidate`: 336
- `llm_candidate`: 231
- `state_graph_node`: 226

## Row Review

- 750: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 2978: gold `seizure free for 9 month`; deterministic `seizure free for 9 month`; adapted `seizure free for 9 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 4076: gold `1 per 2 to 3 week`; deterministic `1 per 2 to 3 week`; adapted `1 per 2 to 3 week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12060: gold `multiple per day`; deterministic `multiple per day`; adapted `multiple per day`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12080: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12090: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12169: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12173: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13590: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13591: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13600: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
