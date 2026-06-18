# ExECTv2 Focused Diagnosis Route Predeclaration

Date: 2026-06-18
Status: PREDECLARED for no-call pilot25 -> dev140 assembly replay only
Split: dev ladder only (`pilot25` -> `dev140`); full-200/test audit blocked
Model: no new model call authorized
Parent plan: `docs/plans/exectv2/11_llm_first_essential_clinical_evaluation_plan.md`

## Purpose

The current family-routed Plan 11 comparison leaves Diagnosis on the shared
all-entities pass. That keeps Prescription and Investigations stable, but it
makes Diagnosis the largest non-SeizureFrequency weakness:

| Diagnosis candidate | Dev140 F1 | P | R | Evidence exact/valid | Current read |
| --- | ---: | ---: | ---: | ---: | --- |
| Shared routed Diagnosis | 0.2898 | tbd | tbd | 1.0000 | weak concept selection |
| Diagnosis verifier v0.6 | 0.651 | 0.706 | 0.604 | 0.9906 | usable but recall limited |
| Diagnosis decomposer v0.1 | 0.642 | 0.631 | 0.653 | 1.0000 | higher recall, precision leak |
| Diagnosis reconciler v0.1 | 0.658 | 0.658 | 0.658 | 0.9954 | current numeric Diagnosis candidate |
| Diagnosis reconciler v0.2 | 0.647 | 0.636 | 0.658 | 0.9956 | rejected; over-emission worsened |

This predeclaration tests whether the family-routed architecture should replace
the weak shared-pass Diagnosis lane with a focused Diagnosis route while keeping
the existing Prescription, Investigations, and SeizureFrequency lanes unchanged:

```text
letter
  -> shared all-entities pass for Prescription and Investigations
  -> focused Diagnosis route for Diagnosis
  -> SF event/state route for SeizureFrequency
  -> exact evidence validation
  -> deterministic certainty, CUI, and benchmark-format projection
  -> ownership-aware clinical and projection readouts
```

This is an architecture assembly question, not a new Diagnosis target-clear
claim. The Diagnosis ceiling note remains binding: the current candidate set is
not expected to reach the `0.8` Diagnosis target, and a route that improves over
`0.2898` can still be reported as weak.

## Candidate To Replay

Primary no-call candidate:

```text
family_routed_with_focused_diagnosis_route
```

It may use only frozen, existing dev artifacts:

- Shared pass P/I source:
  `experiments/exectv2_llm_only_all_entities_dev140_gpt41mini_20260612.jsonl`
- Focused Diagnosis source:
  `experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl`
- SF route source:
  `experiments/exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl`
- Comparator hybrid all-entities source:
  `experiments/exectv2_hybrid_all_entities_dev140_gpt41mini_20260617.jsonl`
- Existing family-routed comparison:
  `experiments/exectv2_family_routed_llm_first_dev140_gpt41mini_20260618.json`

If the v0.1 Diagnosis reconciler artifact is missing or not replayable, the
execution must stop. Do not substitute v0.2 or any new prompt output without a
new predeclaration.

## Allowed Inputs

Allowed:

- ExECTv2 dev split letters for `pilot25` and `dev140`.
- Gold annotations for scoring on dev only.
- The named frozen JSONL artifacts above.
- Existing parser, evidence validator, CUI projection, certainty projection,
  benchmark projection, and clinical-recovery scorer.
- Existing aggregate and residual reports listed in this document for
  pre-run design rationale.

Blocked:

- Gan `test450` row-level failures, rationales, evidence, selected events, or
  transitions.
- ExECTv2 full-200/test row-level artifacts or any holdout-facing audit.
- New model calls, including prompt-only edits followed by live Diagnosis calls.
- New deterministic clinical-selection rules that add, remove, or rewrite
  Diagnosis concepts after the focused route has emitted mentions.
- Reusing v0.2 residual rows to build a new accept/reject rule or threshold.

## Ownership

The aggregate candidate must not be reported as clean `llm_first`.

| Component | Prediction-bearing owner | Allowed deterministic work | Disallowed deterministic work |
| --- | --- | --- | --- |
| Prescription/Investigations shared pass | LLM shared pass | schema validation, exact evidence gate, format-preserving normalization, projection | adding or replacing medication/investigation concepts |
| Diagnosis focused route | `hybrid_diagnosis_reconciler` unless a later artifact proves cleaner ownership | exact evidence gate, schema repair, CUI/certainty/benchmark projection | post-route concept suppression, concept expansion, certainty rewriting, or v0.2-derived residual fixes |
| SeizureFrequency route | `hybrid_sf_route` | named SF projection and unknown-suppression layers already reported | hiding deterministic SF candidate/projection behavior as LLM-owned |
| CUI/certainty/projection | deterministic adapter | project from already selected facts | selecting the clinical fact |

The expected aggregate ownership label is:

```text
llm_first_with_hybrid_diagnosis_and_sf_routes
```

If implementation discovers that the Diagnosis replay artifact contains
additional deterministic semantic selection beyond the reconciler's recorded
output, the route must be downgraded further to `hybrid_diagnosis_route`.

## Evaluation Surface

Run only this ladder:

1. `pilot25` no-call assembly replay for artifact shape, parse/schema status,
   evidence validation, and catastrophic route-regression smoke.
2. `dev140` no-call assembly replay only if pilot25 passes.

Primary headline:

- CUI-free essential clinical recovery on the routed four-family surface:
  Prescription, Investigations, Diagnosis, SeizureFrequency.

Companion headline:

- CUI-projected four-family recovery, reported as deterministic projection
  effect and never as a separate clinical extraction improvement.

Required comparators on the same four-family surface:

- `deterministic_all9`
- `llm_only_all_entities`
- `hybrid_all_entities`
- current `family_routed_llm_first`
- `family_routed_with_focused_diagnosis_route`

Required per-family readout:

| Family | Required comparison |
| --- | --- |
| Prescription | must match shared-pass routed result unless the assembler is broken |
| Investigations | must match shared-pass routed result unless the assembler is broken |
| Diagnosis | compare shared-pass `0.2898`, verifier v0.6 `0.651`, reconciler v0.1 `0.658`, and focused-route replay |
| SeizureFrequency | must match current SF route unless the assembler is broken |

## Promotion Criteria

Pilot25 may promote to dev140 only if all are true:

- zero call attempts and zero new raw model outputs;
- zero unexplained parse/schema failures from the named artifacts;
- every emitted prediction is evidence-validated or explicitly counted as
  evidence-invalid;
- Prescription, Investigations, and SF counts match the current routed assembly
  on the pilot rows;
- Diagnosis route source is exactly the v0.1 reconciler artifact named above.

The focused Diagnosis route may be considered a useful dev architecture route
only if dev140 shows all of the following:

- four-family CUI-free F1 exceeds current `family_routed_llm_first` on the same
  surface;
- Diagnosis F1 improves by at least `+0.25` absolute over shared routed
  Diagnosis `0.2898`;
- Diagnosis F1 is at least `0.60`;
- Diagnosis exact/evidence-valid rate remains at least `0.99`;
- Prescription, Investigations, and SeizureFrequency scores are unchanged to
  within scorer rounding (`<= 0.001` absolute F1 drift);
- the readout preserves the qualified aggregate ownership label and does not
  claim the route is benchmark-complete.

The route is not promoted as a Diagnosis solution unless a future, separately
predeclared candidate clears a stronger Diagnosis target. If the route improves
the aggregate only by substituting the existing v0.1 Diagnosis candidate, the
correct claim is architecture routing evidence, not new Diagnosis learning.

## Required Diagnostics

The readout must include:

- artifact path and hash or stable size/mtime for each replay input;
- per-family clinical recovery, CUI-free and CUI-projected;
- exact evidence rate by family and for changed Diagnosis rows;
- call/parse/schema failure counts by source artifact;
- component owner counts by family;
- Diagnosis residual summary from existing dev-only ledgers, without adding new
  residual-tuned rules;
- comparison against current family-routed aggregate and current focused
  Diagnosis v0.1/v0.2 reports.

Do not generate a new residual ledger unless it is dev-only and the report
predeclares that it is diagnostic, not a tuning input for this route.

## Why This Is Not Post-Test Tuning

- No Gan test, ExECTv2 full-200/test, or holdout row-level artifact is
  authorized.
- The route uses only existing dev artifacts whose paths are fixed before the
  assembly replay.
- No new model call, prompt edit, threshold, concept suppressor, or residual
  repair is authorized by this document.
- The evaluation is a no-call assembly replay of named components, so any gain
  must come from route selection among already recorded dev candidates.
- The claim is limited to dev architecture evidence. It cannot support a
  benchmark or holdout generalization claim.
- Any future full-200/test audit requires a separate frozen protocol with
  aggregate-only holdout readout and no post-hoc row-level tuning.

## Stop Rules

Stop and mark the route diagnostic if:

- the v0.1 Diagnosis artifact is unavailable or differs from the recorded report;
- pilot25 reveals route assembly drift outside Diagnosis;
- Diagnosis evidence validity falls below `0.99`;
- dev140 Diagnosis remains below `0.60`;
- aggregate ownership cannot be described without hiding deterministic or hybrid
  behavior.

## Claim Language

Supported if gates pass:

> A no-call dev140 assembly replay shows that replacing the weak shared-pass
> Diagnosis lane with the focused Diagnosis reconciler improves the routed
> four-family ExECTv2 development headline, while preserving Prescription,
> Investigations, and SeizureFrequency behavior.

Supported regardless of gates:

> Diagnosis remains a qualified, development-only route: evidence validity is
> high, but concept/assertion scope limits keep the route below the standalone
> Diagnosis target.

Not supported:

> The focused Diagnosis route is a clean LLM-first component.

Not supported:

> The focused Diagnosis route solves Diagnosis or is ready for full-200/test
> evaluation.

