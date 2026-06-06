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
- Focused validation for the reset path passed:
  `99 passed` across clinical-assessment projection/render, verification route,
  and candidate-set clinical assessment tests.
- Full suite status after this thread: `1304 passed, 1 failed`. The remaining
  failure is unrelated to the reset files:
  `tests/test_gan2026_normalize.py::test_repair_prediction_label_with_evidence_repairs_single_count_over_window`
  currently returns `3 per 3 month` where the test expects `3 per 7 month`.

## Core Artifacts

- Reset synthesis and decisions:
  `docs/research/gan2026_architecture_reset_synthesis_and_next_questions_2026-06-06.md`.
- Validation750 reset artifacts live under
  `experiments/gan2026_*validation750*gpt41mini*2026-06-06.*`.
- June 5 staged-assembly holdout docs remain a separate frozen thread; do not
  blend that protocol with reset validation mechanics.

## Work Board

### Now

- Fix or triage the unrelated normalize regression: diary evidence for
  `3 events over 7 months` currently returns `3 per 3 month`, expected
  `3 per 7 month`.
- Run a fresh validation750 reset mechanics replay after the post-V5 family
  ports and value-language/cluster-route contract changes.
- Regenerate and compare reset reports: null-render analysis, historical
  crosswalk, route report, V0 baseline, recovered rows, routed rows, and
  audit-only W->C/C->W.

### Next

- Review refreshed residual null-render families by count, cleanliness, and
  transfer value; choose from refreshed evidence, not stale V5 counts.
- Complete the cluster-family pass: render explicit cadence plus per-cluster
  burden; route unresolved cadence, burden, convention, or axis ownership.
- Define the null-render/action taxonomy: clinically unknown, abstain, human
  review, missing upstream parser/policy, and verifier-eligible ambiguity.
- Create a reset-stage component inventory: old name, new family, portability
  category, ablation switch, and status.
- Update reset completed-tasks/review docs with the validation750 read, post-V5
  ports, value-language decision, and cluster route contract.

### Blocked

- LLM-verifier work is blocked until the deterministic normalization/projection
  and route surface is stable after a fresh validation750 replay.
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
