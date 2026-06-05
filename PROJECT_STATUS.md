# Project Status

Last updated: 2026-06-05

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions under
exact-evidence, attribution, hidden-family, and split-discipline constraints.
No benchmark-comparable claim is authorized.

## Current Strategy

Use saved artifacts as research instruments for component questions, not
whole-pipeline validation F1. Deterministic rules are frozen comparators, safety
floors, and miss-slice definers, not eligible answers for RQ1-RQ4.

RQ1-RQ10 now have bounded validation-development answers or explicit claim
boundaries. RQ3 remains positive but has unresolved projection-policy work.

Important numbers: `selective_safety_floor_gate_v0` changed 21 validation750
rows with 11 W->C and 0 C->W, and 14 frozen local test450 rows with 8 W->C and
0 C->W. RQ9 v3 covers 716/750 validation rows, abstains on 26, routes 8 to
human review, and has covered-row Purist accuracy 0.9469. RQ10 found 23
`underdetermined_note`, 19 `true_extraction_failure`, 11
`benchmark_convention_dominated`, and 0 strong likely gold defects among 53
residual Purist misses.

## Active Question

Multi-Component Assembly

End-to-end construction, implementation, validation, and frozen-test planning
now lives in
`docs/research/gan2026_multi_component_assembly_end_to_end_plan_2026-06-04.md`.

Status: component-home cleanup has started under ADR 0010. Source tracing and
suspicious selected-state policy now have independent component modules. The
promoted `binary_quote_highest_answer_selector` verifier also has a component
home, and the first no-call staged-hybrid assembly surface can wire selected
state union, suspicious routing, and saved verifier replay without owning their
logic. The saved assembly replay currently covers the 75-row hard panel, with
verifier coverage on the 42-row verifier slice; it is not a validation750
readout.

The validation750 input inventory now identifies three saved full-validation
surfaces that are available for assembly adaptation:
`hybrid_reasoner_replay`, `selective_safety_floor_gate_v0`, and
`rq9_selective_action_router_v3`, each at 750/750 source-row coverage. It also
marks the missing module-shaped inputs explicitly:
`rich_selected_state_fact_carrier`,
`boundary_v3_selected_state_candidates`, and full-validation
`promoted_binary_selective_verifier`. The next step is adapting the available
validation750 source-candidate, safety-floor, and router surfaces into assembly
rows while keeping the verifier slice separate until a full-validation verifier
protocol exists. That validation750 no-call assembly now exists at 750 joined
rows with all three available components present on every row, router actions
of 716 predict / 26 abstain / 8 human review, and 750/750 safety-floor rows
with exact selected evidence and valid selected source ids.

The explicit staged decision layer now exists over those assembled rows. It is
conservative: only router `predict` rows are prediction-bearing, while
`abstain` and `human_review` remain non-predictions. It has 750 rows, 716
prediction-bearing rows, 34 non-prediction rows, selective Purist accuracy
0.9469 and selective Pragmatic accuracy 0.9539 over prediction-bearing rows,
and 0 verifier rows used.

The residual non-prediction audit now explains the 34 non-prediction rows: 26
abstain and 8 human review; 24 `trigger_conditioned_frequency`, 8
`last_event_boundary`, and 2 `missing_denominator_anchor`. Development
accounting shows the blocked source candidate was Purist-correct on 19 rows
and Purist-wrong on 15 rows, with 5 non-`unknown` gold rows. This argues for a
selective abstention-pressure review before any full-validation verifier use
or promotion.

The selective abstention-pressure review is now materialized. It classifies the
34 residual non-predictions into 19 coverage-cost rows and 15 protective
blocks. Review lanes are: 2 `trigger_release_candidate`, 13
`trigger_sentinel_boundary_review`, 8 `date_policy_needed`, 2
`anchor_policy_needed`, and 9 `keep_nonprediction`. The next change should be
a predeclared gold-blinded trigger-context release rule plus a frozen
last-event date policy, not a broad verifier release.

The abstention-policy predeclaration is now frozen. It allows only the 2
`trigger_release_candidate` rows to be considered for direct behavior change
under gold-blinded criteria, allows 0 automatic last-event releases until date
instrumentation exists, keeps sentinel trigger rows in boundary review, keeps
anchor rows abstained until stable anchor extraction exists, and keeps the 9
protective blocks as non-predictions.

The trigger-context release proposal is now materialized. Of the 2 considered
trigger release candidates, the stricter evidence rule releases 1 row (`5977`)
as `multiple per 6 week`; row `6319` remains unreleased because its selected
evidence does not itself name the event target. The proposed decision layer has
717 prediction-bearing rows, 25 abstain rows, 8 human-review rows, selective
Purist accuracy 0.9470, and selective Pragmatic accuracy 0.9540. This is still
a validation-development proposal, not a promoted behavior change.

The last-event date instrumentation prerequisite is now materialized over the
8 `date_policy_needed` rows. It finds 1 row with a full date (`11216`), 3 rows
with partial dates missing a year (`11272`, `14810`, `14821`), and 4 rows with
no explicit date in the selected evidence (`11254`, `11259`, `11262`, `11282`).
All 8 rows now have source-record reference-date anchors from `Clinic Date:` or
`Sent:` headers. This started as instrumentation-only and has now been extended
by the duration policy below; last-event rows remain blocked from
prediction-bearing behavior.

`last_event_duration_policy_v0` is now implemented and rematerialized over the
same 8 validation rows. It derives 1 duration-auditable row (`11216`,
`seizure free for 4 month`) but keeps automatic release-ready rows at 0 because
that row is a validation protective block; the other 7 rows are blocked by
partial or missing selected-evidence dates. Details live in
`experiments/gan2026_multi_component_assembly_experiment_log_2026-06-05.md`.

The first component evidence matrix for
`hybrid_multi_component_staged_assembly_v0` is now materialized at
`experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_component_matrix_2026-06-04.csv`.
It has 750/750 unique validation rows, 716 prediction-bearing rows, 34
non-predictions, 0 contract issues, 0 verifier rows used, 0
parse/evidence/schema issue rows, 1 trigger-release proposal row, and 1
last-event duration-auditable row. This satisfies the matrix artifact gate for
the conservative validation candidate, but it does not yet freeze a
behavior-changing trigger release or authorize test evaluation.

The trigger-context release promotion gate is now materialized at
`experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_trigger_release_promotion_2026-06-04.json`.
It rejects promotion: the only release row (`5977`) has 0 W->C rows, 0 C->W
rows, and 1 category-correct-not-exact-label caveat (`unknown` gold versus
`multiple per 6 week` proposal), so it does not satisfy the predeclared 1 W->C /
0 C->W gate.

An aggregate-only diagnostic applied the existing RQ9 selective router
mechanically to the already-frozen test450 reasoner artifact without row-level
test inspection. It predicted 449/450 rows with selective Purist accuracy
0.7617 and a full-row Purist proxy of 0.7600, so router packaging alone will not
reach the >=0.9 locked-test target.

Validation failure recoverability is now materialized at
`experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_failure_recoverability_2026-06-05.json`.
Among the 53 conservative assembly W-failure rows, 21 have exact/source-valid
actionable candidates in saved components: 16 exact-label and 5 Purist-category
only. The exact-label oracle upper bound is 694/750 (0.9253) and the
all-actionable oracle upper bound is 699/750 (0.9320), so there is validation
headroom, but the selector is not yet implementable without gold-derived
choice.

The exact-label selector ablation is now materialized at
`experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_exact_label_selector_ablation_2026-06-05.json`.
Broad deterministic and LLM replacement selectors were rejected because they
created large C->W damage. The narrow
`nonprediction_llm_unknown_any_v0` validation ablation selected 13 rows with 13
W->C and 0 C->W, projecting 691/750 (0.9213), but the frozen aggregate
test450 audit found it selected 0 holdout rows because the router predicted on
449/450 rows. This branch is therefore diagnostic, not a path to the >=0.9
test target.

The candidate-union branch now looks like the next mechanism target rather
than more router packaging. The saved hard-panel union recalls 47/75 rows and
contains Purist-correct alternatives for 16 of 38 comparator misses, but naive
selectors are destructive (`first_live` introduces 6 C->W and 0 W->C). The next
development step should be a small-union candidate-ranking or verifier
component with W->C/C->W accounting on validation hard panels.

The first candidate-union ranker ablation is now materialized at
`experiments/gan2026_candidate_union_ranker_ablation_hard_panel_2026-06-05.json`.
It confirms the selector bottleneck: hard-panel oracle recoverability is 16
miss rows, but only `diary_log_only_v0` is clean so far, with 3 W->C and 0
C->W. The broader comparator-absent quality ranker is net positive (13 W->C,
5 C->W) but not promotable because all 5 C->W rows are live boundary cluster
candidates overriding correct comparator labels. Next step: expand diary/log
negative tests and materialize the diary ranker on full validation before any
holdout use.

The diary/log full-validation audit is now materialized at
`experiments/gan2026_diary_log_full_validation_audit_2026-06-05.json`. The
frozen selected rule subset (`diary.date_list`, `diary.monthly_count_log`,
`diary.sleep_awake_month_summary`) selected 2 validation rows with 2 W->C and
0 C->W, projecting 680/750 (0.9067). It also rejected 3 diary rows, including
2 `diary.increasing_monthly_count` rows that would otherwise be regression
risk. A frozen aggregate-only test450 audit selected 0 rows and left the proxy
unchanged at 342/450 (0.7600), so diary/log selection is safe but not a path to
the >=0.9 holdout target.

The structural-guard candidate-union branch is now materialized through hard
panel, full validation, and frozen aggregate-only holdout audit. On the 75-row
hard panel, `comparator_absent_structural_guard_rank_v0` selected 24 rows with
10 W->C and 0 C->W. On validation750 it selected 34 rows with 21 W->C and 0
C->W, projecting 699/750 (0.9320). The frozen aggregate-only test450 audit then
selected only 9 rows with 1 W->C and 0 C->W, projecting 343/450 (0.7622). This
is high-precision but too low-coverage on holdout; do not tune from test row
identities. The next mechanism must improve prediction-bearing validation hard
slices rather than relying on nonprediction repair opportunities.

A stronger-model smoke with `openai/gpt-4.1` is now materialized at
`experiments/gan2026_parallel_reasoner_gpt41_prediction_bearing_hardslice40_validation_2026-06-05.md`.
It ran the existing hybrid parallel reasoner on 20 prediction-bearing validation
misses plus 20 prediction-bearing controls. Infrastructure was healthy (0 call
failures, 40/40 structured adjudicator records, 40/40 exact selected evidence),
but the prompt shape failed as a rescue mechanism: deterministic/adapted layers
stayed at 20/40 Purist, while raw adjudication fell to 13/40. Do not scale this
full-label adjudicator prompt; the next model-backed branch should be a
change-only verifier over candidate alternatives with an explicit
default-to-current-label policy.

`change_only_candidate_verifier_v0` is now implemented and calibrated. On a
constructed validation calibration panel of 15 prediction-bearing recoverable
misses plus 45 correct controls, the GPT-4.1 change-only verifier with a
parseable-label switch gate produced 12 W->C and 0 C->W, projecting 57/60
(0.9500). However, a non-gold full-family audit for current seizure-free labels
with LLM `unknown` alternatives was rejected: 5 W->C but 10 C->W, projecting
26/38 (0.6842). The C->W errors are mostly duration/convention failures where
the current seizure-free label is Purist-correct but the verifier over-switches
to `unknown` because the exact duration is less than "multiple year." Next step:
add a duration-preserving gate before any seizure-free-to-unknown verifier use.

That duration-preserving gate is now implemented as an active-event requirement
for `seizure free*` current labels versus `unknown` alternatives. A same-output
validation reparse of the saved seizure-free/unknown family moved it to 7 W->C
and 0 C->W, but the frozen aggregate-only test450 audit selected 16 eligible
rows with 13 C->C, 3 W->W, and 0 W->C, leaving the holdout proxy unchanged at
342/450 (0.7600). The branch is now safe but not target-moving; continue the
validation-only mechanism search.

The exact LLM-selector change-only verifier branch is now materialized. A
frequency-first exact `llm_candidate_selector_raw` ranker over validation had
281 eligible rows and, after validation-derived convention gates, reparsed to
7 W->C and 0 C->W, projecting validation 697/750 -> 704/750. The frozen
aggregate-only test450 audit had 161 eligible rows, 159 call-ok rows, 7 W->C
and 2 C->W, moving the `hybrid_adjudicator_raw` Purist proxy only from
342/450 (0.7600) to 347/450 (0.7711). No test row-level failures or raw outputs
were stored. This branch is rejected as a goal-achieving path despite being a
positive validation mechanism.

The combined change-only switch layer is now materialized as
`gan2026_combined_change_only_switch_layer_v0`. It composes the validation-clean
deterministic/state exact switch family before the exact LLM-selector switch
family over the same staged reasoner scorer-facing label. Validation was clean:
34 changed rows, 11 W->C, 0 C->W, projecting 697/750 -> 708/750. The frozen
aggregate-only test450 audit had 446/450 call-ok rows, 31 changed rows, 13 W->C
and 1 C->W, moving the holdout proxy from 342/450 (0.7600) to 354/450
(0.7867). This is the best switch-layer holdout movement so far but still far
below the >=0.9 target, so saved exact-alternative switching is not sufficient.
The next mechanism should add candidate-generation coverage or materially
change the architecture, not merely add more gates over the same candidate
pool.

The retrieved train-exemplar few-shot branch is now closed as a goal-achieving
candidate. The validation replay of `gan2026_fewshot_train_exemplar_contract_v0`
was strong (708/750 -> 726/750; 18 W->C, 0 C->W), but the frozen aggregate-only
test450 audit moved only 353/450 -> 357/450 with 4 W->C and 0 C->W. The exact
frozen audit used `openai/gpt-4.1`,
`gan2026_fewshot_train_exemplar_direct_labeler_v0`, max tokens 900, verifier
max tokens 500, and source artifact
`experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`.
No test row ids, clinical text, raw model outputs, row-level failures, or
row-level diagnostics were written. The branch is safe but far too
low-coverage for the >=0.9 locked-test target, so the next mechanism should be
a typed candidate contract or structured event architecture with explicit
coverage targets.

Core verifier artifacts live under
`docs/research/gan2026_selective_verifier_*2026-06-04.md`.

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
- Locked test is not for row-level tuning.
- `rules_only_v1` remains the frozen transparent comparator.
- Treat saturated aggregate validation scores as low-information.
- Any holdout-facing use needs a frozen predeclared audit and explicit user
  authorization; do not change scorer/gold policy from RQ10 alone.
- Final F1 is secondary to candidate recall, evidence exactness, projection
  consistency, metadata completeness, ambiguity preservation, and regression
  accounting.

## Work Board

### Now

- Pivot from narrow switch layers to a typed candidate contract or structured
  event architecture with explicit coverage targets before any new holdout use.
- Keep the frozen validation assembly conservative: 716 predict / 26 abstain /
  8 human review. Trigger-context release is rejected and last-event automatic
  release remains blocked under `last_event_duration_policy_v0`.
- Return to validation/synthetic hard panels for a new mechanism that can beat
  the deterministic locked-test ceiling; do not tune from test row-level
  failures.
- Next validation ablation: define a structured candidate/event surface that
  covers at least 150 holdout-like prediction-bearing rows on validation
  hard/control panels, accepts at least 60 validation W->C opportunities with
  <=5% C->W on matched controls, and reaches >=95% parse-ok plus exact-evidence
  rows before any frozen test audit.

### Next

- Decide whether the next architecture should be a typed candidate contract
  layered over current components or a richer structured event representation
  with explicit projection ownership.
- Write a frozen test450 protocol addendum only after the new validation
  coverage gates pass.
- If cost/latency/token efficiency is needed, run a telemetry-only pass over
  surviving primitives before strengthening RQ8 claims.

### Blocked

- Benchmark-comparable language remains blocked; current holdout evidence is a
  local frozen audit only.
- Whole-pipeline promotion is blocked until the family-indexed matrix is
  implemented as an auditable assembled candidate and any holdout-facing use
  has a frozen protocol.
- The few-shot train-exemplar contract is blocked as a goal-achieving path:
  clean precision but only 4 accepted W->C rows on frozen test450.

### Done Recently

- 2026-06-05: Added the direct-labeler candidate-generation branch over the
  combined switch-layer current label. The full validation750 direct pass made
  750/750 calls but was destructive as a replacement (405/750 raw direct
  correct; 26 W->C and 329 C->W). The full exact-evidence change-only verifier
  panel was also rejected (11 W->C, 25 C->W, projected 694/750). A targeted
  non-gold policy, `gan2026_direct_labeler_targeted_switch_v0`, is validation
  clean: 20 selected rows, 9 W->C, 0 C->W, 7 W->W, 4 C->C, projecting the
  combined switch-layer validation score from 708/750 (0.9440) to 717/750
  (0.9560). The frozen aggregate-only test450 audit selected only 4 rows with
  1 W->C and 0 C->W, leaving the final proxy at 354/450 (0.7867). It is safe
  but far too low-coverage for the >=0.9 test target; no test row-level
  inspection was performed or authorized.
- 2026-06-05: Closed the train-exemplar few-shot branch as non-goal-achieving.
  Nearest train-label replacement was rejected at 239/750 validation Purist
  proxy. A retrieved-train-exemplar GPT-4.1 panel over 42 validation misses plus
  42 controls produced strong raw coverage but unsafe regressions (27 W->C,
  8 C->W), and the existing change-only verifier stayed unsafe (6 W->C,
  3 C->W). The few-shot-specific contract was clean on validation750
  (708/750 -> 726/750; 18 W->C, 0 C->W), but the frozen aggregate-only test450
  audit reached only 357/450 (0.7933), with 4 W->C, 0 C->W, and 4 selected
  rows. No test row-level diagnostics were written. Pivot to a typed candidate
  contract or structured event architecture with explicit coverage targets.
- 2026-06-05: Implemented `last_event_duration_policy_v0`, added focused
  policy tests, and rebuilt the validation750 staged assembly chain. The policy
  found 1 duration-auditable last-event row but 0 automatic release-ready rows:
  row `11216` remains blocked by validation protective accounting, 3 rows are
  partial-date blocked, and 4 rows lack explicit selected-evidence dates.
- 2026-06-05: Added `component_evidence_matrix_v0` and materialized the
  candidate validation750 component matrix: 750 unique rows, 716 predict / 26
  abstain / 8 human review, 0 contract issues, 0 verifier rows used, 0
  parse/evidence/schema issue rows, and visible trigger/last-event proposal
  fields without changing candidate predictions.
- 2026-06-05: Ran an aggregate-only diagnostic applying the existing RQ9
  selective router to the frozen test450 source artifact. It predicted 449/450
  rows with full-row Purist proxy 0.7600, confirming that router packaging alone
  is not a path to the >=0.9 test target.
- 2026-06-05: Added `trigger_release_promotion_analysis_v0` and rejected the
  1-row trigger-context release proposal for the assembly candidate. The
  component matrix shows 0 W->C and a category-correct-not-exact-label caveat,
  violating the predeclared trigger promotion gate.
- 2026-06-05: Added `assembly_failure_recoverability_v0`. It found 53
  conservative assembly W-failure rows, 21 actionable candidate-recall rows
  already present in saved components, and an oracle validation upper bound of
  694/750 exact-label-only or 699/750 with Purist-category alternatives.
- 2026-06-05: Added `exact_label_selector_ablation_v0`. Broad selectors were
  rejected; the narrow validation-only nonprediction LLM-unknown selector
  projected 691/750 with 13 W->C and 0 C->W, but an aggregate-only test audit
  selected 0 holdout rows and left the proxy at 342/450 (0.7600).
- 2026-06-05: Rechecked the candidate-union/selected-state branch. It has
  recall headroom but not a safe selector: 16 comparator-miss hard-panel rows
  have a correct union candidate, while naive selectors introduce C->W damage.
- 2026-06-05: Added the GPT-4.1 change-only candidate verifier branch for
  deterministic/state exact alternatives. Validation calibration initially
  found 6 W->C and 5 C->W, then benchmark-convention gates removed subtype,
  single-event, imprecise-cluster, partial-window, and arithmetic regressions.
  Full validation-family reparse was clean but small: 149 rows, 4 W->C,
  0 C->W, validation projection 697/750 -> 701/750. The frozen aggregate-only
  test450 audit selected 92 rows with 9 W->C and 1 C->W, moving the
  `hybrid_adjudicator_raw` Purist proxy from 342/450 (0.7600) to 350/450
  (0.7778), still far below the requested >=0.9 target. No test row-level
  failures were inspected or stored.
- 2026-06-05: Added `candidate_union_ranker_ablation_v0`. On the selected-state
  union hard panel, `diary_log_only_v0` recovered 3 rows with 0 C->W; broader
  quality ranking was net positive but unsafe with 5 C->W cluster-boundary
  regressions.
- 2026-06-05: Added `diary_log_full_validation_audit_v0` and ran a frozen
  aggregate-only test audit. Full validation was clean but tiny (2 W->C, 0
  C->W); test selected 0 rows and stayed at 342/450 (0.7600).
- 2026-06-04: Added the `last_event_date_instrumentation` component and
  materialized the staged-hybrid last-event date review. It covers the 8
  `date_policy_needed` rows, classifies 1 full-date row, 3 partial-date rows,
  and 4 rows with no explicit date in selected evidence. A follow-up source
  record join now finds reference-date anchors for all 8 rows, but keeps
  automatic release-ready rows at 0 until duration derivation and conflict
  checks exist.
- 2026-06-04: Added the `trigger_context_release_rule` component and
  materialized the proposed trigger-context release layer. The rule considered
  the 2 predeclared trigger release candidates and released 1 row (`5977`),
  raising the proposed prediction-bearing count from 716 to 717 while leaving
  last-event rows blocked pending date instrumentation.
- 2026-06-04: Added the `abstention_policy_predeclaration` component and
  materialized the staged-hybrid abstention-policy predeclaration. It freezes
  `trigger_context_release_rule_v0` and `last_event_date_policy_v0`, permits
  only 2 direct trigger release candidates for possible behavior change, and
  permits 0 last-event automatic releases until date instrumentation exists.
- 2026-06-04: Added the `selective_abstention_pressure` component and
  materialized the staged-hybrid pressure review: 34 rows, 19 coverage-cost
  rows, 15 protective blocks, 2 trigger release candidates, 13 trigger sentinel
  boundary reviews, 8 date-policy rows, 2 anchor-policy rows, and 9 rows to
  keep as non-predictions. It recommends a predeclared trigger-context release
  rule plus a frozen last-event date policy before behavior changes.
- 2026-06-04: Added the `residual_nonprediction_audit` component and
  materialized the staged-hybrid residual audit: 34 non-prediction rows, 26
  abstain, 8 human review, 24 trigger-conditioned rows, 8 last-event boundary
  rows, 2 missing-denominator rows, 19 blocked Purist-correct source
  candidates, and 15 blocked Purist-wrong source candidates. The recommended
  next step is selective abstention-pressure review.
- 2026-06-04: Added the `staged_decision_policy` component and materialized the
  validation750 no-call decision layer: 750 rows, 716 prediction-bearing rows,
  26 abstain, 8 human review, selective Purist accuracy 0.9469, selective
  Pragmatic accuracy 0.9539, and 0 verifier rows used.
- 2026-06-04: Materialized the validation750 no-call staged-hybrid assembly
  from the available full-validation component surfaces. The assembly has 750
  joined rows with reasoner replay, safety-floor gate, and RQ9 router present
  on every row; router actions are 716 predict, 26 abstain, and 8 human review.
  Historical reasoner prompt payload strings are omitted from the assembly
  rows.
- 2026-06-04: Added the `validation_surface_inventory` component and artifact
  for staged assembly inputs. The inventory confirms 750/750 coverage for
  `hybrid_reasoner_replay`, `selective_safety_floor_gate_v0`, and
  `rq9_selective_action_router_v3`; identifies missing module-shaped inputs for
  selected-state fact carrying, boundary-v3 selected-state candidates, and the
  promoted verifier; and records that old saved prompt payloads are historical
  evidence, not prompt text to reuse.
- 2026-06-04: Added ADR 0010 for component homes before pipeline assembly;
  extracted Gan source-trace, suspicious selected-state policy, and promoted
  selective-verifier components; added the first `staged_hybrid_assembly`
  no-call composition surface and focused component/assembly tests; materialized
  the saved assembly replay at 75 joined rows with 42 verifier rows, 0
  projection source-id inconsistencies, 7 verifier W->C, 1 verifier C->W
  (`7168`), 10 C->review, and 3 W->review.
- 2026-06-04: Adjudicated all 5 selective-verifier C->W regression rows and
  rejected v0 for prediction-bearing use; live-ran two plain-language verifier
  prompt designs, then a full-letter support-parts variant with 5 W->C and 1
  C->W, a binary quote/highest design with 7 W->C and 3 C->W, and a stronger
  binary prompt with 7 W->C, 1 C->W, and 10 C->review; promoted the stronger
  binary prompt and marked verifier prompt-design work complete for integration.
- 2026-06-04: Ran the frozen 42-row selective-verifier live readout with
  42/42 calls ok, 42/42 parseable outputs, 38/42 exact evidence-quote rows, 6
  W->C, 5 C->W, and changed-decision precision 0.522.
- 2026-06-04: Replayed staged hybrid assembly and suspicious routing with
  source-id tracing: 75/75 source-id-consistent rows, routing at 35
  `route_unknown`, 9 `route_review`, and 31 render rows.
- 2026-06-04: Added RQ6-RQ8 answers, RQ8 telemetry guard, ADR 0009, and the
  architecture readiness decision; telemetry remains incomplete at 0/21 rows.
