# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_replay_2026-06-03.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 750
- Model: `openai/gpt-4.1-mini`
- Mode: `prompt-only`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Smoke outcome: `reject`

## Smoke Summary

- Structured LLM candidates: 739/750
- Structured adjudicator records: 750/750
- Parse/schema failures: 11
- Selected evidence exact: 750/750
- Selected source ids valid: 750/750
- candidate-recall rescue rows: 1
- graph-representability rescue rows: 42
- deterministic-correct regressions: 23
- adapter-changed rows: 48

## Score Layers

- `deterministic_top_candidate`: scorable 750, Purist 697/750 (0.9293), Pragmatic 704/750 (0.9387)
- `state_graph_projection`: scorable 750, Purist 655/750 (0.8733), Pragmatic 664/750 (0.8853)
- `llm_candidate_selector_raw`: scorable 161, Purist 107/750 (0.1427), Pragmatic 130/750 (0.1733)
- `hybrid_adjudicator_raw`: scorable 750, Purist 693/750 (0.9240), Pragmatic 701/750 (0.9347)
- `hybrid_adjudicator_with_adapters`: scorable 750, Purist 676/750 (0.9013), Pragmatic 691/750 (0.9213)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 750, Purist 676/750 (0.9013), Pragmatic 691/750 (0.9213)

## Provenance

- `deterministic_candidate`: 704
- `llm_candidate`: 493
- `state_graph_node`: 553

## Row Review

- 278: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 744: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 1687: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per day`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 2965: gold `seizure free for 16 month`; deterministic `seizure free for 16 month`; adapted `seizure free for 16 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3082: gold `seizure free for 10 month`; deterministic `seizure free for 10 month`; adapted `seizure free for 10 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3281: gold `8 per month`; deterministic `8 per month`; adapted `8 per month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3371: gold `unknown`; deterministic `unknown`; adapted `unknown`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3469: gold `unknown`; deterministic `unknown`; adapted `unknown`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3482: gold `unknown`; deterministic `unknown`; adapted `unknown`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3534: gold `unknown`; deterministic `unknown`; adapted `unknown`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 3753: gold `1 per day`; deterministic `1 per day`; adapted `multiple per day`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 3995: gold `1 per month`; deterministic `1 per month`; adapted `1 per month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 4026: gold `1 per month`; deterministic `1 per month`; adapted `1 per month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 4116: gold `1 per 1 to 2 day`; deterministic `1 per 1 to 2 day`; adapted `1 per 1 to 2 day`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 4592: gold `1 per 2 month`; deterministic `1 per 2 month`; adapted `1 per 2 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 4992: gold `seizure free for 11 month`; deterministic `seizure free for 11 month`; adapted `seizure free for 11 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 5351: gold `seizure free for 18 month`; deterministic `seizure free for 18 month`; adapted `seizure free for 18 month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 5567: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 5763: gold `2 per month`; deterministic `6 per 3 month`; adapted `2 per 3 month`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 5827: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 5873: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 6321: gold `unknown`; deterministic `1 per day`; adapted `multiple per day`; candidate-recall rescue `True`; graph rescue `False`; deterministic regression `False`
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
- 12788: gold `6 per 4 month`; deterministic `6 per 4 month`; adapted `6 per year`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 12810: gold `5 per 2 month`; deterministic `5 per 2 month`; adapted `5 per year`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 12823: gold `9 per month`; deterministic `9 per month`; adapted `9 per year`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 12827: gold `5 per 5 month`; deterministic `5 per 5 month`; adapted `5 per year`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 12835: gold `4 per month`; deterministic `4 per month`; adapted `4 per year`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 12877: gold `10 per 4 month`; deterministic `10 per 4 month`; adapted `10 per year`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 12882: gold `7 per 4 month`; deterministic `7 per 4 month`; adapted `7 per year`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 12901: gold `8 per 5 month`; deterministic `8 per 5 month`; adapted `8 per year`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 12949: gold `9 per 6 month`; deterministic `9 per 6 month`; adapted `9 per year`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 12950: gold `7 per 3 month`; deterministic `7 per 3 month`; adapted `7 per year`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 13008: gold `4 per month`; deterministic `4 per month`; adapted `4 per year`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 13385: gold `seizure free for 1.5 year`; deterministic `seizure free for 1.5 year`; adapted `seizure free for 1.5 year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13513: gold `seizure free for 1.5 year`; deterministic `seizure free for 1.5 year`; adapted `seizure free for 1.5 year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13574: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13595: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13598: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13608: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 14282: gold `multiple per month`; deterministic `multiple per month`; adapted `multiple per day`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 15470: gold `1 cluster per 5 day, multiple per cluster`; deterministic `1 cluster per 5 day, multiple per cluster`; adapted `multiple per day`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 15964: gold `11 per 3 month`; deterministic `11 per 3 month`; adapted `11 per 2 month`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 15997: gold `10 per 3 month`; deterministic `10 per 3 month`; adapted `10 per 2 month`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 16021: gold `9 per 3 month`; deterministic `9 per 3 month`; adapted `9 per 2 month`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 16041: gold `9 per 3 month`; deterministic `9 per 3 month`; adapted `9 per 2 month`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 16203: gold `9 per 3 month`; deterministic `9 per 3 month`; adapted `8 per 2 month`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 16450: gold `1 per multiple day`; deterministic `1 per multiple day`; adapted `1 per multiple day`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 16645: gold `5 per 7 month`; deterministic `5 per 7 month`; adapted `4 per 2 month`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 16685: gold `10 per 3 month`; deterministic `10 per 3 month`; adapted `9 per 2 month`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 16824: gold `11 per 5 month`; deterministic `11 per 5 month`; adapted `10 per 2 month`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 17135: gold `5 cluster per month, multiple per cluster`; deterministic `5 cluster per month, multiple per cluster`; adapted `1 cluster per month, multiple per cluster`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
