# Gan 2026 Selector v0.4 Synthetic Component-Stress Panel

Date: 2026-06-15

This is a predeclared synthetic mechanism probe for the v0.4 consensus+fresh agreement selector. It uses hand-specified component outputs and the real selector implementation. It is not validation, holdout, benchmark, or model-performance evidence.

## Experiment Unit

- Work class: synthetic component-stress / selector mechanics.
- Split: `synthetic_validation_probe`; no Gan rows are read.
- Scorer: current Gan-compatible Purist mapping for synthetic labels.
- Selector: `cluster_cadence_precision_v0_4`.
- Stress families: cluster cadence, unknown boundary, denominator/window, multi-semiology, seizure-free boundary, and agreement controls.
- Stop rule: record safety behavior and known conservative costs; do not freeze for holdout from this artifact alone.

## Summary

- Rows: 20
- Deterministic Purist: 13/20
- Consensus Purist: 11/20
- Fresh Purist: 12/20
- Selected Purist: 18/20
- Expected v0.4 action matches: 20/20
- Desired future action matches: 18/20
- False negatives from conservative unknown-origin gate: 2
- Safety successes where v0.4 blocks a wrong agreed switch: 9
- Selector changed labels: 7
- Selector W->C / C->W: 5 / 0
- Actions: `{'keep_deterministic_baseline': 13, 'accept_consensus_fresh_agreement': 7}`

## Family Summary

| Family | Rows | Deterministic | Consensus | Fresh | Selected | Expected Action Matches | Desired Matches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `agreement_control` | 2 | 2 | 1 | 2 | 2 | 2 | 2 |
| `cluster_cadence` | 6 | 5 | 4 | 4 | 6 | 6 | 6 |
| `denominator_window` | 4 | 1 | 3 | 3 | 4 | 4 | 4 |
| `multi_semiology` | 1 | 0 | 1 | 1 | 1 | 1 | 1 |
| `seizure_free_boundary` | 1 | 1 | 0 | 0 | 1 | 1 | 1 |
| `unknown_boundary` | 6 | 4 | 2 | 2 | 4 | 6 | 4 |

## Case Readout

| Case | Family | Gold | Deterministic | Consensus | Fresh | Action | Gate | Selected Correct | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- |
| `cluster_demote_plain_rate` | `cluster_cadence` | `3 cluster per month, multiple per cluster` | `3 cluster per month, multiple per cluster` | `3 per month` | `3 per month` | `keep_deterministic_baseline` | `cluster_cadence_precision_v0_4:cluster_label_demoted` | True | A cluster cadence should not be demoted to a plain rate. |
| `cluster_cadence_change` | `cluster_cadence` | `5 cluster per month, multiple per cluster` | `5 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `keep_deterministic_baseline` | `cluster_cadence_precision_v0_4:cluster_cadence_changed` | True | The selector should preserve the deterministic cluster cadence. |
| `same_cadence_burden_refinement` | `cluster_cadence` | `2 to 3 cluster per month, 5 per cluster` | `2 to 3 cluster per month, multiple per cluster` | `2 to 3 cluster per month, 5 per cluster` | `2 to 3 cluster per month, 5 per cluster` | `accept_consensus_fresh_agreement` | `cluster_cadence_precision_v0_4` | True | Same-cadence burden refinement is allowed. |
| `plain_monthly_to_cluster_weekly` | `cluster_cadence` | `1 cluster per week, 2 to 3 per cluster` | `2 per month` | `1 cluster per week, 2 to 3 per cluster` | `1 cluster per week, 2 to 3 per cluster` | `accept_consensus_fresh_agreement` | `cluster_cadence_precision_v0_4` | True | Consensus can add a cluster label when the deterministic label has no cluster cadence to protect. |
| `last_event_only_unknown` | `unknown_boundary` | `unknown` | `unknown` | `1 per month` | `1 per month` | `keep_deterministic_baseline` | `cluster_cadence_precision_v0_4:deterministic_boundary_origin:unknown` | True | Last-event date alone should not become a frequency. |
| `open_ended_since_diet_unknown` | `unknown_boundary` | `unknown` | `unknown` | `3 per month` | `3 per month` | `keep_deterministic_baseline` | `cluster_cadence_precision_v0_4:deterministic_boundary_origin:unknown` | True | Open-ended since-starting evidence lacks a usable denominator. |
| `explicit_count_window_from_unknown` | `unknown_boundary` | `2 per 2 month` | `unknown` | `2 per 2 month` | `2 per 2 month` | `keep_deterministic_baseline` | `cluster_cadence_precision_v0_4:deterministic_boundary_origin:unknown` | False | Current v0.4 is conservative out of unknown origins; this is a known false-negative cost. |
| `no_reference_origin_suppressed` | `unknown_boundary` | `no seizure frequency reference` | `no seizure frequency reference` | `2 per week` | `2 per week` | `keep_deterministic_baseline` | `cluster_cadence_precision_v0_4:deterministic_boundary_origin:no_reference` | True | No-reference origins should not be overwritten by a specific rate. |
| `unknown_replacement_suppressed` | `unknown_boundary` | `2 per month` | `2 per month` | `unknown` | `unknown` | `keep_deterministic_baseline` | `cluster_cadence_precision_v0_4:uncertain_or_ambiguous_replacement:unknown` | True | Specific deterministic rates should not be replaced by unknown. |
| `seizure_free_replacement_suppressed` | `seizure_free_boundary` | `2 per month` | `2 per month` | `seizure free` | `seizure free` | `keep_deterministic_baseline` | `cluster_cadence_precision_v0_4:uncertain_or_ambiguous_replacement:seizure_free` | True | A current frequency should not be replaced by historical seizure-free wording. |
| `ambiguous_plural_other_suppressed` | `denominator_window` | `2 per month` | `2 per month` | `2 per 5 months` | `2 per 5 months` | `keep_deterministic_baseline` | `cluster_cadence_precision_v0_4:uncertain_or_ambiguous_replacement:other` | True | Parser-ambiguous replacements are suppressed by v0.4. |
| `daily_correction_accepted` | `denominator_window` | `1 per day` | `1 per year` | `1 per day` | `1 per day` | `accept_consensus_fresh_agreement` | `cluster_cadence_precision_v0_4` | True | A specific non-boundary correction with fresh agreement is accepted. |
| `weekly_denominator_accepted` | `denominator_window` | `5 per week` | `2 per month` | `5 per week` | `5 per week` | `accept_consensus_fresh_agreement` | `cluster_cadence_precision_v0_4` | True | Weekly denominator corrections are allowed when specific and agreed. |
| `multi_semiology_highest_current` | `multi_semiology` | `3 per week` | `1 per month` | `3 per week` | `3 per week` | `accept_consensus_fresh_agreement` | `cluster_cadence_precision_v0_4` | True | The selected current burden should follow the highest current seizure frequency. |
| `fresh_disagrees_keep` | `agreement_control` | `5 per week` | `5 per week` | `1 per day` | `5 per week` | `keep_deterministic_baseline` | `fresh_evidence_disagrees_with_consensus` | True | Consensus without fresh-evidence agreement is not enough to switch. |
| `consensus_same_unchanged` | `agreement_control` | `2 per month` | `2 per month` | `2 per month` | `2 per month` | `keep_deterministic_baseline` | `consensus_matches_deterministic` | True | No selector action is needed when consensus matches deterministic. |
| `same_day_cluster_demotion_category_neutral` | `cluster_cadence` | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `1 per 5 day` | `1 per 5 day` | `keep_deterministic_baseline` | `cluster_cadence_precision_v0_4:uncertain_or_ambiguous_replacement:other` | True | Even when Purist category is unchanged, cluster semantics should be preserved. |
| `explicit_followup_from_unknown` | `unknown_boundary` | `3 per month` | `unknown` | `3 per month` | `3 per month` | `keep_deterministic_baseline` | `cluster_cadence_precision_v0_4:deterministic_boundary_origin:unknown` | False | Another explicit count-window case exposes the conservative unknown-origin cost. |
| `plain_to_cluster_monthly_refinement` | `cluster_cadence` | `1 cluster per month, multiple per cluster` | `2 per month` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `accept_consensus_fresh_agreement` | `cluster_cadence_precision_v0_4` | True | Adding cluster semantics is allowed when deterministic had no cluster cadence. |
| `monthly_within_band_churn` | `denominator_window` | `2 per month` | `1 per month` | `2 per month` | `2 per month` | `accept_consensus_fresh_agreement` | `cluster_cadence_precision_v0_4` | True | Specific same-band refinements may be accepted, but they do not improve Purist. |

## Interpretation

v0.4 behaves as designed on the stress panel: it protects cluster cadence, suppresses last-event-only and open-ended unknown-boundary over-inference, blocks seizure-free/unknown replacements of specific rates, and requires fresh-evidence agreement before switching.

The panel also exposes the main conservative cost: explicit count-plus-window cases that start from deterministic `unknown` are kept as unknown by the current selector. That is safer under Yujian's guidance, but it likely leaves recoverable rows on the table. A future v0.5 should only relax this with a narrow evidence feature for explicit count plus usable follow-up period, and should be tested on a separate predeclared panel before any holdout-facing protocol.

Decision: revise, not freeze. This synthetic probe supports the v0.4 mechanism but does not establish validation/test generalization or authorize a `test450` audit.
