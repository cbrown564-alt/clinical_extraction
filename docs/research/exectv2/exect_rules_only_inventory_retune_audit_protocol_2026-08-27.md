# ExECT rules-only inventory retune audit

Date: 2026-08-27
Status: answered; see the report
Report: [rules-only inventory retune audit](exect_rules_only_inventory_retune_audit_2026-08-27.md)
Owner: this file
Report: [rules-only inventory retune audit](exect_rules_only_inventory_retune_audit_2026-08-27.md)

## Primary question

On the current 4-family inventory scorer, which standalone ExECT rules still
assume Compact/headline Diagnosis collapse, and which recall-first then
precision-after moves from cell 3 are unused by `exect_rules`?

## Why it matters

Cell 3 was rebuilt after recognise / encode / select and after the cited
scorer stopped collapsing Diagnosis. Standalone rules were last moved for
Investigations result-binding (2026-08-15). The locked five-cell gap
(0.7725 vs 0.8674) is therefore a comparison of two programs, not of the
same later-stage ideas applied to rules. This audit names the mismatch
before any retune.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Split | `dev140` only |
| Holdout | not loaded |
| Calls | none |
| Candidate | current `extract_deterministic_all9` |
| Comparator | same letters scored with `clinical_headline_unit_keys` and `clinical_inventory_unit_keys` |
| Diagnostic arms | Diagnosis without overlap suppression; Investigations without same-result collapse; inventory Select replayed on the rules ledger |
| Scorer | 4-family micro F1 (`clinical_inventory_unit_keys`); headline as the historical collapse view |

Do not inspect `test60` rows. Do not retune from this audit. Do not change
the cited five-cell grid.

## Stop rule

Answer when the development artifact records: headline vs inventory P/R for
rules-only; Diagnosis parent-missed-while-child-present counts; overlap and
same-result suppression counts; inventory Select replay on the current
ledger and on the recall-first Diagnosis ledger; and a bounded claim about
what a later retune may try.

## Claim boundary

Development mechanism only. A positive diagnostic does not change the
locked rules cell. It does not say rules-only would match cell 3 after
retune.
