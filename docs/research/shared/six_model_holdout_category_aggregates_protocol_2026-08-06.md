# Protocol: sealed holdout category aggregates

Date: 2026-08-06  
Status: complete; bucket arms unlocked via machine-only sealed scoring; ExECT rules-only family scores included  
Parent: [category-cut performance](six_model_category_cut_performance_2026-08-06.md)  
Unlock extension: [blocked-arm unlock protocol](six_model_holdout_category_aggregates_unlock_protocol_2026-08-06.md)  
Report: [holdout category aggregates](six_model_holdout_category_aggregates_2026-08-06.md)

## Primary question

On sealed holdout splits, which gold categories remain common competence
(**x**), model-separating (**y**), or shared difficulty (**z**) under the same
lens thresholds as the development category-cut study—without opening sealed
row files for human inspection?

## Why it matters

Development category cuts show rules create Gan easy mass and promote ExECT
Prescription while SF stays the floor. Without holdout category aggregates, it
is unclear whether those lenses transfer or whether gold-mix shift alone could
explain overall holdout gaps.

## Scope and row policy

| Track | Split | What is in scope now | Source class |
| --- | --- | --- | --- |
| ExECT | `test60` | Four-family F1 × model × surface; x/y/z lenses, plus independent rules-only family scores | Public stage panel and Decision 0046 rules-only aggregate |
| Gan | `test450` | Overall Purist bands by surface; gold a_priori mix | Public panels + gold taxonomy |
| Gan | `test450` | a_priori bucket × model accuracy | Machine-only sealed scoring (unlock protocol) |
| ExECT | `test60` | a_priori letter-bucket × model F1 | Machine-only sealed scoring (unlock protocol) |

Hard rules:

- No sealed row JSONL opened for human review.
- No letter IDs, `source_row_index`, notes, predictions, or failure examples in
  public outputs.
- Public artifact must pass the locked-aggregate safety key checks.
- No new model calls. No Decision 0046 method-fill rewrite.

## Lens rule (unchanged)

Same thresholds as
[category-cut protocol](six_model_category_cut_protocol_2026-08-06.md):

| Lens | Rule |
| --- | --- |
| **x** | min ≥ 0.85 and (max − min) ≤ 0.08 |
| **z** | max ≤ 0.75 |
| **y** | neither |

ExECT family lenses use `n = 59` letters (full holdout). Gan a_priori bucket
lenses remain deferred.

## Method

1. Read ExECT `test60` stage panel family F1 for `raw_lane` (`llm`) and
   `clinical_headline` (`llm_with_rules`).
2. Read the aggregate-only Decision 0046 rules-only four-family scores.
3. Assign x/y/z per family on the two six-model surfaces; report
   high/mid/floor bands for rules-only.
4. Compare those lenses to development family lenses from the category-cut
   artifact (transfer reading only).
5. Report Gan overall holdout Purist bands from retained llm-only and
   current-floors hybrid aggregates.
6. Report gold a_priori mix shares for Gan `validation` vs `test` and ExECT
   `dev` vs `test` from taxonomy artifacts.
7. When sealed ledgers are present, unlock Gan a_priori / ExECT letter-bucket
   scores under the
   [unlock protocol](six_model_holdout_category_aggregates_unlock_protocol_2026-08-06.md);
   do not invent bucket scores from overall panels.

## Stop rule

- **Answer** when ExECT holdout family lenses, Gan overall bands, gold-mix
  share comparison, and (when ledgers exist) fidelity-checked bucket lenses
  are stated.
- Bucket arms follow the unlock protocol and restore runbook:
  [sealed ledger restore runbook](../../runbooks/restore_sealed_holdout_ledgers_for_category_cuts.md).

## Claim boundary

Aggregate-only sealed holdout category packaging, including machine-only
bucket scores when sealed ledgers are scored in-process. Not human
row-level holdout competence analysis. Not a repair or Decision 0046 rewrite.
Development mechanism claims remain owned by the 2026-08-06 development ladder.
