# Gan 2026 Repaired Architecture Matched Validation25 Comparison

- Date: 2026-06-03
- Split: `validation` / `gan2026_split_v1`
- Rows: 25 matched validation-prefix rows
- Model: `openai/gpt-4.1-mini`
- Run mode: live, followed by saved-output replay for narrow contract repairs discovered in the live outputs
- LLM-heavy live artifact: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v1_live_contractfix_2026-06-03.jsonl`
- Hybrid live artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation25_gpt41mini_v0_live_contractfix_2026-06-03.jsonl`
- LLM-heavy replay artifact: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v1_live_contractfix_replay_2026-06-03.jsonl`
- Hybrid replay artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation25_gpt41mini_v0_live_contractfix_replay_2026-06-03.jsonl`
- Claim language: validation development comparison, not a benchmark result.

## Decision

Both repaired candidates pass their validation25 promotion gates after narrow saved-output contract replay of the fresh live outputs.

The fresh LLM-heavy live run reached 25/25 raw and mechanical-adapter Purist with one malformed `≤` selected-evidence copy on row `409`; the source-checked entity repair replay clears selected evidence to 25/25 without changing labels.

The fresh hybrid live run reached 25/25 selected evidence exact, 25/25 source ids valid, and 25/25 adapted Purist, with two LLM-candidate selector schema failures from `assertion_status=historical` on historical candidates; the schema repair replay clears structured LLM candidates to 25/25 without changing adjudicator labels.

## Matched Summary

| Metric | LLM-heavy live | LLM-heavy replay | Hybrid live | Hybrid replay |
|---|---:|---:|---:|---:|
| Structured model records | 25/25 | 25/25 | 23/25 LLM; 25/25 adj | 25/25 LLM; 25/25 adj |
| Call failures | 0 | 0 | 0 | 0 |
| Blocking parse/schema failures | 0 | 0 | 2 | 0 |
| Selected evidence exact | 24/25 | 25/25 | 25/25 | 25/25 |
| Selected source ids valid | n/a | n/a | 25/25 | 25/25 |
| Raw/adjudicator Purist | 25/25 | 25/25 | 24/25 | 24/25 |
| Primary adapted Purist | 25/25 | 25/25 | 25/25 | 25/25 |
| Adapter raw-correct to wrong | 0 | 0 | 0 | 0 |
| Deterministic-correct regressions | n/a | n/a | 0 | 0 |
| Graph-representability rescues | n/a | n/a | 1 | 1 |

## Interpretation

Validation50 escalation is now warranted as a separately predeclared development run if budget permits. Keep the no-call replays labeled as contract-repair replays, not fresh model evidence.

LLM-heavy remains the cleaner LLM-owned clinical-selection story on this prefix because raw parser labels are already 25/25. Hybrid remains the stronger safety-net architecture for graph/deterministic participation and preserves 25/25 adapted Purist after parser repair, but its LLM-candidate selector still needs schema-contract pressure before broader runs.

## Next Action

Predeclare validation50 for the candidate being escalated first. Prefer hybrid if the next question is architecture robustness with deterministic/graph participation; prefer LLM-heavy if the next question is whether model-owned clinical selection plus mechanical adapters generalizes beyond the saturated prefix.