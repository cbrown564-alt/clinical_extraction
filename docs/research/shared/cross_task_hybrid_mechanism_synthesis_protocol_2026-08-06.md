# Protocol: Cross-task hybrid mechanism synthesis

Date: 2026-08-06  
Status: complete; no-call synthesis from retained 2026-08-06 ladder  
Report: [cross-task hybrid mechanism synthesis](cross_task_hybrid_mechanism_synthesis_2026-08-06.md)

## Primary question

Across Gan 2026 and ExECTv2, what does `llm_with_rules` actually do on
development retained artifacts: which gold categories become easy, which
named hybrid stages own first-changer rescue and harm, and which residuals
remain after the full stack?

## Why it matters

Today’s ladder already answers each piece separately (task shape → category
cut → error catalogs → hybrid stage ablations). Without one cross-task
readout, paper-facing and handoff language can still treat “rules” as a
single polish step or restate aggregate six-model similarity. This study
packages the mechanism map and residual ownership without new calls or
policy changes.

## Scope

| Item | Value |
| --- | --- |
| Inputs | Retained 2026-08-06 artifacts only (category cut, both catalogs, both stage ablations, hard-slice precursors) |
| Surfaces | Development `llm` and `llm_with_rules` where the parents already measured them; stage ownership is hybrid-only |
| Splits | Gan `dev750`; ExECT `dev140` |
| Calls | none |
| Holdout | sealed; no new category cuts |
| Code / policy | none; synthesis and residual slices only |

## Method

1. Load the parent machine-readable artifacts listed in the regenerator.
2. Extract: category x/y/z lenses; llm→hybrid mode shifts for floors;
   hybrid band first-changers; residual ownership counts; named harm
   surfaces (`unknown_sentinel`, cluster residual, SF inventory, Rx lens).
3. Write one synthesis artifact and one readable report that answers the
   primary question with claim boundaries and next executable actions.
4. Do not invent leave-one-stage-out necessity, holdout transfer, or
   Decision 0046 rewrites.

## Stop rule

Answer when the report states (a) what rules create vs promote on each
track, (b) the mass first-changer on each track, (c) the four residual
ownership slices with parent evidence links, and (d) what remains blocked
(holdout cuts, factorial necessity, policy counterfactuals).

## Claim boundary

Development mechanism synthesis from retained no-call artifacts. Not
holdout competence. Not leave-one-stage-out. Not a Decision 0046 or C16
rewrite. Not clinical validation. Gan and ExECT scores remain
non-interchangeable.
