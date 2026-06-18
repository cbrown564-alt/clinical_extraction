# Gan 2026 Structured Projection Port Test450 Aggregate Audit

User-authorized frozen locked-test aggregate-only audit for the structured projection port. This artifact omits test row ids, note text, evidence snippets, predictions, gold labels, and row-level failures. It is not benchmark-comparable.

## Decision

promoted_audit_rejected_or_revise

## Metrics

| Metric | Value |
| --- | ---: |
| test rows | 450 |
| base correct rows | 342 |
| final correct rows | 337 |
| base purist proxy | 0.7600 |
| final purist proxy | 0.7489 |
| changed rows | 46 |
| invalid candidate label rows | 117 |
| changed label precision | 0.3684 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 330 |
| `C_to_W` | 12 |
| `W_to_C` | 7 |
| `W_to_W` | 101 |

## Selected Families

| Family | Rows |
| --- | ---: |
| `cluster_frequency` | 2 |
| `daily_frequency` | 1 |
| `keep_current` | 404 |
| `other_frequency` | 2 |
| `seizure_free` | 1 |
| `unknown_frequency` | 36 |
| `weekly_frequency` | 4 |

## Selected Sources

| Source | Rows |
| --- | ---: |
| `deterministic_candidate` | 3 |
| `keep_current` | 404 |
| `llm_candidate` | 43 |

## Artifacts

- Summary JSON: `experiments/gan2026_structured_projection_port_test450_aggregate_audit_2026-06-05.json`
- Protocol: ``
- Source test artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`
