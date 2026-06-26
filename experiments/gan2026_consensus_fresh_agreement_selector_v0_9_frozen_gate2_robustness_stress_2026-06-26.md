# Gan 2026 Consensus/Fresh v0.9 Frozen Gate 2 Robustness Stress

Date: 2026-06-26

This is a synthetic/source-near validation-only mechanism panel over the frozen v0.9 selector. It makes no model calls and reads no locked test rows.

## Experiment Unit

- Work class: hybrid selector robustness and component-state stress.
- Surface: synthetic/source-near validation-only component states.
- Selector: `gan2026_consensus_fresh_agreement_selector_v0_9`.
- Scorer: Gan-compatible Purist first; Pragmatic sidecar.
- Stop rule: pass authorizes Gate 3 source-symmetry preflight only.

## Summary

- Rows: 24
- Desired-action match: 24/24 (1.0)
- Selected Purist: 23/24
- Selected Pragmatic: 24/24
- Changed labels: 12
- Wrong->correct: 12
- Correct->wrong: 0
- Changed-label precision: 1.0
- Deterministic-correct negative-control false positives: 0
- Cluster demotions: 0
- Forbidden no-reference-to-unknown churn: 0
- Actions: `{'accept_normalized_equivalent_agreement': 3, 'keep_deterministic_baseline': 12, 'accept_unknown_uncertainty_rescue': 2, 'accept_fresh_boundary_rescue': 3, 'accept_consensus_fresh_agreement': 1, 'accept_parseable_denominator_window_refinement': 3}`

## Family Readout

| Family | Rows | Match Rate | W->C | C->W | Selected Purist | Selected Pragmatic | Actions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `normalized_equivalent_agreement` | 3 | 1.0 | 2 | 0 | 3 | 3 | `{'accept_normalized_equivalent_agreement': 2, 'keep_deterministic_baseline': 1}` |
| `unknown_uncertainty` | 3 | 1.0 | 2 | 0 | 3 | 3 | `{'accept_unknown_uncertainty_rescue': 2, 'keep_deterministic_baseline': 1}` |
| `unknown_no_reference_churn` | 3 | 1.0 | 1 | 0 | 3 | 3 | `{'accept_fresh_boundary_rescue': 1, 'keep_deterministic_baseline': 2}` |
| `last_event_seizure_free_overinference` | 3 | 1.0 | 2 | 0 | 3 | 3 | `{'accept_fresh_boundary_rescue': 2, 'keep_deterministic_baseline': 1}` |
| `cluster_burden_preservation` | 3 | 1.0 | 1 | 0 | 3 | 3 | `{'accept_consensus_fresh_agreement': 1, 'keep_deterministic_baseline': 2}` |
| `multiple_semiology_denominator_conflict` | 3 | 1.0 | 1 | 0 | 3 | 3 | `{'accept_parseable_denominator_window_refinement': 1, 'keep_deterministic_baseline': 2}` |
| `non_equivalent_consensus_fresh_disagreement` | 3 | 1.0 | 1 | 0 | 2 | 3 | `{'accept_normalized_equivalent_agreement': 1, 'keep_deterministic_baseline': 2}` |
| `parseable_denominator_window_refinement` | 3 | 1.0 | 2 | 0 | 3 | 3 | `{'accept_parseable_denominator_window_refinement': 2, 'keep_deterministic_baseline': 1}` |

## Case Readout

| Case | Family | Type | Desired | Actual | Gate | Selected Correct | Match |
| --- | --- | --- | --- | --- | --- | ---: | ---: |
| `norm_equiv_positive_month_spelling` | `normalized_equivalent_agreement` | `positive` | `accept_normalized_equivalent_agreement` | `accept_normalized_equivalent_agreement` | `semantic_equiv_unknown_uncertainty_v0_9:normalized_equivalent_consensus_fresh` | True | True |
| `norm_equiv_negative_deterministic_already_same` | `normalized_equivalent_agreement` | `deterministic_correct_negative` | `keep_deterministic_baseline` | `keep_deterministic_baseline` | `fresh_evidence_disagrees_with_consensus` | True | True |
| `norm_equiv_paraphrase_week_to_month` | `normalized_equivalent_agreement` | `paraphrase` | `accept_normalized_equivalent_agreement` | `accept_normalized_equivalent_agreement` | `semantic_equiv_unknown_uncertainty_v0_9:normalized_equivalent_consensus_fresh` | True | True |
| `unknown_uncertainty_positive_unquantified_logs` | `unknown_uncertainty` | `positive` | `accept_unknown_uncertainty_rescue` | `accept_unknown_uncertainty_rescue` | `semantic_equiv_unknown_uncertainty_v0_9:specific_rate_to_unknown_uncertainty_supported` | True | True |
| `unknown_uncertainty_negative_missing_profile` | `unknown_uncertainty` | `deterministic_correct_negative` | `keep_deterministic_baseline` | `keep_deterministic_baseline` | `semantic_equiv_unknown_uncertainty_v0_9:missing_unknown_uncertainty_profile` | True | True |
| `unknown_uncertainty_paraphrase_patient_unsure` | `unknown_uncertainty` | `paraphrase` | `accept_unknown_uncertainty_rescue` | `accept_unknown_uncertainty_rescue` | `semantic_equiv_unknown_uncertainty_v0_9:specific_rate_to_unknown_uncertainty_supported` | True | True |
| `unknown_no_reference_positive_seizure_free_rescue` | `unknown_no_reference_churn` | `positive` | `accept_fresh_boundary_rescue` | `accept_fresh_boundary_rescue` | `profile_guard_boundary_rescue_v0_6:no_reference_to_seizure_free_supported` | True | True |
| `unknown_no_reference_negative_no_ref_to_unknown` | `unknown_no_reference_churn` | `deterministic_correct_negative` | `keep_deterministic_baseline` | `keep_deterministic_baseline` | `semantic_equiv_unknown_uncertainty_v0_9:deterministic_boundary_origin:no_reference` | True | True |
| `unknown_no_reference_paraphrase_absence_only` | `unknown_no_reference_churn` | `paraphrase` | `keep_deterministic_baseline` | `keep_deterministic_baseline` | `parseable_denominator_window_refinement_v0_8:profile_only_no_reference_absence` | True | True |
| `last_event_positive_seizure_free_overreach` | `last_event_seizure_free_overinference` | `positive` | `accept_fresh_boundary_rescue` | `accept_fresh_boundary_rescue` | `profile_guard_boundary_rescue_v0_6:seizure_free_to_uncertain_supported` | True | True |
| `last_event_negative_affirms_seizure_free` | `last_event_seizure_free_overinference` | `deterministic_correct_negative` | `keep_deterministic_baseline` | `keep_deterministic_baseline` | `parseable_denominator_window_refinement_v0_8:profile_affirms_seizure_free` | True | True |
| `last_event_paraphrase_no_further_events_but_short` | `last_event_seizure_free_overinference` | `paraphrase` | `accept_fresh_boundary_rescue` | `accept_fresh_boundary_rescue` | `profile_guard_boundary_rescue_v0_6:seizure_free_to_uncertain_supported` | True | True |
| `cluster_positive_same_cadence_events_per_cluster` | `cluster_burden_preservation` | `positive` | `accept_consensus_fresh_agreement` | `accept_consensus_fresh_agreement` | `semantic_equiv_unknown_uncertainty_v0_9:base_consensus` | True | True |
| `cluster_negative_demote_to_plain_rate` | `cluster_burden_preservation` | `deterministic_correct_negative` | `keep_deterministic_baseline` | `keep_deterministic_baseline` | `semantic_equiv_unknown_uncertainty_v0_9:cluster_label_demoted` | True | True |
| `cluster_paraphrase_fully_specified_unknown_block` | `cluster_burden_preservation` | `paraphrase` | `keep_deterministic_baseline` | `keep_deterministic_baseline` | `semantic_equiv_unknown_uncertainty_v0_9:unknown_uncertainty_profile_blocked` | True | True |
| `multi_semiology_positive_parseable_refinement` | `multiple_semiology_denominator_conflict` | `positive` | `accept_parseable_denominator_window_refinement` | `accept_parseable_denominator_window_refinement` | `parseable_denominator_window_refinement_v0_8:profile_supported_parseable_refinement` | True | True |
| `multi_semiology_negative_lower_burden_selected` | `multiple_semiology_denominator_conflict` | `deterministic_correct_negative` | `keep_deterministic_baseline` | `keep_deterministic_baseline` | `parseable_denominator_window_refinement_v0_8:unsafe_parseable_refinement_profile` | True | True |
| `multi_semiology_paraphrase_highest_active_block` | `multiple_semiology_denominator_conflict` | `paraphrase` | `keep_deterministic_baseline` | `keep_deterministic_baseline` | `parseable_denominator_window_refinement_v0_8:unsafe_parseable_refinement_profile` | True | True |
| `non_equiv_positive_equiv_disagreement` | `non_equivalent_consensus_fresh_disagreement` | `positive` | `accept_normalized_equivalent_agreement` | `accept_normalized_equivalent_agreement` | `semantic_equiv_unknown_uncertainty_v0_9:normalized_equivalent_consensus_fresh` | True | True |
| `non_equiv_negative_disagreement_kept` | `non_equivalent_consensus_fresh_disagreement` | `deterministic_correct_negative` | `keep_deterministic_baseline` | `keep_deterministic_baseline` | `fresh_evidence_disagrees_with_consensus` | True | True |
| `non_equiv_paraphrase_near_numeric_disagreement` | `non_equivalent_consensus_fresh_disagreement` | `paraphrase` | `keep_deterministic_baseline` | `keep_deterministic_baseline` | `fresh_evidence_disagrees_with_consensus` | False | True |
| `parseable_positive_current_denominator_window` | `parseable_denominator_window_refinement` | `positive` | `accept_parseable_denominator_window_refinement` | `accept_parseable_denominator_window_refinement` | `parseable_denominator_window_refinement_v0_8:profile_supported_parseable_refinement` | True | True |
| `parseable_negative_seizure_free_interval` | `parseable_denominator_window_refinement` | `deterministic_correct_negative` | `keep_deterministic_baseline` | `keep_deterministic_baseline` | `parseable_denominator_window_refinement_v0_8:unsafe_parseable_refinement_profile` | True | True |
| `parseable_paraphrase_explicit_count_window` | `parseable_denominator_window_refinement` | `paraphrase` | `accept_parseable_denominator_window_refinement` | `accept_parseable_denominator_window_refinement` | `parseable_denominator_window_refinement_v0_8:profile_supported_parseable_refinement` | True | True |

## Gate Checks

- desired_action_match_at_least_0_90: `True`
- no_family_below_0_80: `True`
- correct_to_wrong_zero: `True`
- deterministic_correct_negative_false_positives_zero: `True`
- no_cluster_burden_demotion: `True`
- no_forbidden_no_reference_to_unknown_churn: `True`
- gate_passed: `True`

## Spelling/Equivalence Diagnostics

- Spelling/equivalence probe rows: 5; failures: `[]`
The panel includes equivalent textual variants (`1 per 1 month` versus `1 per month`, `2 per 2 week` versus `1 per week`) and near numeric disagreements (`11 per 3 month` versus `10 per 3 month`).

## Interpretation

Gate 2 passes as a mechanism test: desired-action match is 24/24 (1.0), no family falls below 0.80, Purist correct-to-wrong is 0, deterministic-correct controls have 0 false-positive selector actions, cluster burden is not demoted, and no forbidden no-reference-to-unknown churn appears. This authorizes only Gate 3 source-symmetry preflight, not locked test.

- JSON summary: `experiments\gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate2_robustness_stress_2026-06-26.json`.
- Markdown report: `experiments\gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate2_robustness_stress_2026-06-26.md`.
