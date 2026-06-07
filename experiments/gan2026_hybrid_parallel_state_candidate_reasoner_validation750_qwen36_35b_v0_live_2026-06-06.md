# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments\gan2026_hybrid_parallel_state_candidate_reasoner_validation750_qwen36_35b_v0_live_2026-06-06.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 750
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `reject`

## Smoke Summary

- Structured LLM candidates: 720/750
- Structured adjudicator records: 738/750
- Parse/schema failures: 42
- Selected evidence exact: 735/750
- Selected source ids valid: 738/750
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 41
- deterministic-correct regressions: 11
- adapter-changed rows: 5

## Score Layers

- `deterministic_top_candidate`: scorable 750, Purist 697/750 (0.9293), Pragmatic 704/750 (0.9387)
- `state_graph_projection`: scorable 750, Purist 655/750 (0.8733), Pragmatic 664/750 (0.8853)
- `llm_candidate_selector_raw`: scorable 245, Purist 84/750 (0.1120), Pragmatic 84/750 (0.1120)
- `hybrid_adjudicator_raw`: scorable 738, Purist 683/750 (0.9107), Pragmatic 691/750 (0.9213)
- `hybrid_adjudicator_with_adapters`: scorable 738, Purist 686/750 (0.9147), Pragmatic 693/750 (0.9240)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 738, Purist 686/750 (0.9147), Pragmatic 693/750 (0.9240)

## Provenance

- `deterministic_candidate`: 704
- `llm_candidate`: 91
- `state_graph_node`: 116

## Row Review

- 278: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 744: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 959: gold `1 per 2 month`; deterministic `1 per 2 month`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 1687: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 1773: gold `11 per 3 month`; deterministic `11 per 3 month`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
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
- 5763: gold `2 per month`; deterministic `6 per 3 month`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 5827: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 5837: gold `2 cluster per 3 week, multiple per cluster`; deterministic `2 cluster per 3 week, multiple per cluster`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 5873: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 6029: gold `unknown`; deterministic `no seizure frequency reference`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
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
- 12145: gold `multiple per week`; deterministic `multiple per week`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 12665: gold `1 per day`; deterministic `5 per day`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 12676: gold `1 per day`; deterministic `1 per day`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 12963: gold `unknown`; deterministic `no seizure frequency reference`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 13385: gold `seizure free for 1.5 year`; deterministic `seizure free for 1.5 year`; adapted `seizure free for 1.5 year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13513: gold `seizure free for 1.5 year`; deterministic `seizure free for 1.5 year`; adapted `seizure free for 1.5 year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13574: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13595: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13598: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 13608: gold `seizure free for multiple year`; deterministic `seizure free for multiple year`; adapted `seizure free for multiple year`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 14282: gold `multiple per month`; deterministic `multiple per month`; adapted `multiple per month`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 14628: gold `2 per 2 month`; deterministic `2 per 2 month`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 15965: gold `13 per 2 month`; deterministic `13 per 2 month`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 16450: gold `1 per multiple day`; deterministic `1 per multiple day`; adapted `1 per multiple day`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
