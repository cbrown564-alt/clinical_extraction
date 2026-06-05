# Gan 2026 Change-Only Verifier LLM-Selector Test450 Aggregate Audit

Frozen locked-test aggregate-only audit over exact LLM-selector alternatives. This summary intentionally omits row ids, clinical text, raw model outputs, and row-level errors.

## Decision

Aggregate-only holdout result remains below the requested Purist F1 >= 0.9.

## Artifacts

- Summary JSON: `experiments/gan2026_change_only_verifier_llm_selector_exact_test450_aggregate_audit_2026-06-05.json`
- Source artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| test rows | 450 |
| eligible rows | 161 |
| call ok rows | 159 |
| parse ok rows | 161 |
| parse error rows | 0 |
| all evidence quotes exact rows | 155 |
| base correct rows | 342 |
| projected correct rows | 347 |
| base purist proxy | 0.7600 |
| projected purist proxy | 0.7711 |
| changed label precision | 0.7778 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 118 |
| `C_to_W` | 2 |
| `W_to_C` | 7 |
| `W_to_W` | 34 |

## Inspection Boundary

No test row ids, clinical text, raw model outputs, or row-level failures are stored in this report.
