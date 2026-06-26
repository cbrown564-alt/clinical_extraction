# Gan 2026 Hybrid Parallel State Candidate Reasoner

- JSONL: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation50_gpt41mini_v0_conservative_replay_2026-06-03.jsonl`
- Pipeline family: `hybrid_parallel_state_candidate_reasoner`
- Prompt version: `gan2026_hybrid_parallel_state_candidate_reasoner_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 50
- Model: `openai/gpt-4.1-mini`
- Mode: `prompt-only`
- Claim language: hybrid validation development result with deterministic candidate, state-graph, LLM-candidate, adjudicator, and adapter layers.
- Smoke outcome: `promote_to_50`

## Smoke Summary

- Structured LLM candidates: 50/50
- Structured adjudicator records: 50/50
- Parse/schema failures: 0
- Selected evidence exact: 50/50
- Selected source ids valid: 50/50
- candidate-recall rescue rows: 0
- graph-representability rescue rows: 2
- deterministic-correct regressions: 0
- adapter-changed rows: 2

## Score Layers

- `deterministic_top_candidate`: scorable 50, Purist 50/50 (1.0000), Pragmatic 50/50 (1.0000)
- `state_graph_projection`: scorable 50, Purist 48/50 (0.9600), Pragmatic 48/50 (0.9600)
- `llm_candidate_selector_raw`: scorable 9, Purist 9/50 (0.1800), Pragmatic 9/50 (0.1800)
- `hybrid_adjudicator_raw`: scorable 50, Purist 49/50 (0.9800), Pragmatic 49/50 (0.9800)
- `hybrid_adjudicator_with_adapters`: scorable 50, Purist 50/50 (1.0000), Pragmatic 50/50 (1.0000)
- `adapter_only_sidecar_from_adjudicator_selection`: scorable 50, Purist 50/50 (1.0000), Pragmatic 50/50 (1.0000)

## Provenance

- `deterministic_candidate`: 46
- `llm_candidate`: 47
- `state_graph_node`: 45

## Row Review

- 278: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
- 744: gold `multiple per week`; deterministic `multiple per week`; adapted `multiple per week`; candidate-recall rescue `False`; graph rescue `True`; deterministic regression `False`
