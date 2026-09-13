# ExECTv2 semantic-support review substrate protocol

Date: 2026-07-20
Status: simplified first-round rubric frozen; independent review not started

## Question

Is the extracted clinical finding supported by the cited text and supplied
letter context?

This is separate from the exact-evidence check. Exact source presence is an
eligibility condition for the sample, not a positive semantic-support label.

## Data boundary

- Dataset: ExECTv2.
- Split: manifest `dev140` only.
- Row inspection: permitted development rows.
- Models: the fixed six-model comparison roster.
- Families: Diagnosis, Seizure Frequency, Prescription, and Investigations.
- Stage: final assembled finding.
- Model calls: none.
- `test60`: excluded by source path and validation checks.

The generated substrate does not copy the complete letter text. It records the
letter identifier, selected conclusion, exact evidence text, assertion,
attributes, rationale, component owner, fact origin, and retained source
identity. A governed review session may retrieve full dev140 context when the
reviewer needs it.

## Sampling rule

Eligible items are final findings with `evidence_valid=true` and non-empty
evidence. Within each model-family stratum, findings are ordered by SHA-256 of:

```text
runtime model | family | letter ID | finding ID
```

The first two findings from distinct letters are selected. This produces 48
items: six models × four families × two findings. Automated correctness,
confidence, and future review labels do not affect selection.

The sample is intended to prepare a bounded independent review, not estimate a
clinical prevalence or support a model ranking. A future protocol must justify
a larger or outcome-stratified sample before making those claims.

## Review fields

The first-round review deliberately collects only:

- `clinical_support`: whether the extracted finding is clinically supported;
- `review_notes`: optional source-based context that may help later analysis;
- reviewer identity and review date.

`clinical_support` allows exactly `supported`, `unsupported`, or `unclear`.
Use `unclear` whenever the supplied text permits more than one reasonable
judgment or does not contain enough information to decide. Notes remain
optional for every value. If the first-round results are ambiguous, a later
predeclared protocol may introduce a more detailed schema; this review must
not infer those additional dimensions after collection.

Two named clinical reviewers should review all 48 items independently without
seeing model scores, gold correctness, or the other reviewer's decisions. A
matching `clinical_support` value is accepted provisionally. A disagreement is
unresolved until a third named clinical reviewer records an adjudication after
reading both reviewers' optional notes. The final export must retain both
original decisions, every revision, and the adjudication; it must never rewrite
the sampling substrate.

The builder deliberately leaves every field null and rejects a substrate that
contains review conclusions while its status is pending. The local review API
stores decisions in a separate revisioned SQLite database and returns only the
named reviewer's decisions during independent review.

## Fast-review workflow

1. Review the selected conclusion and cited evidence before opening the full
   letter. Use the full letter whenever assertion, timing, or clinical context
   is not explicit in the excerpt.
2. Record one support judgment. Add a concise source-based note only when it is
   useful.
3. Save and advance. Reviewers may revise a decision; revisions remain in the
   audit log.
4. Export each completed reviewer file separately. Do not compare reviewers or
   calculate agreement until both independent queues are complete.

## Generation and checks

```powershell
.venv\Scripts\python.exe scripts\build_exectv2_semantic_support_review_substrate.py
.venv\Scripts\python.exe scripts\build_exectv2_semantic_support_review_substrate.py --check
```

The check requires all 24 model-family strata, two distinct letters per
stratum, exact source hashes, dev140-only sources, and null review fields.

## Claim boundary

The generated file is an unreviewed development sampling substrate. It is not
semantic-support evidence, an independent clinical review result, clinical
validation, a six-model comparative faithfulness result, or permission to
inspect `test60`.
