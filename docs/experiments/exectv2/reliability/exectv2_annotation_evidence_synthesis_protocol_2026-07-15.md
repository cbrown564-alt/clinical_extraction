# ExECTv2 annotation-evidence synthesis protocol

Date: 2026-07-15  
Status: complete no-call evidence synthesis; predeclared before generation  
Mode: permitted-development evidence consolidation

## Primary question

Can the retained annotation records be combined into one reproducible taxonomy
that identifies each cited case's defect, convention, ambiguity, multiplicity,
scoring effect, handling, sensitivity treatment, and review status without
changing gold, any scorer, or the strength of the clinical claim?

This matters because the current retained package contains the underlying
ledgers and row analyses but does not provide one traceable view of how each
finding affects evaluation or how strongly it was reviewed.

## Data and inspection policy

- Dataset: ExECTv2 2025 permitted development evidence. Any cross-task record
  retained in `gold_data_issues.jsonl` must keep its own named dataset and split.
- ExECT row inspection is restricted to `dev140` and already retained review
  artifacts. Test60 must not be read.
- No model calls, new clinical adjudication, gold edits, or scorer edits are
  permitted.
- The retained-evidence manifest owns the exact input files and hashes. The
  synthesis must fail if a declared source is missing or its recorded hash does
  not match.

## Candidate and comparator

- Comparator: the current fragmented annotation package: four entity ledgers,
  `gold_data_issues.jsonl`, the canonical Seizure Frequency and Diagnosis row
  analyses, the blind re-review, the completed Diagnosis review, and its fixed
  sensitivity results.
- Candidate: a generated JSON artifact and concise narrative report that join
  those records through stable source and case identifiers.
- Component under study: evidence organization only. No extraction, repair,
  normalization, projection, or scoring component may change.

## Measures and required analysis

Primary completeness checks:

1. every input selected by the annotation-quality manifest entry is registered;
2. every explicitly cited letter or review key that can be mechanically located
   is represented with its source;
3. each taxonomy entry states issue class, score treatment, handling, sensitivity
   treatment, review method, and clinical-review boundary;
4. source totals used in the report reconcile with the retained artifacts; and
5. unresolved or historically superseded evidence is labelled rather than
   silently combined with the completed 2026-07-14 Diagnosis review.

Required slices are Diagnosis, Seizure Frequency, Prescription,
Investigations, cross-family defect records, scoring artifacts, internal review,
blind re-review, and independent-clinical-review status.

## Artifact schema

The machine-readable artifact must contain:

- synthesis date, source-commit or dirty-tree note, and schema version;
- source path, recorded SHA-256, observed SHA-256, dataset, split, and row policy;
- one entry per cited case or aggregate evidence statement with a stable ID;
- family, letter/review key when available, issue class and mechanism;
- original-score treatment, handling, and sensitivity treatment;
- review method, review status, provenance limit, and clinical-review state;
- source statement or structured source fields sufficient to audit the mapping;
- aggregate reconciliations and unresolved limitations.

## Stop rule and claim boundary

Accept the synthesis only if every retained source is hash-checked, all
mechanically identifiable cited cases are mapped, and the reported totals
reconcile. If a narrative claim cannot be linked to a stable case identifier,
retain it as aggregate evidence with that limitation. Do not infer missing
clinical judgments.

A positive result is a reproducibility and evidence-handling result for retained
development artifacts. It may support a bounded statement that some measured
ExECT disagreements involve annotation defects, conventions, ambiguity,
multiplicity, or scoring representation. It cannot establish corrected gold,
clinical validity, test60 performance, holdout generalization, or the prevalence
of these mechanisms outside the inspected records. Independent clinical review
remains required for clinical-validity claims.

## Result

The generator hash-checked all 13 retained sources and produced 584 overlapping
taxonomy records: 334 historical family-ledger cases, 246 current Diagnosis
review cases, and four direct gold issues. All 57 letter IDs explicitly cited in
the retained narrative reports map to a taxonomy record. Gold and all scorers
remain unchanged, no model call occurred, and test60 was not read.

The historical Diagnosis narrative reports 209 concept disagreements while its
selected generated ledger contains 199 rows. The ten unavailable concept rows
remain aggregate-only rather than being reconstructed. The full result and
claim boundary are in the
[annotation-evidence synthesis](exectv2_annotation_evidence_synthesis_2026-07-15.md).
