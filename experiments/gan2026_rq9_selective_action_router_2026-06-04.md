# Gan 2026 RQ9 Selective-Action Router

This is a no-call validation-development router artifact over a saved validation750 source candidate.

## Decision

Materialized `gan2026_rq9_selective_action_router_v0` over 750 validation rows. It predicts on 555 rows, abstains on 41, routes 154 to human review, and keeps 0 for extraction-error analysis.

## Claim Boundary

Validation-development no-call selective-action router artifact. The router uses saved source predictions and predeclared boundary features; gold labels and human audit classes are development accounting only. It does not change scorer policy, prompts, deterministic rules, projection policy, locked-test behavior, or benchmark-comparable claims.

## Artifacts

- Router JSONL: `experiments/gan2026_rq9_selective_action_router_2026-06-04.jsonl`
- Router summary JSON: `experiments/gan2026_rq9_selective_action_router_2026-06-04.json`
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
| covered rows | 555 |
| abstained rows | 41 |
| human review rows | 154 |
| extraction error analysis rows | 0 |
| coverage | 0.7400 |
| abstention rate | 0.0547 |
| human review rate | 0.2053 |
| selective accuracy | 0.9568 |
| reviewed rows | 140 |
| reviewed nonprediction rows | 43 |
| reviewed human correct nonprediction rows | 24 |
| reviewed human noncorrect nonprediction rows | 19 |
| over abstention rate reviewed | 0.0465 |
| over review rate reviewed | 0.5116 |
| rescue value rate | 0.1487 |
| hidden error rate | 0.0000 |

## Reasons

| Reason | Rows |
| --- | ---: |
| `benchmark_convention_boundary` | 35 |
| `cluster_projection_boundary` | 111 |
| `last_event_boundary` | 8 |
| `missing_denominator_anchor` | 2 |
| `plain_no_reference` | 54 |
| `plain_predictable_frequency` | 391 |
| `plain_predictable_seizure_free` | 109 |
| `trigger_conditioned_frequency` | 39 |
| `unknown_frequency_unquantified` | 1 |

## Non-Prediction Rows

| Row | Action | Reason | Source label | Human class |
| ---: | --- | --- | --- | --- |
| 704 | `abstain` | `trigger_conditioned_frequency` | `2 per month` | `` |
| 1317 | `human_review` | `cluster_projection_boundary` | `no seizure frequency reference` | `correct` |
| 1694 | `human_review` | `cluster_projection_boundary` | `1 cluster per 2 week, 3 per cluster` | `` |
| 1706 | `human_review` | `cluster_projection_boundary` | `multiple cluster per month, multiple per cluster` | `` |
| 2822 | `abstain` | `trigger_conditioned_frequency` | `1 per day` | `` |
| 3224 | `human_review` | `cluster_projection_boundary` | `1 cluster per month, 6 to 7 per cluster` | `` |
| 3242 | `human_review` | `cluster_projection_boundary` | `2 cluster per month, 5 per cluster` | `correct` |
| 3261 | `human_review` | `cluster_projection_boundary` | `2 cluster per month, 4 per cluster` | `` |
| 3262 | `human_review` | `cluster_projection_boundary` | `2 cluster per month, 5 per cluster` | `` |
| 3356 | `abstain` | `trigger_conditioned_frequency` | `seizure free for multiple year` | `ambiguous` |
| 3371 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `wrong` |
| 3468 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 3469 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `` |
| 3482 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `` |
| 3493 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `ambiguous` |
| 3999 | `abstain` | `trigger_conditioned_frequency` | `1 per month` | `` |
| 4731 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 4771 | `human_review` | `cluster_projection_boundary` | `no seizure frequency reference` | `wrong` |
| 5379 | `human_review` | `benchmark_convention_boundary` | `seizure free for 6 month` | `correct` |
| 5406 | `human_review` | `benchmark_convention_boundary` | `seizure free for multiple year` | `correct` |
| 5490 | `abstain` | `missing_denominator_anchor` | `no seizure frequency reference` | `` |
| 5837 | `human_review` | `cluster_projection_boundary` | `2 cluster per 3 week, multiple per cluster` | `` |
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
| 7401 | `human_review` | `cluster_projection_boundary` | `2 cluster per 6 week, 1 to 2 per cluster` | `correct` |
| 8564 | `human_review` | `benchmark_convention_boundary` | `seizure free for 6 month` | `` |
| 8577 | `human_review` | `benchmark_convention_boundary` | `seizure free for multiple year` | `ambiguous` |
| 8581 | `human_review` | `benchmark_convention_boundary` | `seizure free for multiple year` | `` |
| 9103 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 9877 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 9879 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `` |
| 9937 | `human_review` | `cluster_projection_boundary` | `1 per multiple week` | `ambiguous` |
| 9943 | `human_review` | `cluster_projection_boundary` | `1 per 4 to 5 week` | `` |
| 9955 | `human_review` | `cluster_projection_boundary` | `1 per month` | `` |
| 10003 | `human_review` | `cluster_projection_boundary` | `1 cluster per week, multiple per cluster` | `` |
| 10047 | `human_review` | `cluster_projection_boundary` | `2 cluster per 3 month, multiple per cluster` | `` |
| 10063 | `human_review` | `cluster_projection_boundary` | `3 cluster per 3 month, multiple per cluster` | `` |
| 10097 | `human_review` | `cluster_projection_boundary` | `3 cluster per month, multiple per cluster` | `` |
| 10147 | `human_review` | `cluster_projection_boundary` | `no seizure frequency reference` | `` |
| 10183 | `human_review` | `cluster_projection_boundary` | `no seizure frequency reference` | `ambiguous` |
| 10189 | `human_review` | `cluster_projection_boundary` | `no seizure frequency reference` | `correct` |
| 10200 | `human_review` | `cluster_projection_boundary` | `no seizure frequency reference` | `correct` |
| 10237 | `human_review` | `cluster_projection_boundary` | `4 cluster per month, multiple per cluster` | `` |
| 10245 | `human_review` | `cluster_projection_boundary` | `3 cluster per month, multiple per cluster` | `` |
| 10260 | `human_review` | `cluster_projection_boundary` | `no seizure frequency reference` | `` |
| 10264 | `human_review` | `cluster_projection_boundary` | `no seizure frequency reference` | `` |
| 10266 | `human_review` | `cluster_projection_boundary` | `1 per 5 day` | `` |
| 10268 | `human_review` | `cluster_projection_boundary` | `no seizure frequency reference` | `` |
| 10371 | `human_review` | `cluster_projection_boundary` | `seizure free for 25 month` | `` |
| 10383 | `human_review` | `cluster_projection_boundary` | `1 cluster per week, 5 per cluster` | `` |
| 10386 | `human_review` | `cluster_projection_boundary` | `1 per day` | `correct` |
| 10434 | `human_review` | `cluster_projection_boundary` | `multiple cluster per week, 2 to 3 per cluster` | `` |
| 10481 | `human_review` | `cluster_projection_boundary` | `4 cluster per month, multiple per cluster` | `` |
| 10487 | `human_review` | `cluster_projection_boundary` | `4 cluster per month, multiple per cluster` | `` |
| 10509 | `human_review` | `cluster_projection_boundary` | `no seizure frequency reference` | `ambiguous` |
| 10517 | `human_review` | `cluster_projection_boundary` | `3 to 4 cluster per week, multiple per cluster` | `correct` |
| 10542 | `human_review` | `cluster_projection_boundary` | `no seizure frequency reference` | `` |
| 10578 | `human_review` | `cluster_projection_boundary` | `unknown, 3 to 4 per cluster` | `` |
| 10583 | `human_review` | `cluster_projection_boundary` | `unknown, 2 to 3 per cluster` | `` |
| 10594 | `human_review` | `cluster_projection_boundary` | `unknown, 2 per cluster` | `` |
| 10618 | `human_review` | `cluster_projection_boundary` | `seizure free for multiple year` | `ambiguous` |
| 10629 | `human_review` | `cluster_projection_boundary` | `no seizure frequency reference` | `correct` |
| 10630 | `human_review` | `cluster_projection_boundary` | `multiple cluster per 2 week, 5 per cluster` | `` |
| 10673 | `human_review` | `cluster_projection_boundary` | `1 cluster per month, multiple per cluster` | `` |
| 10677 | `human_review` | `cluster_projection_boundary` | `1 per month` | `` |
| 10753 | `human_review` | `cluster_projection_boundary` | `no seizure frequency reference` | `correct` |
| 10807 | `human_review` | `cluster_projection_boundary` | `2 cluster per month, multiple per cluster` | `correct` |
| 10829 | `human_review` | `cluster_projection_boundary` | `2 cluster per month, multiple per cluster` | `correct` |
| 10862 | `human_review` | `cluster_projection_boundary` | `1 cluster per week, multiple per cluster` | `` |
| 10865 | `human_review` | `cluster_projection_boundary` | `1 cluster per week, multiple per cluster` | `` |
| 10873 | `human_review` | `cluster_projection_boundary` | `1 cluster per week, 6 per cluster` | `` |
| 10894 | `human_review` | `cluster_projection_boundary` | `1 cluster per week, 4 per cluster` | `` |
| 10896 | `human_review` | `cluster_projection_boundary` | `1 cluster per week, 3 to 4 per cluster` | `` |
| 10902 | `human_review` | `cluster_projection_boundary` | `1 cluster per week, 4 per cluster` | `` |
| 10933 | `human_review` | `cluster_projection_boundary` | `2 to 3 cluster per month, multiple per cluster` | `` |
| 10942 | `human_review` | `cluster_projection_boundary` | `5 per month` | `` |
| 10965 | `human_review` | `cluster_projection_boundary` | `2 cluster per month, 4 to 5 per cluster` | `` |
| 10967 | `human_review` | `cluster_projection_boundary` | `3 cluster per month, 4 to 5 per cluster` | `` |
| 10984 | `human_review` | `cluster_projection_boundary` | `3 cluster per month, multiple per cluster` | `` |
| 10996 | `human_review` | `cluster_projection_boundary` | `1 to 2 cluster per month, multiple per cluster` | `` |
| 11002 | `human_review` | `cluster_projection_boundary` | `2 to 4 cluster per month, multiple per cluster` | `` |
| 11035 | `human_review` | `cluster_projection_boundary` | `1 per 3 month` | `` |
| 11109 | `human_review` | `cluster_projection_boundary` | `2 cluster per month, 5 per cluster` | `` |
| 11118 | `human_review` | `cluster_projection_boundary` | `2 cluster per month, 6 per cluster` | `` |
| 11131 | `human_review` | `cluster_projection_boundary` | `2 cluster per month, 3 to 4 per cluster` | `` |
| 11197 | `human_review` | `cluster_projection_boundary` | `1 cluster per month, 4 to 6 per cluster` | `` |
| 11216 | `human_review` | `last_event_boundary` | `seizure free for 4 month` | `` |
| 11254 | `human_review` | `last_event_boundary` | `seizure free for multiple year` | `` |
| 11259 | `human_review` | `last_event_boundary` | `seizure free for multiple year` | `` |
| 11262 | `human_review` | `last_event_boundary` | `unknown` | `` |
| 11272 | `human_review` | `last_event_boundary` | `seizure free for multiple year` | `` |
| 11282 | `human_review` | `last_event_boundary` | `unknown` | `wrong` |
| 11337 | `abstain` | `trigger_conditioned_frequency` | `no seizure frequency reference` | `wrong` |
| 11400 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11405 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `correct` |
| 11408 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11409 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `ambiguous` |
| 11411 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11434 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11463 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `correct` |
| 11562 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11585 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11606 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11614 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11632 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11640 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11658 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11681 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11706 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11711 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11728 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11734 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `correct` |
| 11737 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11752 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11756 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11763 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11804 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11824 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11841 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 11852 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
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
| 13843 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 13858 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 13889 | `human_review` | `benchmark_convention_boundary` | `no seizure frequency reference` | `` |
| 14040 | `abstain` | `missing_denominator_anchor` | `no seizure frequency reference` | `ambiguous` |
| 14187 | `abstain` | `trigger_conditioned_frequency` | `2 to 3 per month` | `correct` |
| 14214 | `abstain` | `trigger_conditioned_frequency` | `2 to 4 per month` | `` |
| 14250 | `abstain` | `trigger_conditioned_frequency` | `2 per month` | `` |
| 14282 | `abstain` | `trigger_conditioned_frequency` | `multiple per month` | `correct` |
| 14284 | `abstain` | `trigger_conditioned_frequency` | `2 to 3 per month` | `` |
| 14810 | `human_review` | `last_event_boundary` | `12 per month` | `` |
| 14821 | `human_review` | `last_event_boundary` | `17 per month` | `` |
| 15242 | `human_review` | `cluster_projection_boundary` | `multiple cluster per 15 month, multiple per cluster` | `` |
| 15262 | `human_review` | `cluster_projection_boundary` | `multiple cluster per 13 month, multiple per cluster` | `ambiguous` |
| 15376 | `human_review` | `cluster_projection_boundary` | `1 cluster per 2 week, 4 to 6 per cluster` | `` |
| 15404 | `human_review` | `cluster_projection_boundary` | `1 cluster per 4 month, 3 to 4 per cluster` | `correct` |
| 15429 | `human_review` | `cluster_projection_boundary` | `1 cluster per 2 month, 4 per cluster` | `` |
| 15431 | `human_review` | `cluster_projection_boundary` | `1 cluster per 4 month, 5 per cluster` | `` |
| 15442 | `human_review` | `cluster_projection_boundary` | `1 cluster per 4 day, 2 per cluster` | `ambiguous` |
| 15470 | `human_review` | `cluster_projection_boundary` | `1 cluster per 5 day, multiple per cluster` | `ambiguous` |
| 15479 | `human_review` | `cluster_projection_boundary` | `1 cluster per 4 to 5 day, 2 per cluster` | `ambiguous` |
| 15497 | `human_review` | `cluster_projection_boundary` | `1 cluster per 4 to 5 day, 5 per cluster` | `` |
| 15503 | `human_review` | `cluster_projection_boundary` | `1 cluster per 5 day, 3 to 4 per cluster` | `` |
| 15513 | `human_review` | `cluster_projection_boundary` | `1 cluster per 4 to 5 day, 2 to 3 per cluster` | `` |
| 15519 | `human_review` | `cluster_projection_boundary` | `1 cluster per 4 day, 3 per cluster` | `` |
| 15529 | `human_review` | `cluster_projection_boundary` | `1 cluster per 3 day, 4 per cluster` | `` |
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
| 17110 | `human_review` | `cluster_projection_boundary` | `4 to 5 cluster per week, multiple per cluster` | `` |
| 17135 | `human_review` | `cluster_projection_boundary` | `5 cluster per month, multiple per cluster` | `` |
