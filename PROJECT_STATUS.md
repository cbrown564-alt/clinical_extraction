# Project Status

Last updated: 2026-06-07

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

- HN1 (source-near frequency value recovery) is now **promoted** on a frozen
  `test450` aggregate audit, closing the validation-to-holdout loop from
  `docs/research/gan2026_test450_null_reduction_synthesis_and_hypotheses_2026-06-07.md`:
  `docs/research/gan2026_test450_hn1_frozen_aggregate_audit_2026-06-07.md`.
  - Frozen holdout replay moved from `341 -> 358` rendered, `108 -> 91` null,
    `271 -> 282` Purist-correct, `280 -> 294` Pragmatic-correct, and
    `41 -> 29` routed rows, with **zero** `W->C`/`C->W`/newly-null transitions
    on already-rendered rows and **zero** new routes.
  - The `12`-row routed-surface contraction is concentrated in
    `mixed_window_or_vague_addition` (`13 -> 1`); every row that left the
    routed surface also became newly rendered, so HN1 resolved the underlying
    additive/multi-window ambiguity upstream rather than routing nulls away.
  - Artifacts: `experiments/gan2026_reset_clinical_assessment_pipeline_test450_hn1_frozen_audit_2026-06-07.*`.
- While producing that audit, a pre-existing text-normalization bug was found
  and fixed in
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py`:
  `_normalize_phrase_for_parse` unconditionally rewrote every hyphen/en-dash/
  em-dash as `" to "`, corrupting clinical compound terms (`tonic-clonic` ->
  `tonic to clonic`) before frequency-rate parsing and silently turning
  several previously-correct holdout renders into nulls or wrong labels
  (rows `2795`, `7327`, `12826`, `13079`, `16253`). The regex now anchors the
  substitution to digit-bounded numeric ranges
  (`r"(?<=\d)\s*[-–—]\s*(?=\d)"`), preserving `24-48 hours -> 24 to 48 hours`
  while leaving `tonic-clonic` intact. Three regression tests were added in
  `tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py`; the
  fix turned the first frozen-audit pass from a mixed `+11`/`-8` transition
  profile into the clean `+17`/`0` profile reported above. Focused suite
  (`43` tests) and the broader `gan2026`-tagged suite (`1348` passed) are
  green, with only the same `3` pre-existing unrelated failures.
- Validation750 `context_repair_v6` remains the current reset baseline:
  `580` rendered labels, `170` null renders, `488/580` Purist-correct scored
  rows, and full split discipline preserved.
- A fresh saved-artifact GPT-4.1-mini replay after the new HN1 multi-month
  family shows the reset-native pipeline is still moving materially on
  validation750:
  `592` rendered labels, `158` null renders, `494/592` Purist-correct scored
  rows, and `40` routed rows in
  `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0_hn1_multimonth_replay_2026-06-07.*`.
  - The whole-pipeline direction is positive, but the targeted
    `frequency_rate_values_unparsed` slice is not yet cleanly improved because
    the row universe expanded and the new family introduces denominator-span
    regressions on some already-correct month-bucket rows.
  - On the stable original `71`-row HN1 proxy slice, rendered rows move only
    `24 -> 25` and null rows `47 -> 46`, while Purist-correct rows fall
    `23 -> 21`; the refreshed read therefore supports fixing the current
    multi-month contract before treating it as the stable GPT comparator for
    Qwen.
- After tightening the multi-month contract and reassembling the saved
  ClinicalAssessment drafts, the refreshed GPT-4.1-mini validation750 replay
  is now materially better again:
  `597` rendered labels, `153` null renders, `500/597` Purist-correct scored
  rows, and the routed surface remains `40` rows in
  `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0_hn1_multimonth_contract_replay_2026-06-07.*`.
  - The prior denominator-span regressions are resolved on `16084`, `16195`,
    and `16220`, which now all render correctly at `4`-month windows again.
  - The intended explicit multi-month target rows `16674`, `16697`, `16758`,
    and `16833` now all render and score Purist-correct under the narrow
    family.
  - This refreshed replay is the current GPT-4.1-mini comparator contract for
    the next reset-native Qwen validation750 run.
- The validation-only null-reduction proxy slice packet now matches the
  synthesis contract more closely for both the baseline replay and the
  refreshed HN1 contract replay.
  - The analyzer now consumes both score and route artifacts, reports
    rendered/null/routed counts, audit-only `W->C` / `C->W`, newly
    rendered/newly null rows, and exact-trace plus source-id validity checks.
  - The refreshed comparison packet lives in
    `docs/research/gan2026_validation750_null_reduction_slices_after_hn1_multimonth_contract_2026-06-07.md`
    and
    `experiments/gan2026_validation750_null_reduction_slices_after_hn1_multimonth_contract_2026-06-07.json`.
  - On the current HN1 contract replay, the largest frequency-family proxy
    slice expands from `71 -> 85` rows, improves rendered rows from `24 -> 31`,
    and shows `7` audit-only `W->C` against `3` `C->W`, with only `1` routed
    row left on that surface.
- A reset-native no-call composition runner now exists for the saved
  ClinicalAssessment path:
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid/reset_clinical_assessment_pipeline.py`.
  It chains saved ClinicalAssessment rows and CandidateSet artifacts through
  projection/render, score audit, verification route, and deterministic
  VerificationDecision V0 without adding new clinical logic or model calls.
- The key near-term priority is now to run and iterate the reset-native
  composable pipeline on validation750. The first pass should use GPT-4.1-mini
  for quick iteration; after that, run the same pipeline with Qwen
  validation750 so model differences are measured on the reset-stage contract
  rather than on the older parallel-adjudicator architecture.
- The `hybrid_parallel_state_candidate_reasoner` validation750 run has
  completed and should be treated as a comparison point for the new
  reset-native GPT-4.1-mini and Qwen validation750 runs, not as the primary
  execution path for the reset architecture.
- The reset thread has now ported the key mature deterministic families into
  explicit reset-stage ownership: selected-evidence frequency repair, vague
  period rates, relative/conditional guards, diary-date lists, current-vs-
  historical policies, major-recent-relapse priority, provenance route fields,
  evidence-trace route families, and denominator-window mismatch.
- Reset-stage issue language is standardized around `values`, and cluster-route
  ownership is explicit:
  `cluster_cadence_unknown_with_per_cluster_burden` routes as
  `unresolved_cluster_cadence_with_per_cluster_burden`.
- The first component ablation surface is live and machine-readable. It tracks
  family-level recovered rows, newly routed rows, remaining nulls, provenance
  validity, and audit-only `W->C` / `C->W`; the saved V5->V6 table isolates the
  `+7` recovered rows as `5` selected-evidence frequency-value recoveries and
  `2` vague-period recoveries.
- The second HN1 Normalize family is now implemented as an explicit ablatable
  component in
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py`:
  `multi_month_bucket_frequency_value_recovery` with ablation switch
  `normalize_frequency_multi_month_bucket_value_recovery`.
  - The component is intentionally narrow: it recovers explicit multi-month
    count-bearing month buckets and explicit source-window summaries while
    refusing broad single-month rescue and per-cluster flattening.
  - Focused regression tests cover named-bucket aggregation, explicit
    source-window summary recovery, ablation-disable behavior, and a
    single-month negative control; the reset-stage component inventory now
    records the family as `general`.
- The first clean verifier experiment input is frozen as a `56`-row
  clinical/policy surface: `29` main ambiguity rows plus `4` abstain, `18`
  upstream-policy, and `5` rendered-policy appendices. Provenance-only rows are
  excluded from the main verifier score surface.
- The first live action-only verifier run over that clean surface was
  contract-clean: `56/56` parseable outputs, `56/56` contract-valid rows, and
  `27` non-abstain actions overall. On the `29`-row main ambiguity table the
  split was `1` affirm, `5` reject, `15` human_review, and `8` abstain.
- The tightened `action_only` prompt was then rerun on the isolated
  `29`-row main ambiguity surface. The run stayed contract-clean at `29/29`
  parseable and `29/29` contract-valid rows, but it collapsed to
  `29/29 human_review`, with `0` affirm, `0` reject, and `0` abstain. This
  indicates the new policy text is conservative but currently over-biases the
  model away from decisive contradiction and policy-aware abstention.
- The first forced-choice verifier comparison is also complete on the same
  `56`-row surface. It produced `40` affirm, `11` human_review, `5` reject, and
  `0` abstain, agreeing with the action-only run on only `8/56` rows
  (`0.1429` agreement rate); this makes forced choice look substantially more
  aggressive than the abstain-capable baseline.
- Post-run accounting for the action-only verifier is now materialized by route
  bucket and report section, preserving the main-table versus appendix split.
  Operationally, only the `29`-row ambiguity table should be treated as the
  primary success/failure surface; appendix behavior is still audit context.
- Candidate-trace provenance follow-through is repaired. Unresolved source ids
  now map to `source_id_not_resolved`, acceptable non-routing statuses are
  whitelisted, and the prior `selected_source_id_invalid` tail drops to `0`
  after replay regeneration.
- Executable one-family-off switches exist for seizure-free duration and the
  current projection-policy families. On validation750, seizure-free duration
  instrumentation owns `41` rendered rows on the clean candidate-trace baseline
  (`580 -> 539` rendered when disabled), while the three current projection-
  policy switches execute with `0` aggregate delta on this saved surface.
- Focused reset-path validation remains green at `99 passed`, and the full suite
  status recorded for this thread is `1320 passed`.

## Core Artifacts

- Overfitting reduction and generalization hypotheses:
  `docs/research/gan2026_overfitting_reduction_and_generalization_hypotheses_2026-06-07.md`.
- Validation750 reset error analysis report:
  `C:\Users\cbrow\.gemini\antigravity\brain\c23859fe-0530-4d64-8a6f-952cc9cb2d20\error_analysis_report.md`.
- Validation750 reset null rendering report:
  `C:\Users\cbrow\.gemini\antigravity\brain\c23859fe-0530-4d64-8a6f-952cc9cb2d20\null_analysis_report.md`.
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
- HN1 frozen `test450` aggregate audit (promotion decision):
  `docs/research/gan2026_test450_hn1_frozen_aggregate_audit_2026-06-07.md`.
- HN1 month-bucket evaluation read:
  `docs/research/gan2026_validation750_hn1_month_bucket_frequency_recovery_evaluation_2026-06-07.md`.
- HN1 multi-month rerun read:
  `docs/research/gan2026_validation750_hn1_multimonth_slice_rerun_read_2026-06-07.md`.
- HN1 multi-month contract replay read:
  `docs/research/gan2026_validation750_hn1_multimonth_contract_replay_read_2026-06-07.md`.
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
- First verifier post-run accounting:
  `docs/research/gan2026_validation750_first_verifier_accounting_v6_2026-06-06.md`.
- First forced-choice verifier comparison:
  `docs/research/gan2026_validation750_forced_choice_verifier_live_clean29_context_repair_v6_2026-06-06.md`.
- First main-ambiguity outcome taxonomy:
  `docs/research/gan2026_validation750_first_verifier_main_ambiguity_outcome_taxonomy_v6_2026-06-06.md`.
- Verifier action-policy decision memo:
  `docs/research/gan2026_validation750_verifier_action_policy_decision_v6_2026-06-06.md`.
- Main-ambiguity-only verifier input:
  `docs/research/gan2026_validation750_first_verifier_experiment_input_main29_context_repair_v6_2026-06-06.md`.
- Main-ambiguity-only verifier live run:
  `docs/research/gan2026_validation750_first_verifier_live_main29_context_repair_v6_2026-06-06.md`.
- First live action-only verifier summary JSON:
  `experiments/gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.json`.
- First verifier accounting JSON:
  `experiments/gan2026_validation750_first_verifier_accounting_v6_2026-06-06.json`.
- First forced-choice verifier summary JSON:
  `experiments/gan2026_validation750_forced_choice_verifier_live_clean29_context_repair_v6_2026-06-06.json`.
- Main-ambiguity-only verifier input JSON:
  `experiments/gan2026_validation750_first_verifier_experiment_input_main29_context_repair_v6_2026-06-06.json`.
- Main-ambiguity-only verifier live summary JSON:
  `experiments/gan2026_validation750_first_verifier_live_main29_context_repair_v6_2026-06-06.json`.
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

- Begin HN2 (bounded vague-with-window rendering) on validation-only proxy
  slices, per the recommended execution order in
  `docs/research/gan2026_test450_null_reduction_synthesis_and_hypotheses_2026-06-07.md`
  section 8: build a `vague_count` proxy slice, an ablatable `Project`-owned
  component, then a frozen `test450` aggregate audit using the same protocol
  as `docs/research/gan2026_test450_hn1_frozen_aggregate_audit_2026-06-07.md`.
- Run the reset-native pipeline on Qwen validation750 using the refreshed
  GPT-4.1-mini multi-month contract replay as the comparator state.
- Compare the refreshed GPT-4.1-mini contract replay against both Qwen and the
  completed `hybrid_parallel_state_candidate_reasoner` validation750 baseline.
- Use the completed `hybrid_parallel_state_candidate_reasoner` validation750
  run only as a comparison baseline when interpreting reset-native GPT-4.1-mini
  and Qwen outputs.
- Continue replacing stale mentions of the intermediate
  `selected_source_id_invalid` provenance tail in reset-thread reads as those
  docs are touched.

### Next

- Compare the reset-native GPT-4.1-mini and Qwen validation750 outputs against
  each other and against the completed `hybrid_parallel_state_candidate_reasoner`
  validation750 baseline.
- Keep broad single-month rescue off the table unless a later read shows a
  clean Normalize-owned residual family distinct from selection/window or
  anchor debt.
- If the reset-native model runs land near the same residual surface, return to
  prompt tuning on the `29`-row ambiguity table with the full-run failures as
  the new decision surface.
- Continue filling component-level ablation coverage for ported deterministic
  families, keeping report fields to newly rendered, newly routed, remaining
  null, evidence validity, route-family changes, and audit-only `W->C`/`C->W`.

### Blocked

- Whole-pipeline promotion remains blocked; no benchmark-comparable language or
  holdout-facing reset protocol is authorized.
- Locked-test row-level inspection remains prohibited for development.

### Backlog

- Decide whether comparator-label preservation can return as a named action
  policy after verifier reject/abstain.
- Revisit prior-visit/event-date context only if refreshed residual analysis
  shows broad value and a clean source contract.

### Done Recently

- 2026-06-07: Promoted HN1 (source-near frequency value recovery) on a frozen
  `test450` aggregate audit:
  `docs/research/gan2026_test450_hn1_frozen_aggregate_audit_2026-06-07.md`.
  - Frozen holdout replay moved `341 -> 358` rendered, `108 -> 91` null,
    `271 -> 282` Purist-correct, `41 -> 29` routed, with `0`
    `W->C`/`C->W`/newly-null transitions and `0` new routes — meeting every
    promotion criterion in the synthesis doc section 7.4.
  - Found and fixed a pre-existing bug in `_normalize_phrase_for_parse`
    (`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py`)
    that rewrote every hyphen as `" to "`, corrupting `tonic-clonic` into
    `tonic to clonic` and silently nulling/misrendering several holdout rows.
    The regex now only converts digit-bounded numeric ranges
    (`r"(?<=\d)\s*[-–—]\s*(?=\d)"`). Three regression tests were added; the
    fix turned a mixed `+11`/`-8` first-pass result into the clean `+17`/`0`
    promoted result.
  - Artifacts: `experiments/gan2026_reset_clinical_assessment_pipeline_test450_hn1_frozen_audit_2026-06-07.*`.
- 2026-06-07: Tightened the
  `multi_month_bucket_frequency_value_recovery` contract, added targeted
  regression coverage, and reran the saved GPT-4.1-mini validation750 replay.
  - The contract now preserves `this month so far` denominator span, includes
    numeric current-month counts when present, and allows the multi-month
    family to repair from the saved assessment summary phrase when that phrase
    already preserves the intended clinical fact.
  - The refreshed replay in
    `docs/research/gan2026_validation750_hn1_multimonth_contract_replay_read_2026-06-07.md`
    improves from `592 -> 597` rendered, `158 -> 153` null, and
    `494 -> 500` Purist-correct scored rows with routed rows unchanged at `40`.
  - The prior denominator regressions on `16084`, `16195`, and `16220` are
    repaired, and the intended explicit multi-month target rows `16674`,
    `16697`, `16758`, and `16833` now all render Purist-correct.
- 2026-06-07: Upgraded the validation null-reduction slice analyzer so the
  proxy packets now include route-aware transition accounting rather than only
  static score counts.
  - `null_reduction_validation_slices.py` now reads score plus route artifacts
    and can compare a refreshed replay against a baseline replay by
    `source_row_index`.
  - The refreshed packet now reports rendered/null/routed counts, newly
    rendered/newly null rows, audit-only `W->C` / `C->W`, and exact-trace plus
    source-id validity checks for each required synthesis family.
  - Focused tests pass in
    `tests/test_gan2026_null_reduction_validation_slices.py`.
- 2026-06-07: Reran the `frequency_rate_values_unparsed` validation slice audit
  after the HN1 multi-month family using a fresh saved-artifact GPT-4.1-mini
  reset-native replay.
  - Whole-pipeline validation750 replay improved from `580 -> 592` rendered,
    `170 -> 158` null, `488 -> 494` Purist-correct scored rows, and
    `73 -> 40` routed rows.
  - The refreshed HN1 read in
    `docs/research/gan2026_validation750_hn1_multimonth_slice_rerun_read_2026-06-07.md`
    shows only a small stable-row gain on the named proxy slice (`24 -> 25`
    rendered on the original `71` rows), while the current family still misses
    the intended explicit multi-month target rows and regresses denominator span
    on some already-correct month-bucket rows.
  - Decision: residual single-month nulls still look mostly like
    selection/window or anchor debt, not a license for broad new Normalize
    rescue.
- 2026-06-07: Implemented the second HN1 ablatable recovery component in
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py`.
  - New family:
    `multi_month_bucket_frequency_value_recovery`
    with ablation switch
    `normalize_frequency_multi_month_bucket_value_recovery`.
  - The component recovers explicit multi-month month-bucket summaries such as
    `3 brief absences in Dec, 5 drop attacks in Mar, and 1 tonic seizure in Apr`
    and explicit source-window summaries such as
    `Three seizures recorded over six months: September, November, and February`.
  - Guardrails intentionally block broad single-month rescue and per-cluster
    flattening; focused regression tests and the reset-stage component
    inventory were updated alongside the implementation.
- 2026-06-07: Evaluated whether explicit month-bucket aggregation should become
  the next HN1 null-reduction family in
  `docs/research/gan2026_validation750_hn1_month_bucket_frequency_recovery_evaluation_2026-06-07.md`.
  - The validation read supports promotion only for a narrow multi-month bucket
    aggregation family, not for broad single-month rescue.
  - Clean next-family examples are rows like `16674`, `16697`, `16758`, and
    `16833`, while many single-month rows appear to be broader selection/window
    debt rather than pure Normalize loss.
- 2026-06-07: Implemented the first HN1 ablatable recovery component in
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py`.
  - New family:
    `anchor_window_frequency_value_recovery`
    with ablation switch
    `normalize_frequency_anchor_window_value_recovery`.
  - The component recovers explicit count-plus-anchor frequency statements such
    as `four brief morning jerks since 3/2015` and
    `3 morning jerks since last tonic-clonic seizure in Apr 2022` by deriving a
    bounded month window from source-backed anchors.
  - Focused regression tests were added for positive recovery, last-event anchor
    counting, ablation-disable behavior, and qualitative trigger-only negative
    control behavior; the reset-stage component inventory now records the new
    family as `general`.
- 2026-06-07: Completed the first HN1 validation-only proxy-slice read as
  `docs/research/gan2026_validation750_hn1_frequency_value_recovery_slice_read_2026-06-07.md`.
  - On the `frequency_rate_values_unparsed` slice, `24 / 71` rows are already
    rendered through source-near primary-candidate recovery, while the
    remaining `47` null rows all still carry
    `frequency_rate_values_incomplete`.
  - The read narrows the next implementation target to explicit date-bucket and
    count-plus-anchor frequency recovery inside `Normalize`, while treating
    qualitative/trigger-only rows as guardrail negatives and additive
    multi-semiology rows as a smaller secondary family.
- 2026-06-07: Ran validation750 and test450 on GPT-4.1-mini using the reset-native composable ClinicalAssessment pipeline runner (`reset_clinical_assessment_pipeline.py`).
  - The `validation750` run matched the baseline `context_repair_v6` results: 750 inputs, 580 rendered labels, 170 null renders, 488/580 Purist-correct scored rows, and 73 routed/abstain rows. Artifacts saved under `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0`.
  - The `test450` run successfully completed: 450 inputs (449 projected), 341 rendered labels, 108 null renders, 268/341 Purist-correct scored rows (~0.7858 accuracy on rendered subset), and 43 routed/abstain rows. Artifacts saved under `experiments/gan2026_reset_clinical_assessment_pipeline_test450_gpt41mini_v0`.
- 2026-06-07: Reprioritized the work board around the reset-native composable
  ClinicalAssessment pipeline. The completed
  `hybrid_parallel_state_candidate_reasoner` validation750 run is now a
  comparison baseline, while the next execution priority is GPT-4.1-mini
  validation750 on the reset-native pipeline followed by Qwen validation750 on
  the same pipeline.
- 2026-06-07: Added the reset-native composable no-call pipeline runner
  `reset_clinical_assessment_pipeline.py`, bundling the existing
  ClinicalAssessment projection/render, scoring audit, verification route, and
  VerificationDecision V0 builders behind one replay CLI and report bundle.
  Focused reset-stage tests pass at `88 passed`, and a real saved validation750
  scratch replay completed structurally before the scratch artifacts were
  removed.
- 2026-06-06: Corrected the first full validation750 local-Qwen rerun plan so
  the runnable path is the combined
  `hybrid_parallel_state_candidate_reasoner` pipeline under
  `ollama_chat/qwen3.6:35b`; stage-specific candidate/projection/verification
  work remains downstream analysis only.
- 2026-06-06: Added first-class `main29` verifier input/report artifacts in
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_first_verifier_report.py`
  and repointed the live verifier runner to
  `main29` defaults for the next prompt iteration.
- 2026-06-06: Materialized the `29`-row main-ambiguity-only verifier input as
  `experiments/gan2026_validation750_first_verifier_experiment_input_main29_context_repair_v6_2026-06-06.{jsonl,json}`
  plus
  `docs/research/gan2026_validation750_first_verifier_experiment_input_main29_context_repair_v6_2026-06-06.md`.
- 2026-06-06: Ran the tightened action-only verifier on the isolated
  `29`-row main ambiguity table and generated
  `experiments/gan2026_validation750_first_verifier_live_main29_context_repair_v6_2026-06-06.{jsonl,json}`
  plus
  `docs/research/gan2026_validation750_first_verifier_live_main29_context_repair_v6_2026-06-06.md`.
  The run was contract-clean (`29/29`) but returned `29/29 human_review`,
  showing the new prompt boundary is conservative and currently over-collapsed.
- 2026-06-06: Tightened the action-only first-verifier prompt contract in
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_first_verifier_report.py`
  so `affirm` requires one dominant explicit burden, `reject` requires
  contradiction, `human_review` covers unresolved but clinically plausible
  competing burdens, and `abstain` remains for known policy/aggregation debt
  with no safe action move.
- 2026-06-06: Decided that the next verifier prompt/policy iteration should
  temporarily focus on the `29`-row main ambiguity table, while the clean
  `56`-row surface remains the broader comparison packet for the following
  replay.
- 2026-06-06: Continued the reset-thread documentation cleanup so the
  controlling synthesis, completed-tasks, and review-plan reads all mark the
  intermediate candidate-trace `selected_source_id_invalid` tail as historical
  rather than current.
- 2026-06-06: Completed the `29`-row main ambiguity outcome taxonomy as
  `docs/research/gan2026_validation750_first_verifier_main_ambiguity_outcome_taxonomy_v6_2026-06-06.md`,
  separating the first verifier surface into one rare `affirm`, five
  contradiction-driven `reject` rows, fifteen clinically plausible but
  unresolved `human_review` rows, and eight policy-known unresolved `abstain`
  rows.
- 2026-06-06: Wrote the verifier action-policy decision memo
  `docs/research/gan2026_validation750_verifier_action_policy_decision_v6_2026-06-06.md`
  and fixed the primary reset-thread policy as `action_only`; the forced-choice
  run remains diagnostic only because it over-selects dominant burdens on the
  true ambiguity surface.
- 2026-06-06: Updated the active reset research docs so the repaired
  candidate-trace `selected_source_id_invalid` tail is no longer described as a
  current residual verifier surface; the older route/provenance reads now
  explicitly mark that state as historical intermediate context.
- 2026-06-06: Reframed the immediate verifier task after the first live runs:
  the action-only and forced-choice comparisons are both complete, so the next
  step is to decide protocol direction on the `29`-row ambiguity surface rather
  than continue “designing the first verifier comparison.”
- 2026-06-06: Implemented first-verifier post-run comparison/accounting script and generated cross-tabulation reports; also decided to include global non-routed V5->V6 transitions in a dedicated Scorer Audit Appendix in the component ablation table.
- 2026-06-06: Decided that the three zero-delta projection-policy off-switches (`current_summary_rate_priority`, `previous_active_month_over_current_month_zero`, and `major_recent_relapse_over_background_frequency`) do not require targeted hard slices of the `validation750` dataset, since their functionality is already robustly verified by explicit unit tests.
- 2026-06-06: Repaired the `27`-row candidate-trace `selected_source_id_invalid` tail by mapping unresolved source-ids to `"source_id_not_resolved"` and whitelisting acceptable non-routing statuses in routing and suspicious state checks. Regenerated validation750 projection render, route, and component ablation artifacts on disk; `selected_source_id_invalid` dropped to `0`.
- 2026-06-06: Completed the first live forced-choice verifier run over the clean
  `56`-row V6 surface via
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_forced_choice_verifier_experiment.py`.
  The run materialized:
  `experiments/gan2026_validation750_forced_choice_verifier_live_clean29_context_repair_v6_2026-06-06.{jsonl,json}`
  plus
  `docs/research/gan2026_validation750_forced_choice_verifier_live_clean29_context_repair_v6_2026-06-06.md`.
  All `56` rows parsed and passed contract checks. Equivalent action counts were `40`
  affirm, `11` human_review, `5` reject, and `0` abstain, with an agreement rate
  of `0.1429` (8/56) against the action-only baseline.
- 2026-06-06: Implemented and ran the first action-only verifier over the clean
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
