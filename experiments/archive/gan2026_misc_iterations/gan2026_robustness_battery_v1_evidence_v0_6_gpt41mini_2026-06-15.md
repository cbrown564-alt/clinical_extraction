# Gan 2026 Robustness Battery v1 — Result

Date: 2026-06-15

Fitness tier 2 (OOD / robustness survival) for the F1 dynamic workflow. This is the predeclared overfit/transfer gate; it does not read or run test450. Cases are authored-fresh (NOT Gan rows). Gold Purist is computed from each authored label via the project normalizer + `labels.map_purist`.

Candidate: llm_only_direct_labeler (prompt v0.6 Cycle-2 triage-scaffold evidence presentation) live on openai/gpt-4.1-mini, temperature 0

Predeclaration: `experiments\gan2026_evidence_presentation_v0_6_predeclaration_2026-06-15.md`
Cases: `experiments\gan2026_robustness_battery_v1_cases.json`

## Verdict

**overfit**

| Panel | Result | Bar | Pass |
| --- | --- | --- | :---: |
| A (minimal pairs) | 3/6 pairs both-correct; 2 overfit-only (9/12 cases) | every pair both-correct, zero overfit-only pairs | NO |
| B (source-near) | 5/7 correct | >= 6/7 correct, trigger-word-independent | NO |
| C (KCL OOD) | 8/8 correct (100%) | >= 80% correct | yes |

Weakest clinical axis: `cluster_axis_retention`
Axis failure counts: `{'adherence_confound_vs_baseline': 1, 'cluster_axis_retention': 2, 'last_event_only_vs_recurrent_rate': 1, 'transient_exacerbation_vs_habitual': 1}`

## Failing cases

| Panel | Case | Axis | Gold Purist | Predicted | Pred Purist |
| --- | --- | --- | --- | --- | --- |
| A_minimal_pairs | A2a | transient_exacerbation_vs_habitual | seizure_freq_unknown | 3 per 6 week | seizure_freq_more1mon_less1week |
| A_minimal_pairs | A4a | cluster_axis_retention | seizure_freq_more1mon_less1week | multiple per day | seizure_freq_unknown |
| A_minimal_pairs | A6a | adherence_confound_vs_baseline | seizure_freq_unknown | 2 per 6 week | seizure_freq_more1mon_less1week |
| B_source_near_perturbations | B3 | last_event_only_vs_recurrent_rate | seizure_freq_unknown | seizure free for multiple year | currently_no_seizure |
| B_source_near_perturbations | B6 | cluster_axis_retention | seizure_freq_more1mon_less1week | 1 per 4 to 5 week | seizure_freq_more1per6mon_less1mon |

## Panel A — minimal-pair detail

| Pair | Axis | Both correct | Quantify side | Unknown/hard side | Overfit-only |
| --- | --- | :---: | :---: | :---: | :---: |
| A1 | provoked_situational_vs_habitual | yes | yes | yes | no |
| A2 | transient_exacerbation_vs_habitual | no | yes | no | yes |
| A3 | descriptive_semiology_vs_stated_rate | yes | yes | yes | no |
| A4 | cluster_axis_retention | no | no | n/a | no |
| A5 | true_seizure_free_vs_last_event_only | yes | yes | yes | no |
| A6 | adherence_confound_vs_baseline | no | yes | no | yes |

## A_minimal_pairs — rows

| Case | Axis | Gold Purist | Predicted | Pred Purist | Correct |
| --- | --- | --- | --- | --- | :---: |
| A1a | provoked_situational_vs_habitual | seizure_freq_unknown | unknown | seizure_freq_unknown | yes |
| A1b | provoked_situational_vs_habitual | seizure_freq_more1per6mon_less1mon | 2 per 3 month | seizure_freq_more1per6mon_less1mon | yes |
| A2a | transient_exacerbation_vs_habitual | seizure_freq_unknown | 3 per 6 week | seizure_freq_more1mon_less1week | no |
| A2b | transient_exacerbation_vs_habitual | seizure_freq_more1mon_less1week | 3 per 6 week | seizure_freq_more1mon_less1week | yes |
| A3a | descriptive_semiology_vs_stated_rate | seizure_freq_unknown | no seizure frequency reference | seizure_freq_unknown | yes |
| A3b | descriptive_semiology_vs_stated_rate | seizure_freq_1_per_mon | 1 per month | seizure_freq_1_per_mon | yes |
| A4a | cluster_axis_retention | seizure_freq_more1mon_less1week | multiple per day | seizure_freq_unknown | no |
| A4b | cluster_axis_retention | seizure_freq_more1per6mon_less1mon | 1 per 4 to 5 week | seizure_freq_more1per6mon_less1mon | yes |
| A5a | true_seizure_free_vs_last_event_only | currently_no_seizure | seizure free for 4 month | currently_no_seizure | yes |
| A5b | true_seizure_free_vs_last_event_only | seizure_freq_unknown | unknown | seizure_freq_unknown | yes |
| A6a | adherence_confound_vs_baseline | seizure_freq_unknown | 2 per 6 week | seizure_freq_more1mon_less1week | no |
| A6b | adherence_confound_vs_baseline | seizure_freq_more1mon_less1week | 2 per 6 week | seizure_freq_more1mon_less1week | yes |

## B_source_near_perturbations — rows

| Case | Axis | Gold Purist | Predicted | Pred Purist | Correct |
| --- | --- | --- | --- | --- | :---: |
| B1 | provoked_situational_vs_habitual | seizure_freq_unknown | unknown | seizure_freq_unknown | yes |
| B2 | transient_exacerbation_vs_habitual | seizure_freq_unknown | unknown | seizure_freq_unknown | yes |
| B3 | last_event_only_vs_recurrent_rate | seizure_freq_unknown | seizure free for multiple year | currently_no_seizure | no |
| B4 | adherence_supply_confound_vs_baseline | seizure_freq_unknown | unknown | seizure_freq_unknown | yes |
| B5 | descriptive_semiology_vs_stated_rate | seizure_freq_unknown | no seizure frequency reference | seizure_freq_unknown | yes |
| B6 | cluster_axis_retention | seizure_freq_more1mon_less1week | 1 per 4 to 5 week | seizure_freq_more1per6mon_less1mon | no |
| B7 | true_seizure_free_vs_last_event_only | seizure_freq_unknown | unknown | seizure_freq_unknown | yes |

## C_kcl_style_ood — rows

| Case | Axis | Gold Purist | Predicted | Pred Purist | Correct |
| --- | --- | --- | --- | --- | :---: |
| C1 | transient_exacerbation_vs_habitual | seizure_freq_unknown | unknown | seizure_freq_unknown | yes |
| C2 | provoked_situational_vs_habitual | seizure_freq_unknown | unknown | seizure_freq_unknown | yes |
| C3 | true_seizure_free_vs_last_event_only | currently_no_seizure | seizure free for 6 month | currently_no_seizure | yes |
| C4 | genuine_rate_positive | seizure_freq_more1mon_less1week | 2 per month | seizure_freq_more1mon_less1week | yes |
| C5 | genuine_rate_positive | seizure_freq_more1week_less1day | 1 per week | seizure_freq_more1week_less1day | yes |
| C6 | cluster_axis_retention | seizure_freq_more1mon_less1week | 1 cluster per 3 week, multiple per cluster | seizure_freq_more1mon_less1week | yes |
| C7 | adherence_confound_vs_baseline | seizure_freq_unknown | unknown | seizure_freq_unknown | yes |
| C8 | descriptive_semiology_vs_stated_rate | seizure_freq_unknown | unknown | seizure_freq_unknown | yes |

## Interpretation

This baseline quantifies how much of the component-generation wall is surface-overfit versus genuine clinical gap. A `transfers` verdict requires all three predeclared bars; anything less is reported as `overfit` (or `inconclusive` only on wiring failure) and sent back as `revise`. Failure is the informative outcome and is reported verbatim.
