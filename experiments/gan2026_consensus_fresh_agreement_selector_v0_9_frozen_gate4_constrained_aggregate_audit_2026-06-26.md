# Gan 2026 Consensus/Fresh v0.9 Gate 4 Constrained Aggregate Audit

- Date: `2026-06-26`
- Authorization: `user_authorized_2026-06-26`
- Surface: locked `test450`, aggregate-only readout
- Source symmetry: `constrained`, not exact
- Row-level output written: `false`

## Aggregate Readout

- Deterministic Purist: `329/450` (`0.7311`)
- Deterministic Pragmatic: `341/450` (`0.7578`)
- Consensus Purist: `365/450` (`0.8111`)
- Fresh-evidence Purist: `351/450` (`0.78`)
- Selected Purist: `348/450` (`0.7733`)
- Selected Pragmatic: `358/450` (`0.7956`)
- Net Purist gain vs deterministic: `19`
- Changed labels: `44`
- Wrong->correct: `26`
- Correct->wrong: `7`
- Changed-label precision: `0.5909`
- Selector actions: `{'keep_deterministic_baseline': 406, 'accept_consensus_fresh_agreement': 20, 'accept_fresh_boundary_rescue': 20, 'accept_parseable_denominator_window_refinement': 1, 'accept_normalized_equivalent_agreement': 3}`

## Gate Checks

- gate_passed: `False`
- selected_gain_at_least_10: `True`
- correct_to_wrong_at_most_5: `False`
- changed_label_precision_at_least_0_60: `False`
- source_integrity_ok: `True`
- source_symmetry_exact: `False`
- claim_scope_limited_to_constrained_holdout_evidence: `True`

## Component Integrity

| Component | Rows | Unique Rows | Duplicate Rows | Call Failures | Parse/Repair Rows | SHA-256 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `deterministic` | 450 | 450 | 0 | 0 | 0 | `df6bd9314a9fcfd8be2a68b3998dc91a917370cd221b83a3ea6b2243d1176de3` |
| `consensus` | 450 | 450 | 0 | 0 | 0 | `b336273f1bfa499e5465f4509a3dc8f447c972794f3c79ac60ff221789e09736` |
| `fresh_evidence` | 450 | 450 | 0 | 0 | 450 | `e317b088bbcdc0a2f668b0e600bccaf17664a5d4ae2e734c0531684e786a1295` |

## Interpretation

Gate 4 numeric bars fail. Record as final-evaluation evidence and return any follow-up to validation-only component-generation work.

No test row-level failures, rationales, evidence, selected events, or row-level transitions were written to this artifact.
