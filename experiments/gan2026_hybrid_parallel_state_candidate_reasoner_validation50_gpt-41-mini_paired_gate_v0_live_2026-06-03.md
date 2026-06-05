# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments\gan2026_hybrid_parallel_state_candidate_reasoner_validation50_gpt-41-mini_paired_gate_v0_live_2026-06-03.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 50
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Run gate outcome: `validation50_signal_result`

## Smoke Summary

- Structured LLM candidates: 49/50
- Structured adjudicator records: 50/50
- Parse/schema failures: 1
- Selected evidence exact: 50/50
- Selected source ids valid: 50/50
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 2
- deterministic-correct regressions: 0
- adapter-changed rows: 1

## Score Layers

- `deterministic_top_candidate`: scorable 50, Purist 50/50 (1.0000), Pragmatic 50/50 (1.0000)
- `state_graph_projection`: scorable 50, Purist 48/50 (0.9600), Pragmatic 48/50 (0.9600)
- `llm_candidate_selector_raw`: scorable 10, Purist 10/50 (0.2000), Pragmatic 10/50 (0.2000)
- `hybrid_adjudicator_raw`: scorable 50, Purist 49/50 (0.9800), Pragmatic 49/50 (0.9800)
- `hybrid_adjudicator_with_adapters`: scorable 50, Purist 50/50 (1.0000), Pragmatic 50/50 (1.0000)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 50, Purist 50/50 (1.0000), Pragmatic 50/50 (1.0000)

## Provenance

- `deterministic_candidate`: 47
- `llm_candidate`: 45
- `state_graph_node`: 44

## Row Review

- 278: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 744: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
