# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `test` / `gan2026_split_v1`
- Rows: 320
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `validation250_development_result`

## Smoke Summary

- Structured LLM candidates: 315/320
- Structured adjudicator records: 320/320
- Parse/schema failures: 5
- Selected evidence exact: 320/320
- Selected source ids valid: 320/320
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 8
- deterministic-correct regressions: 0
- adapter-changed rows: 1

## Score Layers

- `deterministic_top_candidate`: scorable 320, Purist 233/320 (0.7281), Pragmatic 238/320 (0.7438)
- `state_graph_projection`: scorable 320, Purist 226/320 (0.7063), Pragmatic 232/320 (0.7250)
- `llm_candidate_selector_raw`: scorable 66, Purist 60/320 (0.1875), Pragmatic 61/320 (0.1906)
- `hybrid_adjudicator_raw`: scorable 320, Purist 232/320 (0.7250), Pragmatic 237/320 (0.7406)
- `hybrid_adjudicator_with_adapters`: scorable 320, Purist 233/320 (0.7281), Pragmatic 238/320 (0.7438)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 320, Purist 233/320 (0.7281), Pragmatic 238/320 (0.7438)

## Provenance

- `deterministic_candidate`: 283
- `llm_candidate`: 206
- `state_graph_node`: 193

## Row Review

- 750: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 2978: gold `seizure free for 9 month`; deterministic `seizure free for 9 month`; adapted `seizure free for 9 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 4076: gold `1 per 2 to 3 week`; deterministic `1 per 2 to 3 week`; adapted `1 per 2 to 3 week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12060: gold `multiple per day`; deterministic `multiple per day`; adapted `multiple per day`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12080: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12090: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12169: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12173: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
