# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 750
- Model: `openai/gpt-4.1-mini`
- Mode: `prompt-only`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Smoke outcome: `promote_to_50`

## Smoke Summary

- Structured LLM candidates: 739/750
- Structured adjudicator records: 750/750
- Parse/schema failures: 11
- Selected evidence exact: 750/750
- Selected source ids valid: 750/750
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 42
- deterministic-correct regressions: 0
- adapter-changed rows: 4

## Score Layers

- `deterministic_top_candidate`: scorable 750, Purist 697/750 (0.9293), Pragmatic 704/750 (0.9387)
- `state_graph_projection`: scorable 750, Purist 655/750 (0.8733), Pragmatic 664/750 (0.8853)
- `llm_candidate_selector_raw`: scorable 161, Purist 107/750 (0.1427), Pragmatic 130/750 (0.1733)
- `hybrid_adjudicator_raw`: scorable 750, Purist 693/750 (0.9240), Pragmatic 701/750 (0.9347)
- `hybrid_adjudicator_with_adapters`: scorable 750, Purist 697/750 (0.9293), Pragmatic 704/750 (0.9387)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 750, Purist 697/750 (0.9293), Pragmatic 704/750 (0.9387)

## Provenance

- `deterministic_candidate`: 704
- `llm_candidate`: 493
- `state_graph_node`: 553

## Row Review

- 278: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 744: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 1687: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 2965: gold `seizure free for 16 month`; deterministic `seizure free for 16 month`; adapted `seizure free for 16 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3082: gold `seizure free for 10 month`; deterministic `seizure free for 10 month`; adapted `seizure free for 10 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3281: gold `8 per month`; deterministic `8 per month`; adapted `8 per month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3371: gold `unknown`; deterministic `unknown`; adapted `unknown`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3469: gold `unknown`; deterministic `unknown`; adapted `unknown`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3482: gold `unknown`; deterministic `unknown`; adapted `unknown`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3534: gold `unknown`; deterministic `unknown`; adapted `unknown`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3995: gold `1 per month`; deterministic `1 per month`; adapted `1 per month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 4026: gold `1 per month`; deterministic `1 per month`; adapted `1 per month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 4116: gold `1 per 1 to 2 day`; deterministic `1 per 1 to 2 day`; adapted `1 per 1 to 2 day`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 4592: gold `1 per 2 month`; deterministic `1 per 2 month`; adapted `1 per 2 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 4992: gold `seizure free for 11 month`; deterministic `seizure free for 11 month`; adapted `seizure free for 11 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 5351: gold `seizure free for 18 month`; deterministic `seizure free for 18 month`; adapted `seizure free for 18 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 5567: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 5827: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 5873: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 7961: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 8089: gold `seizure free for 16 month`; deterministic `seizure free for 16 month`; adapted `seizure free for 16 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 8355: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 8474: gold `seizure free for multiple month`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 8564: gold `seizure free for 6 month`; deterministic `seizure free for 6 month`; adapted `seizure free for 6 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 8969: gold `seizure free for multiple month`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12036: gold `multiple per day`; deterministic `multiple per day`; adapted `multiple per day`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12041: gold `multiple per day`; deterministic `multiple per day`; adapted `multiple per day`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12046: gold `multiple per day`; deterministic `multiple per day`; adapted `multiple per day`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12051: gold `multiple per day`; deterministic `multiple per day`; adapted `multiple per day`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12111: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12127: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12130: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12139: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 12145: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13385: gold `seizure free for 1.5 year`; deterministic `seizure free for 1.5 year`; adapted `seizure free for 1.5 year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13513: gold `seizure free for 1.5 year`; deterministic `seizure free for 1.5 year`; adapted `seizure free for 1.5 year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13574: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13595: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13598: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13608: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 14282: gold `multiple per month`; deterministic `multiple per month`; adapted `multiple per month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 16450: gold `1 per multiple day`; deterministic `1 per multiple day`; adapted `1 per multiple day`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
