# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `test` / `gan2026_split_v1`
- Rows: 450
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: frozen locked-test generalization audit for a hybrid deterministic-safety-floor candidate with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers. This is not a benchmark claim and must not be used for row-level test tuning.
- Run gate outcome: `locked_test_generalization_audit_result`

## Smoke Summary

- Structured LLM candidates: 443/450
- Structured adjudicator records: 450/450
- Parse/schema failures: 7
- Selected evidence exact: 450/450
- Selected source ids valid: 450/450
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 11
- deterministic-correct regressions: 0
- adapter-changed rows: 1

## Score Layers

- `deterministic_top_candidate`: scorable 450, Purist 343/450 (0.7622), Pragmatic 354/450 (0.7867)
- `state_graph_projection`: scorable 450, Purist 333/450 (0.7400), Pragmatic 345/450 (0.7667)
- `llm_candidate_selector_raw`: scorable 95, Purist 75/450 (0.1667), Pragmatic 78/450 (0.1733)
- `hybrid_adjudicator_raw`: scorable 450, Purist 342/450 (0.7600), Pragmatic 353/450 (0.7844)
- `hybrid_adjudicator_with_adapters`: scorable 450, Purist 343/450 (0.7622), Pragmatic 354/450 (0.7867)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 450, Purist 343/450 (0.7622), Pragmatic 354/450 (0.7867)

## Provenance

- `deterministic_candidate`: 404
- `llm_candidate`: 263
- `state_graph_node`: 277

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
