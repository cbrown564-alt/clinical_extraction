# Gan 2026 Consensus + Fresh Agreement Selector

Date: 2026-06-15

This is a validation-only no-call selector replay. It keeps the deterministic baseline unless exact structured-event consensus proposes a different label and V12 fresh-evidence reasoning independently emits that same label.

## Experiment Unit

- Selector: `gan2026_consensus_fresh_agreement_selector_v0_4`.
- Work class: hybrid selector / saved-output replay.
- Split: `validation`, manifest `gan2026_split_v1`.
- Row policy: aligned source rows present in all three source artifacts.
- Scorer: Gan-compatible Purist, unchanged.
- Inspection policy: validation aggregate and validation-band summaries.
- Stop rule: promote only if gains are robust by band and changed-label precision is high enough for a holdout-facing freeze; otherwise revise.

## Source Artifacts

- `consensus`: `experiments\gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13.jsonl`
- `deterministic`: `experiments\gan2026_three_way_comparison_validation750_deterministic_gpt41mini_2026-06-07.jsonl`
- `fresh_evidence_v12_v0_4`: `experiments\gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl`

## Summary

- Deterministic Purist: 697/750
- Consensus Purist: 708/750
- V12 fresh-evidence Purist: 682/750
- Selected Purist: 714/750
- Net Purist gain vs deterministic: 17
- Changed labels: 26
- Wrong->correct: 17
- Correct->wrong: 0
- Changed-label precision: 0.6538
- Actions: `{'keep_deterministic_baseline': 724, 'accept_consensus_fresh_agreement': 26}`
- JSONL artifact: `experiments\gan2026_consensus_fresh_agreement_selector_v0_4_validation750_no_call_replay_2026-06-15.jsonl`

## Boundary Bands

| Band | Rows | Deterministic | Selected | Net | Changed | W->C | C->W | Precision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `band_zero` | 112 | 109 | 109 | 0 | 0 | 0 | 0 | None |
| `band_unknown` | 170 | 143 | 148 | 5 | 6 | 5 | 0 | 0.8333 |
| `band_submonthly` | 87 | 84 | 84 | 0 | 1 | 0 | 0 | 0.0 |
| `band_monthly` | 141 | 133 | 135 | 2 | 3 | 2 | 0 | 0.6667 |
| `band_weekly` | 177 | 171 | 175 | 4 | 10 | 4 | 0 | 0.4 |
| `band_daily` | 63 | 57 | 63 | 6 | 6 | 6 | 0 | 1.0 |

## Decision

Revise, not freeze. v0.4 removes the remaining validation correct-to-wrong regressions from v0.3 and improves weekly-band net gain, but it is still a validation-only saved-output replay and needs a predeclared hard-slice or frozen protocol before any holdout-facing claim.
