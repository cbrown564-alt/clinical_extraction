# Protocol: Gan 2026 llm_with_rules stage ablation

Date: 2026-08-06  
Status: complete; no-call development stage ablation  
Parent: [category error catalog](category_error_catalog_2026-08-06.md)  
Report: [hybrid stage ablation](hybrid_stage_ablation_2026-08-06.md)

## Primary question

Inside retained `llm_with_rules` only (not llm vs hybrid), which observable
pipeline bands and named repair families erase, reshape, or amplify category
error modes on `dev750`, and which family is the first Purist-changing stage
on rescued or damaged rows?

## Why it matters

The [category error catalog](category_error_catalog_2026-08-06.md)
treats semantic rules as one blob after format repair. Architecture manifests
name ten ordered clinical repair families plus normalize/resolve. Without a
band + first-changer reading, hybrid residual talk cannot say which stages
earn their keep or create unknown-gold damage.

## Scope

| Item | Value |
| --- | --- |
| Split | Gan `dev750` (`validation`); development inspection permitted |
| Surface | `llm_with_rules` only (six retained JSONL ledgers) |
| Baseline | post-`resolve_label` answer from saved `model_prediction.record` |
| Bands | representation → evidence reconcile → clinical selection → free-interval |
| Families | the ten `gan.llm_with_rules.repair.*` stages in manifest order |
| Metric | Purist correctness; predicted-shape error modes (same vocabulary as category catalog) |
| Calls | none; replay saved model ledgers through current repair functions |
| Holdout | sealed |

## Method

1. Load each retained `*--llm_with_rules.jsonl` row’s
   `row_trace.model_prediction.record` (pre-repair ledger), not the post-repair
   `structured_record`.
2. Replay normalize → resolve → ten repair families in manifest order, recording
   the label after each prediction-bearing step.
3. Score Purist and error mode at band endpoints; attribute each label-changing
   hop to its stage; credit **first-changer** for Purist rescue/harm.
4. Aggregate pooled six-model band mode deltas and family ledgers; keep up to
   two development examples per high-volume pathway / family effect.
5. Report fidelity: exact and Purist agreement of replayed finals vs retained
   historical after-labels and vs the floors-panel finals used by the parent
   catalog.

## Stop rule

Answer when every `dev750` a_priori bucket has band-level mode counts, each
repair family has fire / first-changer / help / hurt counts, signature pathway
vignettes cover the mass effects, and fidelity is stated in the claim boundary.

## Claim boundary

Development stage ablation inside `llm_with_rules` on `dev750`. First-changer
attribution under ordered replay; not a leave-one-family-out factorial. Not a
replacement for the parent llm-vs-hybrid catalog scores. Not holdout competence.
