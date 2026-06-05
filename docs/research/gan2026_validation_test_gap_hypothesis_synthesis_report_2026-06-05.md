# Gan 2026 Validation-Test Gap Hypothesis Synthesis Report

Date: 2026-06-05

Status: living validation-development synthesis. This report summarizes named
hypotheses tested under `gan2026_split_v1` and should be updated as additional
setup-heavy hypotheses are run.

Claim boundary: no benchmark-comparable claim is authorized. Locked-test
row-level failure inspection remains unauthorized. Test450 evidence in this
program must remain aggregate-only or predeclared-slice-only until a separate
frozen audit is explicitly authorized.

## Executive Interpretation

The first controlled pass supports a narrow interpretation: the current staged
assembly is conservative and preserves the H6 selective-action control arm, but
the H2/H4 validation hard panel did not reveal prediction-bearing W->C gains.
Instead, the strongest actionable finding is action-policy overblocking:
deterministic-correct rows are being routed to nonprediction.

The untagged-nonprediction release candidate is a safe validation-development
patch for that specific action-policy failure. It recovers 19 staged
nonpredictions through deterministic-comparator fallback with 0 observed
release-wrong rows and 37/37 H6 controls preserved. It is not evidence that the
validation-test gap is solved, and it does not authorize holdout use.

The next useful work is not another broad validation run. Move to setup-heavy
hypotheses that explain transfer: first H1 hidden-family mix through
predeclared validation/test slice aggregates, then H3/H7-style candidate
exposure and adversarial panels if H1 does not concentrate the gap.

After the H1 readout, the research priority should be more explicit: stop
optimizing primarily for validation exact-label score. Seizure-free duration and
benchmark-format convention are particular problem areas, and a principled
candidate may accept a validation-score drop if it separates clinical semantics
from benchmark rendering and plausibly transfers better.

## Evidence Base

Primary source artifacts:

- `docs/research/gan2026_validation_test_generalisation_gap_implementation_plan_2026-06-05.md`
- `experiments/gan2026_validation_test_surface_map_v0_2026-06-05.json`
- `experiments/gan2026_validation_test_gap_matrix_v0_validation750_2026-06-05.jsonl`
- `experiments/gan2026_validation_test_gap_hypothesis_selection_v0_2026-06-05.json`
- `experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.json`
- `experiments/gan2026_h2_h4_validation_component_stress_ablation_v0_2026-06-05.json`
- `experiments/gan2026_nonprediction_recovery_audit_v0_2026-06-05.json`
- `experiments/gan2026_untagged_nonprediction_release_candidate_v0_2026-06-05.json`
- `experiments/gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_2026-06-05.json`
- `experiments/gan2026_h1_hidden_family_slice_aggregates_v0_2026-06-05.json`
- `docs/research/gan2026_generalization_first_boundary_and_benchmark_solution_design_2026-06-05.md`
- `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.json`
- `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.json`

## Hypothesis Outcomes

| Hypothesis | Current Status | Tested Surface | Key Result | Interpretation | Recommended Action |
| --- | --- | --- | --- | --- | --- |
| H2 component ownership explains the gap | partially tested; inconclusive for transfer | validation750 gap matrix and H2/H4 component-stress panel | Owner strata differ on validation: deterministic_adapter has 701 rows with 671 correct and 30 incorrect; safety_floor has 49 rows with 7 correct, 8 incorrect, and 34 nonpredictions. The H2/H4 ablation found 0 W->C and 0 C->W on the hard panel. | Component ownership is useful for organizing failures, but the tested no-call ablation did not produce a component fix. The dominant observed issue is nonprediction pressure, not a label-switching win. | Keep owner labels in all future artifacts. Do not promote a new architecture from H2 alone; use H2 as stratification for H1, H3, H7, and future hard panels. |
| H4 evidence transfers but projection/rendering does not | partially tested; not supported as the main actionable mechanism in this pass | validation hard/control panel with evidence/source-id fields | On the 106-row panel, deterministic_comparator had 75 exact-evidence rows; staged_final_policy had the same 75 exact-evidence rows but only 75 scorable rows and 31 nonpredictions. | Exact evidence availability did not translate into final predictions for many hard rows. The observed bottleneck is final action policy rather than evidence exactness alone. | Preserve evidence/source-id fields, but prioritize action-policy and candidate-exposure instrumentation before broad projection changes. |
| H6 selective-action policy transfers better than replacement | supported as a control, not as a full solution | validation750 selective-action context, locked-test aggregate summary, and H2/H4 H6 controls | Selective safety floor: validation750 changed 21 rows with 11 W->C and 0 C->W; locked_test450 aggregate changed 14 rows with 8 W->C and 0 C->W. H2/H4 controls preserved 37/37. | Selective action remains a high-precision safety/control mechanism. It should be used as a guardrail for candidate patches, not treated as solving the aggregate gap. | Keep H6 as the no-regression control arm for setup-heavy hypotheses and any future frozen audit. |
| Action-policy nonprediction recovery, derived from H2/H4/H6 findings | supported for validation-development only | nonprediction recovery audit and assembled candidate artifact | Untagged nonprediction release candidate: 750 rows, 19 release-eligible rows, 19 releases, 0 release-wrong rows, 735 prediction-bearing rows, 697 correct prediction rows, and 37/37 H6 controls preserved. | The candidate safely recovers deterministic-correct staged nonpredictions when no hidden-family tags are present. This is deterministic-comparator fallback, not LLM-owned improvement. | Keep as an auditable assembled validation artifact. Do not run holdout until a separate protocol freezes candidate, slice definitions, and allowed readouts. |
| H1 hidden-family mix explains the aggregate gap | tested; inconclusive | aggregate-only predeclared hidden-family validation/test readout over selective_safety_floor_gate_v0 | Validation proxy was 0.9440 and test proxy was 0.7800. Family gaps were broad: diary/log 0.1702, current-vs-historical 0.1661, competing semiologies 0.1686, rate/denominator 0.1643, seizure-free duration 0.2431, benchmark convention 0.2369. | Hidden-family mix contributes useful stratification but does not cleanly explain the aggregate gap by itself. Family tags overlap heavily, and broad classifier families are high-incidence, so this should not be accepted as a concentrated-family explanation. | Move to H3 candidate-exposure instrumentation and H7 template-brittleness panels, using H1 families as strata rather than as the primary explanation. |
| Generalization-first boundary/convention design | predeclared design pivot | synthesis of H1, RQ10, normalization semantics, and saturated-validation protocol | Seizure-free duration and benchmark-format convention show larger within-family gaps than the aggregate surface. RQ10 shows some rows are benchmark-convention dominated or clinically defensible alternatives rather than ordinary extraction failures. | A lower validation score can be acceptable if it comes from source-grounded boundary states and explicit benchmark rendering instead of validation-fit label switching. | Build typed `seizure_free_boundary_event_v0` and `benchmark_convention_renderer_v0` panels before final-label promotion. |
| H3/H7 boundary and benchmark seed panel | panel contract created; mechanism not yet implemented | synthetic hard/control minimal-pair panel | 12 rows, 6 pairs, 6 clinical-state invariant pairs, 12 exact-evidence rows, 6 `seizure_free_boundary_event_v0` rows, and 6 `benchmark_convention_renderer_v0` rows. | The next mechanism now has an explicit contract for candidate exposure, boundary state, renderer transparency, and pair consistency. This is mechanism scaffolding, not performance evidence. | Implement typed boundary and benchmark-renderer contract tests against the panel before connecting either mechanism to final-label policy. |
| H3/H7 boundary and benchmark contract smoke | mechanism contract passed; final policy disconnected | synthetic seed-panel replay | 12 rows, 6 pairs, 6 clinical-state invariant pairs, 12 contract-matched rows, 12 exact-evidence rows, 6 boundary rows, 6 renderer rows, and final-label policy connected = false. | The first executable mechanism separates `clinical_final_state` from `gan_rendered_label` while preserving exact evidence and pair consistency. It remains synthetic mechanism evidence only. | Broaden the mechanism contract with generated hard/control cases, then port stable typed fields to validation hard-slice panels. |

## Detailed Results

### H2/H4 Component-Stress Pass

The selected experiment combined H2 component ownership and H4
evidence-versus-projection/rendering, using H6 controls. It was validation-only
and made no live model calls.

Key accounting:

- Panel rows: 106.
- Hard rows: 69.
- Controls: 37.
- Deterministic comparator condition: 106 scorable rows, 53 correct, 75 exact
  evidence rows.
- Staged final policy condition: 75 scorable rows, 37 correct, 31
  nonpredictions, 75 exact evidence rows.
- Final policy changes versus comparator: 31.
- W->C: 0.
- C->W: 0.
- C->nonprediction: 16.
- W->nonprediction: 15.
- H6 controls preserved: 37/37.

Interpretation: the staged policy is conservative and avoids label regressions
on this panel, but it does not recover hard rows. It often converts comparator
predictions into nonpredictions. This makes action eligibility and fallback
ownership the immediate mechanism to audit.

### Nonprediction Recovery And Assembled Candidate

The follow-up nonprediction recovery audit evaluated release lanes using
validation-only component-matrix fields. The selected lane was
`untagged_nonprediction`: staged nonpredictions with no hidden-family tags,
released through deterministic-comparator fallback.

Assembled candidate accounting:

- Rows: 750.
- Original nonpredictions: 34.
- Release-eligible rows: 19.
- Release-applied rows: 19.
- Candidate prediction-bearing rows: 735.
- Candidate correct prediction rows: 697.
- Release-correct rows: 19.
- Release-wrong rows: 0.
- H6 controls: 37.
- H6 regressions: 0.
- Locked-test row-level artifacts used: 0.
- Holdout authorized: false.

Component ownership:

- deterministic_adapter: 701 rows.
- deterministic_comparator_fallback: 19 rows.
- safety_floor: 30 rows.

Interpretation: this is a clean validation-cycle patch for one specific
overblocking lane. It should be treated as deterministic fallback ownership and
reported separately from LLM or projection mechanisms.

### H1 Hidden-Family Slice Aggregates

The H1 pass generated an aggregate-only validation/test readout for
`selective_safety_floor_gate_v0`. It writes no locked-test row ids, clinical
text, raw model outputs, or row-level failure records.

Surface accounting:

- Validation rows: 750.
- Validation correct rows: 708.
- Validation proxy: 0.9440.
- Test rows: 450.
- Test correct rows: 351.
- Test proxy: 0.7800.
- Families emitted: 10.
- Locked-test row-level artifacts written: 0.

Top family gaps by test-weighted contribution:

| Family | Validation rows | Validation proxy | Test rows | Test proxy | Gap | Contribution |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `diary_or_log_aggregation` | 727 | 0.9477 | 436 | 0.7775 | 0.1702 | 0.1649 |
| `current_vs_historical` | 739 | 0.9432 | 444 | 0.7770 | 0.1661 | 0.1639 |
| `competing_semiologies` | 640 | 0.9406 | 386 | 0.7720 | 0.1686 | 0.1446 |
| `rate_bucket_or_denominator` | 595 | 0.9395 | 347 | 0.7752 | 0.1643 | 0.1267 |
| `cluster_burden` | 420 | 0.9333 | 264 | 0.7765 | 0.1568 | 0.0920 |
| `uncertainty_or_ambiguity` | 282 | 0.9255 | 178 | 0.7247 | 0.2008 | 0.0794 |
| `seizure_free_duration` | 202 | 0.8960 | 121 | 0.6529 | 0.2431 | 0.0654 |
| `benchmark_format_convention` | 83 | 0.9036 | 48 | 0.6667 | 0.2369 | 0.0253 |

Decision: `h1_inconclusive_gap_not_strongly_concentrated`.

Interpretation: H1 should remain a stratification hypothesis, not the primary
explanation. The broad, overlapping family classifier shows that many families
move together with the aggregate gap. The sharper signal is that seizure-free
duration, benchmark-format convention, and uncertainty slices have larger
within-family gaps, but their denominators are smaller than the high-incidence
families. Those sharper families are good H3/H7 panel seeds.

## Recommended Action

1. Keep the assembled untagged-nonprediction artifact as the current auditable
   validation-development assembly record.
2. Do not authorize holdout use yet.
3. Treat H1 as inconclusive for primary explanation but decisive for research
   prioritization: seizure-free duration and benchmark-format convention need
   targeted mechanism work.
4. Stop optimizing primarily for validation exact-label score. Accept validation
   loss only when it follows a predeclared, source-grounded clinical mechanism
   that separates benchmark rendering from clinical semantic selection.
5. Use H6 as a required no-regression control for every next hypothesis.
6. Move next to H3 candidate-generation recall instrumentation and H7
   adversarial/minimal-pair panels, prioritizing seizure-free duration and
   benchmark-format convention before broader family coverage.

## Next Update: H3/H7 Work Package

H3 question: does candidate-generation recall fail to transfer?

Required setup:

- Define candidate-exposure fields over validation hard slices and synthetic
  controls: gold-relevant candidate present, supported candidate present,
  unsupported candidate rate, metadata completeness, and exact evidence.
- Use H1 sharper families as strata, especially seizure-free duration,
  benchmark-format convention, uncertainty, cluster burden, and diary/log
  aggregation.
- Keep locked-test H3 work aggregate/predeclared-slice only unless a frozen
  audit is separately authorized.
- Add typed boundary fields for seizure-free cases: asserted seizure-free
  interval, last-event-only, conditional/trigger-only, non-epileptic current
  events, residual active semiology, duration evidence, and projection policy.

H7 question: does template brittleness, not clinical complexity, cause the gap?

- Build minimal pairs that preserve the gold fact while changing wording,
  section/order, distractors, uncertainty, or semiology placement.
- Report pair consistency, not only accuracy.
- Do not use synthetic panels as benchmark evidence.
- Include benchmark-convention renderer cases that separate clinical final state
  from Gan-rendered label, especially unresolved clusters, vague `multiple`
  labels, unknown/no-reference sentinel collapse, and last-event-only policy.

This report should be updated after each H3/H7 artifact with:

- a new hypothesis outcome row;
- component and family-specific candidate-exposure or pair-consistency tables;
- an explicit decision: promote to a validation hard/control panel, revise the
  mechanism, or reject the hypothesis branch.

### H3/H7 Seed Panel v0

Artifact:

- `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.json`
- `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.jsonl`
- `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.md`

Panel contract:

- Rows: 12.
- Minimal pairs: 6.
- Clinical-state invariant pairs: 6.
- Exact evidence rows: 12.
- Boundary rows: 6.
- Renderer rows: 6.
- Hard rows: 10.
- Control rows: 2.

Target mechanisms:

- `seizure_free_boundary_event_v0`: asserted seizure-free interval,
  last-event-only, and residual-active-semiology cases.
- `benchmark_convention_renderer_v0`: unresolved cluster burden,
  unknown/no-reference sentinel behavior, and vague multiple-frequency cases.

Decision: `ready_for_boundary_renderer_contract_tests`.

Interpretation: this panel creates the next contract surface. It should not be
used as a final-label score target. The next useful step is to implement typed
boundary and benchmark-renderer contract tests that expose clinical state and
Gan-rendered label separately.

### H3/H7 Boundary/Benchmark Contract Smoke v0

Artifact:

- `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.json`
- `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.jsonl`
- `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.md`

Contract accounting:

- Rows: 12.
- Minimal pairs: 6.
- Clinical-state invariant pairs: 6.
- Contract-matched rows: 12.
- Exact evidence rows: 12.
- Target mechanisms: 6 `seizure_free_boundary_event_v0`, 6
  `benchmark_convention_renderer_v0`.
- Benchmark rules: 2 `gan_cluster_multiple_per_cluster`, 2
  `gan_unknown_sentinel`, 2 `gan_vague_multiple_frequency`, and 6
  `none_boundary_state_only`.
- Final-label policy connected: false.

Decision: `boundary_renderer_contract_passed`.

Interpretation: this is the first executable mechanism proof for the pivot. It
does not claim validation or holdout performance. Its value is that the typed
boundary classifier and benchmark renderer now expose separate fields for
clinical state and Gan-rendered label, with exact evidence and pair consistency
preserved.

## Update Log

- 2026-06-05: Created initial synthesis from H2/H4/H6 selection, H2/H4
  component-stress ablation, nonprediction recovery audit, and
  `untagged_nonprediction_release_candidate_v0_assembled_candidate`.
- 2026-06-05: Added H1 aggregate-only hidden-family slice readout. H1 remains
  inconclusive as a primary gap explanation; use the family table as strata for
  H3 candidate exposure and H7 template-brittleness work.
- 2026-06-05: Added the generalization-first boundary/convention design pivot:
  a lower validation exact-label score is acceptable only when a predeclared,
  source-grounded mechanism separates seizure-free boundary semantics from
  benchmark-format rendering and is tested on hard/control panels.
- 2026-06-05: Added and broadened `boundary_benchmark_seed_panel_v0`, a 36-row
  H3/H7 synthetic hard/control panel for typed seizure-free boundary events and
  explicit benchmark rendering. It has 18 invariant pairs and 36/36 exact
  evidence rows.
- 2026-06-05: Added and broadened `boundary_benchmark_contract_v0`, a no-call
  mechanism contract smoke over the seed panel. It passed all 36 rows while
  keeping final-label policy disconnected.
- 2026-06-05: Added `boundary_benchmark_validation_panel_v0`, a validation-only
  hard-slice panel that ports stable boundary/renderer typed fields without raw
  note text. It selected 30 rows, 19 boundary rows, 11 renderer rows, 30/30
  exact-evidence rows, and no final-label policy connection.
