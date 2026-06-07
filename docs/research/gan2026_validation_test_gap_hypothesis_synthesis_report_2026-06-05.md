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

The H5 semantic-repair gap test makes the core failure sharper. Much of the
apparent validation performance is coming from deterministic semantic repair
and contract rules, not from a model-owned clinical decision that transfers.
Those repair rules are too tightly attuned to validation examples. Validation
repair gain is 0.2320, locked-test aggregate repair gain is only 0.0333, and the
full-repair validation-test gap is 0.1747. This is a semantic-repair policy
failure, not merely an ordinary candidate miss.

After the H1 and H5 readouts, the research priority should be more explicit:
stop optimizing primarily for validation exact-label score. Seizure-free
duration, benchmark-format convention, and broad semantic repair are particular
problem areas. The next repair set should be designed for generalization first,
with source-grounded clinical semantics, explicit portability categories, and a
willingness to accept a lower validation score if that removes
validation-example-tuned behavior.

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
- `experiments/gan2026_h5_semantic_repair_gap_test_v0_2026-06-05.json`
- `experiments/gan2026_h5_repair_inventory_v0_2026-06-05.json`
- `experiments/gan2026_h5_repair_family_ablation_v0_2026-06-05.json`
- `experiments/gan2026_h5_repair_policy_v1_reparse_validation250_2026-06-05.json`
- `experiments/gan2026_h5_semantic_kind_transformations_policy_v1_validation250_2026-06-05.csv`
- `docs/research/gan2026_generalization_first_boundary_and_benchmark_solution_design_2026-06-05.md`
- `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.json`
- `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.json`
- `experiments/gan2026_boundary_benchmark_validation_panel_v0_2026-06-05.json`
- `experiments/gan2026_boundary_benchmark_validation_contract_v0_2026-06-05.json`
- `experiments/gan2026_boundary_benchmark_candidate_assembly_v0_2026-06-05.json`
- `experiments/gan2026_h3_h7_full_boundary_benchmark_test_v0_2026-06-05.json`
- `experiments/gan2026_h9_action_policy_gap_v0_2026-06-05.json`
- `experiments/gan2026_h10_runtime_variance_audit_v0_2026-06-05.json`
- `experiments/gan2026_h10_fresh_live_variability_audit_v0_2026-06-05.json`

## Hypothesis Outcomes

| Hypothesis | Current Status | Tested Surface | Key Result | Interpretation | Recommended Action |
| --- | --- | --- | --- | --- | --- |
| H2 component ownership explains the gap | partially tested; inconclusive for transfer | validation750 gap matrix and H2/H4 component-stress panel | Owner strata differ on validation: deterministic_adapter has 701 rows with 671 correct and 30 incorrect; safety_floor has 49 rows with 7 correct, 8 incorrect, and 34 nonpredictions. The H2/H4 ablation found 0 W->C and 0 C->W on the hard panel. | Component ownership is useful for organizing failures, but the tested no-call ablation did not produce a component fix. The dominant observed issue is nonprediction pressure, not a label-switching win. | Keep owner labels in all future artifacts. Do not promote a new architecture from H2 alone; use H2 as stratification for H1, H3, H7, and future hard panels. |
| H4 evidence transfers but projection/rendering does not | partially tested; not supported as the main actionable mechanism in this pass | validation hard/control panel with evidence/source-id fields | On the 106-row panel, deterministic_comparator had 75 exact-evidence rows; staged_final_policy had the same 75 exact-evidence rows but only 75 scorable rows and 31 nonpredictions. | Exact evidence availability did not translate into final predictions for many hard rows. The observed bottleneck is final action policy rather than evidence exactness alone. | Preserve evidence/source-id fields, but prioritize action-policy and candidate-exposure instrumentation before broad projection changes. |
| H6 selective-action policy transfers better than replacement | supported as a control, not as a full solution | validation750 selective-action context, locked-test aggregate summary, and H2/H4 H6 controls | Selective safety floor: validation750 changed 21 rows with 11 W->C and 0 C->W; locked_test450 aggregate changed 14 rows with 8 W->C and 0 C->W. H2/H4 controls preserved 37/37. | Selective action remains a high-precision safety/control mechanism. It should be used as a guardrail for candidate patches, not treated as solving the aggregate gap. | Keep H6 as the no-regression control arm for setup-heavy hypotheses and any future frozen audit. |
| Action-policy nonprediction recovery, derived from H2/H4/H6 findings | supported for validation-development only | nonprediction recovery audit and assembled candidate artifact | Untagged nonprediction release candidate: 750 rows, 19 release-eligible rows, 19 releases, 0 release-wrong rows, 735 prediction-bearing rows, 697 correct prediction rows, and 37/37 H6 controls preserved. | The candidate safely recovers deterministic-correct staged nonpredictions when no hidden-family tags are present. This is deterministic-comparator fallback, not LLM-owned improvement. | Keep as an auditable assembled validation artifact. Do not run holdout until a separate protocol freezes candidate, slice definitions, and allowed readouts. |
| H1 hidden-family mix explains the aggregate gap | tested; inconclusive | aggregate-only predeclared hidden-family validation/test readout over selective_safety_floor_gate_v0 | Validation proxy was 0.9440 and test proxy was 0.7800. Family gaps were broad: diary/log 0.1702, current-vs-historical 0.1661, competing semiologies 0.1686, rate/denominator 0.1643, seizure-free duration 0.2431, benchmark convention 0.2369. | Hidden-family mix contributes useful stratification but does not cleanly explain the aggregate gap by itself. Family tags overlap heavily, and broad classifier families are high-incidence, so this should not be accepted as a concentrated-family explanation. | Move to H3 candidate-exposure instrumentation and H7 template-brittleness panels, using H1 families as strata rather than as the primary explanation. |
| H5 deterministic semantic repair masks LLM weakness on validation | partially supported; hypothesis wording revised; policy failure identified | same-output validation repair ladder plus aggregate-only validation/test few-shot readouts | Same-output validation ladder: raw model-selected label 0.7520, format-only repair 0.7520, selected-evidence arithmetic 0.8760, benchmark-aligned adapter 0.8160. Validation repair gain is 0.2320, locked-test aggregate repair gain is 0.0333, and repair-gain validation minus test is 0.1987. Locked-test row-level artifacts used: 0. | The important signal is not that raw LLM has a larger validation-test gap than full repair. It does not. The signal is that validation performance is heavily carried by deterministic semantic repair and contract rules that fail to transfer. This should be treated as a semantic-repair policy failure: we designed rules too precisely around examples we had seen. | Freeze validation-attuned semantic repair expansion. Run a complete semantic-repair policy review. Redesign repair families for portability, source grounding, ablation visibility, and acceptable validation-score decline before any new holdout-facing candidate. |
| H5 repair inventory and same-output family ablation | first review pass complete; policy bounds still needed | validation-development static taxonomy plus saved same-output H5 ladder | Inventory found 6 repair families: 1 format-only family, 5 semantic families, and 4 review-required or quarantine-required families. Same-output family ablation keeps format-only repair allowed; selected-evidence arithmetic has 57 changed rows, 32 W->C, 1 C->W, and 16 semantic-kind transitions, so it is `revise_or_bound`; benchmark convention rendering has 28 changed rows, 16 W->C, 0 C->W, and 15 semantic-kind transitions, so it remains `review_required`. | The review confirms H5 is not just a metric story. Format-only cleanup can stay, but the prediction-bearing repair gains are semantic and must be bounded before another candidate assembly. Benchmark rendering cannot be counted as clinical extraction unless clinical-state preservation is shown separately. | Write explicit repair-policy bounds before boundary/renderer expansion: allow format-only, bound selected-evidence arithmetic with C->W controls, and keep benchmark rendering separated from clinical-state selection. |
| H5 repair policy v1 | validation-development no-call reparse complete | saved raw labels and selected evidence from validation250, reparsed under bounded repair policy | Policy v1 removes broad frequency-to-no-reference demotion, maps per-hour rates to `multiple per day`, keeps vague frequency words as unresolved-multiple labels, and preserves cluster frequency content. Benchmark-aligned replay improves from 204/250 to 213/250 Purist-correct rows, with 25 W->C, 0 C->W, and 12 semantic-kind transitions. No `frequency->no_reference` transitions remain; one bounded `frequency->unknown` case remains for an unquantified seizure phrase with gold `unknown`. | This supports the user's policy read: the unsafe part was broad sentinel demotion, not all benchmark rendering. The remaining semantic transitions are mostly frequency-to-unresolved-multiple renderer choices, which should still be reported separately from clinical selection. | Use v1 as the current bounded repair policy for the next validation diagnostic. Do not restore broad frequency-to-sentinel repair. |
| H9 abstention/review policy hides different failure modes by split | partially supported; not primary gap explanation | validation gap matrix plus aggregate-only locked-test nonprediction selector readout | Validation750 has 34 nonprediction/review rows: 26 abstain, 8 human review, rate 0.0453. All are safety-floor-owned; 19 block deterministic-correct labels and 15 block deterministic-wrong labels. The aggregate locked-test selector readout has 1/450 nonprediction row, rate 0.0022, with no row-level test failure artifacts written. | Action policy is not neutral on validation and does hide both overblocking and blocked-miss pressure, but the locked-test aggregate surface has much lower nonprediction burden while the accuracy gap remains large. H9 is therefore an action-policy shift/control finding, not the main explanation for the validation-test gap. | Keep H9 fields in future frozen audit protocols as aggregate owner/family action summaries. Do not prioritize action-policy widening over H3/H7/H8 mechanism work. |
| Generalization-first boundary/convention design | predeclared design pivot | synthesis of H1, RQ10, normalization semantics, and saturated-validation protocol | Seizure-free duration and benchmark-format convention show larger within-family gaps than the aggregate surface. RQ10 shows some rows are benchmark-convention dominated or clinically defensible alternatives rather than ordinary extraction failures. | A lower validation score can be acceptable if it comes from source-grounded boundary states and explicit benchmark rendering instead of validation-fit label switching. | Build typed `seizure_free_boundary_event_v0` and `benchmark_convention_renderer_v0` panels before final-label promotion. |
| H3/H7 boundary and benchmark seed panel | panel contract created and broadened | synthetic hard/control minimal-pair panel | 36 rows, 18 pairs, 18 clinical-state invariant pairs, 36 exact-evidence rows, 20 `seizure_free_boundary_event_v0` rows, and 16 `benchmark_convention_renderer_v0` rows. | The next mechanism has an explicit contract for candidate exposure, boundary state, renderer transparency, and pair consistency. This is mechanism scaffolding, not performance evidence. | Keep the synthetic panel as a regression/control surface; use validation hard slices for source-backed mechanism pressure. |
| H3/H7 boundary and benchmark contract smoke | mechanism contract passed; final policy disconnected | synthetic seed-panel replay | 36 rows, 18 pairs, 18 clinical-state invariant pairs, 36 contract-matched rows, 36 exact-evidence rows, 20 boundary rows, 16 renderer rows, and final-label policy connected = false. | The executable mechanism separates `clinical_final_state` from `gan_rendered_label` while preserving exact evidence and pair consistency. It remains synthetic mechanism evidence only. | Port stable typed fields to validation hard-slice panels and run a validation contract smoke before candidate assembly. |
| H3/H7 boundary and benchmark validation panel | validation hard-slice panel created; final policy disconnected | validation-only hard/control typed-field panel | 30 validation rows, 22 hard rows, 8 controls, 19 boundary rows, 11 renderer rows, 30/30 exact-evidence rows, and no note text written to artifacts. | Stable typed boundary/renderer fields can be represented over real validation slices without leaking note text or connecting to final-label policy. | Run a validation typed-field contract smoke before any candidate assembly or holdout-facing protocol. |
| H3/H7 boundary and benchmark validation contract smoke | validation mechanism contract passed; final policy disconnected | validation panel typed-field replay | 30 rows, 22 hard rows, 8 controls, 30/30 contract-matched rows, 30/30 exact-evidence rows, 0 source-note-text rows, 19 boundary rows, 11 renderer rows, and final-label policy connected = false. | This is the first source-backed validation mechanism control for the boundary/renderer pivot. It supports transparency and exact-evidence carry-through, but remains validation-development evidence only and does not authorize candidate assembly or holdout use. | Decide whether to connect the typed fields through a validation-only candidate assembly protocol or build a richer structured event representation with explicit projection ownership. |
| H3/H7 boundary and benchmark candidate assembly | diagnostic only; architecture chosen but not promotion-ready | validation-only typed-candidate bridge over current assembled candidate | 30 candidate rows, 30 selected prediction-bearing rows, 6 W->C, 1 C->W, 30/30 exact-evidence rows, parse-ok plus exact-evidence rate 1.0000, 0 source-note-text rows, and final-label policy connected = false. Gate failures: coverage below 150 and W->C below 60. | The next architecture should start as a shallow typed-candidate-contract layer, not an immediate richer event rewrite. However, this panel is undercovered and has one validation C->W row, so it remains diagnostic and cannot authorize holdout or final-label promotion. | Expand validation hard/control coverage and audit the C->W row on validation only; if coverage or W->C remains insufficient, move to richer structured events with explicit projection ownership. |
| H3/H7/H8 full boundary/benchmark test | H3 rejected for current typed layer; H7 supported on pair panel; H8 partially supported on validation panel | all eligible validation boundary/benchmark rows plus synthetic minimal-pair component comparison | Validation all-eligible contract rows: 36/36 candidate-present, 36/36 exact evidence, 0 unsupported candidates, 36/36 metadata-complete. Validation transitions were 6 W->C, 1 C->W, and 29 C->C, failing exposure >=150 and W->C >=60 gates. Synthetic pairs: typed mechanism was consistent on 18/18 pairs; deterministic comparator flipped on 4/18 pairs. H8 benchmark-convention rows: 11/11 selected, 11/11 clinical/rendering separated, all C->C, with 7 vague-multiple, 3 cluster-multiple-per-cluster, and 1 unknown-sentinel rows. | H3 is no longer merely untested: candidate exposure is clean but too small and too low-yield for the current shallow layer. H7 is supported as deterministic template brittleness on the predeclared synthetic pair panel. H8 has validation-development support that benchmark conventions can be explicitly separated from clinical state, but this does not prove the locked-test transfer portion of H8. | Do not promote the shallow typed layer or run holdout. Use H7/H8 as evidence to move toward a richer structured event representation with explicit projection ownership, broader benchmark-convention coverage, and H6 no-regression controls. |
| H10 model/runtime variance is being mistaken for generalisation gap | tested on fresh uncached prefix; supported for byte-level raw JSON variance, not final-policy variance on prefix | two uncached validation live replicates over the same first 20 completed validation rows; cache disabled and no reused outputs | Run A completed 25 rows; Run B was interrupted after 20 completed rows because the final block hung. On the 20 matched rows, `reused_llm_candidate_output` and `reused_adjudicator_output` were 0 in both runs, with 0 call failures. Byte-level raw JSON strings differed on 19/20 rows for `llm_candidate_raw_output`, `adjudicator_raw_output`, and `raw_output`; many differences were rationale/source/evidence/formatting changes with the same normalized label. Scorer-visible labels changed on 3/20 LLM-candidate rows, 1/20 raw-adjudicator rows, and 0/20 final `hybrid_adjudicator_with_adapters` rows. | The cached replay audit was only a same-output provenance control. Fresh uncached calls show substantial byte/string-level raw runtime variability, but most changes were not label-level changes, and the current deterministic adapter/final-policy layer absorbed them on this 20-row prefix. H10 is therefore plausible as a raw-output phenomenon but not yet shown to explain the validation-test gap. | Repeat with explicit request timeouts and a predeclared larger validation sample before making a full-gap claim. Report raw JSON variance, normalized/scorer-visible label variance, and adapter/final-policy variance as separate quantities. |

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

### H5 Semantic Repair Policy Failure

The H5 readout tested whether deterministic semantic repair is masking weak LLM
behavior on validation. It used a same-output validation repair ladder and
aggregate-only validation/test few-shot readouts. It made no live model calls
and used no locked-test row-level artifacts.

Artifact:

- `experiments/gan2026_h5_semantic_repair_gap_test_v0_2026-06-05.json`
- `experiments/gan2026_h5_semantic_repair_gap_test_v0_2026-06-05.md`

Same-output validation ladder:

| Layer | Purist proxy | Changed from raw | Raw W->C | Raw C->W | Owner |
| --- | ---: | ---: | ---: | ---: | --- |
| `raw_model_selected_label` | 0.7520 | 0 | 0 | 0 | LLM |
| `format_only_repair` | 0.7520 | 7 | 0 | 0 | LLM |
| `selected_evidence_arithmetic_only` | 0.8760 | 57 | 32 | 1 | LLM-selected evidence plus deterministic arithmetic |
| `benchmark_aligned_adapter` | 0.8160 | 28 | 16 | 0 | Deterministic benchmark renderer |

Validation-test repair-gain accounting:

| Surface | Raw/base proxy | Full repair proxy | Repair gain | Rows |
| --- | ---: | ---: | ---: | ---: |
| Validation750 | 0.7360 | 0.9680 | 0.2320 | 750 |
| Locked test450 | 0.7600 | 0.7933 | 0.0333 | 450 |

Additional accounting:

- Raw validation-test gap: -0.0240.
- Full-repair validation-test gap: 0.1747.
- Repair-gain validation minus test: 0.1987.
- Locked-test row-level artifacts used: 0.

Decision: `h5_partially_supported_revise_and_review_semantic_repair_policy`.

Interpretation: H5 is supported in the narrow and more worrying sense that
validation performance is being propped up by deterministic semantic repair.
The original H5 signal should be revised: the raw/base layer does not have a
larger validation-test gap than full repair. Instead, the repair layer creates
most of the validation lift and that lift barely transfers to the aggregate
locked-test readout. This means the repair policy became too
validation-example-attuned.

This should be treated as a process failure. We should have caught it much
earlier by requiring every semantic repair family to declare its portability
category, target mechanism, allowed clinical transformation, negative controls,
and same-output validation/test aggregate behavior before it could contribute
to headline validation performance. Repair rules that precisely match examples
we have reviewed are not generalizable semantic policy; they are
validation-specific patches unless proven otherwise.

Required repair-policy review:

1. Inventory every deterministic semantic repair family that can change
   selected event, semantic kind, sentinel state, rate denominator, seizure-free
   boundary, cluster interpretation, benchmark convention, or Purist/Pragmatic
   category.
2. Classify each repair as `general`, `clinical_epilepsy`,
   `seizure_frequency`, `gan2026_specific`, or `benchmark_format`, and reject
   any family whose classification depends on individual validation examples.
3. For each family, define a source-grounded mechanism and at least one
   hard/control panel that can falsify it.
4. Require same-output ablations for raw model, format-only repair,
   selected-evidence repair, semantic repair, benchmark rendering, and final
   policy before any repair family contributes to promoted metrics.
5. Explicitly allow validation exact-label performance to decline when a rule
   is removed or narrowed because it is not portable. A lower validation score
   is acceptable if the remaining repair policy is more clinically principled
   and plausibly transferable.
6. Do not add new semantic repair rules from validation row review unless the
   rule is first expressed as a general mechanism and tested against controls
   that were not used to design it.

First review pass:

- `h5_repair_inventory_v0` inventories 6 repair families: 1 format-only family,
  5 semantic families, and 4 review-required or quarantine-required families.
- `h5_repair_family_ablation_v0` interprets saved same-output ladder transitions
  by family. Format-only repair remains `keep_allowed`. Selected-evidence
  arithmetic is `revise_or_bound` because it has 32 W->C but 1 C->W and 16
  semantic-kind transitions. Benchmark convention rendering remains
  `review_required` because it has 16 W->C and 0 C->W but still owns semantic
  kind plus Purist/Pragmatic category transitions.
- Decision: resolve explicit repair-policy bounds before another
  prediction-bearing boundary/renderer candidate assembly.

Repair policy v1:

- Broad `frequency->no seizure frequency reference` repair is removed.
- Per-hour rates render as `multiple per day`.
- Vague frequency words render as unresolved-multiple labels rather than
  sentinels.
- Cluster context preserves frequency content instead of falling to `unknown`.
- Validation250 no-call reparse: benchmark-aligned Purist-correct rows increase
  from 204 to 213; W->C increases from 16 to 25; C->W remains 0; semantic-kind
  transitions fall from 15 to 12; `frequency->no_reference` transitions fall to
  0.

## Recommended Action

1. Keep the assembled untagged-nonprediction artifact as the current auditable
   validation-development assembly record.
2. Do not authorize holdout use yet.
3. Treat H1 as inconclusive for primary explanation but decisive for research
   prioritization: seizure-free duration and benchmark-format convention need
   targeted mechanism work.
4. Treat H5 as a semantic-repair policy failure. Much of the validation score
   comes from deterministic semantic repair that does not transfer; freeze
   validation-attuned repair expansion and run a complete repair-policy review.
5. Stop optimizing primarily for validation exact-label score. Accept validation
   loss when it follows from removing or narrowing validation-attuned semantic
   repairs, or from a predeclared source-grounded mechanism that separates
   benchmark rendering from clinical semantic selection.
6. Use H6 as a required no-regression control for every next hypothesis.
7. Treat H9 as a partial action-policy finding: validation overblocking is real,
   but it does not explain the locked-test gap on the aggregate readout.
8. Treat H3/H7/H8 boundary/benchmark work as tested for the current shallow
   typed layer: H3 is rejected for promotion because exposure and W->C yield
   are too small, H7 supports deterministic template brittleness on the
   synthetic pair panel, and H8 is partially supported as a validation-only
   benchmark-convention separation mechanism.
9. Treat H10 as unresolved for the full gap but real at the raw-output layer:
   fresh uncached calls differed on 19/20 paired rows, while final
   hybrid-with-adapters labels stayed stable on that prefix.

## H9 Action-Policy Gap

Artifact:

- `experiments/gan2026_h9_action_policy_gap_v0_2026-06-05.json`
- `experiments/gan2026_h9_action_policy_gap_v0_2026-06-05.md`

Claim boundary: this is a no-call validation plus aggregate-only locked-test
readout. It writes no locked-test row ids, clinical text, raw model outputs, or
row-level failure records.

Key accounting:

- Validation rows: 750.
- Validation nonprediction/review rows: 34.
- Validation nonprediction rate: 0.0453.
- Validation action split: 26 abstain, 8 human review.
- Validation action ownership: 34/34 safety-floor-owned; 0/701
  deterministic-adapter rows have nonprediction actions.
- Blocked deterministic-correct validation rows: 19.
- Blocked deterministic-wrong validation rows: 15.
- Locked-test aggregate nonprediction rows: 1/450.
- Locked-test aggregate nonprediction rate: 0.0022.
- Locked-test row-level artifacts written: 0.

Validation action reasons:

| Reason | Rows | Blocked deterministic-correct | Blocked deterministic-wrong |
| --- | ---: | ---: | ---: |
| `trigger_conditioned_frequency` | 24 | 15 | 9 |
| `last_event_boundary` | 8 | 2 | 6 |
| `missing_denominator_anchor` | 2 | 2 | 0 |

High-pressure validation families by nonprediction rate:

| Family | Rows | Nonprediction rows | Rate | Blocked deterministic-wrong |
| --- | ---: | ---: | ---: | ---: |
| `unknown_boundary` | 20 | 11 | 0.5500 | 11 |
| `uncertainty_or_ambiguity` | 24 | 11 | 0.4583 | 11 |
| `seizure_free_duration` | 27 | 10 | 0.3704 | 10 |
| `current_vs_historical` | 25 | 8 | 0.3200 | 8 |
| `competing_semiologies` | 26 | 7 | 0.2692 | 7 |

Decision: `h9_partially_supported_action_policy_shift_not_primary_gap_explanation`.

Interpretation: H9 is supported only in a narrow sense. Validation action policy
does hide different failure modes: some rows are overblocked despite a
deterministic-correct label, and sharper hidden-family slices contain blocked
deterministic misses. But locked-test aggregate nonprediction burden is much
lower than validation burden while the test score gap remains large, so action
policy should remain a guardrail and audit field rather than the lead mechanism
for closing the generalisation gap.

## H3/H7/H8 Completed Work Package

H3 question: does candidate-generation recall fail to transfer?

Decision: rejected for the current shallow typed boundary/renderer layer. The
all-eligible validation surface has clean candidate exposure, exact evidence,
metadata completeness, and no unsupported candidates, but only 36 eligible rows
and 6 W->C rows. This fails the predeclared 150-row coverage and 60 W->C gates.

H7 question: does template brittleness, not clinical complexity, cause the gap?

Decision: supported on the predeclared synthetic minimal-pair panel. The typed
mechanism is pair-consistent on 18/18 clinical-state-invariant pairs, while the
deterministic comparator flips on 4/18 pairs under superficial wording/order
variants.

H8 question: do benchmark-format conventions dominate a subset of the gap?

Decision: partially supported on validation-development evidence. The readout
found 11 benchmark-convention rows, all selected, exact-evidence, and separated
into clinical-state and Gan-rendered-label fields. All 11 were C->C under the
typed layer. This supports the mechanism design, but not the locked-test
transfer claim, because no locked-test row-level readout was used.

Next action: do not promote the shallow layer or run holdout. Use the H7/H8
signals to justify a richer structured event representation with explicit
projection ownership, broader benchmark-convention coverage, and H6
no-regression controls.

### H3/H7 Seed Panel v0

Artifact:

- `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.json`
- `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.jsonl`
- `experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.md`

Panel contract:

- Rows: 36.
- Minimal pairs: 18.
- Clinical-state invariant pairs: 18.
- Exact evidence rows: 36.
- Boundary rows: 20.
- Renderer rows: 16.
- Boundary states: asserted seizure-free interval, last-event-only,
  conditional/trigger-only, non-epileptic current events, residual seizure
  activity, and no-boundary-evidence controls.
- Benchmark renderer rules: unresolved cluster burden, unknown sentinel, vague
  multiple frequency, and non-epileptic seizure-free projection.

Target mechanisms:

- `seizure_free_boundary_event_v0`: asserted seizure-free interval,
  last-event-only, conditional/trigger-only, non-epileptic current events,
  residual-active-semiology cases, and no-boundary controls.
- `benchmark_convention_renderer_v0`: unresolved cluster burden,
  unknown/no-reference sentinel behavior, vague multiple-frequency cases, and
  non-epileptic benchmark projection cases.

Decision: `ready_for_boundary_renderer_contract_tests`.

Interpretation: this panel creates a synthetic regression/control surface. It
should not be used as a final-label score target. Its purpose is to protect
typed boundary states, renderer transparency, exact evidence, and pair
consistency before moving stable fields onto validation hard slices.

### H3/H7 Boundary/Benchmark Contract Smoke v0

Artifact:

- `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.json`
- `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.jsonl`
- `experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.md`

Contract accounting:

- Rows: 36.
- Minimal pairs: 18.
- Clinical-state invariant pairs: 18.
- Contract-matched rows: 36.
- Exact evidence rows: 36.
- Target mechanisms: 20 `seizure_free_boundary_event_v0`, 16
  `benchmark_convention_renderer_v0`.
- Benchmark rules: 6 `gan_cluster_multiple_per_cluster`, 4
  `gan_unknown_sentinel`, 4 `gan_vague_multiple_frequency`, 2
  `gan_non_epileptic_seizure_free_projection`, and 20
  `none_boundary_state_only`.
- Final-label policy connected: false.

Decision: `boundary_renderer_contract_passed`.

Interpretation: this is the executable synthetic mechanism proof for the pivot.
It does not claim validation or holdout performance. Its value is that the
typed boundary classifier and benchmark renderer expose separate fields for
clinical state and Gan-rendered label, with exact evidence and pair consistency
preserved.

### H3/H7 Boundary/Benchmark Validation Panel v0

Artifact:

- `experiments/gan2026_boundary_benchmark_validation_panel_v0_2026-06-05.json`
- `experiments/gan2026_boundary_benchmark_validation_panel_v0_2026-06-05.jsonl`
- `experiments/gan2026_boundary_benchmark_validation_panel_v0_2026-06-05.md`

Panel accounting:

- Rows: 30.
- Hard rows: 22.
- Control rows: 8.
- Boundary rows: 19.
- Renderer rows: 11.
- Exact evidence rows: 30.
- Source-note-text rows written: 0.
- Final-label policy connected: false.

Slices:

| Slice | Rows |
| --- | ---: |
| `asserted_seizure_free_interval` | 8 |
| `cluster_multiple_per_cluster` | 3 |
| `conditional_or_trigger_only` | 3 |
| `last_event_only` | 6 |
| `non_epileptic_current_events` | 2 |
| `unknown_sentinel` | 1 |
| `vague_multiple_frequency` | 7 |

Decision: `ready_for_boundary_renderer_validation_contract`.

Interpretation: this panel ports only stable typed fields from the synthetic
mechanism design onto real validation hard/control slices. It demonstrates that
the boundary/renderer work can be represented without storing raw note text in
artifacts and without connecting to final-label policy.

### H3/H7 Boundary/Benchmark Validation Contract Smoke v0

Artifact:

- `experiments/gan2026_boundary_benchmark_validation_contract_v0_2026-06-05.json`
- `experiments/gan2026_boundary_benchmark_validation_contract_v0_2026-06-05.jsonl`
- `experiments/gan2026_boundary_benchmark_validation_contract_v0_2026-06-05.md`

Contract accounting:

- Rows: 30.
- Hard rows: 22.
- Control rows: 8.
- Contract-matched rows: 30.
- Exact evidence rows: 30.
- Source-note-text rows: 0.
- Target mechanisms: 19 `seizure_free_boundary_event_v0`, 11
  `benchmark_convention_renderer_v0`.
- Benchmark rules: 3 `gan_cluster_multiple_per_cluster`, 1
  `gan_unknown_sentinel`, 7 `gan_vague_multiple_frequency`, and 19
  `none_boundary_state_only`.
- Final-label policy connected: false.

Decision: `boundary_renderer_validation_contract_passed`.

Interpretation: this is the first validation-development mechanism control for
the H3/H7 boundary/renderer pivot. It checks typed-field classification,
exact-evidence carry-through, renderer transparency, absence of source note text
in artifacts, and disconnection from final-label policy. It does not authorize
candidate assembly or holdout use. The next decision is architectural: connect
the typed boundary/renderer fields through a validation-only candidate assembly
protocol, or build a richer structured event representation with explicit
projection ownership first.

### H3/H7 Boundary/Benchmark Candidate Assembly v0

Artifact:

- `experiments/gan2026_boundary_benchmark_candidate_assembly_v0_2026-06-05.json`
- `experiments/gan2026_boundary_benchmark_candidate_assembly_v0_2026-06-05.jsonl`
- `experiments/gan2026_boundary_benchmark_candidate_assembly_v0_2026-06-05.md`

Architecture decision:

- Use a shallow typed-candidate-contract layer over the current assembled
  validation candidate.
- Defer a richer structured event representation until this layer either fails
  expansion or cannot explain projection ownership safely.

Candidate accounting:

- Candidate rows: 30.
- Selected prediction-bearing rows: 30.
- W->C rows: 6.
- C->W rows: 1.
- C->W rate: 0.0333.
- Parse-ok plus exact-evidence rows: 30.
- Parse-ok plus exact-evidence rate: 1.0000.
- Source-note-text rows: 0.
- Final-label policy connected: false.
- Holdout authorized: false.
- Locked-test row-level artifacts used: 0.

Gate failures:

- `coverage_below_150`.
- `w_to_c_below_60`.

Decision: `candidate_contract_layer_diagnostic_only`.

Interpretation: the bridge makes candidate exposure and projection ownership
auditable without writing note text or promoting final labels. It is useful as a
validation-development diagnostic, but not as a holdout-facing candidate. The
single C->W row should be audited on validation only before broadening. If an
expanded typed layer remains undercovered or produces unsafe regressions, the
next branch should be a richer structured event representation with explicit
projection ownership.

### H3/H7/H8 Full Boundary/Benchmark Test v0

Artifact:

- `experiments/gan2026_h3_h7_full_boundary_benchmark_test_v0_2026-06-05.json`
- `experiments/gan2026_h3_h7_full_boundary_benchmark_test_v0_2026-06-05.jsonl`
- `experiments/gan2026_h3_h7_full_boundary_benchmark_test_v0_2026-06-05.md`

H3 accounting:

- All eligible validation boundary/benchmark rows: 36.
- Candidate-present rows: 36.
- Exact-evidence rows: 36.
- Unsupported candidate rows: 0.
- Metadata-complete rows: 36.
- Validation transitions: 6 W->C, 1 C->W, and 29 C->C.
- Gate failures: `validation_candidate_exposure_below_150` and
  `validation_w_to_c_below_60`.

Decision: `tested_rejected_for_current_typed_layer`.

Interpretation: H3 is now tested, not merely scaffolded. The typed candidate
layer exposes supported candidates cleanly on the all-eligible validation
surface, but the surface is too small and too low-yield to explain or close the
validation-test gap. This rejects the current shallow typed layer as a
promotable candidate-generation explanation.

H7 accounting:

- Synthetic rows: 36.
- Clinical-state-invariant pairs: 18.
- Typed pair-consistent pairs: 18.
- Deterministic pair-consistent pairs: 14.
- Deterministic flip pairs: 4.
- Typed-correct rows: 36.
- Deterministic-correct rows: 21.

Decision: `tested_supported_for_deterministic_template_brittleness`.

Interpretation: H7 is supported on this predeclared synthetic pair panel. The
typed boundary/renderer mechanism is stable under superficial wording/order
changes, while the deterministic comparator flips on 4/18 pairs. This remains
mechanism evidence, not benchmark evidence, and it does not authorize holdout
use.

H8 accounting:

- Validation benchmark-convention rows: 11.
- Selected prediction-bearing rows: 11.
- Clinical/rendering separated rows: 11.
- H8 transitions: 11 C->C, 0 W->C, 0 C->W.
- Benchmark rules: 7 `gan_vague_multiple_frequency`, 3
  `gan_cluster_multiple_per_cluster`, and 1 `gan_unknown_sentinel`.
- Gate failures: none.
- Locked-test row-level artifacts used: 0.
- Holdout authorized: false.

Decision:
`tested_partial_validation_support_for_benchmark_convention_subset`.

Interpretation: H8 has partial validation-development support. The current
typed layer can keep benchmark-format rendering explicit and separate from
clinical state with exact evidence, but all H8 validation rows are C->C and the
artifact does not test locked-test transfer. H8 should therefore remain a
mechanism-supported but transfer-unproven hypothesis.

### H10 Same-Output Provenance Control v0

Artifact:

- `experiments/gan2026_h10_runtime_variance_audit_v0_2026-06-05.json`
- `experiments/gan2026_h10_runtime_variance_audit_v0_2026-06-05.md`

Protocol boundary:

- No live model calls were made.
- No locked-test row-level failures were inspected.
- Locked-test evidence is limited to the saved aggregate surface map.

Raw-output identity over paired validation750 artifacts:

| Field | Identical rows | Identity rate |
| --- | ---: | ---: |
| `raw_output` | 750 | 1.0000 |
| `llm_candidate_raw_output` | 750 | 1.0000 |
| `adjudicator_raw_output` | 750 | 1.0000 |

Score-layer drift under same saved raw outputs:

| Score layer | Final-label changed | Purist changed | Live accuracy | Replay accuracy |
| --- | ---: | ---: | ---: | ---: |
| `adapter_only_sidecar_from_adjudicator_selection` | 114 | 58 | 0.8920 | 0.9293 |
| `deterministic_top_candidate` | 0 | 0 | 0.9293 | 0.9293 |
| `hybrid_adjudicator_raw` | 69 | 26 | 0.9107 | 0.9240 |
| `hybrid_adjudicator_with_adapters` | 114 | 58 | 0.8920 | 0.9293 |
| `llm_candidate_selector_raw` | 0 | 0 | 0.6646 | 0.6646 |
| `state_graph_projection` | 0 | 0 | 0.8733 | 0.8733 |

Saved surface-map context:

- Paired candidates with validation/test gap: 3.
- Maximum validation-minus-test gap: 0.1747.
- Mean validation-minus-test gap: 0.1713.

Decision: `same_output_provenance_control_only`.

Interpretation: this cached/saved-output comparison does not test live model
variance. It only proves that when the saved raw outputs are held fixed,
downstream parser, adapter, repair, and policy code can still change labels and
correctness. It should be used as an attribution control, not as the H10
decision.

### H10 Fresh Live Variability Audit v0

Artifact:

- `experiments/gan2026_h10_fresh_live_variability_audit_v0_2026-06-05.json`
- `experiments/gan2026_h10_fresh_live_variability_audit_v0_2026-06-05.md`
- `experiments/gan2026_h10_fresh_live_variability_validation25_run_a_2026-06-05.jsonl`
- `experiments/gan2026_h10_fresh_live_variability_validation25_run_b_2026-06-05.jsonl`

Protocol boundary:

- Both runs used `--disable-dspy-cache`.
- No raw-output reuse paths were supplied.
- `reused_llm_candidate_output` and `reused_adjudicator_output` were 0 in both
  runs.
- No locked-test rows or locked-test failures were inspected.
- Run A completed 25 rows. Run B completed 20 rows and was interrupted after a
  hung final block, so the audit compares the 20 matched completed rows.

Raw-output identity over the 20 matched fresh-call rows.
Important distinction: this table compares the full raw JSON strings returned
by the model. A row can be counted as different here even when the parsed
clinical label is unchanged, because rationale wording, selected evidence span,
selected source ids, optional fields, or JSON formatting changed.

| Field | Identical rows | Different rows | Identity rate |
| --- | ---: | ---: | ---: |
| `llm_candidate_raw_output` | 1 | 19 | 0.0500 |
| `adjudicator_raw_output` | 1 | 19 | 0.0500 |
| `raw_output` | 1 | 19 | 0.0500 |

Score-layer drift under fresh uncached calls:

| Score layer | Final-label changed | Purist changed | Run A accuracy | Run B accuracy |
| --- | ---: | ---: | ---: | ---: |
| `adapter_only_sidecar_from_adjudicator_selection` | 0 | 0 | 1.0000 | 1.0000 |
| `deterministic_top_candidate` | 0 | 0 | 1.0000 | 1.0000 |
| `hybrid_adjudicator_raw` | 1 | 1 | 0.9500 | 0.9000 |
| `hybrid_adjudicator_with_adapters` | 0 | 0 | 1.0000 | 1.0000 |
| `llm_candidate_selector_raw` | 3 | 0 | 1.0000 | 1.0000 |
| `state_graph_projection` | 0 | 0 | 0.9500 | 0.9500 |

Decision:
`h10_supported_for_raw_runtime_variance_but_not_final_policy_variance_on_prefix`.

Interpretation: fresh uncached validation calls show substantial byte-level raw
JSON variance: 19/20 paired rows differ at both the LLM-candidate and
adjudicator raw-output layers. Most of that variance is not scorer-visible label
variance. Parsed labels changed on 3/20 LLM-candidate rows and 1/20 raw
adjudicator rows; deterministic adapters and the final hybrid-with-adapters
layer absorbed those changes, with 0 final label changes and 0 Purist-status
changes. H10 is therefore real at the raw string layer, but this prefix does not
show final-policy variance large enough to explain the validation-test gap. A
broader fresh-call audit with explicit request timeouts is needed before
estimating full-gap contribution.

## Implementation Plan

Status: implementation-control plan for turning this synthesis into the next
validation-development cycle. This plan is intentionally narrower than a full
architecture roadmap: it defines what may be built, which evidence can promote
or block it, and which claims remain off limits.

### Scope And Non-Goals

In scope:

- validation-only mechanism work for the hypotheses already supported by this
  report: H5 semantic-repair policy, H7 template brittleness, H8 benchmark
  convention separation, H9 action-policy sidecars, and H10 provenance hygiene;
- controlled component changes inside the Gan 2026 seizure-frequency task;
- source-grounded structured event and projection ownership artifacts;
- synthetic/adversarial panels and validation hard/control panels;
- aggregate-only or predeclared-slice-only locked-test readouts, but only after
  a separate freeze gate and explicit authorization.

Out of scope:

- new broad validation-score optimization;
- whole-pipeline rewrites that mix extraction, repair, projection, verification,
  rendering, and action policy in one experiment;
- locked-test row-level failure inspection;
- benchmark-comparable claims;
- treating deterministic semantic repair, benchmark rendering, or fallback
  release as LLM-owned clinical reasoning.

The controlling implementation question is:

```text
Can the system replace validation-attuned label repair with source-grounded,
auditable clinical-state selection and explicit benchmark rendering, while
preserving safety controls and producing evidence that could plausibly transfer?
```

### Fixed Boundaries

Use these boundaries for every implementation task derived from this report.

| Boundary | Required Rule | Blocks Promotion If Violated |
| --- | --- | --- |
| Split policy | Use `gan2026_split_v1`; validation is the development surface; test is locked. | Any row-level test failure is inspected or used to choose a rule, prompt, threshold, slice, or model. |
| Scorer policy | Report Gan-compatible Purist first; Pragmatic is a side-car for ambiguity. | Candidate success is claimed from a nonstandard scorer without an explicit contract change. |
| Attribution | Classify post-LLM behavior by semantic effect, not module name. | Semantic repair or renderer changes are described as normalization or LLM-owned output. |
| Component isolation | Change one prediction-bearing layer per experiment. | Repair, projection, action policy, model prompt, and scorer all move together. |
| Evidence | Changed clinical-state rows need exact evidence or an explicit evidence-not-applicable reason. | Changed rows lack source ids, exact evidence, parse status, or projection metadata. |
| Final-label connection | Mechanism contracts run disconnected before diagnostic candidate assembly. | A new typed field is wired into final labels before synthetic and validation contract gates pass. |
| Artifact hygiene | Do not write raw source note text into row artifacts unless a protocol explicitly allows it. | Validation artifacts leak note text unnecessarily or locked-test row artifacts are written. |
| Claim language | Use validation-development, diagnostic, bounded component, or frozen local holdout language as appropriate. | The result is described as benchmark-comparable or as solving the gap without frozen evidence. |

### Implementation Guidelines

Prefer small, named mechanisms over broad policy edits. Every new component or
policy should have a versioned name, an explicit owner, and a row-level artifact
schema that can be inspected without guessing where the final label came from.

Assign a portability category before adding or changing deterministic logic:

- `general`: reusable parsing, schema, arithmetic, or evidence bookkeeping.
- `clinical_epilepsy`: epilepsy-domain concepts that are not Gan-specific.
- `seizure_frequency`: frequency, cadence, denominator, interval, cluster, or
  seizure-free logic that generalizes beyond this dataset.
- `gan2026_specific`: behavior needed because of the Gan task construction.
- `benchmark_format`: scorer-facing rendering or sentinel convention.

Use these labels for decision ownership:

- `llm_clinical_selection`: a model selected the clinically relevant state or
  event from available evidence.
- `deterministic_extraction_or_normalization`: source-near parsing, schema
  cleanup, unit spelling, arithmetic over already selected evidence, or
  deterministic candidate construction.
- `deterministic_semantic_repair`: post-selection logic changed semantic kind,
  sentinel state, clinical event, denominator, cluster interpretation, or
  Purist/Pragmatic category.
- `benchmark_renderer`: clinical state was preserved but converted to a
  Gan-facing label or sentinel under a named benchmark policy.
- `action_policy`: abstain, human-review, fallback release, or nonprediction
  policy changed whether a label is emitted.

Every experiment record should include:

- hypothesis ids and mechanism under test;
- split name, split manifest, row counts, and row-selection policy;
- candidate version, control artifact, scorer, and mapping policy;
- raw model output reuse status and cache/live-call status;
- enabled repair families, projection policies, renderer rules, and action
  lanes;
- W->C, C->W, C->C, W->W, nonprediction/review counts, and changed-label
  precision;
- evidence validity, parse validity, source-id validity, metadata completeness,
  and source-note-text artifact count;
- H6 control status and H9 action summary;
- interpretation: promote, reject, revise, or keep diagnostic.

### Workstream A: Control Freeze And Artifact Contract

Purpose: make the current synthesis actionable without moving the denominator.

Implementation tasks:

1. Create or refresh a compact control manifest that names the exact comparator
   artifacts, split manifest, scorer policy, working-tree note, and allowed
   inspection levels.
2. Register the H6 selective-action controls, H9 action-summary fields, and
   H10 provenance fields as mandatory sidecars for every candidate.
3. Add artifact-contract tests or schema checks that fail when an experiment
   lacks hypothesis ids, split manifest, scorer policy, artifact provenance, or
   inspection policy.
4. Define the first post-synthesis control candidate as the latest auditable
   validation assembly, not as a new score target.

Gate to continue:

- all required control artifacts can be named and reproduced by path;
- every planned row read is validation, synthetic, same-output replay, or
  explicitly aggregate/predeclared test;
- no prediction-bearing code change is bundled into the control freeze.

Success indicators:

- one immutable control manifest exists for the next cycle;
- H6, H9, and H10 sidecar fields are reusable across later artifacts;
- a future candidate can be compared without reconstructing provenance from
  narrative notes.

### Workstream B: Semantic Repair Policy Freeze

Purpose: resolve the H5 finding before building new label-changing behavior.
This workstream narrows or disables validation-attuned semantic repair; it does
not introduce a new clinical selection mechanism.

Implementation tasks:

1. Inventory all repair and normalization functions that can change final label
   meaning.
2. Classify each family by portability category and decision ownership.
3. Split repair reporting into a ladder:
   raw model-selected label, format-only repair, selected-evidence arithmetic,
   semantic repair, benchmark rendering, and final action policy.
4. Run one-family-at-a-time same-output validation replays for semantic repair
   families.
5. Promote only repair that is format-preserving or source-grounded under a
   predeclared policy; quarantine broad frequency-to-sentinel demotion and
   validation-example-specific behavior.

Gates:

- no semantic repair family can be promoted without W->C, C->W,
  semantic-kind-transition, and H6-control accounting;
- selected-evidence arithmetic is allowed only when operands were already
  selected and evidence remains exact;
- benchmark convention rendering must be reported separately from clinical
  semantic selection;
- any repair-induced exact-threshold success remains diagnostic until
  same-raw-output attribution is complete.

Success indicators:

- all semantic repair families have owner, portability category, effect, and
  ablation status;
- format-only repair can be separated from label-changing repair in artifacts;
- validation exact-label loss is accepted when it removes validation-attuned
  behavior and improves attribution clarity;
- no future LLM-first claim depends on hidden deterministic semantic repair.

### Workstream C: Structured Clinical State And Projection Ownership

Purpose: replace shallow final-label switching with source-near clinical state,
explicit projection policy, and separate Gan rendering.

Implementation tasks:

1. Define or refine structured state fields for candidate-bearing rows:
   `clinical_event`, `boundary_state`, `selected_frequency_state`,
   `projection_policy`, `clinical_final_state`, `gan_rendered_label`,
   `benchmark_policy_id`, and `benchmark_format_rule_id`.
2. Keep `seizure_free_boundary_event_v0` and
   `benchmark_convention_renderer_v0` as named mechanisms until a new version
   is justified.
3. Build synthetic fixture coverage for seizure-free duration, last-event-only,
   residual seizure activity, non-epileptic current events, cluster burden,
   vague multiple frequency, unknown sentinel, and no-reference sentinel cases.
4. Port only stable typed fields onto validation hard/control panels with final
   label policy disconnected.
5. Connect typed fields to a validation diagnostic assembly only after contract
   tests pass.

Gates:

- synthetic mechanism contract must preserve clinical-state invariant pairs;
- validation panel artifacts must have exact evidence, source-id validity,
  metadata completeness, and zero raw source-note-text rows unless explicitly
  authorized;
- renderer fixtures must show clinical-state preservation before emitting
  benchmark-facing labels;
- no final-label connection is allowed while unsupported candidates or silent
  sentinel collapses remain;
- any C->W outside predeclared benchmark-convention or underdetermined rows
  blocks promotion.

Success indicators:

- typed clinical state and Gan-rendered label can disagree visibly in the
  artifact;
- benchmark-format wins are counted separately from clinical extraction wins;
- last-event-only, seizure-free interval, residual activity, and non-epileptic
  event states do not collapse into one sentinel pathway;
- target hard slices improve or become more interpretable without H6
  regression;
- the mechanism can be promoted, at most, as a bounded component before any
  whole-pipeline claim.

### Workstream D: Robustness And Template-Brittleness Stress Tests

Purpose: make H7 operational. The system should preserve clinical state under
surface paraphrase when the underlying fact is unchanged.

Implementation tasks:

1. Build frozen minimal-pair panels before running components on them.
2. Vary only one surface feature per pair: wording, order, section, distractor,
   semiology placement, time anchor, or benchmark convention wording.
3. Run component-level stress tests with first-failure ownership.
4. Run repair-sensitivity checks only after Workstream B repair policy is
   frozen.
5. Record synthetic results as mechanism evidence, not benchmark evidence.

Gates:

- every pair has a named invariant clinical state and one named perturbation;
- typed boundary/renderer behavior must be more pair-consistent than the
  deterministic comparator before it is used as robustness evidence;
- robustness cannot be owned primarily by semantic repair;
- failures must be assigned to candidate exposure, evidence selection,
  boundary classification, projection, rendering, repair, or action policy.

Success indicators:

- pair consistency improves on predeclared H7 axes;
- first-failure ownership identifies the next implementation target;
- exact-evidence and metadata completeness remain high under perturbation;
- synthetic success produces only a validation-development next step, not a
  benchmark claim.

### Workstream E: Action Policy And Verification Guardrails

Purpose: keep H6 and H9 useful without letting action widening become the lead
gap-closing story.

Implementation tasks:

1. Attach action summaries to every candidate:
   prediction-bearing coverage, abstain count, human-review count, monitor
   count, fallback release count, lane owner, and family action rates.
2. Replay H6 controls for every label-changing candidate.
3. If verification is used, separate route decision, verifier decision, and
   rendered-label emission.
4. Test release lanes one at a time after the prediction-bearing candidate is
   frozen.
5. Keep action-policy changes out of semantic repair and projection
   experiments.

Gates:

- H6 controls must show zero or explicitly bounded C->W before promotion;
- fallback releases need changed-label precision and release-lane ownership;
- a lower nonprediction rate is not success unless changed labels are precise;
- action policy cannot be described as solving the validation-test gap while
  locked-test aggregate nonprediction burden remains low.

Success indicators:

- candidate artifacts show whether errors are misses, abstentions, reviews,
  fallbacks, or rendered-label choices;
- high-precision release lanes can remain as safety/fallback policy;
- verifier work has a clean comparison against deterministic action baselines;
- action summaries make later frozen audits interpretable without row-level
  test failure inspection.

### Workstream F: Provenance And Runtime Hygiene

Purpose: prevent H10-class variance or replay drift from being mistaken for
clinical generalization evidence.

Implementation tasks:

1. Add raw-output identity sidecars before any live-versus-replay comparison.
2. Store prompt/program version, model id, cache status, timeout policy, parser
   version, repair policy version, projection policy version, and renderer
   policy version.
3. Use same-output ladders to attribute downstream drift to parser, adapter,
   repair, projection, safety floor, scorer, or action policy.
4. For fresh live audits, use explicit request timeouts and compare byte-level
   raw output, parsed labels, scorer-visible labels, and final policy labels
   separately.

Gates:

- no live/replay score delta can be interpreted without raw-output reuse or
  identity status;
- if raw outputs differ, report raw-string variance separately from parsed-label
  variance and final-policy variance;
- if raw outputs match but labels change, classify the result as downstream
  policy drift;
- interrupted live runs are prefix diagnostics unless a completion policy is
  predeclared.

Success indicators:

- model behavior, parser drift, repair drift, and action-policy drift are
  distinguishable in artifacts;
- same-output attribution is available before any LLM-first or verifier claim;
- runtime variance is bounded enough to interpret future fresh-call audits.

### Workstream G: Frozen Aggregate Holdout Audit

Purpose: evaluate transfer only after the candidate, readout plan, and claim
language are frozen.

Preconditions:

- Workstream A control manifest is complete;
- Workstream B repair policy is frozen;
- Workstream C or D mechanism has passed synthetic and validation hard/control
  gates;
- Workstream E H6/H9 sidecars are complete;
- Workstream F provenance sidecar is complete;
- candidate code, prompts, model ids, parser, scorer, repair policy, projection
  policy, renderer policy, action policy, slice definitions, and output fields
  are frozen;
- the user explicitly authorizes the audit.

Allowed readouts:

- overall Purist and Pragmatic aggregate;
- prediction-bearing coverage and action counts;
- predeclared hidden-family aggregates;
- predeclared component-owner aggregate summaries;
- predeclared score-layer aggregate ladder;
- H6 selective-action aggregate W->C/C->W when computable under the frozen plan.

Disallowed readouts:

- locked-test row-level failure inspection;
- new test-derived slices;
- post-test prompt, parser, repair, threshold, model, route, renderer, or action
  changes treated as the same candidate;
- final benchmark language.

Gates:

- if the candidate fails frozen aggregate controls, record the result and
  restart a validation-only cycle;
- if the candidate succeeds, report it as a frozen local holdout result with
  explicit non-comparability boundaries;
- no failed test aggregate can be mined for row-level fixes.

Success indicators:

- aggregate gap reduction occurs with preserved H6/H9 controls and clear
  attribution;
- predeclared slices support the same mechanism story observed on validation;
- no development decision is made from locked-test row-level failures;
- the final wording remains local, frozen, and non-benchmark-comparable.

### Stage Gates Summary

| Stage | Entry Requirement | Exit Gate | Promotion Level |
| --- | --- | --- | --- |
| Control freeze | Existing synthesis artifacts are available. | Control manifest, H6/H9/H10 sidecar contracts complete. | Development denominator only. |
| Repair policy | Control manifest complete. | Semantic repair families ablated and classified. | Allowed repair policy or quarantine. |
| Structured state | Repair policy frozen. | Contract tests pass with exact evidence and final policy disconnected. | Mechanism diagnostic. |
| Diagnostic assembly | Structured-state contracts pass. | Target hard-slice gains, bounded C->W, H6 preserved. | Bounded component only. |
| Robustness | Panel contract frozen. | Pair consistency and first-failure ownership reported. | Mechanism support only. |
| Action/verification | Candidate behavior frozen. | Action summaries, release precision, H6 controls complete. | Safety/fallback guardrail. |
| Provenance | Candidate or replay comparison exists. | Raw-output and downstream drift attribution complete. | Attribution support. |
| Frozen holdout | All prior gates passed and user authorizes. | Aggregate/predeclared-slice result recorded with no tuning. | Frozen local holdout result. |

### Global Stop Rules

Stop promotion and return to validation-only diagnosis if any of these occur:

- broad validation F1 improves while target hard slices or robustness panels do
  not;
- semantic repair changes clinical state while being reported as normalization;
- benchmark rendering silently changes `clinical_final_state`;
- exact evidence, source ids, parse status, or projection metadata are missing
  for changed rows;
- H6 controls regress;
- H9 action widening lowers nonprediction but introduces imprecise changed
  labels;
- H10 provenance is unavailable for a live/replay comparison;
- a candidate reaches a threshold only after mixed-provenance repair;
- any locked-test row-level failure is used to design the next change.

### Claim And Documentation Gates

Before a result is written into project status, a report, or paper-facing notes,
assign one of these labels:

- `diagnostic_validation_development`: useful for learning, not promoted.
- `bounded_component`: safe or useful inside a named eligible family only.
- `hybrid_development_artifact`: score depends on deterministic semantic repair
  or mixed provenance.
- `llm_first_validation_result`: allowed only after same-output attribution
  shows the prediction-bearing source is model-owned.
- `frozen_local_holdout_result`: authorized frozen aggregate/predeclared-slice
  holdout readout with no follow-on test tuning.
- `not_comparable_yet`: scorer, data surface, split policy, or attribution is
  unresolved.

Documentation success means the narrative claim is no stronger than the weakest
gate that actually passed.

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
- 2026-06-05: Added `boundary_benchmark_validation_contract_v0`, a validation
  typed-field smoke over the panel. It passed 30/30 contract matches with
  30/30 exact-evidence rows, 0 source-note-text rows, and no final-label policy
  connection. It remains validation-development mechanism evidence only.
- 2026-06-05: Added `boundary_benchmark_candidate_assembly_v0`, resolving the
  architecture decision in favor of a validation-only typed-candidate-contract
  layer over the current assembled candidate. The artifact is diagnostic only:
  30 selected rows, 6 W->C, 1 C->W, 100% parse-ok plus exact-evidence, and
  blocked by coverage plus W->C gates.
- 2026-06-05: Added `h3_h7_full_boundary_benchmark_test_v0`. H3 is rejected for
  the current shallow typed layer because all-eligible validation exposure is
  clean but only 36 rows with 6 W->C, below coverage and W->C gates. H7 is
  supported on the synthetic pair panel: typed behavior is consistent on 18/18
  pairs while the deterministic comparator flips on 4/18 pairs. H8 is partially
  supported as validation-development mechanism evidence: 11/11 benchmark
  convention rows have exact evidence and separated clinical/rendered fields,
  but no locked-test transfer audit was run.
- 2026-06-05: Added `h9_action_policy_gap_v0`. H9 is partially supported as an
  action-policy split-shift finding: validation has 34/750 nonprediction/review
  rows, all safety-floor-owned, including 19 blocked deterministic-correct rows;
  the aggregate locked-test selector readout has only 1/450 nonprediction row.
  This does not explain the main locked-test accuracy gap, and no locked-test
  row-level artifacts were written.
- 2026-06-05: Added `h10_runtime_variance_audit_v0` as a same-output
  provenance control, not a live-variance test. Corrected the H10 interpretation
  after fresh uncached runs showed that cached replay cannot determine runtime
  variability.
- 2026-06-05: Clarified `h10_fresh_live_variability_audit_v0`: the 19/20
  variance count is byte-level raw JSON-string variance, not label-level
  variance. Scorer-visible labels changed on 3/20 LLM-candidate rows, 1/20 raw
  adjudicator rows, and 0/20 final hybrid-with-adapters rows. H10 is supported
  as raw-string variance, but not yet as a final-policy explanation for the
  validation-test gap.
- 2026-06-05: Added `h5_semantic_repair_gap_test_v0`. H5 is partially supported
  and revised: validation repair gain is 0.2320 versus 0.0333 on locked test,
  while raw/base validation-test gap is not larger than the full-repair gap.
  The synthesis now treats this as a semantic-repair policy failure: too much
  validation performance came from deterministic repair rules that were too
  precisely attuned to reviewed validation examples. No locked-test row-level
  artifacts were used.
- 2026-06-07: Added an implementation-control plan with explicit scope,
  fixed boundaries, workstreams, stage gates, success indicators, stop rules,
  and claim/documentation gates for the next validation-development cycle.
