# Project Status

Last updated: 2026-06-06

## Active Objective

Continue the Gan 2026 architecture reset as validation-development mechanics:
make the pipeline legible, stage-owned, evidence-traced, and ablatable before
any LLM-verifier or holdout-facing work. No benchmark-comparable claim is
authorized. The reset path is:

```text
Extract -> Select / Clinical Assessment -> Normalize -> Project -> Verify -> Render / Score
```

Controlling thread:
`docs/research/gan2026_architecture_reset_synthesis_and_next_questions_2026-06-06.md`.

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
- Locked test is not for row-level tuning; any holdout-facing use needs a
  frozen protocol and explicit user authorization.
- Treat Gan validation runs as development mechanics, not benchmark claims.
- Keep comparator/gold context audit-only; route/verifier decisions must not
  consume gold labels.
- Do not resurrect broad hybrid fallback. Port old behavior only as named,
  stage-owned, inspectable, ablatable components.
- Prefer plain-language artifact vocabulary: reset-stage parsed quantities are
  `values`, not parser jargon.

## Current Evidence

- Initial validation750 GPT-4.1-mini mechanics had 732 valid clinical
  assessments, 498 rendered rows, 234 true null renders, and 42 routed
  V0-abstain verifier rows.
- Context/date/value repair passes reduced the null-render surface to 177 rows
  after V5 while preserving split discipline.
- Post-V5 work ported mature old component families into reset ownership:
  selected-evidence frequency repair, vague period rates, relative/conditional
  guards, diary date lists, current-vs-historical policies, major recent relapse
  priority, provenance route fields, evidence-trace route families, and
  denominator-window mismatch.
- The latest thread standardized reset-stage issue/rule language around
  `values` and added explicit cluster route ownership:
  `cluster_cadence_unknown_with_per_cluster_burden` routes as
  `unresolved_cluster_cadence_with_per_cluster_burden`.
- Fresh validation750 replay (`context_repair_v6`) now reaches all 750 rows:
  580 rendered labels, 170 null renders, 488/580 Purist-correct scored rows,
  and 276 routed V0-abstain verifier rows.
- The replay's route surface is no longer null-only. In addition to the prior
  null-render families, it now exposes provenance-sensitive route families led
  by `selected_evidence_missing_exact_trace` (250 rows) plus
  `selected_source_id_invalid` (9 rows); this needs a deliberate report read,
  not silent promotion.
- Focused validation for the reset path passed:
  `99 passed` across clinical-assessment projection/render, verification route,
  and candidate-set clinical assessment tests.
- Full suite status after this thread: `1305 passed`.

## Core Artifacts

- Reset synthesis and decisions:
  `docs/research/gan2026_architecture_reset_synthesis_and_next_questions_2026-06-06.md`.
- Fresh replay comparison read:
  `docs/research/gan2026_validation750_context_repair_v6_read_2026-06-06.md`.
- Route bucket split read:
  `docs/research/gan2026_validation750_route_bucket_split_v6_2026-06-06.md`.
- Cluster-family pass read:
  `docs/research/gan2026_validation750_cluster_family_pass_v6_2026-06-06.md`.
- Verifier-candidate surface read:
  `docs/research/gan2026_validation750_verifier_candidate_surface_v6_2026-06-06.md`.
- Null action taxonomy read:
  `docs/research/gan2026_validation750_null_action_taxonomy_v6_2026-06-06.md`.
- First verifier report predeclaration:
  `docs/research/gan2026_validation750_first_verifier_report_predeclaration_v6_2026-06-06.md`.
- Validation750 reset artifacts live under
  `experiments/gan2026_*validation750*gpt41mini*2026-06-06.*`.
- June 5 staged-assembly holdout docs remain a separate frozen thread; do not
  blend that protocol with reset validation mechanics.

## Work Board

### Now

- Keep the 220 provenance-only routed rows out of the first verifier
  success/failure table and track them as audit/instrumentation debt.
- Use the new null-action taxonomy operationally: 29 verifier-eligible
  ambiguity rows, 18 upstream policy/parser rows, and 4 abstain rows.
- Use the predeclared first verifier layout: 29-row main ambiguity score table,
  4 abstain exemplars, 18 upstream-policy appendix, 5 rendered
  policy-sensitive appendix, and 220 provenance-only audit appendix.

### Next

- Create a reset-stage component inventory: old name, new family, portability
  category, ablation switch, and status.
- Update reset completed-tasks/review docs with the validation750 read, post-V5
  ports, value-language decision, and cluster route contract.
- Decide whether vague cluster-count cadence needs a reset-native contract, or
  should remain routed policy debt after the current verifier-candidate report.
- Prepare the first saved verifier comparison using the predeclared layout and
  visible provenance sidecars on the 39 mixed clinical/policy rows.

### Blocked

- LLM-verifier work is blocked until the deterministic normalization/projection
  and route surface is stable after the fresh validation750 replay is read and
  the provenance-route expansion is adjudicated.
- Whole-pipeline promotion remains blocked; no benchmark-comparable language or
  holdout-facing reset protocol is authorized.
- Locked-test row-level inspection remains prohibited for development.

### Backlog

- Design the first LLM-verifier saved-replay comparison over routed V0
  `abstain`/`human_review` rows, using route evidence and exact source evidence
  only; verifier output must be action-only and emit no replacement label.
- Add component-level ablation reporting for each ported deterministic family:
  newly rendered, newly routed, remaining null, evidence validity, route-family
  changes, and audit-only W->C/C->W.
- Decide whether comparator-label preservation can return as a named action
  policy after verifier reject/abstain.
- Revisit prior-visit/event-date context only if refreshed residual analysis
  shows broad value and a clean source contract.

### Done Recently

- 2026-06-06: Decided that provenance sidecars remain visible to the first
  verifier prompt on the 39 mixed clinical/policy rows, but stay secondary to
  the non-provenance action family; also predeclared the first verifier report
  layout around the 29-row ambiguity set plus abstain, upstream-policy,
  rendered-policy, and provenance-only appendices.
- 2026-06-06: Defined the `context_repair_v6` null-render/action taxonomy for
  the 51 null verifier rows: 29 verifier-eligible ambiguity rows, 18 missing
  upstream policy/parser rows, 4 abstain rows, and no clean clinically-unknown
  or human-review-first rows on this surface.
- 2026-06-06: Defined the primary `context_repair_v6` verifier-candidate
  surface as the 56 clinical/policy routed rows only: 51 null ambiguity rows
  plus 5 rendered policy-sensitive rows, with the 220 provenance-only routed
  rows explicitly kept out of the first verifier score table.
- 2026-06-06: Completed the `context_repair_v6` cluster-family pass and found
  no safe narrow deterministic recovery patch; the 22 routed cluster rows split
  into 4 intentional rendered unresolved-cadence rows, 5 cyclic-window rows,
  and 13 axis-ownership null rows that need explicit future contract decisions,
  not hidden fallback.
- 2026-06-06: Ran a fresh validation750 reset mechanics replay as
  `context_repair_v6`; rendered rows increased from 573 to 580, null renders
  fell from 177 to 170, and the verifier route surface expanded sharply to 276
  abstain-only rows because provenance route families are now visible.
- 2026-06-06: Fixed the unrelated normalize regression where diary evidence
  overrode an explicit raw `3 events over 7 months` window with a shorter
  date-span guess; full suite now passes at `1305 passed`.
- 2026-06-06: Completed the reset synthesis and addenda covering validation750
  mechanics, context/date repairs, post-V5 family ports, provenance route
  fields, denominator-window routing, value terminology, and unresolved-cluster
  route ownership.
- 2026-06-06: Ported mature old behavior families into reset-native ownership
  without broad fallback: frequency repair, selected-evidence/benchmark repair,
  ACD-style projection policies, route families, and provenance checks.
- 2026-06-05: Wrote/reviewed the separate frozen aggregate-only holdout
  protocol for `hybrid_multi_component_staged_assembly_v1`; it does not
  authorize reset-thread holdout use.
