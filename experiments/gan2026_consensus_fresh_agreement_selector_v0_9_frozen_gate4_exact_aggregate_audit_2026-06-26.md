# Gan 2026 Consensus/Fresh v0.9 Gate 4 Exact Aggregate Audit

- Date: `2026-06-26`
- Authorization: `user_authorized_2026-06-26_proceed_after_exact_gate3`
- Surface: locked `test450`, aggregate-only readout
- Source symmetry: `exact_source_symmetry`
- Row-level output written: `false`

## Aggregate Readout

- Deterministic Purist: `343/450` (`0.7622`)
- Deterministic Pragmatic: `354/450` (`0.7867`)
- Consensus Purist: `366/450` (`0.8133`)
- Fresh-evidence Purist: `351/450` (`0.78`)
- Selected Purist: `359/450` (`0.7978`)
- Selected Pragmatic: `368/450` (`0.8178`)
- Net Purist gain vs deterministic: `16`
- Changed labels: `35`
- Wrong->correct: `21`
- Correct->wrong: `5`
- Changed-label precision: `0.6`
- Selector actions: `{'keep_deterministic_baseline': 415, 'accept_consensus_fresh_agreement': 14, 'accept_fresh_boundary_rescue': 20, 'accept_normalized_equivalent_agreement': 1}`

## Gate Checks

- gate_passed: `True`
- selected_gain_at_least_10: `True`
- correct_to_wrong_at_most_5: `True`
- changed_label_precision_at_least_0_60: `True`
- selected_at_least_prior_closest_anchor: `True`
- prior_closest_anchor_selected_purist: `348`
- source_integrity_ok: `True`
- source_symmetry_exact: `True`
- claim_scope_exact_source: `True`

## Component Integrity

| Component | Rows | Unique Rows | Duplicate Rows | Call Failures | Parse/Repair Rows | SHA-256 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `deterministic` | 450 | 450 | 0 | 0 | 0 | `8155612105b462ec126df3aaebe5e81e2d730448babe1fcc3bfa60348e45dbf2` |
| `consensus` | 450 | 450 | 0 | 0 | 0 | `ad651d457b04c25611bf78fc262a9ada39416ca93de7fb809794fc6cb9efab59` |
| `fresh_evidence` | 450 | 450 | 0 | 0 | 450 | `e317b088bbcdc0a2f668b0e600bccaf17664a5d4ae2e734c0531684e786a1295` |

## Interpretation

Exact-source Gate 4 promotion bars pass. Record as an exact v0.9 selector holdout result under the frozen source set. Do not tune from this test result or open row-level failures for development.

No test row-level failures, rationales, evidence, selected events, or row-level transitions were written to this artifact.
