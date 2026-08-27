# Protocol: unlock sealed holdout category-cut bucket scores

Date: 2026-08-06  
Status: complete  
Parent: [holdout category aggregates protocol](six_model_holdout_category_aggregates_protocol_2026-08-06.md)  
Report: [holdout category aggregates](six_model_holdout_category_aggregates_2026-08-06.md)  
Restore runbook: [sealed ledger restore](../../runbooks/restore_sealed_holdout_ledgers_for_category_cuts.md)

## Primary question

On sealed holdout splits, which Gan a_priori buckets and ExECT a_priori letter
buckets remain common competence (**x**), model-separating (**y**), or shared
difficulty (**z**) under the same lens thresholds as the development
category-cut study—via machine-only aggregate scoring of restored sealed
prediction ledgers?

## Why it matters

The parent study answered ExECT family lenses and gold-mix share shifts from
public panels. Per-bucket holdout scores stayed blocked. Sealed trees are now
present on this checkout, so the blocked arms can be scored without inventing
bucket numbers from overall panels.

## Scope and row policy

| Track | Split | Surface | Prediction source | Metric |
| --- | --- | --- | --- | --- |
| Gan | `test450` | `llm` | `scratch/holdout/gan2026_six_model_llm_only_test450_20260801/{slug}/rows.jsonl` | Purist accuracy via `comparison.purist_correct` |
| Gan | `test450` | `llm_with_rules` | matched v0.5 sealed raw outputs, no-call replay through current `hybrid_full_stack` | Purist accuracy after current floors |
| ExECT | `test60` | `llm` | sealed `raw_lane_mentions` | four-family clinical fact F1 (clinical-headline helper) |
| ExECT | `test60` | `llm_with_rules` | sealed `predicted_mentions` | four-family clinical fact F1 (clinical-headline helper) |

Hard rules:

- Machine may read sealed JSONL and locked gold for scoring.
- No human inspection of locked rows, notes, predictions, or failures.
- Public outputs: bucket × model aggregates and lenses only.
- No letter IDs, `source_row_index`, notes, predictions, or examples in
  `experiments/` or docs.
- No new model calls. No Decision 0046 rewrite. No repair/prompt tuning from
  holdout.

## Lens rule (unchanged)

Same thresholds as
[category-cut protocol](six_model_category_cut_protocol_2026-08-06.md):

| Lens | Rule |
| --- | --- |
| **x** | min ≥ 0.85 and (max − min) ≤ 0.08 |
| **z** | max ≤ 0.75 |
| **y** | neither |

Denominator floors: Gan buckets ≥ 20 rows; ExECT letter buckets ≥ 10 letters.
Below floor: report scores, omit lens.

## Fidelity gates (must pass before publishing bucket tables)

1. Gan `llm` overall Purist per model equals the llm-only `test450` panel
   (tolerance 0).
2. Gan `llm_with_rules` overall Purist correct-count per model equals
   `test450_aggregate.after_purist` in the current-floors replay summary
   (tolerance 0).
3. ExECT `llm_with_rules` overall clinical fact F1 per model equals the stage
   panel `clinical_headline` F1 within 0.0001.
4. ExECT `llm` uses the same clinical-headline helper on `raw_lane_mentions`;
   absolute F1 may differ from panel `raw_lane_score` (same note as development
   category-cut). Relative bucket ordering under that fixed helper is the claim
   object for llm.

## Method

1. Confirm sealed tree presence (paths only).
2. Build Gan gold a_priori membership from `load_records_for_split("test")`
   (in-process only).
3. Score Gan llm from sealed llm-only ledgers.
4. Score Gan hybrid by no-call replay of sealed matched-v0.5 raw outputs through
   current `hybrid_full_stack` (do not publish replay rows).
5. Build ExECT gold letter-bucket membership from `load_letters_for_split("test")`.
6. Score ExECT sealed rows with the clinical-headline helper; partition by
   a_priori letter bucket.
7. Assign x/y/z lenses; emit public aggregates; keep family lenses from the
   parent study.
8. Pass `scripts/check_locked_aggregate_safety.py`.

## Stop rule

- **Answer** when both previously blocked arms have fidelity-checked bucket
  scores and lenses (or explicit below-floor null lenses).
- **Blocked** only if a fidelity gate fails or a required sealed ledger is
  missing.

## Claim boundary

Aggregate-only sealed holdout category competence by gold bucket. Machine
scoring of sealed ledgers is allowed; human holdout failure analysis is not.
Not a Decision 0046 rewrite. Not repair/prompt tuning from holdout. Development
mechanism claims remain owned by the 2026-08-06 development ladder.
