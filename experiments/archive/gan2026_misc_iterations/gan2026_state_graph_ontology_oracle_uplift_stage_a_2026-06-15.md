# Gan 2026 State-Graph Ontology Oracle Uplift (Stage A)

Date: 2026-06-15

Stage A no-model-spend gate for the KG-grounded component generator. Validation-only over `gan2026_split_v1`; no holdout rows are read and no model calls are made.

## Summary

- Ontology: `gan2026_admissible_state_ontology_v1`
- Rows: 750
- Baseline oracle representable: 599/750
- Admitted (dual-validated) representable: 599/750
- Projection Purist correct: 641/750
- resolve_label Purist correct: 641/750
- resolve_label - projection: +0 rows
- resolve gains (wrong->correct): []
- resolve regressions (correct->wrong): []

## By boundary band

| Band | Rows | Baseline repr. | Admitted repr. | Projection correct | resolve_label correct |
| --- | ---: | ---: | ---: | ---: | ---: |
| `band_daily` | 63 | 55 | 55 | 55 | 55 |
| `band_monthly` | 141 | 127 | 127 | 130 | 130 |
| `band_submonthly` | 87 | 81 | 81 | 81 | 81 |
| `band_unknown` | 170 | 73 | 73 | 122 | 122 |
| `band_weekly` | 177 | 154 | 154 | 160 | 160 |
| `band_zero` | 112 | 109 | 109 | 93 | 93 |

## Gate reading

Stage A passes only if `resolve_label` lifts Purist correctness over the no-correct-component residual (especially `band_unknown` and `band_weekly`) with near-zero correct->wrong regressions. A non-trivial regression count, or no net gain, stops the branch per the design-note stop rule.
