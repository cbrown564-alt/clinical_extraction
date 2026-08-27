# Protocol: ExECTv2 within-family error catalog

Date: 2026-08-06; within-family correction predeclared 2026-08-08
Status: corrected; no-call development catalog with within-family ablation reading
Parent: [category-cut performance](../shared/six_model_category_cut_performance_2026-08-06.md)  
Report: [family error catalog](family_error_catalog_2026-08-06.md)  
Sibling (stage zoom inside hybrid): [hybrid stage ablation](hybrid_stage_ablation_2026-08-06.md)

## Primary question

For each **gold-defined subtype within** the four ExECT clinical-headline
families on `dev140`, on both `llm` and `llm_with_rules`, which errors dominate;
how do family rules erase, reshape, or amplify those errors relative to the
model lane; and what do concrete development examples look like?

## Why it matters

SeizureFrequency is the practical floor, but Diagnosis, Prescription, and
Investigations each carry distinct inventory and empty-gold failure shapes.
Category competence without family error modes understates where rules help or
hurt. A mode dump alone is hard to use; the report must make the ablation
readable at a glance.

## Scope

| Item | Value |
| --- | --- |
| Split | ExECT `dev140`; development inspection permitted |
| Surfaces | `llm` = `raw_lane_mentions`; `llm_with_rules` = `predicted_mentions` |
| Families | Diagnosis, SeizureFrequency, Prescription, Investigations |
| Letter metric | clinical-headline unit-key multiset exactness per family |
| Secondary | pooled missed/extra key tokens (family-appropriate: state tokens for SF; concept/drug/investigation keys otherwise) |
| Calls | none; retained single-call JSONL only |
| Holdout | sealed |

## Method

1. Assign every gold and predicted mention a deterministic subtype within its
   family using the category-cut classifier.
2. For each letter × model × surface × family × gold subtype, compare
   subtype-isolated clinical-headline unit keys.
3. Assign mutually exclusive modes: `correct_empty`, `correct_nonempty`,
   `empty_gold_spurious`, `missed_all`, `missed_only`, `extra_only`,
   `substituted_or_mixed`.
4. Aggregate six-model mode counts, subtype F1, and consensus imperfect
   letters.
5. Contrast pooled modes `llm` vs `llm_with_rules` (family-rules ablation over
   retained surfaces—not leave-one-rule-out).
6. Select examples by family×subtype×surface, with error mode as the secondary
   explanation rather than the primary category.
7. Emit one machine artifact and one ablation-first narrative report. Retain
   the old family-level set-error summary only as a secondary roll-up.

## Stop rule

Answer when all observed within-family gold subtypes have mode inventories and
representative development examples on both surfaces, with subtype-specific
LLM-vs-hybrid deltas. Whole-family roll-ups alone do not satisfy the stop rule.

## Claim boundary

Development within-family subtype error catalog using unit-key letter exactness
as a mechanism lens. Category-cut subtype-conditioned family F1 remains the
competence metric. Ablation is across
retained surfaces, not a full rule factorial. Not holdout competence; not a
Decision 0046 rewrite.
