# ExECTv2 - Family-Routed LLM-First Essential Comparison - Predeclaration

Date: 2026-06-18
Status: AUTHORIZED for pilot25 -> dev140 dev ladder; full-200/test audit blocked
Split: dev ladder only (`pilot25` -> `dev140`); full-200/test audit blocked
Model: gpt-4.1-mini unless explicitly version-pinned before execution
Plan: `docs/plans/exectv2/11_llm_first_essential_clinical_evaluation_plan.md`

## Purpose

This predeclares the next ExECTv2 LLM-first comparison after the Plan 11
analysis-only replay. The current evidence shows that a single all-entities LLM
pass is a useful clinical-detail extractor for some families, but the wrong
decision unit for SeizureFrequency:

| Family | Single all-entities LLM-first dev140 F1 | Current read |
| --- | ---: | --- |
| Prescription | 0.747 | usable LLM-owned broad-pass component |
| Investigations | 0.748 | usable LLM-owned broad-pass component |
| Diagnosis | 0.316 | weak but retained as concept-selection component |
| SeizureFrequency | 0.012 | collapsed; requires event/state route |
| EpilepsyCause | 0.000 | diagnostic only in this comparison |

The comparison tests whether a family-routed LLM-first architecture improves the
essential clinical headline while preserving ownership discipline:

```text
letter
  -> shared single pass for Prescription, Investigations, Diagnosis
  -> SF event/state route for SeizureFrequency
  -> deterministic evidence validation
  -> deterministic certainty, CUI, and benchmark-format projection
  -> ownership-aware clinical and projection readouts
```

This is not a new full benchmark claim. It is a dev-stage architecture
comparison that decides whether the routed design is worth freezing later.

## Architecture Ownership

The routed candidate has owner label `llm_first` only if the LLM selects the
prediction-bearing clinical facts for every routed family:

| Component | Prediction-bearing owner | Allowed deterministic work | Disallowed deterministic work |
| --- | --- | --- | --- |
| Prescription/Investigations/Diagnosis shared pass | LLM | JSON/schema validation, exact evidence gate, format-preserving normalization, CUI/certainty/benchmark projection | introducing or choosing a medication, investigation, or diagnosis concept absent from the LLM output |
| SeizureFrequency event/state route | LLM | schema repair, evidence gate, arithmetic over selected count/range facts, accepted-label rendering, CUI projection | introducing seizure state, temporal anchor, seizure type, or count/range not selected by the LLM |
| Certainty/negation | deterministic adapter | guideline-rule projection after clinical fact selection | using certainty rules to select the clinical concept |
| CUI | deterministic adapter | finite lexicon/result-conditioned projection after clinical fact selection | using CUI lookup to replace or select the clinical concept |

If the SF route uses deterministic candidate generation followed by LLM
adjudication, the component must be reported as `hybrid_sf_route` in secondary
tables unless the final schema worker documents that candidates are only
non-prediction-bearing scaffolds. If deterministic code changes the selected SF
state, the routed candidate is no longer a clean `llm_first` comparison.

## Split Discipline

- `pilot25` is for output-contract, parse, evidence, and catastrophic route
  failures only.
- `dev140` is the primary development comparison.
- No Gan `test450`, ExECTv2 full-200/test row-level artifacts, holdout evidence,
  holdout rationales, or holdout error rows may be inspected for this work.
- No full-200/test audit may run from this predeclaration. A later full-200
  audit requires benchmark-beating dev evidence and a separate frozen protocol.
- No model-call output may be used to tune after a frozen test protocol is
  authorized.

## Inputs And Artifacts

### Inputs

- Gold/dev split manifest and dev140 letters only.
- Current Plan 11 essential scorer and layer ladder.
- Existing single all-entities LLM artifact as baseline:
  `experiments/exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl`,
  filtered to dev only.
- Current deterministic and hybrid comparators from the Plan 11 replay.
- SF event/state schema from the parallel schema worker, once finalized.

### Produced artifacts

The execution should write artifacts with names that make ownership and split
plain, for example:

```text
experiments/exectv2_family_routed_llm_first_dev140_gpt41mini_YYYYMMDD.jsonl
experiments/exectv2_family_routed_llm_first_dev140_gpt41mini_YYYYMMDD.md
experiments/exectv2_family_routed_llm_first_dev140_gpt41mini_YYYYMMDD.json
```

The JSON/JSONL artifact must preserve, at minimum:

- input letter id and split;
- raw shared-pass output for Prescription, Investigations, and Diagnosis;
- raw SF event/state route output;
- exact evidence strings and evidence-validation status;
- parser/schema repair status by family;
- deterministic projection outputs for certainty, CUI, and benchmark rendering;
- ownership labels by component and for the aggregate candidate;
- dropped/invalid-output records, never silently discarded.

## SF Schema Assumptions Pending Integration

The parallel SF worker owns the final event/state schema. This predeclaration
assumes only the following contract:

- The SF route emits one or more source-grounded event/state records.
- Each record has an evidence field that can be checked as an exact source
  substring or explicitly marked source-near by a deterministic validator.
- The record can represent at least: seizure type or type text, frequency state
  (`active`, `seizure_free`, `unknown`, or final schema equivalents), count or
  range operands, denominator/period, temporal anchor, and assertion/state
  rationale.
- The schema separates extraction fields from benchmark projection fields. It
  does not ask the model for CUI.
- Unknown-state handling is explicit. Any suppression, merging, or defaulting of
  unknown states must be named and reported as deterministic post-LLM behavior.

If the final SF schema uses different field names, nested state transitions, or
claim-table rows instead of flat events, the execution may adapt field mappings
without changing this comparison's gate, provided the ownership rules above
remain intact.

## Primary Metrics

The primary headline is CUI-free essential clinical recovery on dev140 for the
four routed families:

- Prescription
- Investigations
- Diagnosis
- SeizureFrequency

The primary comparison table must include:

| Candidate | Ownership | Routed families | Essential F1 | Precision | Recall |
| --- | --- | --- | ---: | ---: | ---: |
| deterministic_all9 | `rules_only` | all available | tbd | tbd | tbd |
| llm_only_all_entities | `llm_first` | single broad pass | 0.422 five-family prior; recompute four-family routed set | tbd | tbd |
| hybrid_all_entities | `hybrid` | candidate-set + verify | 0.550 five-family prior; recompute four-family routed set | tbd | tbd |
| family_routed_llm_first | `llm_first` or qualified label | shared pass + SF route | tbd | tbd | tbd |

Primary family-level readout:

| Family | Baseline single-pass F1 | Routed F1 | Delta | Precision | Recall | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Prescription | 0.747 | tbd | tbd | tbd | tbd | preserve broad-pass utility |
| Investigations | 0.748 | tbd | tbd | tbd | tbd | preserve broad-pass utility |
| Diagnosis | 0.316 | tbd | tbd | tbd | tbd | concept-selection diagnostic |
| SeizureFrequency | 0.012 | tbd | tbd | tbd | tbd | event/state route test |

EpilepsyCause remains diagnostic in this comparison unless a separate targeted
route is predeclared. It must not be hidden if included in aggregate companion
tables, but it does not decide this routed architecture gate.

## Secondary Metrics

Secondary readouts must include:

- CUI-projected companion F1, with the CUI-free/CUI-projected delta reported as
  deterministic projection loss.
- Evidence presence and exact evidence rate by family.
- Parse/schema failure rate by route and by family.
- Repair rate by field family, separating JSON/schema repair from clinical
  semantic changes.
- Certainty/negation projection accuracy or carry-forward Plan 11 audit numbers
  when no new certainty-bearing family is added to the primary headline.
- Error taxonomy counts: candidate miss, wrong detail selection, evidence
  failure, projection gap, duplicate/over-emission, and SF state/temporal-anchor
  errors.
- Letter-level bootstrap confidence intervals for aggregate dev140 readouts when
  the implementation already supports them; otherwise mark as deferred, not
  omitted.

## Promotion Gates

The routed candidate may be promoted from `pilot25` to `dev140` only if:

- zero unexplained model-call failures;
- zero systemic parse/schema failures;
- every emitted prediction is either evidence-validated or explicitly marked and
  counted as evidence-invalid;
- no deterministic stage introduces a prediction-bearing clinical fact.

The routed candidate may be considered a viable architecture only if dev140
shows all of the following:

- aggregate four-family CUI-free essential F1 exceeds the single broad
  all-entities LLM-first baseline on the same four-family surface;
- Prescription and Investigations do not regress by more than 0.03 absolute F1
  from the single-pass baseline unless the error ledger shows a scorer/projection
  artifact rather than a clinical-detail loss;
- SeizureFrequency improves materially over the single-pass collapse and reaches
  at least 0.60 CUI-free clinical F1, or the readout explains why the event/state
  schema failed before any further SF route work;
- evidence exactness remains >= 0.95 for emitted predictions overall and is
  reported by family;
- ownership remains `llm_first` for the claimed headline, or the readout
  explicitly downgrades the candidate to `hybrid`/qualified ownership.

The routed candidate may be considered for a future frozen full-200 audit only
if a later dev readout clears benchmark-comparable targets on a predeclared
headline and includes a separate full-200 protocol. This document does not
authorize that audit.

## Blocked Full-200 Policy

Full-200/test work remains blocked even if the routed dev140 result improves the
single-pass baseline. To unblock it, a separate predeclaration must specify:

- exact architecture, prompt/schema versions, projection adapters, and artifact
  hashes;
- the benchmark headline and companion clinical headline;
- aggregate-only holdout readout tables;
- no row-level holdout tuning, no repeated holdout calls, and no post-hoc schema
  changes;
- what happens if parse, call, or projection failures occur during the one
  frozen audit.

Until then, all results from this routed comparison are development evidence
only.

## Planned Readout Tables

### Table 1: Architecture Ownership

| Candidate | Owner | Prediction-bearing component | Deterministic adapters | Claim allowed |
| --- | --- | --- | --- | --- |
| deterministic_all9 | rules_only | deterministic rules | scorer/projection | baseline |
| llm_only_all_entities | llm_first | single broad LLM pass | evidence/CUI/certainty/rendering | negative baseline |
| hybrid_all_entities | hybrid | candidate-set + verifier | projection/rendering | comparator |
| family_routed_llm_first | tbd | shared pass + SF route | evidence/CUI/certainty/rendering | tbd |

### Table 2: Aggregate Essential Clinical Recovery

| Candidate | Families | CUI-free F1 | Precision | Recall | CUI-projected F1 | Evidence exact |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| deterministic_all9 | routed four | tbd | tbd | tbd | tbd | tbd |
| llm_only_all_entities | routed four | tbd | tbd | tbd | tbd | tbd |
| hybrid_all_entities | routed four | tbd | tbd | tbd | tbd | tbd |
| family_routed_llm_first | routed four | tbd | tbd | tbd | tbd | tbd |

### Table 3: Per-Family Recovery

| Family | Single-pass F1 | Routed F1 | Delta | Evidence exact | Dominant residual |
| --- | ---: | ---: | ---: | ---: | --- |
| Prescription | 0.747 | tbd | tbd | tbd | tbd |
| Investigations | 0.748 | tbd | tbd | tbd | tbd |
| Diagnosis | 0.316 | tbd | tbd | tbd | tbd |
| SeizureFrequency | 0.012 | tbd | tbd | tbd | tbd |

### Table 4: SF Event/State Diagnostics

Final columns may change with the SF schema, but the readout must include the
same concepts:

| SF diagnostic | Count or rate | Notes |
| --- | ---: | --- |
| emitted event/state records | tbd | by letter and total |
| exact evidence records | tbd | source-substring check |
| active/seizure-free/unknown distribution | tbd | final schema labels allowed |
| count/range parseable | tbd | operands and denominator present |
| temporal anchor present | tbd | source-grounded |
| state/temporal-anchor errors | tbd | row-level dev only |
| deterministic unknown suppression/defaulting | tbd | must be named if present |

### Table 5: Projection And Error Ledger

| Candidate | candidate miss | wrong detail selection | evidence failure | CUI projection gap | certainty/projection gap | over-emission |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| llm_only_all_entities | tbd | tbd | tbd | tbd | tbd | tbd |
| family_routed_llm_first | tbd | tbd | tbd | tbd | tbd | tbd |

## Claim Language

Supported if the dev gates pass:

> A family-routed LLM-first architecture improves ExECTv2 essential clinical
> recovery over the single all-entities prompt by using a shared broad pass for
> medication, investigations, and diagnosis while routing SeizureFrequency to an
> event/state decision unit.

Supported only if ownership remains clean:

> The routed headline is LLM-first: deterministic stages validate evidence and
> project guideline/benchmark formats but do not choose the clinical facts.

Not supported from this predeclaration:

> The routed architecture is benchmark-complete.

Not supported unless a later frozen audit is authorized and run:

> The routed architecture generalizes to the full-200/test surface.
