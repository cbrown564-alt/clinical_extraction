# Results: ExECT rules-only transferred recall-first keep set

Date: 2026-08-27
Protocol: [transferred keep-set protocol](exect_rules_only_recall_first_transferred_protocol_2026-08-27.md)
Artifacts: `experiments/exect_rules_only_recall_first_20260827/transferred_candidate.json`
and `transferred_loo_*.json`.
Split: `dev140` only; `test60` sealed.
Scorer: `clinical_inventory_unit_keys`, zero model calls.
Comparator: `run_letter` (`ACCEPTED_THREE_STAGE_CONFIG`), select **0.9167**.

## Candidate

`TRANSFERRED_RECALL_FIRST_THREE_STAGE_CONFIG`: accepted recognise
flags plus tagged `rx_recall_expansion` and `sf_state_variant` only.
Select keeps those two classes under the existing conditions.
`RECALL_FIRST_THREE_STAGE_CONFIG` is unchanged (Phase C freeze).
`run_letter` is unchanged.

Dropped from the living candidate (Phase D family-band verdicts,
no holdout rows inspected): Diagnosis heading decomposition and
Investigations result variants. Rejected Phase C classes stay unused.

## Gates (all met)

| Check | Result |
| --- | --- |
| Select F1 | **0.9219** >= 0.9167 |
| Comparator-exact regressions | **0** |
| Improved / worsened pairs | 8 / 0 |
| Diagnosis select F1 | **0.8765** (matches comparator) |
| Investigations select F1 | **0.9851** (matches comparator) |
| Prescription select F1 | **0.9854** (comparator 0.9780) |
| SeizureFrequency select F1 | **0.8810** (comparator 0.8640) |
| LOO SF state variant | 0.9186 < 0.9219 |
| LOO Rx recall expansion | 0.9199 < 0.9219 |

Select stop: F1 **0.9219**, P 0.9263, R 0.9175.

## Claim boundary

Development mechanism evidence. The cited rows (dev **0.9167**,
test60 **0.8018**) do not move. This is not a holdout replay and is
not a promotion.
