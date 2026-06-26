# Gan 2026 Consensus/Fresh v0.9 Frozen Gate 1 Hard-Slice Audit

Date: 2026-06-26

This is a validation-only Gate 1 audit over the frozen v0.9 no-call replay and frozen residual component-generation audit. It makes no model calls and does not read locked test rows.

## Experiment Unit

- Work class: hybrid selector hard-slice / selective-action audit.
- Split: `validation`, manifest `gan2026_split_v1`.
- Selector: `gan2026_consensus_fresh_agreement_selector_v0_9`.
- Scorer: unchanged Gan-compatible Purist first; Pragmatic sidecar.
- Stop rule: Gate 1 pass advances only to Gate 2 robustness/stress panels; it does not authorize `test450`.

## Overall Readout

- Deterministic Purist: 697/750
- Consensus Purist: 708/750
- Fresh-evidence Purist: 682/750
- Selected Purist: 733/750
- Selected Pragmatic: 735/750
- Changed labels: 49
- Wrong->correct: 36
- Correct->wrong: 0
- Wrong->wrong: 17
- Correct->correct: 697
- Changed-label precision: 0.7347

## Changed-Label Bands

| Band | Rows | Selected Purist | Selected Pragmatic | Changed | W->C | C->W | W->W | C->C | Net | Precision | Actions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `band_zero` | 3 | 3 | 3 | 3 | 3 | 0 | 0 | 0 | 3 | 1.0 | `{"accept_fresh_boundary_rescue": 3}` |
| `band_unknown` | 18 | 18 | 18 | 18 | 17 | 0 | 0 | 1 | 17 | 0.9444 | `{"accept_consensus_fresh_agreement": 6, "accept_fresh_boundary_rescue": 11, "accept_unknown_uncertainty_rescue": 1}` |
| `band_submonthly` | 5 | 5 | 5 | 5 | 1 | 0 | 0 | 4 | 1 | 0.2 | `{"accept_consensus_fresh_agreement": 1, "accept_parseable_denominator_window_refinement": 4}` |
| `band_monthly` | 7 | 7 | 7 | 7 | 5 | 0 | 0 | 2 | 5 | 0.7143 | `{"accept_consensus_fresh_agreement": 3, "accept_normalized_equivalent_agreement": 1, "accept_parseable_denominator_window_refinement": 3}` |
| `band_weekly` | 10 | 10 | 10 | 10 | 4 | 0 | 0 | 6 | 4 | 0.4 | `{"accept_consensus_fresh_agreement": 10}` |
| `band_daily` | 6 | 6 | 6 | 6 | 6 | 0 | 0 | 0 | 6 | 1.0 | `{"accept_consensus_fresh_agreement": 6}` |

## Residual Slices

| Slice | Rows | Selected Purist | Selected Pragmatic | Changed | W->C | C->W | W->W | C->C | Net | Precision | Actions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `all_changed_labels` | 49 | 49 | 49 | 49 | 36 | 0 | 0 | 13 | 36 | 0.7347 | `{"accept_consensus_fresh_agreement": 26, "accept_fresh_boundary_rescue": 14, "accept_normalized_equivalent_agreement": 1, "accept_parseable_denominator_window_refinement": 7, "accept_unknown_uncertainty_rescue": 1}` |
| `selected_wrong_residual` | 17 | 0 | 2 | 0 | 0 | 0 | 17 | 0 | 0 | None | `{"keep_deterministic_baseline": 17}` |
| `residual_correct_unselected_component` | 6 | 0 | 1 | 0 | 0 | 0 | 6 | 0 | 0 | None | `{"keep_deterministic_baseline": 6}` |
| `residual_no_correct_component_available` | 11 | 0 | 1 | 0 | 0 | 0 | 11 | 0 | 0 | None | `{"keep_deterministic_baseline": 11}` |

## Residual Taxonomy Families

| Family | Rows | No Correct Component | Selected Purist | Selected Pragmatic | W->C | C->W | Net | Actions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `unknown_over_quantified_rate` | 7 | 5 | 0 | 0 | 0 | 0 | 0 | `{"keep_deterministic_baseline": 7}` |
| `last_event_or_seizure_free_overinfer_unknown` | 7 | 6 | 0 | 0 | 0 | 0 | 0 | `{"keep_deterministic_baseline": 7}` |
| `cluster_burden_component_failure` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | `{"keep_deterministic_baseline": 2}` |
| `highest_semiology_or_denominator_conflict` | 3 | 1 | 0 | 2 | 0 | 0 | 0 | `{"keep_deterministic_baseline": 3}` |
| `fresh_only_correct_candidate` | 5 | 0 | 0 | 0 | 0 | 0 | 0 | `{"keep_deterministic_baseline": 5}` |
| `consensus_fresh_correct_but_blocked` | 1 | 0 | 0 | 1 | 0 | 0 | 0 | `{"keep_deterministic_baseline": 1}` |

## Evidence/Source-Validity Diagnostics

The frozen replay does not expose explicit source-validity fields. Available diagnostics are selector decision features and fresh-evidence boundary profiles.

- Fresh uncertainty: `{'low': 740, 'medium': 10}`
- Fresh action: `{'keep_original_structured_event_final': 568, 'replace_with_fresh_evidence_final': 182}`
- Residual top boundary profiles: `{'current/recent frequency': 8, 'no conflicting current/recent frequency evidence': 5, 'denominator/window': 4, 'explicit last event date': 4, 'highest active semiology': 3, 'cluster burden': 2, 'explicit seizure-free interval': 2, 'highest current clinically active burden': 2, 'conditional frequency': 1, 'no explicit count': 1, 'recent 3-month window': 1, 'not seizure free': 1, 'not unknown': 1, 'not no_reference': 1, 'recent single event': 1, 'explicit time window': 1, 'no evidence for recurring rate': 1, 'no explicit seizure-free duration': 1, 'last event in early June 2025': 1, "explicit statement: 'no further events reported' since mid-June 2025": 1}`

## Gate Checks

- selected_purist_at_least_733: `True`
- overall_correct_to_wrong_zero: `True`
- all_predeclared_slices_non_negative_net: `True`
- no_slice_correct_to_wrong: `True`
- changed_label_precision_at_least_0_70: `True`
- residual_no_correct_component_excluded_from_selector_superiority_claims: `True`
- low_precision_bands_named_as_portability_risks: `True`

## Interpretation

Gate 1 passes: v0.9 preserves 733/750 selected Purist, has 0 correct-to-wrong regressions overall and in every predeclared slice, and changed-label precision is 0.7347. The pass is narrow: submonthly and weekly changed-label precision remain portability risks, and 11 residual wrong rows require component-generation work rather than selector-only claims. Advance to Gate 2 robustness/stress panels; do not proceed to locked test.

Portability risks:
- band_submonthly changed-label precision remains low at 1/5.
- band_weekly changed-label precision remains low at 4/10.
- Residual selector-superiority claims must exclude 11/17 selected-wrong rows with no correct component available.

- JSON summary: `experiments\gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate1_hard_slice_audit_2026-06-26.json`.
- Markdown report: `experiments\gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate1_hard_slice_audit_2026-06-26.md`.
