# Gan 2026 Selector v0.7 Residual Headroom Audit

Date: 2026-06-15

This is a validation-only audit over saved v0.7 selector rows. It does not read locked test rows and does not make model calls.

## Summary

- Rows: 750
- Selected correct: 728/750
- Selected wrong: 22
- Selected-wrong rows with a correct unselected component: 11
- Selected-wrong rows with no correct component available: 11
- Selected wrong by band: `{'band_monthly': 6, 'band_submonthly': 3, 'band_unknown': 11, 'band_weekly': 2}`
- Selected wrong by component availability: `{'fresh_evidence': 5, 'none': 11, 'consensus+fresh_evidence': 6}`

## Parseable Other Probe

A tempting next relaxation is to accept all consensus+fresh-agreed replacement labels currently gated as parser-ambiguous `other` when they are actually parseable by the Gan label parser. This probe rejects that broad rule.

- Candidate actions: 27
- Wrong->correct: 4
- Correct->wrong: 5
- Correct->correct churn: 16
- Wrong->wrong churn: 2
- Net Purist gain: -1
- By band: `{'band_monthly': {'correct_to_wrong': 2, 'wrong_to_correct': 2, 'correct_to_correct': 6}, 'band_submonthly': {'correct_to_correct': 5, 'wrong_to_correct': 1, 'correct_to_wrong': 1}, 'band_unknown': {'wrong_to_wrong': 2}, 'band_weekly': {'correct_to_correct': 5, 'wrong_to_correct': 1, 'correct_to_wrong': 2}}`

## Selected-Wrong Component Availability

| Components correct but not selected | Rows |
| --- | ---: |
| `fresh_evidence` | 5 |
| `none` | 11 |
| `consensus+fresh_evidence` | 6 |

## Interpretation

v0.7 leaves 22 validation rows wrong. Eleven have no correct component among deterministic, consensus, and fresh evidence, so selector changes alone cannot recover them. Eleven do have a correct unselected component: six where consensus and fresh are both correct, and five where only fresh is correct.

The broad parseable-`other` relaxation is rejected: it would take 27 actions but net -1 Purist (4 W->C, 5 C->W). The next selector must use a narrower, clinically meaningful profile feature, not parser compatibility alone.

Decision: revise, not freeze. This audit identifies remaining selector headroom but does not produce a holdout-facing candidate.
