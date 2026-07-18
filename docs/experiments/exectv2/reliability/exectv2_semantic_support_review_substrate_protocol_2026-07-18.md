# ExECTv2 semantic-support review substrate protocol

Date: 2026-07-18  
Status: substrate prepared; independent review not started

## Question

Does the cited text sufficiently and decisively support the final clinical
conclusion, including its assertion and temporal status?

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

An independent clinical reviewer must complete:

- `semantic_support`: whether the evidence supports the selected conclusion;
- `evidence_decisive`: whether the evidence is sufficient rather than merely
  compatible;
- `current_fact_warranted`: whether temporal and assertion status are
  warranted;
- `unsupported_inference`: whether the conclusion adds unsupported clinical
  meaning;
- reviewer identity, review date, and notes.

Allowed values and an adjudication rule must be frozen before review begins.
The builder deliberately leaves every field null and rejects a substrate that
contains review conclusions while its status is pending.

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
