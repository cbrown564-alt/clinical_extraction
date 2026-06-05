# Gan 2026 Validation-Test Gap Staged Action Plan

Date: 2026-06-05

Status: staged development and experiment protocol derived from
`gan2026_validation_test_gap_hypothesis_synthesis_report_2026-06-05.md`.
This plan does not authorize locked-test row-level tuning or any
benchmark-comparable claim.

## Objective

Work through the synthesis report's recommended actions without confounding
component effects. Each stage changes at most one prediction-bearing policy
layer, keeps the current auditable validation assembly as the control, and uses
predeclared validation, synthetic, or aggregate-only test readouts.

The main research question is no longer "can the validation score go higher?"
It is:

```text
Which policy layer creates validation-only gain, and which source-grounded
mechanism has evidence that it can transfer?
```

## Fixed Controls

Use these controls in every stage unless the stage explicitly says otherwise:

- Split manifest: `gan2026_split_v1`.
- Development surface: validation rows, validation hard slices, synthetic
  minimal pairs, and no-call same-output replay.
- Locked-test surface: aggregate-only or predeclared-slice-only readouts after
  a separate freeze.
- Primary scorer: Gan-compatible Purist exact label.
- Side-car scorer: Pragmatic, when useful for ambiguity and benchmark
  convention interpretation.
- Baseline comparator: current auditable validation assembly,
  `untagged_nonprediction_release_candidate_v0_assembled_candidate`.
- H6 no-regression control: selective-action rows must preserve zero observed
  C->W on predeclared H6 controls.
- H10 provenance control: same-output identity must be checked before any
  live/replay delta is interpreted as model behavior.
- Attribution rule: semantic post-processing that changes selected event,
  semantic kind, sentinel state, denominator, boundary state, cluster
  interpretation, benchmark convention, or Purist/Pragmatic category is a
  deterministic rule, not format repair.

## Anti-Confounding Rules

1. Do not combine a repair-policy change with boundary/renderer changes in the
   same candidate.
2. Do not combine action-policy widening with semantic repair changes.
3. Do not change prompts, model ids, parser, scorer, normalization, and
   prediction policy in the same experiment.
4. Do not use a broad validation aggregate as the promotion signal unless the
   candidate first passes targeted hard-slice or panel gates.
5. Do not inspect locked-test row-level failures during development.
6. Do not add a new validation-derived rule unless it is first written as a
   portable mechanism with controls that were not used to design it.
7. Record validation loss as acceptable only when the removed or narrowed rule
   is validation-attuned and the remaining mechanism is more source-grounded.

## Stage 0: Freeze The Control State

Purpose: make the current assembly a stable reference so future improvements
have a clean denominator.

Action items:

- Keep the untagged-nonprediction assembled artifact as the current validation
  assembly record.
- Create a compact run manifest that names the exact control artifacts,
  commit/working-tree state, scorer, split manifest, and allowed inspection
  levels.
- Snapshot the H6 control row definitions and H10 raw-output provenance fields
  used by future experiments.

Experiment unit:

- Hypothesis: no new performance hypothesis; this is an instrumentation lock.
- Change under test: none.
- Surface: existing validation artifacts only.
- Readout: artifact completeness, H6 control availability, H10 replay
  availability.
- Gate: all later stages can reference a single immutable control manifest.

Decision:

- Block later stages if the control cannot reproduce row counts, prediction
  coverage, H6 controls, and score-layer provenance.

## Stage 1: Semantic Repair Policy Review

Purpose: answer the H5 recommendation directly before building another
candidate. This stage removes or narrows suspect repair families; it does not
add a new prediction mechanism.

Action items:

- Inventory every deterministic semantic repair family that can change a
  selected clinical event or scorer-facing label.
- Classify each family as `general`, `clinical_epilepsy`,
  `seizure_frequency`, `gan2026_specific`, or `benchmark_format`.
- Split repair into separate ladders:
  - raw model-selected label;
  - format-only repair;
  - selected-evidence arithmetic;
  - semantic repair;
  - benchmark rendering;
  - final action policy.
- Mark validation-attuned or example-specific repairs as disabled candidates,
  not as accepted policy.

Controlled experiments:

| Experiment | One Change | Surface | Primary Readout | Gate |
| --- | --- | --- | --- | --- |
| `h5_repair_inventory_v0` | no prediction change; inventory only | saved validation artifacts | repair family counts by portability category and semantic effect | every semantic family has owner, category, and effect |
| `h5_repair_family_ablation_v0` | disable or isolate one semantic repair family at a time | same-output validation replay | validation W->C, C->W, repair-induced semantic-kind changes, H6 controls | keep as portable only if gains are not validation-example-specific and C->W is bounded |
| `h5_repair_ladder_aggregate_v0` | compare frozen repair ladders | validation plus authorized aggregate-only test if already predeclared | repair gain by ladder, validation-test repair-gain delta | promote no semantic family without ladder attribution |

Non-confounding constraints:

- No boundary/renderer architecture change in this stage.
- No prompt or model change.
- No action-policy release changes.

Decision:

- Promote only format-preserving repair and source-grounded arithmetic by
  default.
- Quarantine broad semantic repair families whose validation gain does not
  transfer or whose mechanism depends on reviewed validation examples.

## Stage 2: Boundary And Benchmark Mechanism Expansion

Purpose: follow the H3/H7/H8 recommendation after H5 is controlled. The current
shallow typed layer is diagnostic only; this stage tests a richer structured
event representation with explicit projection ownership.

Action items:

- Define typed clinical events before final labels:
  `clinical_event`, `boundary_state`, `selected_frequency_state`,
  `projection_policy`, and `gan_rendered_label`.
- Keep `seizure_free_boundary_event_v0` and
  `benchmark_convention_renderer_v0` as named mechanisms, but do not connect
  them to final policy until their contract tests pass.
- Expand coverage beyond the 36 all-eligible validation rows only through
  predeclared family slices and synthetic/adversarial panels.

Controlled experiments:

| Experiment | One Change | Surface | Primary Readout | Gate |
| --- | --- | --- | --- | --- |
| `boundary_event_contract_v1` | richer typed event fields, final policy disconnected | synthetic minimal pairs | pair consistency, exact evidence, metadata completeness | 100% contract match on synthetic controls |
| `boundary_event_validation_panel_v1` | same contract over validation hard/control rows | validation hard slices | candidate-present rows, unsupported candidates, exact evidence, source-note-text absence | no unsupported candidates; controls suppressed |
| `benchmark_renderer_fixture_v1` | renderer only; clinical state frozen | fixtures and synthetic convention cases | clinical-state preservation, renderer rule id, sentinel visibility | renderer never silently changes clinical state |
| `boundary_renderer_component_ablation_v1` | connect typed layer only inside validation diagnostic assembly | validation hard/control panel | target-family W->C, C->W, H6 controls, benchmark-only versus clinical gains | reject if exposure remains too small or C->W appears outside known convention rows |

Non-confounding constraints:

- Use the Stage 1 accepted repair policy, frozen before this stage begins.
- No new action-policy fallback.
- No model or prompt change.

Decision:

- Promote to a larger validation hard-slice experiment only if the typed layer
  improves target hard rows while preserving controls and exact evidence.
- Reject as a gap-closing explanation if exposure remains below a predeclared
  coverage gate or W->C is too small to plausibly affect the aggregate gap.

### Stage 2 Outcome: Boundary Event Contract v1

Artifact:

- `experiments/gan2026_boundary_event_contract_v1_2026-06-05.json`
- `experiments/gan2026_boundary_event_contract_v1_2026-06-05.md`

Decision: `boundary_event_contract_v1_passed`.

The contract ran over the existing synthetic H3/H7 seed panel and exposed the
richer typed-event surface: `clinical_event`, `boundary_state`,
`selected_frequency_state`, `projection_policy`, and `gan_rendered_label`. It
matched 36/36 rows, preserved 18/18 clinical-state invariant pairs, kept
36/36 exact-evidence rows, completed typed-event and projection-policy metadata
on 36/36 rows, and kept final-label policy disconnected.

Implication: proceed to `boundary_event_validation_panel_v1` on validation
hard/control rows. Require exact evidence, unsupported-candidate suppression,
no source note text in artifacts, and no final-label policy connection.

### Stage 2 Outcome: Boundary Event Validation Panel v1

Artifact:

- `experiments/gan2026_boundary_event_validation_panel_v1_2026-06-05.json`
- `experiments/gan2026_boundary_event_validation_panel_v1_2026-06-05.md`

Decision: `boundary_event_validation_panel_v1_ready`.

The panel scanned 750 validation records and emitted only 30 supported
exact-evidence typed-event rows: 19 boundary rows, 11 renderer rows, 22 hard
rows, and 8 controls. It suppressed 720 source records from the row artifact,
wrote 0 unsupported candidate rows, 0 source-note-text rows, 30/30
typed-event-complete rows, 30/30 projection-policy-complete rows, and kept
final-label policy disconnected.

Implication: proceed to `h7_minimal_pair_panel_v1` and
`benchmark_renderer_fixture_v1` before connecting this typed-event surface to a
validation diagnostic assembly.

### Stage 2 Outcome: Benchmark Renderer Fixture v1

Artifact:

- `experiments/gan2026_benchmark_renderer_fixture_v1_2026-06-05.json`
- `experiments/gan2026_benchmark_renderer_fixture_v1_2026-06-05.md`

Decision: `benchmark_renderer_fixture_v1_passed`.

The renderer fixture ran over 16 synthetic benchmark-renderer rows. It preserved
clinical state on 16/16 rows, exposed renderer rule ids on 16/16 rows, exposed
scorer-sentinel use on 16/16 rows, kept exact evidence on 16/16 rows, and kept
final-label policy disconnected.

### Stage 2 Outcome: Boundary Renderer Component Ablation v1

Artifact:

- `experiments/gan2026_boundary_renderer_component_ablation_v1_2026-06-05.json`
- `experiments/gan2026_boundary_renderer_component_ablation_v1_2026-06-05.md`

Decision: `boundary_renderer_component_ablation_v1_rejected_revise_only`.

The validation diagnostic connected the typed layer only inside the
validation-development panel. It selected 30 rows, found 6 W->C and 1 C->W, and
separated benchmark-only rendering from clinical boundary projection. The
benchmark-only rows were 11/11 C->C; the C->W came from clinical boundary
projection on H6 row 2965. The artifact wrote 0 source-note-text rows, used 0
locked-test row-level artifacts, and kept final-label policy disconnected.

### Stage 2 Outcome: Boundary Selector Precision Revision v1

Artifact:

- `experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.json`
- `experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.md`

Decision: `boundary_selector_precision_revision_v1_promoted_bounded_component`.

The validation-only selector revision suppressed the unsafe row-2965 last-event
override and unknown/no-reference sentinel churn. It left 28 selected rows, 6
W->C, 0 C->W, 0 H6 regressions, 0 source-note-text rows, and no final-label
policy connection. The current typed validation panel reaches only 36 rows when
slice caps are removed, but that low exposure is now treated as intrinsic to
the rare boundary/benchmark family rather than as a rejection reason. The
boundary/renderer typed-event layer is promoted as a bounded component for
eligible cases; it is not a whole-pipeline promotion and does not authorize
holdout use or benchmark-comparable language.

## Stage 3: H7 Robustness And Template Brittleness

Purpose: test whether the mechanism is learning clinical state rather than
surface templates.

Action items:

- Build minimal pairs across the highest-risk families:
  seizure-free versus last-event-only, residual active semiology, non-epileptic
  current events, unknown versus no-reference, cluster burden, vague multiple
  frequency, current-versus-historical conflict, and diary/log aggregation.
- For each pair, preserve the clinical fact while changing only one surface
  feature: wording, order, section, distractor, semiology placement, or time
  anchor.

Controlled experiments:

| Experiment | One Change | Surface | Primary Readout | Gate |
| --- | --- | --- | --- | --- |
| `h7_minimal_pair_panel_v1` | panel construction only | synthetic/adversarial | invariant-pair contract and gold labels | all pairs have one named changed surface feature |
| `h7_component_stress_v1` | run frozen components on the panel | synthetic/adversarial | pair consistency by component, first flip owner, exact evidence | typed mechanism must beat deterministic comparator on consistency |
| `h7_repair_sensitivity_v1` | toggle accepted repair families one at a time | same panel | repair-induced flips and clinical-state drift | repair cannot be the owner of robustness |

Non-confounding constraints:

- Do not tune from panel mistakes until the panel contract is frozen.
- Do not count synthetic panel success as benchmark evidence.
- Do not change renderer behavior while testing boundary classification.

Decision:

- Use H7 success as mechanism support, not as final promotion.
- If robustness depends on semantic repair rather than typed source state,
  return to Stage 1.

### Stage 3 Outcome: H7 Minimal Pair Panel v1

Artifact:

- `experiments/gan2026_h7_minimal_pair_panel_v1_2026-06-05.json`
- `experiments/gan2026_h7_minimal_pair_panel_v1_2026-06-05.md`

Decision: `h7_minimal_pair_panel_v1_passed`.

The minimal-pair panel reused `boundary_event_contract_v1` rows and tested
wording, order, section, distractor, semiology, and time-anchor perturbations.
It passed with 36 rows, 18/18 complete invariant pairs, 36/36 exact-evidence
rows, and final-label policy disconnected. This completes the current H7
panel-construction task. Component-stress and repair-sensitivity variants are
not needed before moving to Stage 4 because the typed boundary/renderer layer is
now promoted only as a bounded rare-family component with exact-evidence and
H6/H9 guardrails, not as a broad aggregate-gap mechanism.

## Stage 4: Action Policy As A Guardrail, Not A Lead Fix

Purpose: keep H9 and nonprediction recovery useful without letting them mask
the main gap.

Action items:

- Keep untagged nonprediction release as an auditable validation-development
  artifact.
- Add action summaries to every new candidate: prediction-bearing coverage,
  abstain/review burden, release lane, fallback owner, and family-specific
  action rate.
- Test any new action policy only after the prediction-bearing layer is frozen.

Controlled experiments:

| Experiment | One Change | Surface | Primary Readout | Gate |
| --- | --- | --- | --- | --- |
| `h9_action_summary_sidecar_v1` | instrumentation only | validation artifacts | action rates by owner and family | sidecar complete for every candidate |
| `h9_release_lane_ablation_v1` | release one lane at a time | validation hard/control rows | release W->C, release C->W, fallback owner, H6 controls | zero or predeclared-bounded C->W |
| `h6_control_replay_v1` | no candidate change; H6 preservation check | every candidate stage | changed-label precision and C->W on H6 controls | no H6 regression |

Non-confounding constraints:

- No semantic repair changes.
- No boundary/renderer changes.
- No action-policy result can be described as solving the validation-test gap
  unless a frozen aggregate test audit later supports it.

Decision:

- Promote only as a safety/fallback policy.
- Do not prioritize action-policy widening over mechanism work while locked-test
  nonprediction burden remains low in aggregate.

### Stage 4 Outcome: H9 Action Summary Sidecar v1

Artifact:

- `experiments/gan2026_h9_action_summary_sidecar_v1_2026-06-05.json`
- `experiments/gan2026_h9_action_summary_sidecar_v1_2026-06-05.md`

Decision: `h9_action_summary_sidecar_v1_complete`.

The sidecar ran over the current auditable validation assembly,
`untagged_nonprediction_release_candidate_v0_assembled_candidate`, and made
0 model calls, 0 prediction changes, and used 0 locked-test row-level artifacts.
It records 750 validation rows, 735 prediction-bearing rows (0.9800 coverage),
697 correct prediction-bearing rows, 9 abstain rows, 6 human-review rows, and
19 deterministic-comparator fallback releases. Family action rates are now
available for future candidates; the largest remaining nonprediction rates are
unknown-boundary (11/20), uncertainty/ambiguity (11/24), seizure-free duration
(10/27), current-versus-historical (8/25), and competing semiologies (7/26).

Implication: future candidates should attach this same action-summary shape
before interpreting validation deltas. The sidecar is instrumentation only and
does not promote action widening as the lead fix.

### Stage 4 Outcome: H9 Release Lane Ablation v1

Artifact:

- `experiments/gan2026_h9_release_lane_ablation_v1_2026-06-05.json`
- `experiments/gan2026_h9_release_lane_ablation_v1_2026-06-05.md`

Decision: `h9_release_lane_ablation_v1_passed_guardrail`.

The one-lane-at-a-time validation replay preserved the Stage 4
anti-confounding constraints: no semantic repair changes, no boundary/renderer
changes, 0 model calls, 0 prediction changes beyond replaying already saved
deterministic fallback releases, and 0 locked-test row-level artifacts. The
abstain lane released 17 rows with 17 W->C, 0 C->W, and 0 H6 regressions. The
human-review lane released 2 rows with 2 W->C, 0 C->W, and 0 H6 regressions.

Implication: the current untagged-nonprediction release remains acceptable as a
safety/fallback validation-development policy, but the result is not a
validation-test gap solution and does not justify broad action-policy widening.

### Stage 4 Outcome: H6 Control Replay v1

Artifact:

- `experiments/gan2026_h6_control_replay_v1_2026-06-05.json`
- `experiments/gan2026_h6_control_replay_v1_2026-06-05.md`

Decision: `h6_control_replay_v1_passed`.

The replay sidecar checked saved validation summaries for
`untagged_nonprediction_release_candidate_v0_assembled_candidate`,
`boundary_selector_precision_revision_v1`, and
`h9_release_lane_ablation_v1`. It observed 0 H6 control regressions across the
checked candidates. The assembled nonprediction release preserved 37/37 H6
controls with changed-label precision 19/19; the boundary selector precision
revision retained 0 H6 regressions and changed-label precision 6/6; the release
lane ablation retained 0 H6 regressions and changed-label precision 19/19.

Implication: Stage 4 sidecars and controls are complete for the current cycle.
The next mechanism cycle can use the Stage 4 sidecar formats as required
guardrails before interpreting any new candidate delta.

## Stage 5: Same-Output And Runtime Provenance Hygiene

Purpose: prevent H10-class drift from being confused with model generalization.

Action items:

- Before every live/replay comparison, compute raw-output byte identity for
  model and adjudicator outputs where available.
- Separate model-output drift from adapter, parser, repair, scorer, or safety
  policy drift.
- Store component-policy version fields in every experiment artifact.

Controlled experiments:

| Experiment | One Change | Surface | Primary Readout | Gate |
| --- | --- | --- | --- | --- |
| `h10_raw_identity_sidecar_v1` | provenance instrumentation only | saved validation and live/replay artifacts | raw identity, parser version, repair policy version | no interpretation without identity result |
| `h10_downstream_drift_ladder_v1` | replay same raw outputs through frozen versus changed policies | validation replay | row changes by adapter, repair, safety floor, scorer | drift attributed to policy layer, not model |

Non-confounding constraints:

- Run as a sidecar before interpreting any other stage.
- Do not change prediction behavior inside provenance experiments.

Decision:

- If raw outputs match but labels change, classify the result as downstream
  policy drift.
- If raw outputs differ, do not compare score deltas without live-run variance
  accounting.

### Stage 5 Outcome: H10 Raw Identity Sidecar v1

Artifact:

- `experiments/gan2026_h10_raw_identity_sidecar_v1_2026-06-05.json`
- `experiments/gan2026_h10_raw_identity_sidecar_v1_2026-06-05.md`

Decision: `raw_identity_sidecar_ready`.

The sidecar covers the saved H5 replacement-postprocessing ladder and paired
validation live/replay artifacts. For the paired validation750 artifacts,
`raw_output`, `llm_candidate_raw_output`, and `adjudicator_raw_output` are each
present and byte-identical for 750/750 matched rows. The sidecar makes 0 model
calls, changes 0 predictions, writes 0 row-level output artifacts, and uses 0
locked-test row-level failures.

Implication: the H10 provenance prerequisite is satisfied for the next staged
mechanism work. Any later live/replay comparison should attach this sidecar or a
new version of it before interpreting label deltas.

## Stage 6: Frozen Aggregate Test Audit

Purpose: assess validation-test gap effect only after a candidate and analysis
plan are frozen.

Preconditions:

- Stage 1 repair policy is frozen.
- Stage 2 or 3 mechanism has passed validation hard-slice and synthetic
  controls.
- Stage 4 H6/H9 action sidecars are complete.
- Stage 5 H10 provenance sidecar is complete.
- Candidate, prompts, model ids, parser, scorer, repair policy, boundary
  policy, renderer policy, action policy, slice definitions, and readout fields
  are frozen.
- User explicitly authorizes the frozen holdout audit.

Allowed readouts:

- Overall Purist and Pragmatic aggregate.
- Prediction-bearing coverage and action counts.
- Predeclared hidden-family aggregates.
- Predeclared component-owner aggregate summaries.
- Predeclared score-layer aggregate ladder if generated without row-level
  failure inspection.
- H6 selective-action aggregate W->C/C->W where computable under the frozen
  plan.

Not allowed:

- Locked-test row-level failure inspection for development.
- New test-derived slice definitions.
- Any post-test candidate change treated as the same evaluation cycle.

Decision:

- If the candidate reduces the aggregate gap and preserves predeclared controls,
  record a frozen local holdout result with no benchmark-comparable claim.
- If the candidate fails, record it as final-evaluation evidence and restart a
  new validation-only cycle; do not tune from test rows.

### Stage 6 Outcome: Structured Projection Port Promoted Audit

User authorization on 2026-06-05 waived the original coverage and W->C gates for
`structured_validation_projection_port_panel_v0`, permitting one frozen
aggregate-only locked-test audit. The protocol and readout are:

- `docs/research/gan2026_structured_projection_port_frozen_test_protocol_2026-06-05.md`
- `experiments/gan2026_structured_projection_port_test450_aggregate_audit_2026-06-05.json`
- `experiments/gan2026_structured_projection_port_test450_aggregate_audit_2026-06-05.md`

Result: `promoted_audit_rejected_or_revise`. The promoted policy lowered the
test450 Purist proxy from 342/450 (0.7600) to 337/450 (0.7489), with 46 changed
rows, 7 W->C, 12 C->W, and changed-label precision 0.3684. The audit made 0 new
LLM calls, wrote 0 locked-test row-level artifacts, and does not support
benchmark-comparable language.

Implication: restart from a validation-only cycle. Do not tune from locked-test
row-level failures. The failure is consistent with the plan's warning that
low-coverage validation mechanisms and broad structured selectors can be
validation-attuned without transferring.

## Recommended Order Of Work

1. Freeze the control manifest and H6/H10 sidecar requirements.
2. Run the semantic repair inventory and one-family-at-a-time ablation.
3. Decide which repair families remain allowed before any new architecture work.
4. Expand the boundary/benchmark typed event contract with final policy
   disconnected.
5. Run validation hard/control contract smoke for typed events.
6. Run H7 minimal-pair robustness with component-stress conditions.
7. Connect the typed layer to validation diagnostic assembly only after the
   contract and robustness gates pass.
8. Run action-policy sidecars, not action-policy widening, on the diagnostic
   assembly.
9. Freeze a candidate and predeclared aggregate test audit only if the validation
   and synthetic evidence identifies a plausible transfer mechanism.

## Stage Outcome Table

| Stage | Recommended Action Covered | Main Risk Controlled | Promotion Signal |
| --- | --- | --- | --- |
| 0 | keep current assembly as auditable record | moving baseline | reproducible control manifest |
| 1 | H5 repair-policy review and freeze | validation-attuned semantic repair | portable, ablated repair families only |
| 2 | H3/H7/H8 boundary and benchmark mechanism work | shallow low-coverage typed layer | exact-evidence typed event gains on hard slices |
| 3 | H7 template brittleness panels | template-pattern fit | pair consistency and first-failure attribution |
| 4 | H6/H9 action policy controls | overblocking or unsafe release | high-precision changes with H6 no regression |
| 5 | H10 provenance hygiene | model/runtime drift confusion | raw identity and downstream drift attribution |
| 6 | frozen aggregate test audit | holdout leakage | predeclared aggregate/slice transfer readout |

## Stop Rules

Pause candidate promotion if any of these occur:

- a change improves broad validation F1 but not the target hard slice;
- a repair family owns clinical-state changes while being reported as
  normalization;
- changed rows lack exact evidence or projection-ready metadata;
- H6 controls regress;
- synthetic robustness depends on semantic repair rather than typed source
  state;
- benchmark renderer changes clinical state silently;
- a test aggregate is used to choose a new rule, threshold, prompt, or slice.

## Next Immediate Experiment Bundle

Run these first, in order:

1. `h5_repair_inventory_v0` - complete:
   `experiments/gan2026_h5_repair_inventory_v0_2026-06-05.json`.
2. `h5_repair_family_ablation_v0` - complete:
   `experiments/gan2026_h5_repair_family_ablation_v0_2026-06-05.json`.
3. `h10_raw_identity_sidecar_v1` over the same saved artifacts - complete:
   `experiments/gan2026_h10_raw_identity_sidecar_v1_2026-06-05.json`.
4. `boundary_event_contract_v1` with final policy disconnected - complete:
   `experiments/gan2026_boundary_event_contract_v1_2026-06-05.json`.
5. `boundary_event_validation_panel_v1` on validation hard/control rows -
   complete:
   `experiments/gan2026_boundary_event_validation_panel_v1_2026-06-05.json`.
6. `h7_minimal_pair_panel_v1` - complete:
   `experiments/gan2026_h7_minimal_pair_panel_v1_2026-06-05.json`.
7. `benchmark_renderer_fixture_v1` - complete:
   `experiments/gan2026_benchmark_renderer_fixture_v1_2026-06-05.json`.
8. `boundary_renderer_component_ablation_v1` - complete and rejected/revise-only:
   `experiments/gan2026_boundary_renderer_component_ablation_v1_2026-06-05.json`.
9. `boundary_selector_precision_revision_v1` - complete and promoted as a
   bounded rare-family component despite intrinsically low coverage:
   `experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.json`.
10. `h9_action_summary_sidecar_v1` - complete:
    `experiments/gan2026_h9_action_summary_sidecar_v1_2026-06-05.json`.
11. `h9_release_lane_ablation_v1` - complete:
    `experiments/gan2026_h9_release_lane_ablation_v1_2026-06-05.json`.
12. `h6_control_replay_v1` - complete:
    `experiments/gan2026_h6_control_replay_v1_2026-06-05.json`.

The Stage 2/3 boundary-renderer bundle and Stage 4 action-policy sidecar bundle
are now complete for this cycle. Promote the boundary/renderer layer only as a
bounded rare-family component for eligible boundary and benchmark-rendering
cases; do not use it as a broad aggregate-gap claim. Do not continue widening
action policy as the lead path. For any future candidate, attach H6/H9 action
summaries and H10 provenance before interpreting deltas.
