# Gan 2026 Predeclared Architecture Matched Validation25 Comparison

- Date: 2026-06-03
- Split: `validation` / `gan2026_split_v1`
- Rows: 25 matched validation-prefix rows
- Model: `openai/gpt-4.1-mini`
- Run mode: live
- LLM-heavy artifact: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v0_2026-06-03.jsonl`
- Hybrid artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation25_gpt41mini_v0_2026-06-03.jsonl`
- Claim language: validation development comparison, not a benchmark result.

## Decision

Neither candidate earns validation50 yet.

`llm_heavy_evidence_selection_with_deterministic_adapters` produced valid typed
records on all rows, but its raw parser-facing labels were not scorable and the
mechanical adapter carried nearly all score. Keep it as a Decision 0007
diagnostic and revise selected evidence, operand completeness, and raw
parser-label grammar before escalation.

`hybrid_parallel_state_candidate_reasoner` reached 25/25 Purist on the adapted
adjudicator layer, but the smoke still rejects because source-id provenance is
not reliable and one LLM-candidate output failed validation. Keep it as the
stronger candidate for a targeted provenance repair, not as a promoted
validation50 candidate.

## Matched Summary

| Metric | LLM-heavy Decision 0007 | Hybrid parallel |
|---|---:|---:|
| Structured model records | 25/25 | 24/25 LLM candidates; 25/25 adjudicators |
| Call failures | 0 | 0 |
| Parse or validation failures | 0 | 1 |
| Selected evidence exact | 19/25 | 24/25 |
| Primary adapted layer scorable | 22/25 | 25/25 |
| Primary adapted Purist | 19/25 (0.7600) | 25/25 (1.0000) |
| Primary adapted Pragmatic | 20/25 (0.8000) | 25/25 (1.0000) |
| Raw model/adjudicator Purist | 0/25 raw parser labels | 24/25 adjudicator raw |
| Adapter raw-wrong to correct | 19 | 1 |
| Adapter raw-correct to wrong | 0 | 0 |
| Deterministic-correct regressions | n/a | 0 |
| Candidate-recall rescues | n/a | 0 |
| Graph-representability rescues | n/a | 1 |
| Smoke outcome | reject | reject |

## Rescue And Regression Notes

- Hybrid fixed all six LLM-heavy primary adapted misses on the same rows:
  `10`, `128`, `187`, `190`, `280`, and `446`.
- The hybrid graph rescue occurred on row `278`.
- Hybrid had no deterministic-correct regressions and no graph-projection
  regressions on this prefix.
- The hybrid adapted score is not promotion-sufficient because only 8/25 rows
  had valid selected source ids. Most failures were adjudicator outputs using
  bare `llm-1` or `llm-2` instead of the required `llm:` source-id prefix.

## LLM-Heavy Failure Slice

- Exact-evidence failure: 6 rows.
- Missing selected operands: 1 row.
- Wrong selected clinical fact or operand: 3 rows.
- Rows with primary adapted misses: `10`, `128`, `187`, `190`, `280`, `446`.

The Decision 0007 boundary is still not clean: the mechanical adapter produces
the score-bearing label, while the raw parser-facing model label does not yet
survive scorer parsing. Before another run, tighten the typed raw label grammar
and make selected evidence/operands complete enough that the adapter is not
compensating for an underspecified clinical selection.

## Hybrid Failure Slice

- LLM-candidate selector validation failure: 1 row.
- Selected evidence exact: 24/25.
- Selected source ids valid: 8/25.
- Source provenance counts: deterministic candidate 23, state graph node 23,
  LLM candidate 20.

The dominant defect is provenance formatting, not final-label performance. The
next repair should normalize or instruct selected source ids without relaxing
the trace check: adjudicator outputs must use `det:`, `graph:`, `llm:`, or
`synth:` prefixes that map to supplied source rows.

## Next Action

Revise the hybrid adjudicator source-id contract and the LLM-candidate
temporality enum handling, then rerun validation25. Hold LLM-heavy Decision
0007 for targeted evidence/operand/raw-label repairs rather than escalating it.
