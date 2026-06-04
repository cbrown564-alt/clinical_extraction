# Gan 2026 RQ9 Selective-Action Router

This is a no-call validation-development router artifact over a saved validation750 source candidate.

## Decision

Materialized `gan2026_rq9_selective_action_router_v1` over 750 validation rows. It predicts on 661 rows, abstains on 41, routes 48 to human review, and keeps 0 for extraction-error analysis.

## Claim Boundary

Validation-development no-call selective-action router artifact. The router uses saved source predictions and predeclared boundary features; gold labels and human audit classes are development accounting only. It does not change scorer policy, prompts, deterministic rules, projection policy, locked-test behavior, or benchmark-comparable claims.

## Artifacts

- Router JSONL: `experiments/gan2026_rq9_selective_action_router_v1_2026-06-04.jsonl`
- Router summary JSON: `experiments/gan2026_rq9_selective_action_router_v1_2026-06-04.json`
- Source artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`
- Source layer: `hybrid_adjudicator_with_adapters`
- Inventory artifact: `experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.csv`
- Human decisions: `experiments/gold_audit_decisions.jsonl`
- Contract: `docs/research/gan2026_rq9_selective_action_evaluation_contract_2026-06-04.md`
- Boundary policy: `docs/research/gan2026_rq9_unknown_drop_attack_boundary_policy_2026-06-04.md`

## Metrics

| Metric | Value |
| --- | ---: |
| eligible rows | 750 |
| covered rows | 661 |
| abstained rows | 41 |
| human review rows | 48 |
| extraction error analysis rows | 0 |
| coverage | 0.8813 |
| abstention rate | 0.0547 |
| human review rate | 0.0640 |
| selective accuracy | 0.9576 |
| reviewed rows | 140 |
| reviewed nonprediction rows | 18 |
| reviewed human correct nonprediction rows | 8 |
| reviewed human noncorrect nonprediction rows | 10 |
| over abstention rate reviewed | 0.1111 |
| over review rate reviewed | 0.3333 |
| rescue value rate | 0.2809 |
| hidden error rate | 0.0000 |

## Reasons

| Reason | Rows |
| --- | ---: |
| `cluster_projection_boundary` | 40 |
| `last_event_boundary` | 8 |
| `missing_denominator_anchor` | 2 |
| `plain_no_reference` | 97 |
| `plain_predictable_frequency` | 449 |
| `plain_predictable_seizure_free` | 114 |
| `trigger_conditioned_frequency` | 39 |
| `unknown_frequency_unquantified` | 1 |

## Non-Prediction Rows

| Row | Action | Reason | Source label | Human class |
| ---: | --- | --- | --- | --- |
| 704 | `abstain` | `trigger_conditioned_frequency` | `2 per month` | `` |
| 2822 | `abstain` | `trigger_conditioned_frequency` | `1 per day` | `` |
| 3356 | `abstain` | `trigger_conditioned_frequency` | `seizure free for multiple year` | `ambiguous` |
| 3371 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `wrong` |
| 3468 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 3469 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `` |
| 3482 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `` |
| 3493 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `ambiguous` |
| 3999 | `abstain` | `trigger_conditioned_frequency` | `1 per month` | `` |
| 4731 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 5490 | `abstain` | `missing_denominator_anchor` | `no seizure frequency reference` | `` |
| 5974 | `abstain` | `trigger_conditioned_frequency` | `seizure free for multiple year` | `` |
| 5977 | `abstain` | `trigger_conditioned_frequency` | `multiple per 6 week` | `` |
| 5995 | `abstain` | `trigger_conditioned_frequency` | `3 per 9 month` | `` |
| 5996 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 6065 | `abstain` | `trigger_conditioned_frequency` | `5 per month` | `` |
| 6077 | `abstain` | `trigger_conditioned_frequency` | `seizure free for 8 month` | `` |
| 6087 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 6094 | `abstain` | `trigger_conditioned_frequency` | `3 per week` | `` |
| 6112 | `abstain` | `trigger_conditioned_frequency` | `3 to 5 per month` | `` |
| 6131 | `abstain` | `trigger_conditioned_frequency` | `seizure free for 6 month` | `` |
| 6137 | `abstain` | `trigger_conditioned_frequency` | `1 per 2 to 3 week` | `` |
| 6153 | `abstain` | `trigger_conditioned_frequency` | `1 per 1 to 2 week` | `` |
| 6319 | `abstain` | `trigger_conditioned_frequency` | `1 per week` | `` |
| 6321 | `abstain` | `trigger_conditioned_frequency` | `1 per day` | `` |
| 6331 | `abstain` | `trigger_conditioned_frequency` | `2 per 6 week` | `` |
| 6358 | `abstain` | `trigger_conditioned_frequency` | `seizure free for multiple year` | `` |
| 6368 | `abstain` | `trigger_conditioned_frequency` | `1 per 1 to 2 week` | `` |
| 6501 | `human_review` | `cluster_projection_boundary` | `seizure free for multiple year` | `` |
| 6509 | `human_review` | `cluster_projection_boundary` | `2 per 2 week` | `` |
| 7093 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 7167 | `abstain` | `trigger_conditioned_frequency` | `3 cluster per 6 week, 2 to 4 per cluster` | `ambiguous` |
| 7168 | `abstain` | `trigger_conditioned_frequency` | `2 per year` | `` |
| 9103 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 9877 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 9879 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 9937 | `human_review` | `cluster_projection_boundary` | `1 per multiple week` | `ambiguous` |
| 9943 | `human_review` | `cluster_projection_boundary` | `1 per 4 to 5 week` | `` |
| 9955 | `human_review` | `cluster_projection_boundary` | `1 per month` | `` |
| 10266 | `human_review` | `cluster_projection_boundary` | `1 per 5 day` | `` |
| 10371 | `human_review` | `cluster_projection_boundary` | `seizure free for 25 month` | `` |
| 10386 | `human_review` | `cluster_projection_boundary` | `1 per day` | `correct` |
| 10618 | `human_review` | `cluster_projection_boundary` | `seizure free for multiple year` | `ambiguous` |
| 10677 | `human_review` | `cluster_projection_boundary` | `1 per month` | `` |
| 10942 | `human_review` | `cluster_projection_boundary` | `5 per month` | `` |
| 11035 | `human_review` | `cluster_projection_boundary` | `1 per 3 month` | `` |
| 11216 | `human_review` | `last_event_boundary` | `seizure free for 4 month` | `` |
| 11254 | `human_review` | `last_event_boundary` | `seizure free for multiple year` | `` |
| 11259 | `human_review` | `last_event_boundary` | `seizure free for multiple year` | `` |
| 11262 | `human_review` | `last_event_boundary` | `unknown` | `` |
| 11272 | `human_review` | `last_event_boundary` | `seizure free for multiple year` | `` |
| 11282 | `human_review` | `last_event_boundary` | `unknown` | `wrong` |
| 11337 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `wrong` |
| 12218 | `human_review` | `cluster_projection_boundary` | `1 per day` | `` |
| 12236 | `human_review` | `cluster_projection_boundary` | `1 per day` | `` |
| 12246 | `human_review` | `cluster_projection_boundary` | `1 to 2 per day` | `` |
| 12484 | `human_review` | `cluster_projection_boundary` | `3 to 4 per day` | `correct` |
| 12502 | `human_review` | `cluster_projection_boundary` | `4 per day` | `correct` |
| 12506 | `human_review` | `cluster_projection_boundary` | `4 per day` | `` |
| 13051 | `human_review` | `cluster_projection_boundary` | `2 per 8 month` | `` |
| 13058 | `human_review` | `cluster_projection_boundary` | `2 per 7 month` | `` |
| 13574 | `human_review` | `cluster_projection_boundary` | `seizure free for multiple year` | `` |
| 13595 | `human_review` | `cluster_projection_boundary` | `seizure free for multiple year` | `correct` |
| 13598 | `human_review` | `cluster_projection_boundary` | `seizure free for multiple year` | `` |
| 13608 | `human_review` | `cluster_projection_boundary` | `seizure free for multiple year` | `` |
| 14040 | `abstain` | `missing_denominator_anchor` | `no seizure frequency reference` | `ambiguous` |
| 14187 | `abstain` | `trigger_conditioned_frequency` | `2 to 3 per month` | `correct` |
| 14214 | `abstain` | `trigger_conditioned_frequency` | `2 to 4 per month` | `` |
| 14250 | `abstain` | `trigger_conditioned_frequency` | `2 per month` | `` |
| 14282 | `abstain` | `trigger_conditioned_frequency` | `multiple per month` | `correct` |
| 14284 | `abstain` | `trigger_conditioned_frequency` | `2 to 3 per month` | `` |
| 14810 | `human_review` | `last_event_boundary` | `12 per month` | `` |
| 14821 | `human_review` | `last_event_boundary` | `17 per month` | `` |
| 15593 | `human_review` | `cluster_projection_boundary` | `2 per 6 month` | `` |
| 15672 | `human_review` | `cluster_projection_boundary` | `2 per 6 week` | `` |
| 15697 | `human_review` | `cluster_projection_boundary` | `1 per day` | `` |
| 15715 | `human_review` | `cluster_projection_boundary` | `1 per day` | `` |
| 16356 | `human_review` | `cluster_projection_boundary` | `1 per 4 day` | `` |
| 16394 | `human_review` | `cluster_projection_boundary` | `1 per 2 to 4 day` | `correct` |
| 16529 | `human_review` | `cluster_projection_boundary` | `1 per 5 day` | `correct` |
| 16557 | `human_review` | `cluster_projection_boundary` | `1 per 2 to 3 day` | `` |
| 16574 | `human_review` | `cluster_projection_boundary` | `1 per 4 day` | `` |
| 16590 | `human_review` | `cluster_projection_boundary` | `1 per 4 to 5 day` | `` |
| 16618 | `human_review` | `cluster_projection_boundary` | `1 per 5 day` | `` |
| 16645 | `human_review` | `cluster_projection_boundary` | `5 per 7 month` | `wrong` |
| 16674 | `human_review` | `cluster_projection_boundary` | `7 per 6 month` | `` |
| 16685 | `human_review` | `cluster_projection_boundary` | `10 per 3 month` | `` |
| 16714 | `human_review` | `cluster_projection_boundary` | `5 per 6 month` | `` |
| 16824 | `human_review` | `cluster_projection_boundary` | `11 per 5 month` | `` |
