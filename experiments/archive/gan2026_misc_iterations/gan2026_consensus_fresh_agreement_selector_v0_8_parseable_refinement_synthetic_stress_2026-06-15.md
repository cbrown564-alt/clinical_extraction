# Gan 2026 Selector v0.8 Parseable Refinement Synthetic Stress

Date: 2026-06-15

This is a predeclared synthetic mechanism probe for v0.8. It uses hand-specified component outputs and the real selector implementation. It is not validation, holdout, benchmark, or model-performance evidence.

## Summary

- Rows: 11
- Deterministic Purist: 5/11
- Consensus Purist: 4/11
- Fresh Purist: 4/11
- Selected Purist: 8/11
- Desired action matches: 11/11
- Current-rule false positives: 0
- Conservative false negatives: 1
- Safety successes: 5
- Selector changed labels: 3
- Selector W->C / C->W: 3 / 0
- Changed-label precision: 1.0
- Actions: `{'accept_parseable_denominator_window_refinement': 3, 'keep_deterministic_baseline': 8}`

## Risk-Type Summary

| Risk Type | Rows | Deterministic | Consensus | Fresh | Selected | Desired Matches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `intended_negative` | 8 | 5 | 1 | 1 | 5 | 8 |
| `intended_positive` | 3 | 0 | 3 | 3 | 3 | 3 |

## Case Readout

| Case | Risk | Action | Gate | Selected Correct | Desired Match |
| --- | --- | --- | --- | ---: | ---: |
| `denominator_window_current_rate_positive` | `intended_positive` | `accept_parseable_denominator_window_refinement` | `parseable_denominator_window_refinement_v0_8:profile_supported_parseable_refinement` | True | True |
| `explicit_current_frequency_range_denominator_positive` | `intended_positive` | `accept_parseable_denominator_window_refinement` | `parseable_denominator_window_refinement_v0_8:profile_supported_parseable_refinement` | True | True |
| `explicit_count_over_window_cluster_count_positive` | `intended_positive` | `accept_parseable_denominator_window_refinement` | `parseable_denominator_window_refinement_v0_8:profile_supported_parseable_refinement` | True | True |
| `highest_active_semiology_negative` | `intended_negative` | `keep_deterministic_baseline` | `parseable_denominator_window_refinement_v0_8:unsafe_parseable_refinement_profile` | True | True |
| `seizure_free_interval_negative` | `intended_negative` | `keep_deterministic_baseline` | `parseable_denominator_window_refinement_v0_8:unsafe_parseable_refinement_profile` | True | True |
| `last_event_only_negative` | `intended_negative` | `keep_deterministic_baseline` | `parseable_denominator_window_refinement_v0_8:unsafe_or_unclear_window_profile` | True | True |
| `boundary_origin_not_relaxed_negative` | `intended_negative` | `keep_deterministic_baseline` | `parseable_denominator_window_refinement_v0_8:boundary_origin_not_relaxed` | False | True |
| `fresh_consensus_disagreement_negative` | `intended_negative` | `keep_deterministic_baseline` | `fresh_evidence_disagrees_with_consensus` | False | True |
| `unparseable_replacement_negative` | `intended_negative` | `keep_deterministic_baseline` | `parseable_denominator_window_refinement_v0_8:replacement_not_parseable_specific_rate` | False | True |
| `current_recent_only_negative` | `intended_negative` | `keep_deterministic_baseline` | `parseable_denominator_window_refinement_v0_8:missing_parseable_refinement_profile` | True | True |
| `multiple_active_semiologies_negative` | `intended_negative` | `keep_deterministic_baseline` | `parseable_denominator_window_refinement_v0_8:unsafe_parseable_refinement_profile` | True | True |

## Interpretation

v0.8 accepts parseable consensus+fresh replacements that v0.7 treated as ambiguous `other` only when the fresh profile supports a denominator/window refinement or explicit current count/window. It blocks boundary origins, last-event and seizure-free interval profiles, highest-semiology traps, disagreement, and unparseable replacement labels.

Decision: revise, not freeze. This strengthens the selector on a small validation-backed family, but it is still saved-output development evidence rather than a holdout-facing candidate.
