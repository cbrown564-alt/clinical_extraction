# Gan 2026 Selector v0.4 Unknown-Origin Relaxation Probe

Date: 2026-06-15

This is a validation-only counterfactual check over saved v0.4 selector rows. It tests the tempting v0.5 relaxation: accept exact consensus switches when V12 agrees even if the deterministic origin is `unknown`.

No holdout rows are read. Gold labels are used only post-hoc to score the counterfactual.

## Summary

- Source rows: 750
- Unknown-origin blocked switches: 4
- Counterfactual wrong->correct: 0
- Counterfactual correct->wrong: 2
- Counterfactual correct->correct: 2
- Counterfactual wrong->wrong: 0
- Net if accepted all unknown-origin switches: -2

## Rows

| Source row | Gold | Deterministic | Consensus/Fresh | Counterfactual transition | Gate |
| ---: | --- | --- | --- | --- | --- |
| 338 | `multiple per month` | `unknown` | `multiple per month` | `would_correct_to_correct` | `cluster_cadence_precision_v0_4:deterministic_boundary_origin:unknown` |
| 3482 | `unknown` | `unknown` | `no seizure frequency reference` | `would_correct_to_correct` | `cluster_cadence_precision_v0_4:deterministic_boundary_origin:unknown` |
| 3534 | `unknown` | `unknown` | `seizure free for 7 month` | `would_correct_to_wrong` | `cluster_cadence_precision_v0_4:deterministic_boundary_origin:unknown` |
| 11282 | `unknown` | `unknown` | `1 per 4 month` | `would_correct_to_wrong` | `cluster_cadence_precision_v0_4:deterministic_boundary_origin:unknown` |

## Interpretation

A label-only v0.5 relaxation out of deterministic `unknown` is unsafe on validation: all four candidate switches are gold-unknown rows, and accepting them all would produce two correct-to-wrong regressions with no wrong-to-correct gains. The two regressions are exactly the kind of last-event or seizure-free-duration over-interpretation highlighted in Yujian's guidance.

Decision: keep v0.4. Any future relaxation must depend on a narrow evidence feature for explicit count plus usable follow-up period, not merely on consensus plus fresh agreement.
