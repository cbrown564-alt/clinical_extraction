# Gan 2026 Selector v0.9 Semantic-Equiv/Unknown Synthetic Stress

Date: 2026-06-15

This is a predeclared synthetic mechanism probe for v0.9. It uses hand-specified component outputs and the real selector implementation. It is not validation, holdout, benchmark, or model-performance evidence.

## Summary

- Rows: 7
- Deterministic Purist: 4/7
- Consensus Purist: 5/7
- Fresh Purist: 6/7
- Selected Purist: 6/7
- Desired action matches: 7/7
- Current-rule false positives: 0
- Conservative false negatives: 1
- Safety successes: 1
- Selector changed labels: 2
- Selector W->C / C->W: 2 / 0
- Changed-label precision: 1.0
- Actions: `{'accept_normalized_equivalent_agreement': 1, 'accept_unknown_uncertainty_rescue': 1, 'keep_deterministic_baseline': 5}`

## Case Readout

| Case | Risk | Action | Gate | Selected Correct | Desired Match |
| --- | --- | --- | --- | ---: | ---: |
| `normalized_equivalent_month_positive` | `intended_positive` | `accept_normalized_equivalent_agreement` | `semantic_equiv_unknown_uncertainty_v0_9:normalized_equivalent_consensus_fresh` | True | True |
| `unknown_uncertainty_positive` | `intended_positive` | `accept_unknown_uncertainty_rescue` | `semantic_equiv_unknown_uncertainty_v0_9:specific_rate_to_unknown_uncertainty_supported` | True | True |
| `non_equivalent_disagreement_negative` | `intended_negative` | `keep_deterministic_baseline` | `fresh_evidence_disagrees_with_consensus` | True | True |
| `already_equivalent_deterministic_negative` | `intended_negative` | `keep_deterministic_baseline` | `fresh_evidence_disagrees_with_consensus` | True | True |
| `cluster_burden_specified_unknown_negative` | `intended_negative` | `keep_deterministic_baseline` | `semantic_equiv_unknown_uncertainty_v0_9:unknown_uncertainty_profile_blocked` | True | True |
| `unknown_no_reference_origin_negative` | `intended_negative` | `keep_deterministic_baseline` | `semantic_equiv_unknown_uncertainty_v0_9:deterministic_boundary_origin:no_reference` | True | True |
| `unknown_missing_profile_negative` | `intended_negative` | `keep_deterministic_baseline` | `semantic_equiv_unknown_uncertainty_v0_9:missing_unknown_uncertainty_profile` | False | True |

## Interpretation

v0.9 accepts two small selector-only openings: consensus/fresh disagreement when the labels normalize to the same rate, and specific-rate to unknown when both model sources agree on unknown and the fresh profile explicitly says the evidence is unquantified. It blocks non-equivalent disagreement, no-reference churn, missing unknown profiles, and fully specified cluster-burden demotion.

Decision: revise, not freeze. This is useful residual-headroom cleanup, but the gain is too small and validation-local for a holdout-facing candidate.
