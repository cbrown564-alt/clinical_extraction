> **Superseded for navigation —** canonical summary: [`HOLISTIC_ASSEMBLY_LADDER_CANON.md`](HOLISTIC_ASSEMBLY_LADDER_CANON.md). Full detail retained below.

# ExECTv2 Holistic Finding Assembly v02 Diagnosis Phase 1 Error Analysis

- Date: `2026-06-21`
- Split/stage: `dev` / `dev140`
- Baseline: `exectv2_holistic_finding_assembly_v01_dev140`
- Candidate: `exectv2_holistic_finding_assembly_v02_dev140`
- Model source: frozen Diagnosis producer `openai/gpt-4.1-mini`; v02 adds one deterministic `clinical_epilepsy` lens rule.
- Claim boundary: dev-only row-level development analysis. This does not authorize full-200, holdout, or benchmark claims.

## Phase Question

Diagnosis is the weakest family in the holistic assembly (`0.7572` headline in
v01). The first phase asked whether row-level residuals could be improved by
transparent lens behavior over the existing GPT-4.1-mini Diagnosis route before
spending new live calls.

## Baseline v01

| Family | Headline F1 | P | R | Main residual |
| --- | ---: | ---: | ---: | --- |
| Diagnosis | 0.7572 | 0.7346 | 0.7811 | concept selection: generic epilepsy over-emission plus focal/syndrome/seizure-type misses |
| SeizureFrequency | 0.8068 | 0.7717 | 0.8452 | state correct more often than rate magnitude; active-rate fidelity only 0.3931 |
| Prescription | 0.8214 | 0.8090 | 0.8342 | dose/frequency and rescue/future-regimen distinctions |
| Investigations | 0.8615 | 0.9032 | 0.8235 | EEG/MRI result and performed/result pair misses |

Strict diagnosis concept+assertion ledger was lower (`0.6934`), so diagnosis
remains fragile even where the declared headline forgives some assertion detail.

## Row-Level Diagnosis Findings

The v01 residual ledger showed two coupled failure modes:

1. Over-emission: generic `epilepsy` (`55` strict over-emissions) and `tonic clonic seizures` (`26`) are emitted from weak or over-broad evidence.
2. Misses: generic `epilepsy` (`17` strict misses), `focal epilepsy` (`7`), secondary-generalised and tonic-clonic seizure-type concepts (`6` each), plus syndrome-level concepts such as JME and symptomatic epilepsy.

Simple precision pruning did not solve this:

| Ablation | Diagnosis F1 | Delta | Decision |
| --- | ---: | ---: | --- |
| v01 baseline | 0.7572 | - | control |
| Drop generic epilepsy from weak context such as `epilepsy nurse` | 0.7584 | +0.0012 | reject as insufficient |
| Keep generic epilepsy only in strong assertion contexts | 0.7491 | -0.0081 | reject; recall loss |
| Drop weak tonic-clonic contexts | 0.7436 | -0.0136 | reject; recall loss |
| Naive Diagnosis/Seizure-type heading candidate insertion | 0.7386 | -0.0186 | reject; many plausible but unscored FPs |
| Add only absent non-generic heading concepts | 0.7387 | -0.0185 | reject; selector still needed |
| Add only `focal epilepsy` explicitly present in `Diagnosis:` heading | 0.7658 | +0.0086 | accept as v02 lens |

## v02 Result

v02 introduces `diagnosis_heading_recovery_v02`, which adds a Diagnosis mention
only when the `Diagnosis:` heading explicitly contains `focal epilepsy`. The rule
is recorded as prediction-bearing `clinical_epilepsy` provenance, not as format
normalization.

| View | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| v01 clinical headline | 0.8006 | 0.7572 | 0.8068 | 0.8214 | 0.8615 |
| v02 clinical headline | 0.8038 | 0.7658 | 0.8068 | 0.8214 | 0.8615 |

Changed rows versus v01: `10` Diagnosis rows. Prescription, Investigations, and
SeizureFrequency are unchanged.

## Remaining Error Surface After v02

Diagnosis remains far from `>0.9`. Strict residuals still show:

- Generic `epilepsy` is both the largest miss (`17`) and largest over-emission (`55`).
- Tonic-clonic/seizure-type policy remains unresolved: `tonic clonic seizures` has `6` strict misses and `26` over-emissions.
- Focal-family recovery improved, but focal epilepsy still appears as an over-emission family after structural/symptomatic focal epilepsy normalization.
- Syndrome and subtype mentions such as JME, symptomatic epilepsy, focal seizures with altered awareness, and secondary-generalised seizures need a selector that understands the annotation policy.

The saved-candidate union is not enough: unioning current dev140 Diagnosis
candidate artifacts increases recall but precision collapses, and common gold
concepts remain absent. The next useful step is therefore not broader
deterministic heading insertion.

## Hypotheses For Phase 2

H2: A GPT-4.1-mini diagnosis policy selector can improve generic epilepsy and
tonic-clonic decisions if it is given fixed candidate groups plus explicit
annotation-policy questions. Existing v0.2 grouping did not transfer enough, so
the next selector should be residual-slice first, not full dev140 first.

H3: Some misses require direct re-reading, not candidate selection. Test with a
25-row residual-enriched panel where GPT-4.1-mini may emit concepts absent from
the verifier/decomposer pool, but must quote exact evidence and classify each
concept family.

H4: Deterministic clinical-epilepsy rules should stay narrow unless a term-level
ablation proves positive. The only accepted rule in this phase is explicit
`Diagnosis:` heading `focal epilepsy`; broader heading and seizure-type rules
hurt precision.

## Next Gate

Run a predeclared Diagnosis Phase 2 panel before any dev140 spend:

- rows: dev-only residual-enriched 25 to 40 letters, sampled from generic epilepsy,
  tonic-clonic, focal-family, and syndrome misses/over-emissions;
- model: `openai/gpt-4.1-mini`;
- outputs: candidate selector versus direct re-reader ablation, row-level error
  ledger, changed-row accounting, and same v01/v02 controls;
- promote to dev140 only if the panel shows net W->C without broad new FP
  families, especially for generic epilepsy and tonic-clonic concepts.

