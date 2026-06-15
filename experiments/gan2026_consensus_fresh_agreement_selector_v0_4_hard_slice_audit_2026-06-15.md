# Gan 2026 Consensus + Fresh Agreement Selector v0.4 Hard-Slice Audit

Date: 2026-06-15

This is a validation-only hard-slice audit over saved selector replay rows. It makes no model calls and does not read locked test rows. Gold labels are used only after slice membership for scoring.

## Experiment Unit

- Work class: hybrid selector hard-slice / selective-action audit.
- Split: `validation`, manifest `gan2026_split_v1`.
- Surface: saved v0.1-v0.4 selector replay rows over the same deterministic, consensus, and V12 artifacts.
- Targeted failure modes: cluster cadence preservation, weekly denominator/window behavior, unknown-boundary action, and non-cluster specific corrections.
- Stop rule: keep v0.4 as revise-only unless slices show non-regressive selective action and the next step is a predeclared robustness/frozen protocol.

## Version Comparison

| Selector | Selected Purist | Changed | W->C | C->W | Precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| `v0_1` | 712/750 | 109 | 26 | 11 | 0.2385 |
| `v0_2` | 710/750 | 58 | 21 | 8 | 0.3621 |
| `v0_3` | 712/750 | 28 | 17 | 2 | 0.6071 |
| `v0_4` | 714/750 | 26 | 17 | 0 | 0.6538 |

## v0.4 Slices

| Slice | Rows | W->C | C->W | C->C | W->W | Net | Precision | Row ids |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `v04_all_changed` | 26 | 17 | 0 | 9 | 0 | 17 | 0.6538 | 1687, 4243, 4690, 5954, 5974, 6209, 6889, 8419, 9955, 10386, 10677, 10933, 10942, 10984, 10996, 11002, 11035, 12422, 12438, 12456, 12460, 12468, 15168, 15593, 15672, 15834 |
| `v04_gold_weekly_changed` | 10 | 4 | 0 | 6 | 0 | 4 | 0.4 | 5954, 8419, 10386, 10933, 10942, 10984, 10996, 11002, 15593, 15834 |
| `v04_noncluster_specific_corrections` | 22 | 16 | 0 | 6 | 0 | 16 | 0.7273 | 1687, 4243, 4690, 5954, 5974, 6209, 6889, 8419, 9955, 10386, 10677, 10942, 11035, 12422, 12438, 12456, 12460, 12468, 15168, 15593, 15672, 15834 |
| `v04_same_cadence_cluster_burden_refinement` | 4 | 1 | 0 | 3 | 0 | 1 | 0.25 | 10933, 10984, 10996, 11002 |
| `v04_unknown_band_changed` | 6 | 5 | 0 | 1 | 0 | 5 | 0.8333 | 1687, 4690, 5974, 6209, 6889, 15168 |
| `v04_monthly_or_weekly_changed` | 13 | 6 | 0 | 7 | 0 | 6 | 0.4615 | 4243, 5954, 8419, 9955, 10386, 10677, 10933, 10942, 10984, 10996, 11002, 15593, 15834 |

## Suppressed v0.3 Actions

v0.4 suppresses 2 v0.3 accepted switches: 0 W->C, 2 C->W, 0 C->C, 0 W->W.

Gate counts: `{'cluster_cadence_precision_v0_4:cluster_label_demoted': 1, 'cluster_cadence_precision_v0_4:cluster_cadence_changed': 1}`.
Cluster demotions suppressed: `[10097]`.
Cluster cadence changes suppressed: `[17135]`.

## Block Robustness

| Block | Validation positions | Source-row ids | Changed | W->C | C->W | Net | Precision |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 1-125 | 10-2789 | 1 | 0 | 0 | 0 | 0.0 |
| 2 | 126-250 | 2812-5584 | 2 | 1 | 0 | 1 | 0.5 |
| 3 | 251-375 | 5624-8924 | 5 | 3 | 0 | 3 | 0.6 |
| 4 | 376-500 | 8938-12041 | 9 | 4 | 0 | 4 | 0.4444 |
| 5 | 501-625 | 12046-14821 | 5 | 5 | 0 | 5 | 1.0 |
| 6 | 626-750 | 14872-17287 | 4 | 4 | 0 | 4 | 1.0 |

## Interpretation

v0.4 hard-slice audit supports the cluster-cadence gate: it suppresses 2 v0.3 changes, both correct-to-wrong regressions, while preserving all 17 wrong-to-correct changes. The accepted cluster-burden-refinement slice is non-regressive but mostly correct-to-correct churn, so the next evidence should be a predeclared robustness or synthetic hard-case panel before any holdout-facing claim.

- JSON summary: `experiments\gan2026_consensus_fresh_agreement_selector_v0_4_hard_slice_audit_2026-06-15.json`.
