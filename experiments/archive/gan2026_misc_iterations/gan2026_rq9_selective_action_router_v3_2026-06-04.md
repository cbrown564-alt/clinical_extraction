# Gan 2026 RQ9 Selective-Action Router

This is a no-call validation-development router artifact over a saved validation750 source candidate.

## Decision

Materialized `gan2026_rq9_selective_action_router_v3` over 750 validation rows. It predicts on 716 rows, abstains on 26, routes 8 to human review, and keeps 0 for extraction-error analysis.

## Claim Boundary

Validation-development no-call selective-action router artifact. The router uses saved source predictions and predeclared boundary features; gold labels and human audit classes are development accounting only. It does not change scorer policy, prompts, deterministic rules, projection policy, locked-test behavior, or benchmark-comparable claims.

## Artifacts

- Router JSONL: `experiments/gan2026_rq9_selective_action_router_v3_2026-06-04.jsonl`
- Router summary JSON: `experiments/gan2026_rq9_selective_action_router_v3_2026-06-04.json`
- Source artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`
- Source layer: `hybrid_adjudicator_with_adapters`
- Inventory artifact: `experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.csv`
- Human decisions: `experiments/gold_audit_decisions.jsonl`
- Contract: ``
- Boundary policy: ``

## Metrics

| Metric | Value |
| --- | ---: |
| eligible rows | 750 |
| covered rows | 716 |
| abstained rows | 26 |
| human review rows | 8 |
| extraction error analysis rows | 0 |
| coverage | 0.9547 |
| abstention rate | 0.0347 |
| human review rate | 0.0107 |
| selective accuracy | 0.9469 |
| reviewed rows | 140 |
| reviewed nonprediction rows | 6 |
| reviewed human correct nonprediction rows | 0 |
| reviewed human noncorrect nonprediction rows | 6 |
| over abstention rate reviewed | 0.0000 |
| over review rate reviewed | 0.0000 |
| rescue value rate | 0.4412 |
| hidden error rate | 0.0000 |

## Reasons

| Reason | Rows |
| --- | ---: |
| `last_event_boundary` | 8 |
| `missing_denominator_anchor` | 2 |
| `plain_no_reference` | 97 |
| `plain_predictable_frequency` | 496 |
| `plain_predictable_seizure_free` | 122 |
| `trigger_conditioned_frequency` | 24 |
| `unknown_frequency_unquantified` | 1 |

## Non-Prediction Rows

| Row | Action | Reason | Source label | Human class |
| ---: | --- | --- | --- | --- |
| 3356 | `abstain` | `trigger_conditioned_frequency` | `seizure free for multiple year` | `ambiguous` |
| 3371 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `wrong` |
| 3468 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 3469 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `` |
| 3482 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `` |
| 3493 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `ambiguous` |
| 4731 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 5490 | `abstain` | `missing_denominator_anchor` | `no seizure frequency reference` | `` |
| 5974 | `abstain` | `trigger_conditioned_frequency` | `seizure free for multiple year` | `` |
| 5977 | `abstain` | `trigger_conditioned_frequency` | `multiple per 6 week` | `` |
| 5996 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 6077 | `abstain` | `trigger_conditioned_frequency` | `seizure free for 8 month` | `` |
| 6087 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 6094 | `abstain` | `trigger_conditioned_frequency` | `3 per week` | `` |
| 6131 | `abstain` | `trigger_conditioned_frequency` | `seizure free for 6 month` | `` |
| 6153 | `abstain` | `trigger_conditioned_frequency` | `1 per 1 to 2 week` | `` |
| 6319 | `abstain` | `trigger_conditioned_frequency` | `1 per week` | `` |
| 6321 | `abstain` | `trigger_conditioned_frequency` | `1 per day` | `` |
| 6368 | `abstain` | `trigger_conditioned_frequency` | `1 per 1 to 2 week` | `` |
| 7093 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 7168 | `abstain` | `trigger_conditioned_frequency` | `2 per year` | `` |
| 9103 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 9877 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 9879 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 11216 | `human_review` | `last_event_boundary` | `seizure free for 4 month` | `` |
| 11254 | `human_review` | `last_event_boundary` | `seizure free for multiple year` | `` |
| 11259 | `human_review` | `last_event_boundary` | `seizure free for multiple year` | `` |
| 11262 | `human_review` | `last_event_boundary` | `unknown` | `` |
| 11272 | `human_review` | `last_event_boundary` | `seizure free for multiple year` | `` |
| 11282 | `human_review` | `last_event_boundary` | `unknown` | `wrong` |
| 11337 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `wrong` |
| 14040 | `abstain` | `missing_denominator_anchor` | `no seizure frequency reference` | `ambiguous` |
| 14810 | `human_review` | `last_event_boundary` | `12 per month` | `` |
| 14821 | `human_review` | `last_event_boundary` | `17 per month` | `` |
