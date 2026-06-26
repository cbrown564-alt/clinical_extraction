# Gan 2026 Consensus + Fresh Agreement Selector

Date: 2026-06-15

This is a validation-only no-call selector replay. It starts from v0.8 and adds normalized-equivalent agreement plus explicit unknown-uncertainty rescues.

## Experiment Unit

- Selector: `gan2026_consensus_fresh_agreement_selector_v0_9`.
- Work class: hybrid selector / saved-output replay.
- Split: `validation`, manifest `gan2026_split_v1`.
- Row policy: aligned source rows present in all three source artifacts.
- Scorer: Gan-compatible Purist, unchanged.
- Inspection policy: validation aggregate and validation-band summaries.
- Stop rule: promote only if gains are robust by band and changed-label precision is high enough for a holdout-facing freeze; otherwise revise.

## Source Artifacts

- `replay_source`: `reconstructed component rows from v0.8 selector rows`
- `v0.8_selector_rows`: `C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_consensus_fresh_agreement_selector_v0_8_validation750_no_call_replay_2026-06-15.jsonl`

## Summary

- Deterministic Purist: 697/750
- Consensus Purist: 708/750
- V12 fresh-evidence Purist: 682/750
- Selected Purist: 733/750
- Net Purist gain vs deterministic: 36
- Changed labels: 49
- Wrong->correct: 36
- Correct->wrong: 0
- Changed-label precision: 0.7347
- Actions: `{'keep_deterministic_baseline': 701, 'accept_consensus_fresh_agreement': 26, 'accept_fresh_boundary_rescue': 14, 'accept_parseable_denominator_window_refinement': 7, 'accept_unknown_uncertainty_rescue': 1, 'accept_normalized_equivalent_agreement': 1}`
- JSONL artifact: `C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.jsonl`

## Boundary Bands

| Band | Rows | Deterministic | Selected | Net | Changed | W->C | C->W | Precision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `band_zero` | 112 | 109 | 112 | 3 | 3 | 3 | 0 | 1.0 |
| `band_unknown` | 170 | 143 | 160 | 17 | 18 | 17 | 0 | 0.9444 |
| `band_submonthly` | 87 | 84 | 85 | 1 | 5 | 1 | 0 | 0.2 |
| `band_monthly` | 141 | 133 | 138 | 5 | 7 | 5 | 0 | 0.7143 |
| `band_weekly` | 177 | 171 | 175 | 4 | 10 | 4 | 0 | 0.4 |
| `band_daily` | 63 | 57 | 63 | 6 | 6 | 6 | 0 | 1.0 |

## Decision

Revise, not freeze. v0.9 keeps the v0.8 selector and adds two narrow rescues: normalized-equivalent consensus/fresh disagreement and specific-rate-to-unknown uncertainty. It remains validation-only replay evidence.
