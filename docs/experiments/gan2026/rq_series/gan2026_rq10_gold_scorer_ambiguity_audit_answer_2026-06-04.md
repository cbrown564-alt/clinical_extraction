# Gan 2026 RQ10 Gold/Scorer Ambiguity Audit Answer

This is a validation-development no-call audit over saved replay artifacts. It does not change scorer policy, gold labels, prompts, rules, projection policy, or locked test claims.

## Answer

The residual validation hard rows are mixed: 0.641 of Purist misses carry a non-plain extraction-failure RQ10 class, while the remaining rows still look like true candidate-selection, temporal-selection, denominator, or semiology failures. 29 rows have exact evidence but are scorer/gold-wrong under the saved primary layer, 11 are primarily benchmark-convention dominated, and 0 are strong likely gold defects. The useful conclusion is not that the benchmark is wrong; it is that hard-row residue should be routed through ambiguity/review policy instead of being used as undifferentiated pressure to retune extraction rules.

## Claim Boundary

Answered for saved validation replay only. The audit covers the 53 Purist-wrong `hybrid_adjudicator_with_adapters` rows from `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`. It can guide future scorer-facing normalization, abstention, or human-review work, but it is not benchmark-comparable and does not authorize locked-test tuning.

## Artifacts

- Protocol: ``
- Audit JSONL: `experiments/gan2026_rq10_gold_scorer_ambiguity_audit_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_rq10_gold_scorer_ambiguity_audit_2026-06-04.json`
- Source replay: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`

## Primary Class Counts

| RQ10 class | Rows |
| --- | ---: |
| `underdetermined_note` | 23 |
| `true_extraction_failure` | 19 |
| `benchmark_convention_dominated` | 11 |

## Metrics

| Metric | Value |
| --- | ---: |
| Hard-row ambiguity rate | 0.641 |
| All-system-fail rows | 46 |
| Exact-evidence-but-scorer-wrong rows | 29 |
| Clinically defensible alternative rows | 25 |
| Benchmark-convention dominated rows | 11 |
| Likely gold defects | 0 |
| Possible gold weakness candidates | 3 |
| Purist-wrong but Pragmatic-correct rows | 7 |

## Hidden-Family Readout

| Hidden family | Rows | Main RQ10 class |
| --- | ---: | --- |
| `seizure_free_duration` | 27 | `underdetermined_note` |
| `competing_semiologies` | 25 | `underdetermined_note` |
| `current_vs_historical` | 25 | `underdetermined_note` |
| `uncertainty_or_ambiguity` | 24 | `underdetermined_note` |
| `unknown_boundary` | 20 | `underdetermined_note` |
| `rate_bucket_or_denominator` | 19 | `true_extraction_failure` |
| `cluster_burden` | 11 | `underdetermined_note` |
| `benchmark_format_convention` | 10 | `benchmark_convention_dominated` |
| `diary_or_log_aggregation` | 3 | `benchmark_convention_dominated` |
| `unclassified` | 2 | `underdetermined_note` |

## First-Failure Crosswalk

| First failure owner | Rows | Main RQ10 class |
| --- | ---: | --- |
| `candidate_generation` | 44 | `underdetermined_note` |
| `projection` | 9 | `true_extraction_failure` |

## Row-Level Mechanism Examples

### benchmark_convention_dominated

| Row | Gold | Prediction | Gold reference | Selected evidence | Rationale |
| ---: | --- | --- | --- | --- | --- |
| 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | `1 per 4 to 5 week` | Monthly clusters; within-cluster count unclear | every four to five weeks | Gold uses an unresolved multiple/cluster label that collapses through Gan scorer sentinel or coarse cluster convention. |
| 11216 | `unknown` | `seizure free for 4 month` | Last seizure on 25 December 2023 | Last seizure on 25 December 2023. This episode was described as a generalised convulsion upon waking after... | Gold is unknown for last-event-only style evidence while the prediction renders a seizure-free interval. |
| 13843 | `seizure free for multiple month` | `no seizure frequency reference` | Events at present are considered non-epileptic and have become more manageable now that his anxiety is bett... | He and his partner keep a simple diary which shows fewer episodes over the past six weeks | Gold treats current non-epileptic/seizure-like events as seizure-free rather than no-reference. |

### underdetermined_note

| Row | Gold | Prediction | Gold reference | Selected evidence | Rationale |
| ---: | --- | --- | --- | --- | --- |
| 3356 | `unknown` | `seizure free for multiple year` | Only with sleep deprivation | no events reported | Gold/reference indicates conditional, uncertain, trigger-only, or non-quantified frequency evidence rather than a single stable scorer la... |
| 6321 | `unknown` | `1 per day` | Skipping meals triggers seizure | daily Seizures | Gold/reference indicates conditional, uncertain, trigger-only, or non-quantified frequency evidence rather than a single stable scorer la... |
| 7168 | `unknown` | `2 per year` | Late luteal phase seizure exacerbations noted | Over the past year there have been two brief generalised tonic–clonic seizures | Gold/reference indicates conditional, uncertain, trigger-only, or non-quantified frequency evidence rather than a single stable scorer la... |

### clinically_defensible_alternative

| Row | Gold | Prediction | Gold reference | Selected evidence | Rationale |
| ---: | --- | --- | --- | --- | --- |
| 11216 | `unknown` | `seizure free for 4 month` | Last seizure on 25 December 2023 | Last seizure on 25 December 2023. This episode was described as a generalised convulsion upon waking after... | Gold is unknown for last-event-only style evidence while the prediction renders a seizure-free interval. |
| 13843 | `seizure free for multiple month` | `no seizure frequency reference` | Events at present are considered non-epileptic and have become more manageable now that his anxiety is bett... | He and his partner keep a simple diary which shows fewer episodes over the past six weeks | Gold treats current non-epileptic/seizure-like events as seizure-free rather than no-reference. |
| 15168 | `multiple per 15 month` | `seizure free for multiple year` | He has had no generalised seizures since 9 - 2018, though continues to experience brief jumps from time to... | no generalised seizures since | Gold/reference indicates conditional, uncertain, trigger-only, or non-quantified frequency evidence rather than a single stable scorer la... |

### true_extraction_failure

| Row | Gold | Prediction | Gold reference | Selected evidence | Rationale |
| ---: | --- | --- | --- | --- | --- |
| 12422 | `1 per day` | `4 per year` | Seizure control is inconsistent and while the caregiver perceives stability, she continues to have nightly... | four times per year | Gold/reference appears sufficiently determinate and the saved primary layer selected a different clinical fact, denominator, temporality,... |
| 15834 | `5 per week` | `1 per multiple month` | Drop attacks are now reported 5 times weekly, having previously occurred only sporadically, once every few... | once every few months | Gold/reference appears sufficiently determinate and the saved primary layer selected a different clinical fact, denominator, temporality,... |
| 9496 | `6 per 12 month` | `2 per week` | Focal seizure: 2019: Aug x0, Sep x0, Oct x1, Nov x0, Dec x1. 2020: Jan x0, Feb x2, Mar x0, Apr x1, May x0,... | two per week | Gold/reference appears sufficiently determinate and the saved primary layer selected a different clinical fact, denominator, temporality,... |

## Interpretation

The hard-row residue is not one thing. The biggest scorer-facing ambiguity families are `unknown`/`no_reference` sentinel behavior, last-event-only versus seizure-free duration, unresolved `multiple` labels that score as unknown, cluster cadence/load formatting, and non-epileptic-event convention. Those rows should not be used blindly to tune deterministic precedence rules.

The audit still leaves many rows as true extraction failures, especially when the system selected a historical, lower-frequency, or wrong-semiology fact despite exact evidence for the gold-relevant state. RQ10 therefore reduces the pressure to overfit scorer conventions, but it does not excuse ordinary candidate-selection and projection failures.

## Transfer Confidence

Development confidence is moderate for the taxonomy because every saved primary-layer miss is classified and the classes align with known scorer contracts. Holdout-transfer confidence is low: this was derived from saved validation replay and must not be used to tune or reinterpret locked-test rows.

## Decision

RQ10 is answered for saved validation replay as a development-control audit. Use the artifact to design RQ9 abstention/review routing and any future scorer-normalization policy review. Do not change the scorer or gold labels from this audit alone.

## Next Action

Predeclare an RQ9 abstention/human-review protocol that routes `underdetermined_note`, `clinically_defensible_alternative`, and `benchmark_convention_dominated` rows separately from true extraction failures.
