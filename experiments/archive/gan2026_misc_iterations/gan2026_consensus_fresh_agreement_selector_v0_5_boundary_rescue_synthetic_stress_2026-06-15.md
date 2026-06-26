# Gan 2026 Selector v0.5 Boundary-Rescue Synthetic Stress Panel

Date: 2026-06-15

This is a predeclared synthetic mechanism probe for the v0.5 consensus+fresh agreement selector. It uses hand-specified component outputs and the real selector implementation. It is not validation, holdout, benchmark, or model-performance evidence.

## Experiment Unit

- Work class: synthetic component-stress / selector mechanics.
- Split: `synthetic_boundary_rescue_probe`; no Gan rows are read.
- Scorer: current Gan-compatible Purist mapping for synthetic labels.
- Selector: `fresh_boundary_rescue_v0_5`.
- Stress families: seizure-free to unknown/no-reference, no-reference to seizure-free, valid boundary-state hard negatives, unknown-origin controls, and v0.4 regression guards.
- Stop rule: revise if hard negatives expose boundary-rescue false positives; do not freeze for holdout from this artifact alone.

## Summary

- Rows: 12
- Deterministic Purist: 6/12
- Consensus Purist: 6/12
- Fresh Purist: 6/12
- Selected Purist: 8/12
- Expected v0.5 action matches: 12/12
- Desired future action matches: 8/12
- Current-rule false positives: 3
- Conservative false negatives: 1
- Safety successes: 3
- Selector changed labels: 8
- Selector W->C / C->W: 5 / 3
- Actions: `{'accept_fresh_boundary_rescue': 7, 'keep_deterministic_baseline': 4, 'accept_consensus_fresh_agreement': 1}`

## Risk-Type Summary

| Risk Type | Rows | Deterministic | Consensus | Fresh | Selected | Expected Matches | Desired Matches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `current_rule_false_positive` | 3 | 3 | 3 | 0 | 0 | 3 | 0 |
| `intended_negative` | 3 | 3 | 1 | 0 | 3 | 3 | 3 |
| `intended_positive` | 5 | 0 | 1 | 5 | 5 | 5 | 5 |
| `known_conservative_false_negative` | 1 | 0 | 1 | 1 | 0 | 1 | 0 |

## Family Summary

| Family | Rows | Deterministic | Consensus | Fresh | Selected | Expected Matches | Desired Matches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `no_reference_to_seizure_free` | 1 | 0 | 0 | 1 | 1 | 1 | 1 |
| `seizure_free_to_no_reference` | 1 | 0 | 0 | 1 | 1 | 1 | 1 |
| `seizure_free_to_unknown` | 2 | 0 | 0 | 2 | 2 | 2 | 2 |
| `specific_rate_control` | 1 | 1 | 1 | 0 | 1 | 1 | 1 |
| `unknown_origin_false_negative` | 1 | 0 | 1 | 1 | 0 | 1 | 0 |
| `unknown_origin_safety` | 1 | 1 | 0 | 0 | 1 | 1 | 1 |
| `v04_positive_control` | 1 | 0 | 1 | 1 | 1 | 1 | 1 |
| `v04_regression_guard` | 1 | 1 | 0 | 0 | 1 | 1 | 1 |
| `valid_no_reference_hard_negative` | 1 | 1 | 1 | 0 | 0 | 1 | 0 |
| `valid_seizure_free_hard_negative` | 2 | 2 | 2 | 0 | 0 | 2 | 0 |

## Case Readout

| Case | Risk | Gold | Deterministic | Consensus | Fresh | Action | Gate | Selected Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- |
| `sf_last_event_only_to_unknown` | `intended_positive` | `unknown` | `seizure free for 8 month` | `seizure free for 8 month` | `unknown` | `accept_fresh_boundary_rescue` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | True | Last-event-only evidence should not be converted into a seizure-free duration. |
| `sf_open_since_diet_to_unknown` | `intended_positive` | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | `accept_fresh_boundary_rescue` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | True | Open-ended since-starting evidence lacks a usable denominator. |
| `sf_qualitative_events_to_no_reference` | `intended_positive` | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `no seizure frequency reference` | `accept_fresh_boundary_rescue` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | True | A deterministic seizure-free answer is overreach when current event text is qualitative and not a zero-event statement. |
| `no_reference_explicit_no_seizures_to_seizure_free` | `intended_positive` | `seizure free for multiple month` | `no seizure frequency reference` | `no seizure frequency reference` | `seizure free for multiple year` | `accept_fresh_boundary_rescue` | `fresh_boundary_rescue_v0_5:deterministic_no_reference_to_fresh_seizure_free` | True | Fresh evidence can rescue a missed seizure-free state when the absence applies to epileptic seizures. |
| `valid_seizure_free_duration_false_unknown` | `current_rule_false_positive` | `seizure free for 6 month` | `seizure free for 6 month` | `seizure free for 6 month` | `unknown` | `accept_fresh_boundary_rescue` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | False | v0.5 has no evidence-profile guard, so a wrong fresh `unknown` can erase a valid seizure-free duration. |
| `valid_seizure_free_duration_false_no_reference` | `current_rule_false_positive` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `no seizure frequency reference` | `accept_fresh_boundary_rescue` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | False | A valid zero-event interval should not be demoted to no-reference. |
| `valid_no_reference_false_seizure_free` | `current_rule_false_positive` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `seizure free for multiple year` | `accept_fresh_boundary_rescue` | `fresh_boundary_rescue_v0_5:deterministic_no_reference_to_fresh_seizure_free` | False | No-reference text is not equivalent to seizure-free; v0.5 cannot distinguish a wrong fresh boundary rescue here. |
| `sf_to_specific_rate_blocked` | `intended_negative` | `seizure free for 6 month` | `seizure free for 6 month` | `seizure free for 6 month` | `1 per month` | `keep_deterministic_baseline` | `consensus_matches_deterministic` | True | v0.5 only rescues to uncertain boundary states, not rates. |
| `unknown_explicit_count_window_conservative_cost` | `known_conservative_false_negative` | `2 per 2 month` | `unknown` | `2 per 2 month` | `2 per 2 month` | `keep_deterministic_baseline` | `fresh_boundary_rescue_v0_5:deterministic_boundary_origin:unknown` | False | This mirrors the supervisor-approved count-plus-window exception, but v0.5 still blocks deterministic `unknown` origins. |
| `unknown_last_event_specific_rate_blocked` | `intended_negative` | `unknown` | `unknown` | `1 per month` | `1 per month` | `keep_deterministic_baseline` | `fresh_boundary_rescue_v0_5:deterministic_boundary_origin:unknown` | True | Unknown origins should not relax to a rate from last-event-only text. |
| `cluster_cadence_demote_still_blocked` | `intended_negative` | `3 cluster per month, multiple per cluster` | `3 cluster per month, multiple per cluster` | `3 per month` | `3 per month` | `keep_deterministic_baseline` | `fresh_boundary_rescue_v0_5:cluster_label_demoted` | True | The v0.4 cluster-cadence protection must survive v0.5. |
| `specific_consensus_correction_still_accepted` | `intended_positive` | `5 per week` | `2 per month` | `5 per week` | `5 per week` | `accept_consensus_fresh_agreement` | `cluster_cadence_precision_v0_4` | True | The v0.4 exact consensus plus fresh agreement path should remain active. |

## Interpretation

v0.5 behaves exactly as currently implemented on this stress panel: it preserves the v0.4 consensus path and blocks unknown-origin rate relaxation, but it accepts every seizure-free/no-reference fresh boundary rescue regardless of whether the fresh boundary profile actually refutes the deterministic boundary state.

That is the central revision signal. The intended positives support the validation finding that deterministic seizure-free/no-reference overreach is real. The hard negatives show that the current label-only rescue can erase a valid seizure-free duration or turn a true no-reference row into seizure-free. A safer next design should add a gold-free evidence/profile guard for fresh boundary rescue rather than widening the selector.

Decision: revise, not freeze. This synthetic probe supports the v0.5 direction but blocks any holdout-facing protocol until the boundary rescue is evidence/profile-aware.
