# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments\gan2026_hybrid_multi_component_staged_assembly_v1_gpt41mini_test450_live_source_2026-06-05.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `test` / `gan2026_split_v1`
- Rows: 450
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `locked_test_generalization_audit_result`

## Smoke Summary

- Structured LLM candidates: 441/450
- Structured adjudicator records: 450/450
- Parse/schema failures: 9
- Selected evidence exact: 449/450
- Selected source ids valid: 450/450
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 11
- deterministic-correct regressions: 0
- adapter-changed rows: 0

## Score Layers

- `deterministic_top_candidate`: scorable 450, Purist 343/450 (0.7622), Pragmatic 354/450 (0.7867)
- `state_graph_projection`: scorable 450, Purist 333/450 (0.7400), Pragmatic 345/450 (0.7667)
- `llm_candidate_selector_raw`: scorable 104, Purist 77/450 (0.1711), Pragmatic 86/450 (0.1911)
- `hybrid_adjudicator_raw`: scorable 450, Purist 343/450 (0.7622), Pragmatic 354/450 (0.7867)
- `hybrid_adjudicator_with_adapters`: scorable 450, Purist 343/450 (0.7622), Pragmatic 354/450 (0.7867)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 450, Purist 343/450 (0.7622), Pragmatic 354/450 (0.7867)

## Provenance

- `deterministic_candidate`: 408
- `llm_candidate`: 254
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
