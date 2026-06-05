# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments\gan2026_hybrid_parallel_state_candidate_reasoner_validation250_qwen36_35b_paired_gate_v0_live_2026-06-03.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `reject`

## Smoke Summary

- Structured LLM candidates: 247/250
- Structured adjudicator records: 247/250
- Parse/schema failures: 6
- Selected evidence exact: 247/250
- Selected source ids valid: 247/250
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 16
- deterministic-correct regressions: 3
- adapter-changed rows: 3

## Score Layers

- `deterministic_top_candidate`: scorable 250, Purist 246/250 (0.9840), Pragmatic 246/250 (0.9840)
- `state_graph_projection`: scorable 250, Purist 229/250 (0.9160), Pragmatic 231/250 (0.9240)
- `llm_candidate_selector_raw`: scorable 47, Purist 31/250 (0.1240), Pragmatic 32/250 (0.1280)
- `hybrid_adjudicator_raw`: scorable 247, Purist 241/250 (0.9640), Pragmatic 241/250 (0.9640)
- `hybrid_adjudicator_with_adapters`: scorable 247, Purist 243/250 (0.9720), Pragmatic 243/250 (0.9720)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 247, Purist 243/250 (0.9720), Pragmatic 243/250 (0.9720)

## Provenance

- `deterministic_candidate`: 227
- `llm_candidate`: 73
- `state_graph_node`: 114

## Row Review

- 278: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 744: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 1687: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 1880: gold `8 per 2 month`; deterministic `8 per 2 month`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 1979: gold `6 per 2 month`; deterministic `6 per 2 month`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
- 2965: gold `seizure free for 16 month`; deterministic `seizure free for 16 month`; adapted `None`; candidate-recall rescue `False`; graph rescue `False`; deterministic regression `True`
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
