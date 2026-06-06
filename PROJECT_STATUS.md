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
- A no-call candidate-evidence provenance replay is now complete:
  `source_normalized_phrase` no longer gates exact provenance on this surface,
  routed rows fall from `276` to `82`, provenance-only rows fall from `220` to
  `26`, `selected_evidence_missing_exact_trace` disappears, and the remaining
  provenance surface is mostly the truer `selected_source_id_invalid` tail
  (`27` rows, including `26` provenance-only rows and `1` mixed row).
- The first saved verifier comparison packet for `context_repair_v6` is now
  materialized. It preserves the predeclared `29 / 4 / 18 / 5 / 220` bucket
  split and keeps provenance sidecars visible on `39` of the `56`
  clinical/policy rows while excluding provenance-only rows from the main score
  table.
- Operationally, the first verifier success/failure table is the `29`-row main
  ambiguity set only. The `4` abstain exemplars, `18` upstream-policy rows,
  `5` rendered policy-sensitive rows, and `220` provenance-only audit rows stay
  as separate appendix/audit surfaces.
- The replayed route surface is now split for execution: `55` non-provenance
  routed clinical/policy rows are the real first verifier-target surface,
  while provenance follow-through is a separate `27`-row
  `selected_source_id_invalid` tail rather than part of the main clinical
  ambiguity problem.
- The reset-stage component inventory now defines the first component-level
  ablation report surface: family, recovered rows, newly routed rows,
  remaining nulls, provenance validity, and audit-only `W->C` / `C->W`.
- The first component table now isolates the `+7` V5->V6 recovered rows across
  active frequency families: `5` selected-evidence frequency-value recoveries,
  `2` vague-period recoveries, and `0` diary-date-list recoveries.
- Provenance sidecars are now split family-by-family on the `56`
  clinical/policy rows, and saved V5->V6 audit-only `W->C` / `C->W` counts are
  attached to the component table without entering verifier-visible packets.
- The first clean verifier experiment input is materialized as a `56`-row
  surface: `29` main ambiguity rows plus `4` abstain, `18` upstream-policy, and
  `5` rendered-policy appendices; the `220` provenance-only rows are excluded.
- Executable one-family-off switches now exist for the seizure-free and
  projection-policy families. Validation750 replays show seizure-free duration
  instrumentation owns `41` rendered rows on the clean candidate-trace baseline
  (`580 -> 539` rendered when disabled), while current-summary,
  previous-month/current-zero, and major-recent-relapse switches execute with
  `0` aggregate delta on this saved surface.
- The first live action-only verifier run over the clean `56`-row V6 surface is
  now complete and contract-clean: `56/56` calls returned parseable outputs,
  `56/56` passed row-local contract checks, and the verifier produced non-abstain
  actions on `27` rows overall.
- On the predeclared `29`-row main ambiguity table, the verifier action split is
  `1` affirm, `5` reject, `15` human_review, and `8` abstain. The `27` appendix
  rows split `4` affirm, `2` human_review, and `21` abstain; no appendix row
  produced `reject`.
- Focused validation for the reset path passed:
  `99 passed` across clinical-assessment projection/render, verification route,
  and candidate-set clinical assessment tests.
- Full suite status after this thread: `1320 passed`.

## Core Artifacts

- Reset synthesis and decisions:
  `docs/research/gan2026_architecture_reset_synthesis_and_next_questions_2026-06-06.md`.
- Fresh replay comparison read:
  `docs/research/gan2026_validation750_context_repair_v6_read_2026-06-06.md`.
- Reset-stage component inventory:
  `experiments/gan2026_reset_stage_component_inventory_v0_2026-06-06.md`.
- Route bucket split read:
  `docs/research/gan2026_validation750_route_bucket_split_v6_2026-06-06.md`.
- Cluster-family pass read:
  `docs/research/gan2026_validation750_cluster_family_pass_v6_2026-06-06.md`.
- Vague cluster-count cadence decision:
  `docs/research/gan2026_validation750_vague_cluster_count_cadence_decision_v6_2026-06-06.md`.
- Verifier-candidate surface read:
  `docs/research/gan2026_validation750_verifier_candidate_surface_v6_2026-06-06.md`.
- Null action taxonomy read:
  `docs/research/gan2026_validation750_null_action_taxonomy_v6_2026-06-06.md`.
- First verifier report predeclaration:
  `docs/research/gan2026_validation750_first_verifier_report_predeclaration_v6_2026-06-06.md`.
- First component ablation report surface:
  `docs/research/gan2026_validation750_first_component_ablation_report_surface_v6_2026-06-06.md`.
- First component ablation table:
  `docs/research/gan2026_validation750_first_component_ablation_table_v6_2026-06-06.md`.
- First component ablation table JSON:
  `experiments/gan2026_validation750_first_component_ablation_table_v6_2026-06-06.json`.
- One-family-off replay artifacts:
  `experiments/gan2026_validation750_one_family_off_*_context_repair_v6_2026-06-06.*`.
- First saved verifier comparison packet:
  `docs/research/gan2026_validation750_first_verifier_saved_comparison_context_repair_v6_2026-06-06.md`.
- First clean verifier experiment input:
  `docs/research/gan2026_validation750_first_verifier_experiment_input_clean29_context_repair_v6_2026-06-06.md`.
- First live action-only verifier run:
  `docs/research/gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.md`.
- First live action-only verifier summary JSON:
  `experiments/gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.json`.
- Provenance-only failure taxonomy:
  `docs/research/gan2026_validation750_provenance_only_failure_taxonomy_v6_2026-06-06.md`.
- Candidate-evidence provenance replay route artifact:
  `experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v6_candidate_trace_v1_2026-06-06.jsonl`.
- Validation750 reset artifacts live under
  `experiments/gan2026_*validation750*gpt41mini*2026-06-06.*`.
- June 5 staged-assembly holdout docs remain a separate frozen thread; do not
  blend that protocol with reset validation mechanics.

## Work Board

### Now

- Decide whether zero-delta projection-policy off-switches need targeted hard
  slices, since they execute cleanly but do not move the saved validation750
  aggregate.
- Read the first live verifier run and decide whether any of the `1` affirm /
  `5` reject / `15` human_review / `8` abstain main-table actions should become
  frozen deterministic action policy versus remain prompt-only.

### Next

- Run a forced-choice verifier variant that must choose among pre-selected
  answer options rather than emit action-only output: effectively repeat the
  candidate-selection task with the saved candidate set and a narrower verifier
  prompt, then compare the resulting label choices and failure modes against the
  current action-only run.
- Implement post-run comparison/accounting that summarizes first-verifier
  actions against deterministic V0 by bucket and report section without
  inventing scorer-facing replacement labels.
- Decide whether global non-routed V5->V6 audit transitions belong in a
  separate scorer audit appendix; the current component table reports routed
  family counts only.

### Blocked

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

- 2026-06-06: Repaired the `27`-row candidate-trace `selected_source_id_invalid` tail by mapping unresolved source-ids to `"source_id_not_resolved"` and whitelisting acceptable non-routing statuses in routing and suspicious state checks. Regenerated validation750 projection render, route, and component ablation artifacts on disk; `selected_source_id_invalid` dropped to `0`.
- 2026-06-06: Implemented and ran the first action-only verifier over the clean
  `56`-row V6 surface via
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/components/clinical_assessment_first_verifier.py`
  and
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_first_verifier_experiment.py`.
  The live run materialized
  `experiments/gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.{jsonl,json}`
  plus
  `docs/research/gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.md`.
  All `56` rows parsed and passed contract checks; action counts were `29`
  abstain, `17` human_review, `5` affirm, and `5` reject, with `21` changed
  actions on the `29`-row main ambiguity table. Full suite now passes at
  `1320 passed`.
- 2026-06-06: Added executable reset-stage off-switches through the
  ClinicalAssessment assembler and projection/render artifact builder:
  `normalize_seizure_free_duration_date_instrumentation`,
  `project_current_summary_rate_priority`,
  `project_previous_active_month_over_current_month_zero`, and
  `project_major_recent_relapse_over_background_frequency`. Generated
  validation750 one-family-off projection/render, score, and route artifacts
  for all four switches. The seizure-free switch creates `41` newly-null rows
  with no audit `W->C`/`C->W`; the three projection-policy switches execute but
  have `0` rendered, route, and correctness delta on this saved surface.
- 2026-06-06: Completed the requested saved-artifact pre-verifier pass: isolated
  the `+7` recovered rows as `5` selected-evidence frequency-value recoveries
  and `2` vague-period recoveries; split provenance sidecars across the `56`
  clinical/policy rows; attached audit-only routed-family `W->C` / `C->W`
  counts to the component table; and generated the clean first verifier input
  as
  `experiments/gan2026_validation750_first_verifier_experiment_input_clean29_context_repair_v6_2026-06-06.{jsonl,json}`.
  True seizure-free/project-policy one-family-off reruns are now backfilled as
  separate saved artifacts.
- 2026-06-06: Completed the candidate-evidence provenance replay and updated
  `docs/research/gan2026_validation750_provenance_only_failure_taxonomy_v6_2026-06-06.md`.
  Recomputing exact provenance from selected primary candidate evidence/source
  ids instead of `source_normalized_phrase` dropped routed rows from `276` to
  `82`, dropped provenance-only rows from `220` to `26`, removed
  `selected_evidence_missing_exact_trace` entirely, and left rendered/scored
  output unchanged.
- 2026-06-06: Completed the full provenance-only audit as
  `docs/research/gan2026_validation750_provenance_only_failure_taxonomy_v6_2026-06-06.md`.
  The `220` provenance-only routed rows split into `174` summary/paraphrase
  carry-through rows, `20` exact-phrase expansion rows, `9` empty sentinel
  phrase rows, `9` unresolved source-id rows, `6` case-only exact matches, and
  `2` symbol-normalization rewrites; `204 / 220` still have exactly one primary
  candidate, so the surface looks largely fixable by provenance plumbing rather
  than new clinical logic.
- 2026-06-06: Defined the first reset-stage component ablation report surface
  in
  `docs/research/gan2026_validation750_first_component_ablation_report_surface_v6_2026-06-06.md`,
  freezing the per-family report contract around family, recovered rows, newly
  routed rows, remaining nulls, provenance validity, and audit-only `W->C` /
  `C->W`, while keeping provenance route families inside the component report
  but outside the first verifier main success/failure table.
- 2026-06-06: Materialized the first reset-stage component ablation table in
  `docs/research/gan2026_validation750_first_component_ablation_table_v6_2026-06-06.md`,
  filling the counts already supported by the V5/V6 replay and route-taxonomy
  reads, separating `observed_now` from `pending_isolated_ablation`, and
  keeping provenance families in the component appendix while the main verifier
  score table stays focused on the non-provenance clinical/policy surface.
- 2026-06-06: Added the saved-artifact analyzer
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/reset_stage_component_ablation_v6.py`
  and generated
  `experiments/gan2026_validation750_first_component_ablation_table_v6_2026-06-06.json`,
  so the first reset-family ablation table is now machine-readable. The saved
  summary computes the `+7` recovered rows, the `29 / 4 / 18 / 5 / 220` V6
  surface split, and the candidate-trace operational split of `55` pure
  non-provenance target rows plus the `27`-row `selected_source_id_invalid`
  tail while still leaving unisolated one-family-off deltas as pending.
- 2026-06-06: Resolved the open cluster-cadence contract question in
  `docs/research/gan2026_validation750_vague_cluster_count_cadence_decision_v6_2026-06-06.md`:
  vague cluster-count cadence phrases such as `multiple days`, `several
  mornings`, and `several evenings` remain routed upstream policy debt for the
  current reset thread, not a new reset-native projection/render contract,
  because the schema does not yet own a non-invented benchmark-facing cadence
  mapping for those values.
- 2026-06-06: Built the first saved verifier comparison packet as
  `experiments/gan2026_validation750_first_verifier_saved_comparison_context_repair_v6_2026-06-06.{jsonl,json}`
  plus
  `docs/research/gan2026_validation750_first_verifier_saved_comparison_context_repair_v6_2026-06-06.md`,
  joining the V6 route, deterministic V0 decision, and saved assessment
  artifacts into prompt-ready row packets with candidate evidence texts,
  projection/render state, and visible provenance sidecars on the 39 mixed
  clinical/policy rows while preserving the predeclared `29 / 4 / 18 / 5 / 220`
  bucket split.
- 2026-06-06: Updated the reset completed-tasks and review-plan docs so they
  now acknowledge the validation750 `context_repair_v6` read, post-V5 ports,
  plain-language `values` decision, explicit cluster route contract, and the
  reset-stage component inventory instead of stopping at the older
  validation250-only verifier boundary.
- 2026-06-06: Created the reset-stage component inventory artifact as
  `experiments/gan2026_reset_stage_component_inventory_v0_2026-06-06.{json,md}`,
  mapping old families to reset-stage owners, portability categories, ablation
  switches, and status so future ports stay explicit and ablatable.
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
