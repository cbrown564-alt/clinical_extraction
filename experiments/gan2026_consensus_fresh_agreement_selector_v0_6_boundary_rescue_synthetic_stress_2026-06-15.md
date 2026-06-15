# Gan 2026 Selector v0.6 Boundary-Profile Guard Synthetic Replay

Date: 2026-06-15

This is a no-call replay of v0.6 over the predeclared v0.5 boundary-rescue synthetic stress panel. It is not validation, holdout, benchmark, or model-performance evidence.

## Summary

- Rows: 12
- Deterministic Purist: 6/12
- Consensus Purist: 6/12
- Fresh Purist: 6/12
- Selected Purist: 11/12
- Desired future action matches: 11/12
- Current-rule false positives: 0
- Conservative false negatives: 1
- Safety successes: 6
- Selector changed labels: 5
- Selector W->C / C->W: 5 / 0
- Changed-label precision: 1.0
- Actions: `{'accept_fresh_boundary_rescue': 4, 'keep_deterministic_baseline': 7, 'accept_consensus_fresh_agreement': 1}`

## Risk-Type Summary

| Risk Type | Rows | Deterministic | Consensus | Fresh | Selected | Desired Matches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `current_rule_false_positive` | 3 | 3 | 3 | 0 | 3 | 3 |
| `intended_negative` | 3 | 3 | 1 | 0 | 3 | 3 |
| `intended_positive` | 5 | 0 | 1 | 5 | 5 | 5 |
| `known_conservative_false_negative` | 1 | 0 | 1 | 1 | 0 | 0 |

## Case Readout

| Case | Risk | Action | Gate | Selected Correct | Desired Match |
| --- | --- | --- | --- | ---: | ---: |
| `sf_last_event_only_to_unknown` | `intended_positive` | `accept_fresh_boundary_rescue` | `profile_guard_boundary_rescue_v0_6:seizure_free_to_uncertain_supported` | True | True |
| `sf_open_since_diet_to_unknown` | `intended_positive` | `accept_fresh_boundary_rescue` | `profile_guard_boundary_rescue_v0_6:seizure_free_to_uncertain_supported` | True | True |
| `sf_qualitative_events_to_no_reference` | `intended_positive` | `accept_fresh_boundary_rescue` | `profile_guard_boundary_rescue_v0_6:seizure_free_to_uncertain_supported` | True | True |
| `no_reference_explicit_no_seizures_to_seizure_free` | `intended_positive` | `accept_fresh_boundary_rescue` | `profile_guard_boundary_rescue_v0_6:no_reference_to_seizure_free_supported` | True | True |
| `valid_seizure_free_duration_false_unknown` | `current_rule_false_positive` | `keep_deterministic_baseline` | `profile_guard_boundary_rescue_v0_6:profile_affirms_seizure_free` | True | True |
| `valid_seizure_free_duration_false_no_reference` | `current_rule_false_positive` | `keep_deterministic_baseline` | `profile_guard_boundary_rescue_v0_6:profile_affirms_seizure_free` | True | True |
| `valid_no_reference_false_seizure_free` | `current_rule_false_positive` | `keep_deterministic_baseline` | `profile_guard_boundary_rescue_v0_6:profile_only_no_reference_absence` | True | True |
| `sf_to_specific_rate_blocked` | `intended_negative` | `keep_deterministic_baseline` | `consensus_matches_deterministic` | True | True |
| `unknown_explicit_count_window_conservative_cost` | `known_conservative_false_negative` | `keep_deterministic_baseline` | `profile_guard_boundary_rescue_v0_6:deterministic_boundary_origin:unknown` | False | False |
| `unknown_last_event_specific_rate_blocked` | `intended_negative` | `keep_deterministic_baseline` | `profile_guard_boundary_rescue_v0_6:deterministic_boundary_origin:unknown` | True | True |
| `cluster_cadence_demote_still_blocked` | `intended_negative` | `keep_deterministic_baseline` | `profile_guard_boundary_rescue_v0_6:cluster_label_demoted` | True | True |
| `specific_consensus_correction_still_accepted` | `intended_positive` | `accept_consensus_fresh_agreement` | `cluster_cadence_precision_v0_4` | True | True |

## Interpretation

The v0.6 profile guard blocks all three v0.5 hard-negative false positives while preserving the intended fresh boundary rescues and the v0.4 positive/negative controls. The remaining miss is the known conservative `unknown` origin count-plus-window case, which needs a separate evidence feature before relaxing.

Decision: revise, not freeze. v0.6 is safer than v0.5 on the synthetic boundary panel while preserving the validation replay score, but it is still a saved-output development artifact.
