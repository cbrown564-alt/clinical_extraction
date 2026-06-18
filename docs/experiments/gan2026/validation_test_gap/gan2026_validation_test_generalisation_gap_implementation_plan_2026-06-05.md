# Gan 2026 Validation-Test Generalisation Gap Implementation Plan

Date: 2026-06-05

Status: multi-phase research implementation plan. This is not a
benchmark-comparable claim, and it does not authorize locked-test row-level
tuning.

## Objective

Explain why Gan 2026 validation performance remains much stronger than locked
test performance despite both splits coming from the same synthetic,
template-generated dataset.

The next work should stop optimizing the assembled architecture as a whole. It
should instead instrument, ablate, and stress-test the existing components so we
can answer:

1. Which clinical subproblems transfer from validation to test?
2. Which component owns each subproblem on each split?
3. Where does the validation-test gap appear: candidate generation, evidence
   selection, temporal selection, projection, rendering, safety floor,
   abstention, or benchmark formatting?
4. When an LLM owns a decision, is its validation-test gap different from the
   deterministic-rule-owned rows for the same hidden family?
5. Which hypotheses are supported by controlled evidence, and which are only
   retrospective stories?

## Split Discipline

Use `gan2026_split_v1`.

- Validation750 remains the development surface. Row-level validation review,
  hard-slice construction, controlled ablations, and hypothesis refinement are
  allowed.
- Locked test450 remains a frozen holdout surface. Do not inspect row-level test
  failures during development. Do not change prompts, rules, gates, thresholds,
  model choice, projection, repair policy, or normalization based on test
  results.
- Test450 analysis for this plan must be aggregate-only or predeclared-slice
  only until a final post-hoc audit is explicitly authorized.
- Synthetic and adversarial panels are mechanism probes. They can explain
  behavior, but they are not benchmark evidence.

## Current Working Assumptions

These assumptions should be tested, not treated as conclusions:

- The validation-test gap is unlikely to be explained by broad descriptive
  distribution differences alone.
- The gap is more likely driven by hidden-family incidence, component ownership,
  brittle template-pattern fit, or selective-action coverage.
- Broad validation F1 is saturated and low-information.
- Validation-prefix success is especially unreliable for component transfer.
- LLM components may help in boundary and competing-state families but may lose
  transfer when deterministic projection or formatting becomes the
  prediction-bearing owner.
- Deterministic rules may be high precision on familiar templates but brittle
  when hidden-family wording or benchmark conventions shift.

## Hypothesis Registry

Every experiment in this program should map to one or more named hypotheses.

| ID | Hypothesis | Primary signal | Reject or revise if |
| --- | --- | --- | --- |
| H1 | Hidden-family mix explains the aggregate gap. | Validation and test slice aggregates show the gap is concentrated in a small set of predeclared families. | Gap persists within most matched families. |
| H2 | Component ownership explains the gap. | LLM-owned, deterministic-owned, projection-owned, and safety-floor-owned rows have different validation-test gaps after family stratification. | Ownership strata have similar gaps once family is controlled. |
| H3 | Candidate-generation recall fails to transfer. | Gold-relevant candidate exposure is high on validation hard slices but lower on predeclared test slice aggregates or synthetic paraphrases. | Candidate recall is stable while later components fail. |
| H4 | Evidence selection transfers, but projection/rendering does not. | Exact evidence/source-id rates are stable, while projection or adapter layers create validation-test divergence. | Evidence validity falls alongside final accuracy. |
| H5 | Deterministic semantic repair masks LLM weakness on validation. | Raw LLM or format-only layers have a larger gap than full repair, and full repair owns prediction-bearing changes. | Same-raw-output ladder attributes gains to LLM-owned selected facts. |
| H6 | Safety-floor/selective-action policy transfers better than replacement. | Change-only rows show high changed-label precision and low C->W on both validation and frozen aggregate test summaries. | Safety floor suppresses useful test changes or selective-action gains vanish. |
| H7 | Template brittleness, not clinical complexity, causes the gap. | Paraphrase/minimal-pair panels preserve gold facts but flip component behavior by wording/order/section placement. | Components remain stable across paraphrases. |
| H8 | Benchmark-format conventions dominate a subset of the gap. | Convention-tagged rows have poor transfer and strong disagreement between clinical-state correctness and Gan label exactness. | Gap remains after excluding convention-dominated slices. |
| H9 | Abstention/review policy hides different failure modes by split. | Nonprediction, review, and monitor rates differ by hidden family and component owner across validation and test aggregate summaries. | Action rates are stable and unrelated to misses. |
| H10 | Model/runtime variance is being mistaken for generalisation gap. | Same raw outputs and no-call replays produce stable attribution; live reruns differ materially only in output contract/noise. | Same-output replay still shows the gap. |

## Required Instrumentation

Build a reusable `validation_test_gap_matrix_v0` artifact before running new
architecture experiments.

The matrix should be generated from saved artifacts when possible and should
emit one row per `source_row_index`, `score_layer`, and `clinical_subproblem`.

Required fields:

- `source_row_index`, `split`, `split_manifest`, `distribution`;
- `candidate_name`, `candidate_version`, `pipeline_family`;
- `score_layer`: deterministic comparator, raw model, format-only repair,
  deterministic adapter, projection, safety floor, final policy, abstain/review;
- `clinical_subproblem`: candidate generation, evidence selection, temporal
  selection, seizure-free boundary, rate denominator, cluster/diary aggregation,
  competing event selection, uncertainty boundary, adapter rendering,
  benchmark formatting;
- `component_owner`: deterministic rule, LLM clinical selection, deterministic
  adapter, graph projection, safety floor, schema repair, benchmark format;
- `hidden_family` tags from the atlas;
- `gold_label`, `baseline_label`, `layer_label`, `final_label`;
- Purist and Pragmatic correctness for every score layer where labels exist;
- `changed_from_baseline`, `wrong_to_correct`, `correct_to_wrong`, `net_gain`;
- evidence status, source-id validity, selected operand completeness, schema
  validity, parse validity;
- abstain/review/monitor action and reason;
- first-failure owner for validation rows and for synthetic/adversarial panels;
- for locked test, only aggregate-safe fields and predeclared slice membership.

Existing code to reuse or extend:

- `hidden_family_atlas.py`;
- `atlas_hard_slice_diagnostic.py`;
- `architecture_component_ablation.py`;
- `llm_replacement_postprocessing_ablation.py`;
- `selective_safety_floor_gate_replay.py`;
- `component_projection_panel.py`;
- `rq5_rendering_matrix.py`;
- `rq9_selective_action_router.py`;
- `rq9_abstention_pressure.py`;
- current staged assembly component matrix artifacts.

## Phase 0: Protocol Freeze And Artifact Inventory

Goal: prevent another ambiguous whole-pipeline iteration.

Implementation steps:

1. Create a gap-analysis protocol document that names the candidate/comparator
   surfaces, scorer policy, split manifest, test inspection limits, and stop
   rules.
2. Inventory every saved validation and authorized test aggregate artifact that
   can be replayed without new model calls.
3. Mark artifacts as one of:
   - same-raw-output replay eligible;
   - final-policy-only;
   - validation row-review eligible;
   - locked-test aggregate-only;
   - diagnostic/unusable because fields are missing.
4. Define the exact candidate set for the first analysis wave:
   - `rules_only_v1`;
   - conservative staged assembly;
   - direct-labeler structured candidate panel;
   - selective safety-floor gate;
   - any no-call replayable raw/repair ladders already present.
5. Write the first hypothesis registry as machine-readable JSON so each run
   declares which hypothesis it tests.

Deliverables:

- ``;
- `experiments/gan2026_validation_test_gap_artifact_inventory_2026-06-05.json`;
- tests that fail when a gap experiment lacks hypothesis ids, split manifest,
  scorer policy, inspection policy, or artifact provenance.

Gate to continue:

- every planned test read is aggregate-only or predeclared-slice-only;
- no candidate change is proposed before the matrix exists.

## Phase 1: Validation-Test Surface Map

Goal: quantify where the 15-point gap lives before explaining it.

Implementation steps:

1. Build split-level summary tables for validation750 and every authorized
   test450 aggregate surface:
   - Purist/Pragmatic accuracy;
   - prediction-bearing coverage;
   - abstain/review/monitor rates;
   - label-kind distribution;
   - row-ok distribution;
   - hidden-family incidence where slice membership can be computed without
     using test failures.
2. Compute matched validation-test summaries by label kind and predeclared
   hidden-family membership.
3. Produce confidence intervals for slice gaps, using Wilson or bootstrap
   intervals where denominators are small.
4. Identify high-leverage slices:
   - large absolute gap;
   - large contribution to aggregate gap;
   - high validation confidence but poor frozen test aggregate;
   - large action-rate shift.

Deliverables:

- `experiments/gan2026_validation_test_surface_map_v0_2026-06-05.json`;
- `experiments/gan2026_validation_test_surface_map_v0_2026-06-05.md`;
- optional CSV table for plotting.

Decision output:

- accept H1 as plausible only if the gap concentrates in a small number of
  predeclared families;
- otherwise prioritize component-ownership and layer-ladder hypotheses.

## Phase 2: Score-Layer Ladder And Ownership Matrix

Goal: separate raw model behavior, deterministic repair, projection, safety
floor, and final policy.

Implementation steps:

1. Implement `validation_test_gap_matrix_v0` over validation first.
2. Backfill score-layer rows from saved artifacts:
   - deterministic comparator;
   - raw model output where available;
   - parsed raw model clinical label;
   - format-only repair;
   - deterministic adapter;
   - projection;
   - safety floor;
   - final policy.
3. Assign component owner by decision effect, not module name.
4. Add subproblem ownership labels:
   - candidate generation;
   - evidence selection;
   - temporal selection;
   - seizure-free boundary;
   - rate denominator;
   - cluster/diary aggregation;
   - competing event selection;
   - uncertainty boundary;
   - rendering;
   - benchmark formatting.
5. Generate validation-only first-failure ownership tables by hidden family.
6. For locked test, produce only aggregate and predeclared-slice ownership
   summaries if the needed owner fields are already available without row-level
   failure review.

Deliverables:

- `src/.../artifact_analysis/validation_test_gap_matrix.py`;
- `tests/test_gan2026_validation_test_gap_matrix.py`;
- `experiments/gan2026_validation_test_gap_matrix_v0_validation750_2026-06-05.jsonl`;
- `experiments/gan2026_validation_test_gap_matrix_v0_validation750_2026-06-05.md`;
- authorized aggregate-only test companion if possible.

Decision output:

- accept H2 if component-owner strata show materially different gaps within
  comparable hidden families;
- identify the top three first-failure owners for validation development work.

## Phase 3: Component-Specific Hypothesis Tests

Goal: test mechanisms with controlled ablations, not broad reruns.

Each experiment must declare:

- hypothesis id;
- component owner under test;
- clinical subproblem;
- surface;
- comparator;
- expected mechanism;
- promotion/rejection rule;
- allowed inspection level.

### 3A: Candidate Generation

Question: does the gold-relevant state enter the candidate set?

Surfaces:

- validation hard slices;
- structured synthetic hard/control panels;
- no-call replay over existing validation750 artifacts.

Metrics:

- gold-relevant candidate exposure;
- unsupported candidate rate;
- metadata completeness;
- exact evidence rate;
- candidate count distribution;
- family-specific recall.

Reject a candidate-generation mechanism if it raises candidate recall only by
adding unsupported or metadata-incomplete candidates that projection cannot
safely use.

### 3B: Evidence Selection

Question: does the model or deterministic selector point to exact supporting
text?

Surfaces:

- validation hard slices;
- paraphrase/minimal-pair panels;
- same-raw-output replay where available.

Metrics:

- exact selected evidence;
- valid source id;
- selected operand completeness;
- changed-row exact evidence;
- evidence-regression count.

Reject evidence-selection claims when exact evidence is missing for changed
rows or when source-near evidence is required but not predeclared.

### 3C: Temporal And Boundary Selection

Question: does the system choose the current clinically relevant state?

Surfaces:

- validation hard slices for current-vs-historical, seizure-free boundary,
  uncertainty, last-event-only, and competing semiologies;
- synthetic/adversarial minimal pairs.

Metrics:

- selected state kind;
- currentness flags;
- seizure-free duration completeness;
- unknown/no-reference boundary correctness;
- first-failure owner.

Reject mechanisms that improve one boundary family by broadening projection in
a way that creates C->W in another boundary family.

### 3D: Projection And Rendering

Question: does deterministic projection or adapter rendering create the gap
after correct evidence is already available?

Surfaces:

- no-call validation replay;
- hard slices with exact selected evidence;
- rendering fixtures and synthetic controls.

Metrics:

- selected-evidence-correct to adapter-wrong;
- adapter-correct to final-wrong;
- projection W->C and C->W;
- benchmark-format-only changes;
- semantic drift family.

Reject broad projection mechanisms that are not family-gated and ablatable.

### 3E: Selective Action And Safety Floor

Question: should the LLM act, abstain, or defer to deterministic rules?

Surfaces:

- validation hard slices;
- saved frozen aggregate test summaries where predeclared;
- calibration/change-only panels.

Metrics:

- changed-label rate;
- changed-label precision;
- W->C;
- C->W;
- fallback rate;
- abstain/review/monitor burden;
- family-specific action rate.

Promote only high-precision selective action. A small safe gain may be useful,
but it should not be mistaken for solving the holdout gap.

## Phase 4: Synthetic And Adversarial Transfer Panels

Goal: directly test template brittleness in a controlled setting.

Panel families:

- current versus historical conflict;
- seizure-free statement after recent count;
- no-reference versus unknown;
- last-event-only versus recurring rate;
- cluster cadence versus events-per-cluster burden;
- diary/log aggregation;
- multiple active semiologies;
- negation/hypothetical frequency;
- medication/status distractors;
- relative-date and elapsed-window arithmetic;
- benchmark-format convention cases.

Implementation steps:

1. Build minimal pairs that preserve the gold clinical fact while changing one
   surface feature: wording, section, order, time anchor, distractor, or
   semiology placement.
2. Add matched controls for every hard case.
3. Run component-stress conditions:
   - deterministic comparator;
   - raw LLM clinical selection;
   - format-only repair;
   - deterministic adapter;
   - projection;
   - safety floor;
   - final policy.
4. Report consistency within pairs, not only accuracy.

Deliverables:

- `experiments/gan2026_validation_test_gap_adversarial_panel_v0_2026-06-05.jsonl`;
- `experiments/gan2026_validation_test_gap_component_stress_v0_2026-06-05.json`;
- unit tests for panel generation invariants.

Decision output:

- accept H7 only if components flip under superficial template changes while
  gold facts remain stable.

## Phase 5: Validation Hard-Slice Experiments

Goal: use validation row-level review to test mechanisms that might transfer.

Implementation steps:

1. Freeze hard-slice definitions from the atlas and component matrix, including:
   - hidden family;
   - baseline correctness;
   - final action;
   - component owner;
   - evidence status;
   - label kind.
2. For each high-leverage hypothesis, build a hard/control panel:
   - hard rows where the mechanism should help;
   - matched controls where it should not act;
   - easy rows to catch broad regressions.
3. Run only component-stress ablations, not new architecture variants.
4. Review validation rows with exact examples and failure owners.

Promotion signal:

- W->C concentrated in the target family;
- C->W near zero or explicitly bounded;
- exact evidence for changed rows;
- no benchmark-format drift hidden as clinical reasoning;
- stable behavior on controls.

Deliverables:

- one report per hypothesis/component pair;
- updated family-indexed component evidence matrix;
- list of rejected mechanisms with reason.

## Phase 6: Frozen Test Generalisation Audit

Goal: measure whether a frozen interpretation transfers, without tuning from
test rows.

Preconditions:

- candidate, component policies, prompts, model ids, score layers, scorer,
  slice definitions, and inspection policy are frozen;
- validation hard-slice and synthetic/adversarial results already explain the
  expected mechanism;
- test readout fields are limited to aggregate and predeclared slices;
- user explicitly authorizes the frozen test audit.

Allowed readouts:

- overall Purist/Pragmatic;
- prediction-bearing coverage and action counts;
- predeclared hidden-family aggregates;
- component-owner aggregate gaps;
- score-layer aggregate ladder if generated without row-level failure review;
- selective-action aggregate W->C/C->W if already computable from frozen
  prediction/gold joins and not used for tuning.

Not allowed:

- inspecting individual locked-test failures for fixes;
- changing rules, prompts, thresholds, gates, repair policy, projection, or
  model choice after the test readout and treating it as the same cycle;
- adding new test-derived slice definitions.

Deliverables:

- frozen audit plan addendum;
- aggregate-only test readout;
- final interpretation report naming supported and unsupported claims.

## Phase 7: Synthesis And Research Control

Goal: convert experiments into decisions.

Implementation steps:

1. Build a hypothesis outcome table:
   - supported;
   - partially supported;
   - rejected;
   - inconclusive due to instrumentation gap.
2. Build a component transfer table:
   - component owner;
   - clinical subproblem;
   - validation behavior;
   - test aggregate or predeclared-slice behavior;
   - synthetic/adversarial mechanism behavior;
   - transfer confidence.
3. Write a first-failure ownership synthesis:
   - which component fails first;
   - whether the failure is candidate absence, wrong evidence, wrong temporal
     choice, projection drift, rendering drift, safety-floor overblocking, or
     benchmark convention.
4. Update project control docs:
   - `PROJECT_STATUS.md`;
   - `experiments/RUN_INDEX.md` or registry if applicable;
   - a durable research synthesis under `docs/research/`.

Decision output:

- choose one of:
  - continue with current architecture and targeted component fixes;
  - narrow the LLM to a specific component role;
  - narrow deterministic rules to comparator/safety-floor use;
  - build a new architecture only because a specific component hypothesis
    failed, not because aggregate F1 is disappointing.

## Implementation Order

1. Write protocol and artifact inventory.
2. Implement `validation_test_gap_matrix_v0` for validation-only saved replay.
3. Add tests for split discipline, provenance, score-layer completeness, and
   component-owner assignment.
4. Produce validation surface map and family/component gap tables.
5. Extend aggregate-only test summaries only under predeclared slice fields.
6. Run component-specific validation hard-slice analyses.
7. Build synthetic/adversarial minimal-pair panels for the highest-leverage
   unresolved hypotheses.
8. Run component-stress ablations over hard/control panels.
9. Freeze a test audit only after the hypotheses, components, and slice
   definitions are stable.
10. Write synthesis and update project status.

## Stop Rules

Stop architecture iteration until all are true:

- the gap matrix exists for validation;
- first-failure owner is known for validation misses;
- component-owner gaps are summarized for authorized test aggregate/slice
  readouts;
- at least three named hypotheses have controlled evidence;
- every proposed new component states which hypothesis it addresses.

Reject or pause a mechanism if:

- it improves validation aggregate without improving target hard slices;
- it cannot identify prediction-bearing ownership;
- it relies on deterministic semantic repair while being described as LLM-owned;
- changed rows lack exact evidence;
- it creates deterministic-correct regressions;
- its apparent benefit is benchmark-format-only.

## Near-Term Work Package

The first implementation sprint should be deliberately boring:

1. Create the protocol and inventory artifacts.
2. Implement the validation-only gap matrix by joining the staged assembly
   component matrix, hidden-family atlas, rules-only comparator, and any saved
   score-layer ladder artifacts.
3. Produce four tables:
   - gap by hidden family;
   - gap by component owner;
   - gap by clinical subproblem;
   - gap by score layer.
4. Select no more than three hypotheses for the next controlled experiments.

The likely first three hypotheses are H2, H4, and H6: component ownership,
projection/rendering drift after evidence selection, and selective-action
transfer. H1 should be checked immediately, but it should not dominate the plan
unless the family concentration is strong.

