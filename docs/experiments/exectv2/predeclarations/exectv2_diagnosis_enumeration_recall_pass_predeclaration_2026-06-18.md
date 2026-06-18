# ExECTv2 Diagnosis Enumeration Recall Pass Predeclaration

Date: 2026-06-18
Status: PREDECLARED for dev-ladder live candidate generation (`pilot25` -> `dev140`)
Split: dev ladder only (`pilot25` -> `dev140`); full-200/test audit blocked
Model: one new dev-ladder call authorized, `gpt-4.1-mini`, on dev rows only
Parent plan: `docs/plans/exectv2/11_llm_first_essential_clinical_evaluation_plan.md`
Related: `docs/experiments/exectv2/predeclarations/exectv2_focused_diagnosis_route_predeclaration_2026-06-18.md`

## Purpose

The family-routed Plan 11 comparison leaves Diagnosis the largest
non-SeizureFrequency weakness (`0.2898` shared routed, `-0.0263` vs single pass).
Unlike SeizureFrequency (quantification-bound) and unlike the all-9 benchmark
surface (representation/target-construction artifact), the dev140 row-level
ledger shows Diagnosis is a **candidate-generation recall** gap that no
projection or semantic layer can recover.

Evidence from
`docs/experiments/exectv2/key_entities/exectv2_llm_first_essential_family_error_ledger_2026-06-18.md`
and its CSV
(`experiments/exectv2_llm_first_essential_family_error_ledger_dev140_20260618.csv`):

| Diagnosis candidate_miss measure | dev140 value | Read |
| --- | ---: | --- |
| Letters with a Diagnosis miss | 109 / 140 (78%) | near-universal under-emission |
| FN units | 275 | bulk of the family residual |
| Gold vs predicted concepts | 346 vs 166 | model emits 48% of gold |
| True under-emission rows (gold>pred) | 80 / 109 (193 units) | recall, not representation |
| Recoverable by semantic layer | +3 TP | negligible |
| Recoverable by projection | ~0 (6 projection_gap rows family-wide) | negligible |

The missed concepts are not exotic diagnoses. 75% of distinct missed concepts
(212 of 284) are seizure-type / semiology phrasing: `focal seizures` (26),
`tonic clonic seizures` (25), `complex partial seizures` (12),
`secondary generalised seizures` (10), `altered awareness` (13),
`focal to bilateral convulsive seizures` (12). The remainder are
epilepsy-syndrome / named-dx terms: `juvenile myoclonic epilepsy` (14),
`symptomatic structural focal epilepsy` (12), `temporal lobe epilepsy` (7).

Mechanism (exemplar EA0002): gold Diagnosis = {`focal seizures` x2,
`temporal lobe epilepsy`, `secondary generalised seizures`} (4 concepts); the
single pass emitted one (`focal epilepsy probable temporal`). Those same
seizure-type phrases are also the SeizureFrequency anchors for that letter. The
single all-entities pass collapses each mention into one family / one entry and
under-enumerates Diagnosis. This is the Diagnosis twin of the shared-mention
enumeration problem the SF event/state route already addressed.

## Hypothesis

A Diagnosis-dedicated **enumeration** pass that exhaustively lists every
seizure-type, semiology, and epilepsy-syndrome mention as a Diagnosis candidate
-- explicitly without de-duplicating against SeizureFrequency and without
collapsing repeated gold mentions -- raises Diagnosis recall toward the
already-recorded focused-replay headline (Diagnosis `0.7127`, four-family
`0.7081`) and lifts the routed four-family aggregate above current
`family_routed_llm_first` `0.5592`, at clean `llm_first` ownership.

This is a recall pass, not a verifier and not a projection adapter. Per the
standing convention (`LLM is candidate source`), candidate generation,
reasoning, and selection are the LLM's job; deterministic code only projects,
normalizes, and scores. The pass therefore stays clean `llm_first` and, unlike
the focused reconciler route, does **not** incur a hybrid ownership downgrade.

## Candidate To Run

Primary candidate:

```text
family_routed_with_diagnosis_enumeration_pass
```

New prediction-bearing component: a single Diagnosis enumeration prompt
(`diagnosis_enumeration_v0_1`) run on dev rows, replacing only the shared-pass
Diagnosis lane. Prescription, Investigations, and SeizureFrequency lanes are
reused unchanged from the current routed assembly.

Build/runner expectations:

- new driver under `core/.../exectv2/.../runners/` following the existing
  family-routed runner shape, resumable via `core/run_resume.py`;
- prompt enumerates seizure-type, semiology, and syndrome mentions, preserves
  duplicate mentions, and emits exact source evidence spans per mention;
- no de-duplication of a mention against any other family's emission;
- output written to a dated dev JSONL/JSON artifact pair under `experiments/`.

## Allowed Inputs

Allowed:

- ExECTv2 dev split letters for `pilot25` and `dev140`.
- Gold annotations for scoring on dev only.
- One `gpt-4.1-mini` call per dev row for the Diagnosis enumeration lane.
- Reused frozen routed lanes for the other three families:
  - P/I shared pass source as used by the current family-routed assembly;
  - SF route source as used by the current family-routed assembly.
- Existing parser, evidence validator, CUI/certainty/benchmark projection, and
  clinical-recovery scorer.
- The dev-only Diagnosis candidate_miss ledger above, for pre-run prompt design
  rationale only (not as a row-level tuning oracle after the run).

Blocked:

- Gan `test450` row-level failures, rationales, evidence, selected events, or
  transitions.
- ExECTv2 full-200/test row-level artifacts or any holdout-facing audit.
- More than one model call per dev row, or any rescoring-driven prompt re-edit
  followed by another live call within this predeclaration (that needs a fresh
  predeclaration with a new version tag).
- Any deterministic clinical-selection rule that adds, removes, suppresses, or
  rewrites Diagnosis concepts after the enumeration pass has emitted mentions.
- Building any accept/reject rule or threshold from dev140 residual rows of
  this run.

## Ownership

The Diagnosis enumeration lane is intended to be reportable as clean
`llm_first`. The aggregate stays qualified because the SF lane is hybrid.

| Component | Prediction-bearing owner | Allowed deterministic work | Disallowed deterministic work |
| --- | --- | --- | --- |
| Diagnosis enumeration pass | `llm_first` (LLM enumerates + selects) | exact evidence gate, schema repair, CUI/certainty/benchmark projection | adding/suppressing/rewriting Diagnosis concepts post-emission |
| P/I shared pass | LLM shared pass | schema validation, evidence gate, format projection | adding/replacing medication/investigation concepts |
| SeizureFrequency route | `hybrid_sf_route` | named SF projection and unknown-suppression layers | hiding deterministic SF candidate/projection as LLM-owned |
| CUI/certainty/projection | deterministic adapter | project from already-selected facts | selecting the clinical fact |

Expected aggregate ownership label:

```text
llm_first_with_hybrid_sf_route
```

(The Diagnosis lane does not change the aggregate label because it is itself
clean `llm_first`; the qualifier remains solely from the SF route.)

If implementation discovers the enumeration pass needs any deterministic concept
expansion, gazetteer injection, or post-hoc concept editing to hit its numbers,
the Diagnosis lane must be downgraded to `hybrid_diagnosis_route` and reported
as such.

## Evaluation Surface

Run only this ladder:

1. `pilot25` live enumeration call for artifact shape, parse/schema status,
   evidence validation, and catastrophic route-regression smoke.
2. `dev140` live enumeration call only if pilot25 passes.

Primary headline:

- CUI-free essential clinical recovery on the routed four-family surface
  (Prescription, Investigations, Diagnosis, SeizureFrequency).

Companion headline:

- CUI-projected four-family recovery, reported as deterministic projection
  effect, never as a separate clinical extraction improvement.

Required comparators on the same four-family surface:

- `deterministic_all9` (`0.7184` baseline still leads; report the gap honestly)
- `llm_only_all_entities` (`0.4313`)
- `hybrid_all_entities` (`0.5684`)
- current `family_routed_llm_first` (`0.5592`)
- `family_routed_with_diagnosis_enumeration_pass`

Required per-family readout:

| Family | Required comparison |
| --- | --- |
| Prescription | must match current routed result unless the assembler is broken |
| Investigations | must match current routed result unless the assembler is broken |
| Diagnosis | report F1, precision, recall vs shared `0.2898`, reconciler v0.1 `0.658`, focused replay `0.7127` |
| SeizureFrequency | must match current SF route unless the assembler is broken |

Required Diagnosis sub-split (the distinctive readout for this run):

| Diagnosis slice | Gold instances in candidate_miss | Required report |
| --- | ---: | --- |
| seizure-type / semiology | 174 | recall recovered vs baseline |
| epilepsy-syndrome / named dx | 110 | recall recovered vs baseline |

## Promotion Criteria

`pilot25` may promote to `dev140` only if all are true:

- exactly one model call per dev row, no retries that change emitted concepts;
- zero unexplained parse/schema failures;
- every emitted prediction is evidence-validated or explicitly counted invalid;
- Prescription, Investigations, and SF counts match the current routed assembly
  on the pilot rows.

The enumeration pass is a useful dev architecture route only if `dev140` shows
all of the following:

- four-family CUI-free F1 exceeds current `family_routed_llm_first` `0.5592`;
- Diagnosis F1 improves by at least `+0.25` absolute over shared `0.2898`;
- Diagnosis F1 is at least `0.60`;
- Diagnosis recall strictly improves over the shared-pass routed Diagnosis
  recall (the explicit objective of this run);
- **precision floor**: Diagnosis precision is at least `0.55` (guards against the
  over-enumeration risk this design deliberately courts);
- Diagnosis exact/evidence-valid rate remains at least `0.99`;
- Prescription, Investigations, and SeizureFrequency F1 are unchanged to within
  scorer rounding (`<= 0.001` absolute drift);
- the readout preserves the qualified aggregate ownership label and does not
  claim benchmark completeness.

If Diagnosis recall rises but precision falls below `0.55`, the run is recorded
as a recall/precision-tradeoff datapoint, not a promoted route, and any
follow-up precision control needs its own predeclaration (no inline threshold
tuning on these residuals).

## Required Diagnostics

The readout must include:

- artifact path and hash or stable size/mtime for the enumeration output and
  each reused lane input;
- per-family clinical recovery, CUI-free and CUI-projected;
- Diagnosis precision and recall, not only F1;
- the seizure-type vs syndrome recall sub-split above;
- exact evidence rate by family and for Diagnosis rows;
- call/parse/schema failure counts;
- component owner counts by family;
- duplicate-mention handling check: confirm repeated gold mentions
  (e.g. `focal seizures` x2 in EA0002) are scored as intended under the
  benchmark multiset rule, since duplicate-FN caps can mask recovered recall.

Do not generate a new residual ledger unless it is dev-only and the report
predeclares that it is diagnostic, not a tuning input for this route.

## Risks Predeclared

- **Over-enumeration / precision leak.** Exhaustive enumeration without
  family de-dup will emit more Diagnosis mentions; the benchmark multiset and
  duplicate-FN caps mean some added emissions cannot score and may add FPs. The
  precision floor and the duplicate-handling check are the guards.
- **Syndrome tail under-recovery.** The 110 syndrome/named-dx instances may need
  different handling than seizure-type phrasing; the sub-split makes that
  visible without authorizing a second tuned pass.
- **Ownership creep.** Any temptation to inject a seizure-type gazetteer or
  post-hoc concept list converts this from `llm_first` to hybrid; that is
  disallowed without a fresh predeclaration.

## Why This Is Not Post-Test Tuning

- No Gan test, ExECTv2 full-200/test, or holdout row-level artifact is touched.
- The prompt is designed from dev-only aggregate residual structure (counts and
  concept frequencies), fixed before the run, not from holdout output.
- Exactly one new dev-ladder call per row is authorized; no threshold, concept
  suppressor, gazetteer, or residual repair is authorized.
- The claim is limited to dev architecture evidence and cannot support a
  benchmark or holdout generalization claim.
- Any future full-200/test audit requires a separate frozen protocol with
  aggregate-only holdout readout and no post-hoc row-level tuning, per
  `docs/runbooks/gated_blockers_2026-06-18.md`.

## Stop Rules

Stop and mark the route diagnostic if:

- pilot25 reveals route assembly drift outside Diagnosis;
- Diagnosis evidence validity falls below `0.99`;
- dev140 Diagnosis F1 remains below `0.60`;
- dev140 Diagnosis precision falls below `0.55`;
- hitting the numbers requires any deterministic concept editing;
- aggregate ownership cannot be described without hiding deterministic or hybrid
  behavior.

## Claim Language

Supported if gates pass:

> A dev140 enumeration pass that lists every seizure-type, semiology, and
> syndrome mention as a Diagnosis candidate raises Diagnosis recall and the
> routed four-family ExECTv2 development headline above the current
> family-routed assembly, at clean `llm_first` ownership for the Diagnosis lane,
> while preserving the other three lanes.

Supported regardless of gates:

> Diagnosis is a candidate-generation recall problem on dev140, not a
> projection or representation problem; under-emission of seizure-type mentions
> dominates the residual.

Not supported:

> The enumeration pass solves Diagnosis, beats the deterministic baseline, or is
> ready for full-200/test evaluation.

Not supported:

> Any gain generalizes beyond the ExECTv2 dev split.
