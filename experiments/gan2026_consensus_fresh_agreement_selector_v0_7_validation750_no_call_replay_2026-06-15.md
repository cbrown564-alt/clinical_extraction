# Gan 2026 Consensus + Fresh Agreement Selector

Date: 2026-06-15

This is a validation-only no-call selector replay. It starts from v0.6 profile-guard boundary rescue and adds a narrow unknown-origin rescue for fresh profiles with explicit count plus usable window.

## Experiment Unit

- Selector: `gan2026_consensus_fresh_agreement_selector_v0_7`.
- Work class: hybrid selector / saved-output replay.
- Split: `validation`, manifest `gan2026_split_v1`.
- Row policy: aligned source rows present in all three source artifacts.
- Scorer: Gan-compatible Purist, unchanged.
- Inspection policy: validation aggregate and validation-band summaries.
- Stop rule: promote only if gains are robust by band and changed-label precision is high enough for a holdout-facing freeze; otherwise revise.

## Source Artifacts

- `replay_source`: `reconstructed component rows from v0.6 selector rows`
- `v0.6_selector_rows`: `C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_consensus_fresh_agreement_selector_v0_6_validation750_no_call_replay_2026-06-15.jsonl`

## Summary

- Deterministic Purist: 697/750
- Consensus Purist: 708/750
- V12 fresh-evidence Purist: 682/750
- Selected Purist: 728/750
- Net Purist gain vs deterministic: 31
- Changed labels: 40
- Wrong->correct: 31
- Correct->wrong: 0
- Changed-label precision: 0.775
- Actions: `{'keep_deterministic_baseline': 710, 'accept_consensus_fresh_agreement': 26, 'accept_fresh_boundary_rescue': 14}`
- JSONL artifact: `C:\Users\cbrow\Code\clinical_extraction\experiments\gan2026_consensus_fresh_agreement_selector_v0_7_validation750_no_call_replay_2026-06-15.jsonl`

## Boundary Bands

| Band | Rows | Deterministic | Selected | Net | Changed | W->C | C->W | Precision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `band_zero` | 112 | 109 | 112 | 3 | 3 | 3 | 0 | 1.0 |
| `band_unknown` | 170 | 143 | 159 | 16 | 17 | 16 | 0 | 0.9412 |
| `band_submonthly` | 87 | 84 | 84 | 0 | 1 | 0 | 0 | 0.0 |
| `band_monthly` | 141 | 133 | 135 | 2 | 3 | 2 | 0 | 0.6667 |
| `band_weekly` | 177 | 171 | 175 | 4 | 10 | 4 | 0 | 0.4 |
| `band_daily` | 63 | 57 | 63 | 6 | 6 | 6 | 0 | 1.0 |

## Decision

Revise, not freeze. v0.7 keeps the v0.6 profile-guard boundary rescue and adds a narrow deterministic-unknown rescue for explicit count plus usable window profiles. It remains validation-only replay evidence.
