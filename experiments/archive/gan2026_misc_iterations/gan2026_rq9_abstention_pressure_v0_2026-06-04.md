# Gan 2026 RQ9 Abstention Pressure Interpretation

This is a no-call validation-development interpretation of the remaining nonprediction rows in the tightened v2 RQ9 selective-action router.

## Decision

Some trigger-conditioned abstentions can plausibly stay prediction-bearing, but only under a stricter gold-blinded trigger-context rule. There are 26 trigger rows with non-sentinel candidate labels, 17 of which are development-safe if predicted and 9 of which are not. Missing-anchor rows should remain abstentions, and last-event rows should remain human-review until a frozen date-window policy exists.

## Claim Boundary

Validation-development interpretation of remaining v2 RQ9 nonprediction rows. Development correctness and human classes are offline accounting only; this artifact does not change scorer, gold, router, prompt, projection, locked-test, or benchmark-comparable policy.

## Artifacts

- Source router JSONL: `experiments/gan2026_rq9_selective_action_router_v2_2026-06-04.jsonl`
- Row interpretation JSONL: `experiments/gan2026_rq9_abstention_pressure_v0_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_rq9_abstention_pressure_v0_2026-06-04.json`

## Metrics

| Metric | Value |
| --- | ---: |
| rows | 49 |
| abstain rows | 41 |
| human review rows | 8 |
| candidate prediction bearing rows | 26 |
| development safe candidate rows | 17 |
| development unsafe candidate rows | 9 |
| policy supported nonprediction rows | 15 |
| needs frozen policy before prediction rows | 8 |
| development safe candidate rate | 0.6538 |

## By Reason

### last_event_boundary

| Metric | Value |
| --- | ---: |
| rows | 8 |
| candidate prediction bearing rows | 0 |
| development safe candidate rows | 0 |
| development unsafe candidate rows | 0 |
| policy supported nonprediction rows | 0 |
| needs frozen policy before prediction rows | 8 |

### missing_denominator_anchor

| Metric | Value |
| --- | ---: |
| rows | 2 |
| candidate prediction bearing rows | 0 |
| development safe candidate rows | 0 |
| development unsafe candidate rows | 0 |
| policy supported nonprediction rows | 2 |
| needs frozen policy before prediction rows | 0 |

### trigger_conditioned_frequency

| Metric | Value |
| --- | ---: |
| rows | 39 |
| candidate prediction bearing rows | 26 |
| development safe candidate rows | 17 |
| development unsafe candidate rows | 9 |
| policy supported nonprediction rows | 13 |
| needs frozen policy before prediction rows | 0 |

## Candidate Prediction-Bearing Rows

| Row | Reason | Candidate label | Dev safe | Evidence |
| ---: | --- | --- | --- | --- |
| 704 | `trigger_conditioned_frequency` | `2 per month` | yes | `Frequency is now reported as twice a month, often clustering around the late luteal phase.` |
| 2822 | `trigger_conditioned_frequency` | `1 per day` | yes | `On specific questioning, they report a myoclonic jerk daily, occasionally clustering in the mor...` |
| 3356 | `trigger_conditioned_frequency` | `seizure free for multiple year` | no | `no events reported` |
| 3999 | `trigger_conditioned_frequency` | `1 per month` | yes | `Seizure frequency is described as abs monthly, typically clustering around periods of sleep dep...` |
| 5974 | `trigger_conditioned_frequency` | `seizure free for multiple year` | no | `No convulsive events reported` |
| 5977 | `trigger_conditioned_frequency` | `multiple per 6 week` | yes | `several episodes over the past six weeks` |
| 5995 | `trigger_conditioned_frequency` | `3 per 9 month` | yes | `2025: January 0; February 1 generalised convulsion after missing evening valproate; March 0; Ap...` |
| 6065 | `trigger_conditioned_frequency` | `5 per month` | yes | `September x 5 focal aware motor` |
| 6077 | `trigger_conditioned_frequency` | `seizure free for 8 month` | no | `no episodes in the preceding eight months` |
| 6094 | `trigger_conditioned_frequency` | `3 per week` | no | `three times per week` |
| 6112 | `trigger_conditioned_frequency` | `3 to 5 per month` | yes | `3–5 focal seizures per month` |
| 6131 | `trigger_conditioned_frequency` | `seizure free for 6 month` | no | `No myoclonic jerks on waking for the past six months` |
| 6137 | `trigger_conditioned_frequency` | `1 per 2 to 3 week` | yes | `Frequency over the last three months is reported as approximately one every two to three weeks` |
| 6153 | `trigger_conditioned_frequency` | `1 per 1 to 2 week` | no | `every one to two weeks` |
| 6319 | `trigger_conditioned_frequency` | `1 per week` | yes | `occurring roughly weekly` |
| 6321 | `trigger_conditioned_frequency` | `1 per day` | no | `daily Seizures` |
| 6331 | `trigger_conditioned_frequency` | `2 per 6 week` | yes | `two events over the past six weeks` |
| 6358 | `trigger_conditioned_frequency` | `seizure free for multiple year` | yes | `no events since June 2024 after moderating caffeine and improving sleep` |
| 6368 | `trigger_conditioned_frequency` | `1 per 1 to 2 week` | no | `once every one to two weeks` |
| 7167 | `trigger_conditioned_frequency` | `3 cluster per 6 week, 2 to 4 per cluster` | yes | `Over the past six weeks he has experienced three clusters requiring recovery time off work, eac...` |
| 7168 | `trigger_conditioned_frequency` | `2 per year` | no | `Over the past year there have been two brief generalised tonic–clonic seizures` |
| 14187 | `trigger_conditioned_frequency` | `2 to 3 per month` | yes | `Shortly afterwards, she experienced 2 to 3 seizures` |
| 14214 | `trigger_conditioned_frequency` | `2 to 4 per month` | yes | `Shortly afterwards, she experienced two to four seizures` |
| 14250 | `trigger_conditioned_frequency` | `2 per month` | yes | `In the following week, he had 2 seizures` |
| 14282 | `trigger_conditioned_frequency` | `multiple per month` | yes | `In the following week, he had several seizures` |
| 14284 | `trigger_conditioned_frequency` | `2 to 3 per month` | yes | `In the following week, he had two to three seizures` |

## Policy-Supported Nonprediction Rows

| Row | Reason | Interpretation | Candidate label |
| ---: | --- | --- | --- |
| 3371 | `trigger_conditioned_frequency` | `trigger_only_or_unquantified` | `unknown` |
| 3468 | `trigger_conditioned_frequency` | `trigger_only_or_unquantified` | `no seizure frequency reference` |
| 3469 | `trigger_conditioned_frequency` | `trigger_only_or_unquantified` | `unknown` |
| 3482 | `trigger_conditioned_frequency` | `trigger_only_or_unquantified` | `unknown` |
| 3493 | `trigger_conditioned_frequency` | `trigger_only_or_unquantified` | `no seizure frequency reference` |
| 4731 | `trigger_conditioned_frequency` | `trigger_only_or_unquantified` | `no seizure frequency reference` |
| 5490 | `missing_denominator_anchor` | `missing_denominator_or_anchor` | `no seizure frequency reference` |
| 5996 | `trigger_conditioned_frequency` | `trigger_only_or_unquantified` | `no seizure frequency reference` |
| 6087 | `trigger_conditioned_frequency` | `trigger_only_or_unquantified` | `no seizure frequency reference` |
| 7093 | `trigger_conditioned_frequency` | `trigger_only_or_unquantified` | `no seizure frequency reference` |
| 9103 | `trigger_conditioned_frequency` | `trigger_only_or_unquantified` | `no seizure frequency reference` |
| 9877 | `trigger_conditioned_frequency` | `trigger_only_or_unquantified` | `no seizure frequency reference` |
| 9879 | `trigger_conditioned_frequency` | `trigger_only_or_unquantified` | `no seizure frequency reference` |
| 11216 | `last_event_boundary` | `last_event_needs_date_policy` | `seizure free for 4 month` |
| 11254 | `last_event_boundary` | `last_event_needs_date_policy` | `seizure free for multiple year` |
| 11259 | `last_event_boundary` | `last_event_needs_date_policy` | `seizure free for multiple year` |
| 11262 | `last_event_boundary` | `last_event_needs_date_policy` | `unknown` |
| 11272 | `last_event_boundary` | `last_event_needs_date_policy` | `seizure free for multiple year` |
| 11282 | `last_event_boundary` | `last_event_needs_date_policy` | `unknown` |
| 11337 | `trigger_conditioned_frequency` | `trigger_only_or_unquantified` | `no seizure frequency reference` |
| 14040 | `missing_denominator_anchor` | `missing_denominator_or_anchor` | `no seizure frequency reference` |
| 14810 | `last_event_boundary` | `last_event_needs_date_policy` | `12 per month` |
| 14821 | `last_event_boundary` | `last_event_needs_date_policy` | `17 per month` |
