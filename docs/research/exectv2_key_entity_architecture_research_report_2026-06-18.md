# ExECTv2 Key-Entity Architecture Research Report

Date: 2026-06-18
Scope: Prescription/medication, Diagnosis, SeizureFrequency, Investigations
Model loop: `openai/gpt-4.1-mini`
Status: interim research synthesis; not a benchmark-complete claim

## Executive Summary

We started from the post-Gan hypothesis that ExECTv2 could benefit from the same
discipline that worked for seizure frequency: source-near structured state,
exact evidence, clinically meaningful projection, external gates, and
error-analysis-led prompt iteration. The key architectural question was whether
the four target families should be extracted by one structured schema and one
prompt, or by separate specialist prompts and verifier/adjudicator stages.

The answer so far is mixed but useful:

- A single structured schema is a good substrate. It produces clean, evidence
  grounded drafts across all four families and gives a reusable common state for
  downstream verification.
- A single prompt is not sufficient as the final architecture. It reached all
  four targets on dev25 only after prompt accretion, but that configuration did
  not transfer to dev140.
- Family-specific decomposition is necessary, but not every decomposition helps.
  Medication and Investigations improved with focused verifiers. Diagnosis and
  SeizureFrequency improved only after more explicit candidate/state
  decomposition, and both remain below target.
- The main scientific lesson is that broad source coverage is easier than
  clinical recovery. The hard part is selecting the right concept/state under
  annotation conventions without over-emitting related clinical facts.

Current dev140 best candidates:

| Family | Current best candidate | F1 | Precision | Recall | Status |
| --- | --- | ---: | ---: | ---: | --- |
| Prescription / medication | Prescription verifier v0.1 | 0.817 | 0.773 | 0.865 | Clears target |
| Investigations | Investigations verifier v0.1 | 0.872 | 0.869 | 0.875 | Clears target |
| Diagnosis | Diagnosis reconciler v0.1 | 0.658 | 0.658 | 0.658 | Below target |
| SeizureFrequency | SF state adjudicator v0.5 | 0.721 | 0.710 | 0.733 | Below target |

This is not yet a solved ExECTv2 architecture. It is a much clearer map of the
problem.

## Evaluation Frame

The work used the clinical-recovery scorer from
`docs/plans/exectv2/10_clinical_recovery_scorer_build_plan.md`. That scorer
separates clinical fact recovery from benchmark artifact projection:

- Prescription and Investigations are component-recovery tasks.
- SeizureFrequency is frequency-state recovery by seizure type:
  `active-rate`, `seizure-free`, and `unknown`.
- Diagnosis is concept-identity recovery with assertion attributes.
- CUI attachment and benchmark phrase projection are reported as controlled
  artifact layers, not as model clinical reasoning.

This matters because a model can be clinically close but lose benchmark credit
through CUI or phrase projection, and the reverse can happen if projection
rules hide weak clinical selection. The report below treats exact evidence,
schema validity, evidence validity, and semantic-versus-benchmark gaps as part
of the result, not secondary bookkeeping.

## Architecture Tracks Tested

### 1. Deterministic all-entity substrate

The deterministic all-9 scorecard established an inspectable floor:
`experiments/exectv2_deterministic_all9_dev_20260617.md`. It was not
competitive as a final architecture, but it supplied two important research
assets:

- explicit benchmark-format CUI projection machinery;
- error ledgers that separated phrase coverage, attribute bundles, CUI
  projection gaps, and over-emission.

The deterministic scorecard reached benchmark item F1 `0.3625` and letter F1
`0.6747`, confirming that hand rules alone were not the path to the key-family
target. Its value was diagnostic and infrastructural.

### 2. Single structured schema + single prompt

This was the architecture path we deliberately explored first. The pipeline
`exectv2_llm_only_key_entities_structured` extracted all four key families in
one call using a structured event schema. The sequence was:

| Run | Main change | Key result |
| --- | --- | --- |
| v0.1 dev25 | Initial four-family structured events | Clean gate but weak clinical recovery |
| v0.2 dev25 | Prompt optimization from early errors | Prescription above target; Investigations near target; Diagnosis/SF low |
| v0.3 dev25 | Stronger medication/investigation guidance | Medication and Investigations above target; SF regressed |
| v0.4 dev25 | SF recovery guidance | SF recovered; Diagnosis remained bottleneck |
| v0.5 dev25 | Diagnosis-focused prompt pass | Diagnosis rose to `0.569`; Medication/Investigations stayed above target |

The single-prompt path showed the first major positive result: the structured
schema can carry enough information for downstream use. It also revealed a
capacity problem. By v0.5 the prompt contained medication regimen policy,
diagnosis concept policy, SF temporal/state policy, and investigation result
policy. Adding more rules improved one family while risking another.

The dev25 v0.5 best single-prompt family table was:

| Family | F1 |
| --- | ---: |
| Prescription | 0.897 |
| Diagnosis | 0.569 |
| SeizureFrequency | 0.633 |
| Investigations | 0.837 |

Interpretation: single prompt is the right representation substrate, not the
right final decision procedure.

### 3. Specialist prompt comparison

The old per-entity Diagnosis specialist prompt was tested as a counterpoint to
the single structured schema. It was not competitive: Diagnosis F1 `0.282`
versus single structured v0.5 `0.569` on dev25. This rejected the simplest
"just split by entity with older prompt shape" alternative.

The lesson was narrower: decomposition helps only when the decomposed prompt is
built around the clinical recovery target and the current error modes. Merely
being entity-specific is not enough.

### 4. Diagnosis verifier iterations

Diagnosis then moved to a verifier pattern over the single structured draft.
The verifier improved dev25 in a disciplined way:

| Run | Diagnosis F1 | Main change |
| --- | ---: | --- |
| single structured v0.5 | 0.569 | Broad structured draft |
| verifier v0.1 | 0.592 | Precision-focused verification |
| verifier v0.2 | 0.619 | Model-owned normalized concept text |
| verifier v0.3 | 0.701 | Recovery of residual seizure/epilepsy concepts |
| verifier v0.4 | 0.768 | Targeted residual families |
| verifier v0.5 | 0.837 | First dev25 target-clearing Diagnosis candidate |

This looked excellent locally, but the dev140 transfer readout failed:
Diagnosis verifier v0.5 transferred to only `0.616`. Later dev140 residual-led
work moved the best Diagnosis score to `0.658` with the reconciler v0.1, but
subsequent concept grouping in reconciler v0.2 did not transfer and was
rejected.

Diagnosis experiments tested these architecture ideas:

- verifier over single structured draft;
- heading/narrative decomposition;
- reconciliation of verifier and decomposer outputs;
- explicit concept group classification;
- accept/reject gating over candidate concept families.

Current Diagnosis result: the best dev140 score is still only `0.658`. The
residual pattern is stable: generic epilepsy and tonic-clonic over-emission,
plus focal epilepsy and secondary-generalised misses. The residual convention
decomposition shows that even a generous convention oracle reaches only `0.791`,
below the `0.8` gate. Diagnosis should therefore be treated as a transparent
ceiling/annotation-scope result unless a new architecture changes the
prediction-bearing evidence source, not as a near-miss to be solved by another
reject-prompt loop.

### 5. SeizureFrequency verifier and state adjudicator

SeizureFrequency followed a similar arc. The early verifier improved dev25:

| Run | SF F1 | Main change |
| --- | ---: | --- |
| single structured v0.5 | 0.633 | Broad structured draft |
| verifier v0.1 | 0.667 | Recall-oriented verifier |
| verifier v0.2 | 0.788 | Precision recovery |
| verifier v0.3 | 0.831 | First dev25 target-clearing SF candidate |

Again, dev25 did not transfer. SF verifier v0.3 transferred to dev140 at only
`0.602`.

The dev140 residual ledger then changed the architecture from a verifier into a
candidate-span/state adjudicator:

| Run | SF F1 | Main change | Read |
| --- | ---: | --- | --- |
| verifier v0.4 | 0.623 | Residual-led verifier | Small gain |
| state adjudicator v0.1 | 0.674 | Candidate spans + state adjudication | Clear architecture gain |
| state adjudicator v0.2 | 0.672 | Tightened generic seizure rules | Precision/recall tradeoff; unknown collapsed |
| state adjudicator v0.3 | 0.681 | Unknown/change recovery lane | Small gain |
| state adjudicator v0.4 | 0.707 | Typed candidate decomposition | Clear gain |
| state adjudicator v0.5 | 0.721 | Seizure-free-anchor specialization + finite CUI variants | Current best |

This is the strongest evidence that Gan-style structured state helps ExECTv2.
The model improved when given candidate spans and clinically typed lanes:
generic/named active rate, generic/named seizure-free anchor, generic/named
qualitative change, prior-event reference, unlabelled event, and context-only
diagnosis. v0.5 then improved seizure-free F1 from `0.738` to `0.781`, but
unknown-state F1 regressed to `0.476`.

Current SF result: state decomposition is the right direction, and the residual
convention decomposition sharpened the next loop: an oracle state plus
generic-vs-named ownership projection reaches `0.805`. The predeclared v0.6
deterministic replay recovered part of that headroom (`0.721` -> `0.763`) but
did not clear `0.8`; ownership-only projection made no measurable movement. The
oracle should therefore be treated as an upper bound, not as an achieved or
safely reachable score.

### 6. Medication and Investigations verifiers

The dev140 clinical ledger showed medication and Investigations were near
target but failed for different reasons. A combined medication/investigation
verifier tested whether one small verifier could fix both.

It was a split decision:

| Family | Baseline dev140 F1 | Combined verifier v0.1 F1 | Decision |
| --- | ---: | ---: | --- |
| Prescription | 0.777 | 0.817 | Use |
| Investigations | 0.786 | 0.496 | Reject |

This was an important decomposition finding. Medication needed a verifier that
separates current regimen, rescue medication, previous medication, and future
titration. Investigations needed a simpler modality/result/type decision table.
Bundling them damaged the investigation task.

A dedicated Investigations verifier then cleared target:

| Candidate | Investigations F1 | Precision | Recall |
| --- | ---: | ---: | ---: |
| single structured v0.5 | 0.786 | 0.752 | 0.824 |
| combined verifier v0.1 | 0.496 | 0.408 | 0.632 |
| Investigations verifier v0.1 | 0.872 | 0.869 | 0.875 |

Interpretation: decomposition should follow clinical decision structure, not
surface similarity or convenience.

## What We Iterated On

### Prompt optimization

Prompt changes were most useful when they named a residual family and gave the
model a decision procedure. Examples:

- Diagnosis v0.3-v0.5 targeted repeated tonic-clonic assertions, uncertain focal
  seizure-type diagnoses, probable-cause wording, intractable epilepsy, and
  symptom suppression.
- SF v0.4-v0.5 targeted generic-vs-named state ownership and seizure-free anchor
  rendering.
- Investigations v0.1 targeted performed-versus-planned tests and explicit
  normal/abnormal result extraction.

Broad prompt accretion was less useful. It helped dev25 but tended not to
transfer to dev140, especially for Diagnosis and SF.

### Schema design

The structured event schema was valuable because it forced:

- exact source evidence;
- entity-family typed outputs;
- legal attributes;
- rationale fields;
- separation between source-near fact selection and benchmark CUI projection.

The main schema lesson is that a shared schema can be a substrate, while final
decision ownership may need family-specific modules. The report should not
claim "single prompt failed"; rather, the evidence says "single prompt alone
failed as the final selector, but single structured output remained the best
draft substrate."

### Candidate decomposition

The most productive later iterations turned vague extraction into explicit
candidate decisions:

- Diagnosis: verifier/decomposer/reconciler/gate experiments over normalized
  concept families.
- SF: candidate spans with state hints, candidate types, and decision lanes.
- Medication: current/rescue/future/previous regimen distinction.
- Investigations: performed/planned/result/type distinction.

This supports a broader architectural claim: ExECTv2 needs clinically meaningful
projection surfaces, not just more examples in a prompt.

### Benchmark-format projection

CUI projection repeatedly affected measured F1. We preserved attribution by:

- stripping model-supplied CUI/CUIPhrase in SF adjudication before deterministic
  projection;
- labeling finite lexicon additions as `benchmark_format`;
- reporting source-near, semantic, and benchmark layers separately.

The latest SF v0.5 lexicon additions are a good example. Phrases like
`no further seizures`, `focal to bilateral seizures`, `focal impaired awareness
seizures`, `focal dyscognitive seizures`, and `absence events` are
residual-supported benchmark-format variants. They improve measured matching
without claiming the LLM selected a new clinical fact.

### Error analysis

Error ledgers changed the trajectory more than aggregate F1 did. The most useful
ledgers were:

- key-family dev140 clinical ledger:
  `experiments/exectv2_key_entities_clinical_error_ledger_dev140_20260618.md`;
- Diagnosis residual ledgers for verifier/reconciler/gate loops;
- SF residual ledgers by state for state adjudicator loops;
- projection-gap ledgers separating source coverage, attribute mismatch, CUI
  projection, and over-emission.

The recurring pattern is that source-near recall can look healthy while
clinical recovery remains weak because the model over-emits related facts,
chooses the wrong specificity level, or renders the wrong state.

## What We Discovered

### 1. dev25 was too optimistic

The configuration that cleared all four families on dev25 did not transfer:

| Family | dev25 candidate | dev25 F1 | dev140 F1 |
| --- | --- | ---: | ---: |
| Prescription | single structured v0.5 | 0.897 | 0.777 |
| Diagnosis | verifier v0.5 | 0.837 | 0.616 |
| SeizureFrequency | verifier v0.3 | 0.831 | 0.602 |
| Investigations | single structured v0.5 | 0.837 | 0.786 |

This is the single most important methodological finding. dev25 is useful for
format and pilot safety. It is not enough to promote an architecture.

### 2. Evidence validity is necessary but not sufficient

Most mature runs had zero call failures, zero parse failures, and high evidence
validity. That did not imply clinical correctness. The remaining errors are
mostly selection and projection errors over real text, not hallucinated evidence.

### 3. The target families differ structurally

Medication and Investigations are component-table tasks. Focused verifiers
worked because the decision tables are compact:

- current/rescue/future/previous medication;
- performed/planned investigation and result/type.

Diagnosis and SF are harder because they require hierarchy and state ownership:

- Diagnosis must handle generic epilepsy, focal epilepsy, seizure-type
  diagnoses, certainty, historical/context use, and specificity collapse.
- SF must decide whether generic seizure states and named seizure-type states
  are separately annotated, and whether a phrase is active-rate, seizure-free,
  or unknown/change.

This argues for different modules per family, but with a shared structured
substrate and shared gates.

### 4. Decomposition beats prompt length when it changes the decision unit

The successful decompositions changed what the model was asked to decide:

- from "extract all investigations" to "is this test performed and what result
  does it have?";
- from "extract seizure frequency" to "which candidate span/state lane should be
  kept, split, merged, or rejected?";
- from "extract diagnosis" toward "accept or reject this normalized
  concept/evidence pair."

The unsuccessful decompositions mostly added more prose or grouped candidates
without changing the model's final decision burden.

### 5. The single structured prompt remains valuable

Despite not being final, the single structured prompt should not be discarded.
It provides:

- broad source coverage;
- exact-evidence draft mentions;
- a common JSON artifact for specialist stages;
- a common failure-analysis surface.

The best current architecture is therefore hybrid in the research sense:

```text
clinical letter
  -> single structured key-family draft
  -> family-specific verifier/adjudicator
  -> deterministic evidence/schema validation
  -> finite benchmark-format projection
  -> clinical-recovery scoring + residual ledger
```

## Current Best Architecture

The current best dev140 architecture is an assembled hybrid:

| Family | Source substrate | Final selector/adjudicator | Deterministic layer |
| --- | --- | --- | --- |
| Prescription | single structured v0.5 | Prescription verifier v0.1 | evidence gate + CUI projection |
| Investigations | single structured v0.5 | Investigations verifier v0.1 | evidence gate + modality/result projection |
| Diagnosis | verifier v0.6 + decomposer v0.1 | Diagnosis reconciler v0.1 | evidence gate + benchmark projection |
| SeizureFrequency | single structured v0.5 + candidate spans | SF state adjudicator v0.5 | evidence gate + finite SF CUI projection |

This architecture clears two of four key families on dev140. It should be
treated as revise-only for the overall benchmark objective, but the current
research interpretation is now split: SF has a plausible convention-projection
path over `0.8`, while Diagnosis is likely a benchmark-convention ceiling below
`0.8`.

## Open Problems

### Diagnosis

Current best: `0.658`.

Main residuals:

- generic epilepsy over-emission;
- tonic-clonic seizure diagnosis over-emission;
- focal epilepsy and secondary-generalised recall misses;
- assertion/certainty and concept hierarchy mismatch.

The residual convention decomposition supersedes the earlier gate-v0.2 plan.
Pure convention alignment accounts for a meaningful minority of the residual,
but even a generous oracle that resolves assertion, hierarchy altitude, and
adjacent-family specificity reaches only `0.791`. The next Diagnosis deliverable
is therefore characterization: evidence validity, convention-bound residual
share, semantic/concept-layer reporting, and clear claim language that the
benchmark `0.8` target is not reachable by another legitimate convention gate
on the current candidate set.

This is now captured as a paper-facing ceiling note:
`docs/research/exectv2_diagnosis_ceiling_note_2026-06-18.md`.

### SeizureFrequency

Current best: `0.763` after deterministic v0.6 state projection.

v0.5 nearly solved the seizure-free slice (`0.781`) but regressed unknown-state
recovery (`0.476`). The remaining residuals are balanced:

- active-rate: 17 misses / 28 over-emissions;
- seizure-free: 15 misses / 13 over-emissions;
- unknown: 18 misses / 15 over-emissions.

The v0.6 projection should be treated as a partial improvement, not a target
crossing. It improves recall while keeping precision acceptable, but the unknown
slice remains weak and ownership projection contributes no measurable gain. Any
further SF work should be a targeted residual/error-slice study, not another
broad aggregate prompt or projection pass.

The targeted v0.6 hard-slice diagnostic shows that the remaining blocker is
unknown-state precision: 22 unknown over-emissions versus 8 unknown misses.
Another broad unknown/change recovery rule is therefore not supported.

### Combined readout

After the next Diagnosis and SF loops, regenerate a combined key-family
clinical-recovery readout using the current best candidates. The combined
readout should report:

- per-family F1/P/R;
- call and parse failures;
- evidence validity;
- source-near versus clinical recovery;
- semantic versus benchmark/CUI gap;
- family-specific residual ledgers.

## Recommended Next Research Plan

1. Freeze the current report as the interim architecture synthesis, with the
   residual convention decomposition as the plan-changing companion analysis.
2. Stop ordinary Diagnosis target-chasing on the current candidate set. Treat
   Diagnosis as a ceiling/characterization result unless a new architecture
   changes the prediction-bearing evidence source.
3. Treat SF v0.6 as the current best SF candidate (`0.763`) but not a target
   clearing result. Its state-only and combined ablations match; ownership-only
   contributes no measurable gain.
4. Reassemble the best four-family dev140 candidate:
   - Prescription verifier v0.1;
   - Investigations verifier v0.1;
   - Diagnosis reconciler v0.1 as ceiling/semantic-layer evidence;
   - SF v0.6 state projection.
5. Only after the revised architecture has benchmark-beating dev evidence, write
   a frozen protocol for any full-200 readout. That protocol should predeclare
   the architecture, artifacts, exact metrics, and no row-level post-hoc tuning.

## Claim Language To Use Now

Supported:

> A single structured key-family prompt provides a useful evidence-grounded
> substrate, but reliable ExECTv2 clinical recovery requires family-specific
> verifier/adjudicator stages whose decision units match the clinical structure
> of each entity family.

Supported:

> dev25 target-clearing results did not transfer to dev140, so promotion must be
> based on residual-led dev140 evidence rather than local pilot success.

Supported:

> Medication and Investigations can clear the current dev140 target with focused
> verifier prompts, while Diagnosis and SeizureFrequency require stronger
> concept/state decomposition.

Supported:

> Residual convention decomposition splits the two below-target families:
> SeizureFrequency has a reachable state/ownership convention-projection path
> over `0.8`, while Diagnosis remains below `0.8` even under a generous
> convention oracle.

Supported:

> Deterministic SF state projection over adjudicator candidates improves dev140
> clinical-recovery F1 from `0.721` to `0.763`, but does not clear the `0.8`
> target; the convention oracle is an upper bound rather than achieved evidence.

Not yet supported:

> The ExECTv2 architecture beats the key-family benchmark.

Not supported:

> Diagnosis can reach benchmark-F1 `0.8` on dev140 through another verifier or
> accept/reject gate over the current candidate set.

Not supported:

> SeizureFrequency clears `0.8` after deterministic convention projection.

Not yet supported:

> The current prompt/schema design generalizes beyond the development split.

## Key Artifacts

- Strategy:
  `docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`
- Clinical-recovery scorer plan:
  `docs/plans/exectv2/10_clinical_recovery_scorer_build_plan.md`
- Single structured v0.5 pilot:
  `docs/experiments/exectv2/key_entities/exectv2_key_entities_structured_v05_pilot_report_2026-06-18.md`
- dev140 transfer readout:
  `docs/experiments/exectv2/key_entities/exectv2_key_entities_dev140_transfer_readout_2026-06-18.md`
- dev140 clinical ledger:
  `docs/experiments/exectv2/key_entities/exectv2_key_entities_dev140_clinical_error_ledger_readout_2026-06-18.md`
- Medication/Investigations verifier:
  `docs/experiments/exectv2/medication_investigations/exectv2_med_inv_verifier_v01_dev140_report_2026-06-18.md`
- Investigations verifier:
  `docs/experiments/exectv2/medication_investigations/exectv2_investigations_verifier_v01_dev140_report_2026-06-18.md`
- Diagnosis reconciler:
  `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_reconciler_v02_dev140_report_2026-06-18.md`
- SeizureFrequency state adjudicator:
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_state_adjudicator_v05_dev140_report_2026-06-18.md`
- Diagnosis ceiling note:
  `docs/research/exectv2_diagnosis_ceiling_note_2026-06-18.md`
- SF v0.6 state projection and hard-slice readout:
  `docs/research/exectv2_sf_state_projection_v06_readout_2026-06-18.md`
