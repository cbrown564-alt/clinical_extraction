# ExECTv2 dev140 Error-Led Architecture Decision

Date: 2026-06-20

## Decision

Do not spend the next iteration on projection-family promotion or another
single broad prompt revision. The next predeclared architecture move is a
component-evidence comparison that preserves the strongest current
Prescription/Investigations lanes, then tests focused Diagnosis and
SeizureFrequency lanes on the same dev140 source set with explicit ownership,
evidence, and regression accounting.

Required candidate shape:

- Prescription: preserve the current strongest clinical-headline lane as a
  control, currently v0.42 single-call headline `0.8214` and prior verifier
  evidence up to `0.817`.
- Investigations: preserve the current strongest clinical-headline lane as a
  control, currently v0.42 single-call headline `0.8615` and prior verifier
  evidence up to `0.872`.
- Diagnosis: use a focused diagnosis lane, not the broad single-call output.
  The lane should separate diagnosis-heading decomposition, narrative
  seizure-type collection, and reconciliation, then report negation-aware
  scoring.
- SeizureFrequency: use a focused candidate span/state adjudicator, not broad
  single-call extraction. The lane should classify candidate spans into
  `active-rate`, `seizure-free`, `unknown`, or `reject`, and carry an explicit
  text-anchor normalization field.

The predeclaration must include the exact candidate sources, runtime/model,
score surfaces, and stop rule before any additional live calls.

## Evidence Compared

### v0.42 local-Qwen default-quarantine dev140

Source:
`experiments/exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.md`.

This condition is useful as a same-source, default-quarantined diagnostic, but
not as promotion evidence.

| Surface | Value |
| --- | ---: |
| Headline | 0.7153 |
| Benchmark | 0.2339 |
| Diagnosis.concept_negation | 0.6693 |
| SeizureFrequency.active_rate_fidelity | 0.2887 |

Indicator headline scores: Diagnosis `0.6693`, SeizureFrequency `0.5572`,
Prescription `0.8214`, Investigations `0.8615`. The gate summary includes 1
call failure, 4 parse/schema failures, and 21 evidence-invalid mentions dropped.

Same-raw projection-family ablation:
`docs/experiments/exectv2/key_entities/exectv2_phase3_family_ablation_same_raw_dev140_qwen36_35b_20260620.md`.

`audit_all` moves benchmark only `0.2339 -> 0.2383`; every positive
single-family effect fires on exactly one dev140 letter. This rules out
projection-family restoration as the next architecture move.

### Deterministic and focused-route comparators

Source:
`docs/experiments/exectv2/key_entities/exectv2_adr0030_target_indicator_report_20260619.md`.

| Candidate | Overall target F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| deterministic_all9 | 0.7301 | 0.7302 | 0.7277 | 0.9072 | 0.5263 |
| family_routed_with_focused_diagnosis_route | 0.7081 | 0.7127 | 0.6321 | 0.7472 | 0.7475 |
| v0.42 default-quarantine single-call | 0.7153 | 0.6693 | 0.5572 | 0.8214 | 0.8615 |

Interpretation: no single existing route dominates. Deterministic_all9 remains
the strongest Diagnosis, SeizureFrequency, and Prescription comparator by the
older target report, while v0.42 gives the best current Investigation headline
and a better Prescription/Investigation clinical-headline read. The focused
Diagnosis route shows that specialized lanes can recover broad single-call
Diagnosis failures, but it remains dev-only and ownership-qualified.

## Failure Categories

The dev-only ledger after Diagnosis v0.6 and SeizureFrequency v0.4 remains the
best current failure taxonomy:
`experiments/exectv2_key_entities_clinical_error_ledger_diagv06_sfv04_dev140_20260618.md`.

Diagnosis v0.6 score is `0.651`. Top miss families are affirmed generic
epilepsy (`57`), tonic-clonic seizure concepts (`11`), focal seizures (`8`),
focal epilepsy (`7`), and certainty or hierarchy variants. Top over-emissions
include tonic-clonic seizures (`12`), absences (`8`), focal epilepsy certainty
variants (`5`), focal seizures (`4`), and generic epilepsy certainty variants
(`3`). This is a hierarchy, assertion, and duplicate-reconciliation problem,
not just evidence recall.

SeizureFrequency v0.4 score is `0.623`. Top misses are generic seizures with
unknown (`14`), seizure-free (`10`), and active-rate (`7`) states, plus named
tonic-clonic and absence state variants. Top over-emissions are generic seizure
active-rate (`10`), generic seizure unknown (`10`), tonic-clonic active-rate
(`6`), seizure-free (`6`), and generic seizure-free (`5`). This is a state
classification and generic-vs-specific seizure-type projection problem.

The later v0.7 SF ledger improves the SF headline to `0.782`, but residuals
still concentrate in state splits: gold residuals `17` active-rate, `11`
seizure-free, `8` unknown; predicted residuals `19` active-rate, `17`
seizure-free, `12` unknown. That supports a candidate span/state adjudicator
with changed-row accounting rather than more prompt accretion.

## Required Predeclaration

Before running the next live dev140 experiment, write a predeclaration that
specifies:

- Candidate sources: exact JSONL inputs for the preserved P/I lanes, focused
  Diagnosis lane, and focused SF lane.
- Component owners by subproblem: model-owned clinical selection versus
  deterministic adapter, projection, safety floor, or benchmark format.
- Score ladder: raw model, evidence-valid scored output, CUI/projection layer,
  headline, benchmark, `Diagnosis.concept_negation`, and
  `SeizureFrequency.active_rate_fidelity`.
- Comparator: v0.42 default-quarantine single-call plus deterministic_all9 and
  the existing focused-route dev140 artifacts where available.
- Gates: exact selected evidence, same-source row set, no P/I regression beyond
  `0.01` absolute headline F1, no unreported deterministic semantic replacement,
  and changed-row evidence accounting for Diagnosis and SF.
- Stop rule: promote only if Diagnosis and SF both beat the preserved
  focused-route comparators on the declared fidelity companions, without
  degrading P/I controls; otherwise revise the failing lane or add
  instrumentation before another broad run.

## Claim Language

This decision affects architecture and reporting, not paper-comparable
performance. The current best claim is:

> On dev140, projection-family replay does not justify restoring quarantined
> deterministic repair families. The error-led next step is a hybrid,
> component-attributed focused-lane comparison with P/I controls, Diagnosis
> hierarchy reconciliation, and SF span/state adjudication.

No full-200 or locked-test-facing audit is authorized by this read.
