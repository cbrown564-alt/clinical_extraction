# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments\gan2026_hybrid_parallel_state_candidate_reasoner_validation250_gpt-41-mini_paired_gate_v0_live_2026-06-03.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `validation250_development_result`

## Smoke Summary

- Structured LLM candidates: 247/250
- Structured adjudicator records: 250/250
- Parse/schema failures: 3
- Selected evidence exact: 249/250
- Selected source ids valid: 250/250
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 17
- deterministic-correct regressions: 0
- adapter-changed rows: 2

## Score Layers

- `deterministic_top_candidate`: scorable 250, Purist 246/250 (0.9840), Pragmatic 246/250 (0.9840)
- `state_graph_projection`: scorable 250, Purist 229/250 (0.9160), Pragmatic 231/250 (0.9240)
- `llm_candidate_selector_raw`: scorable 50, Purist 47/250 (0.1880), Pragmatic 47/250 (0.1880)
- `hybrid_adjudicator_raw`: scorable 250, Purist 244/250 (0.9760), Pragmatic 245/250 (0.9800)
- `hybrid_adjudicator_with_adapters`: scorable 250, Purist 246/250 (0.9840), Pragmatic 246/250 (0.9840)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 250, Purist 246/250 (0.9840), Pragmatic 246/250 (0.9840)

## Provenance

- `deterministic_candidate`: 232
- `llm_candidate`: 198
- `state_graph_node`: 199

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
