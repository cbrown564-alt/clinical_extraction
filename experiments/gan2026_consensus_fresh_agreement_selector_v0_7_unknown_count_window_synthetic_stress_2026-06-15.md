# Gan 2026 Selector v0.7 Unknown Count-Window Synthetic Stress

Date: 2026-06-15

This is a predeclared synthetic mechanism probe for v0.7. It uses hand-specified component outputs and the real selector implementation. It is not validation, holdout, benchmark, or model-performance evidence.

## Summary

- Rows: 12
- Deterministic Purist: 5/12
- Consensus Purist: 7/12
- Fresh Purist: 8/12
- Selected Purist: 10/12
- Desired action matches: 12/12
- Current-rule false positives: 0
- Conservative false negatives: 2
- Safety successes: 4
- Selector changed labels: 5
- Selector W->C / C->W: 5 / 0
- Changed-label precision: 1.0
- Actions: `{'accept_unknown_count_window_rescue': 4, 'keep_deterministic_baseline': 7, 'accept_fresh_boundary_rescue': 1}`

## Risk-Type Summary

| Risk Type | Rows | Deterministic | Consensus | Fresh | Selected | Desired Matches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `intended_negative` | 6 | 5 | 2 | 2 | 5 | 6 |
| `intended_positive` | 5 | 0 | 4 | 5 | 5 | 5 |
| `known_conservative_false_negative` | 1 | 0 | 1 | 1 | 0 | 1 |

## Case Readout

| Case | Risk | Action | Gate | Selected Correct | Desired Match |
| --- | --- | --- | --- | ---: | ---: |
| `topiramate_two_seizures_two_months` | `intended_positive` | `accept_unknown_count_window_rescue` | `unknown_count_window_rescue_v0_7:explicit_count_window_supported` | True | True |
| `three_events_three_month_review` | `intended_positive` | `accept_unknown_count_window_rescue` | `unknown_count_window_rescue_v0_7:explicit_count_window_supported` | True | True |
| `two_events_five_month_followup` | `intended_positive` | `accept_unknown_count_window_rescue` | `unknown_count_window_rescue_v0_7:explicit_count_window_supported` | True | True |
| `four_events_four_month_interval` | `intended_positive` | `accept_unknown_count_window_rescue` | `unknown_count_window_rescue_v0_7:explicit_count_window_supported` | True | True |
| `last_event_only_none_since` | `intended_negative` | `keep_deterministic_baseline` | `unknown_count_window_rescue_v0_7:unsafe_or_unclear_window_profile` | True | True |
| `open_ended_since_diet` | `intended_negative` | `keep_deterministic_baseline` | `unknown_count_window_rescue_v0_7:unsafe_or_unclear_window_profile` | True | True |
| `vague_several_with_period` | `intended_negative` | `keep_deterministic_baseline` | `unknown_count_window_rescue_v0_7:unsafe_or_unclear_window_profile` | True | True |
| `fresh_consensus_disagreement` | `intended_negative` | `keep_deterministic_baseline` | `unknown_count_window_rescue_v0_7:fresh_consensus_disagree` | False | True |
| `no_reference_origin_not_relaxed` | `known_conservative_false_negative` | `keep_deterministic_baseline` | `unknown_count_window_rescue_v0_7:deterministic_boundary_origin:no_reference` | False | True |
| `unknown_to_seizure_free_not_count_window` | `intended_negative` | `keep_deterministic_baseline` | `unknown_count_window_rescue_v0_7:unsupported_replacement_unit:seizure_free` | True | True |
| `v06_boundary_positive_control` | `intended_positive` | `accept_fresh_boundary_rescue` | `profile_guard_boundary_rescue_v0_6:seizure_free_to_uncertain_supported` | True | True |
| `cluster_cadence_guard_control` | `intended_negative` | `keep_deterministic_baseline` | `unknown_count_window_rescue_v0_7:cluster_label_demoted` | True | True |

## Interpretation

v0.7 accepts only explicit count-plus-window unknown-origin rescues and blocks last-event-only, open-ended treatment-start, vague-count, unsupported replacement, and disagreement controls. It preserves the v0.6 boundary-rescue and v0.4 cluster-cadence controls.

Decision: revise, not freeze. The synthetic mechanism works, but the saved validation replay has no qualifying unknown-origin W->C rows, so this is robustness/preparation evidence rather than a new holdout-facing candidate.
