# Gan 2026 RQ9 Router Pressure Points

This is a no-call validation-development interpretation of the saved RQ9 selective-action router artifact.

## Decision

The tightened router no longer treats cluster/convention ambiguity flags as automatic human-review criteria. Remaining non-prediction pressure is limited to trigger-conditioned, missing-anchor, and last-event boundaries; cluster/convention cases should be monitored or verifier-sliced separately rather than blocked by default.

## Claim Boundary

Validation-development pressure-point analysis over a saved RQ9 router artifact. Gold labels and human decisions are offline accounting only; this analysis does not change router, scorer, prompt, projection, locked-test, or benchmark-comparable policy.

## Artifacts

- Source router JSONL: `experiments/gan2026_rq9_selective_action_router_v2_2026-06-04.jsonl`
- Pressure summary JSON: `experiments/gan2026_rq9_selective_action_router_v2_pressure_points_2026-06-04.json`

## Overall Non-Prediction Pressure

| Metric | Value |
| --- | ---: |
| rows | 49 |
| blocked wrong predictions | 15 |
| blocked likely correct predictions | 34 |
| source wrong rate | 0.3061 |
| source likely correct rate | 0.6939 |
| reviewed rows | 9 |
| reviewed correct rows | 2 |
| reviewed noncorrect rows | 7 |
| reviewed correct rate | 0.2222 |
| reviewed noncorrect rate | 0.7778 |

## By Reason

### last_event_boundary

| Metric | Value |
| --- | ---: |
| rows | 8 |
| blocked wrong predictions | 6 |
| blocked likely correct predictions | 2 |
| source wrong rate | 0.7500 |
| reviewed rows | 1 |
| reviewed correct rows | 0 |
| reviewed noncorrect rows | 1 |
| reviewed correct rate | 0.0000 |

| Source label bucket | Rows | Source wrong | Reviewed correct |
| --- | ---: | ---: | ---: |
| `label_plain_frequency` | 2 | 2 | 0 |
| `label_seizure_free` | 4 | 4 | 0 |
| `label_unknown` | 2 | 0 | 0 |

### missing_denominator_anchor

| Metric | Value |
| --- | ---: |
| rows | 2 |
| blocked wrong predictions | 0 |
| blocked likely correct predictions | 2 |
| source wrong rate | 0.0000 |
| reviewed rows | 1 |
| reviewed correct rows | 0 |
| reviewed noncorrect rows | 1 |
| reviewed correct rate | 0.0000 |

| Source label bucket | Rows | Source wrong | Reviewed correct |
| --- | ---: | ---: | ---: |
| `label_no_reference` | 2 | 0 | 0 |

### trigger_conditioned_frequency

| Metric | Value |
| --- | ---: |
| rows | 39 |
| blocked wrong predictions | 9 |
| blocked likely correct predictions | 30 |
| source wrong rate | 0.2308 |
| reviewed rows | 7 |
| reviewed correct rows | 2 |
| reviewed noncorrect rows | 5 |
| reviewed correct rate | 0.2857 |

| Source label bucket | Rows | Source wrong | Reviewed correct |
| --- | ---: | ---: | ---: |
| `label_contains_cluster` | 1 | 0 | 0 |
| `label_no_reference` | 10 | 0 | 0 |
| `label_plain_frequency` | 20 | 5 | 2 |
| `label_seizure_free` | 5 | 4 | 0 |
| `label_unknown` | 3 | 0 | 0 |
