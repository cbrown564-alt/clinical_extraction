# ExECTv2 Diagnosis interpretation audit protocol

Date: 2026-07-14  
Status: completed; results owned by the component comparison
Track: ExECTv2 development evidence

## Primary question

Are the paper's Diagnosis conclusions stable under explicit interpretations of
concept identity, multiplicity, certainty, negation, and clinically equivalent
diagnosis wording?

This matters because the retained LLM-only row analysis found 209 Diagnosis
concept disagreements and attributed many to annotation multiplicity or
representation. A blinded internal sample reproduced individual verdicts only
moderately well (60% raw agreement; unweighted kappa 0.389). The existing result
therefore supports a limited mechanism claim, but not a precise corrected F1 or
clinical validation.

## Data and inspection policy

- Dataset: ExECTv2 2025 broad epilepsy phenotyping corpus.
- Split: `dev140` (`dev` in the split manifest); all 140 rows may be inspected.
- Row policy: use only the dev letter identifiers. Never read or derive
  disagreement rows from `test60` or full-corpus artifacts.
- Source text and gold: repository ExECTv2 dev records, unchanged.
- Calls: none. Deterministic predictions may be regenerated locally; model
  predictions must be replayed from saved JSONL artifacts.
- Repository state at predeclaration: commit
  `6277796a0f4a8ee2afe793e6f1dd33a20c2e5ad2` with an existing dirty working tree.
  The audit must record hashes for every consumed prediction artifact.

## Fixed methods

| Method | Fixed input | Role |
| --- | --- | --- |
| Rules only | current deterministic all-nine extractor, regenerated on dev140 with no calls | Retained architecture comparator |
| LLM only | `experiments/exectv2_gepa_dedup_gpt41mini_h2mb8_20260628.jsonl` | Retained negative development comparator |
| LLM with rules | `experiments/exectv2_holistic_finding_assembly_v08_dev140_p7_treatment_20260702.jsonl` | Historical development performance control |

The audit compares interpretations of fixed outputs. It must not tune, repair,
or rerun a model. The GEPA method used an optimizer-only development sub-split;
its result remains a development comparator, not benchmark-cleared evidence.

The completed result is recorded in the
[component comparison](exectv2_diagnosis_component_comparison_2026-07-14.md).
The `v08` input remains valid for this fixed-output Diagnosis audit, but its
other family paths do not satisfy the final model-led contract in
[decision 0040](../../../decisions/0040-final-exect-llm-with-rules-family-ownership.md).

## Scoring and study component

The fixed primary scorer is the existing Diagnosis `clinical_headline`
`concept_only` scorer. It uses entity-agnostic recall, home-tagged precision,
within-letter concept de-duplication, current concept normalization, and current
Diagnosis ancestor/descendant reconciliation.

The component under study is interpretation of the remaining Diagnosis
disagreements after that scorer. No deterministic safety floor, prompt change,
gold edit, or scorer change is allowed in this study.

Secondary fixed diagnostics are:

- `concept_negation`;
- `concept_assertion`;
- counts of unresolved missed and spurious concept units by method;
- method overlap in the union disagreement population;
- phrase, CUI, diagnostic category, certainty, negation, span, duplicate, and
  overlap fields carried into the review record.

## Audit population

For each method, decompose its dev140 Diagnosis `concept_only` result into
unresolved missed and spurious concept units using the same normalization,
specificity collapse, hierarchy relation, recall pool, and home-tagged precision
policy as the fixed scorer.

Construct the review population as the union of those units. The stable review
key is:

`letter_id + direction + normalized_concept`

Record every method in which that key occurs. Preserve method-specific source
mentions because the same normalized concept may arise from different phrases,
attributes, evidence, or source entities.

## Machine-readable artifact

The primary artifact is JSONL with one row per union review key. Each row must
contain:

- schema version, audit date, dev split, and row-inspection policy;
- stable review key and source letter identifier;
- disagreement direction and normalized concept;
- participating methods and method-specific scorer role;
- complete gold Diagnosis mentions;
- relevant method-specific prediction mentions, including source entity;
- selected phrase, CUI, diagnostic category, certainty, negation, evidence, and
  evidence validity when present;
- source offsets and raw gold span where available;
- duplicate or overlapping mention indicators that can be computed without
  clinical judgment;
- adjudication fields initialized to `unreviewed` rather than inferred.

The summary JSON must record input hashes, row counts, exact scorer identities,
per-method primary and secondary scores, disagreement counts, union size, and
method intersections. A narrative report may only summarize values reproducible
from these machine-readable artifacts.

## Adjudication fields

Reviewers must answer observable questions before assigning an error owner:

1. Is the concept supported by the note: `yes`, `no`, or `uncertain`?
2. Do gold and prediction express the same clinical concept: `yes`, `no`, or
   `uncertain`?
3. Is the difference explained by the benchmark's multiplicity convention:
   `yes`, `no`, or `unclear`?
4. Do certainty and negation agree with the note?
5. Is the difference only phrase, CUI, category, span, duplicate, or hierarchy
   representation?
6. Error owner: extraction, entity selection, concept normalization, benchmark
   representation, likely gold omission, or unresolved clinical ambiguity.

Independent reviewers must apply these fields without seeing each other's
answers or the former three-way verdict. Agreement is reported per field with
raw agreement and an appropriate chance-corrected statistic where defined.
Consensus, if performed, must remain separate from the independent responses.

## Predeclared sensitivity views

The original benchmark and fixed `clinical_headline` scores remain unchanged.
Alternative views are separate sensitivity analyses:

1. **Current concept identity:** the fixed `concept_only` result.
2. **Concept plus negation:** the fixed `concept_negation` result.
3. **Concept plus assertion:** the fixed `concept_assertion` result.
4. **Multiplicity-insensitive presence:** one supported diagnosis-group presence
   per letter, ignoring repeated parent/child or compound renderings only where
   the review record explicitly supports that grouping.
5. **Clinically equivalent diagnosis groups:** reviewer-approved equivalence
   groups applied identically to all three methods.

Views 4 and 5 must not be calculated from project inference alone when a grouping
requires clinical judgment. Those cases remain unresolved pending independent
clinical review.

## Required analyses

- Reproduce each method's fixed Diagnosis component scores before interpreting
  any disagreement.
- Show disagreement direction and overlap across the three methods.
- Report results under every completed sensitivity view for every method.
- Test whether rules-only, LLM-only, and LLM-with-rules ordering changes.
- Test whether the hybrid-versus-LLM-only delta changes materially.
- Inspect representative dev rows where an alternative view helps one method,
  helps all methods, or reverses a method-specific error.
- Keep negative results, including low reviewer agreement or unchanged method
  conclusions.

## Stop rules and claim boundary

The study stops with one of four outcomes:

- **Answer:** completed review and sensitivity views show which conclusions are
  stable on dev140.
- **Negative result:** alternative views do not clarify the disagreement or
  reviewer agreement remains too low; retain that result.
- **Revise:** the artifact exposes a reproducible implementation or provenance
  defect; repair it outside this study and predeclare a new candidate.
- **Clinically blocked:** the remaining conclusion depends on an independent
  neurologist or epileptologist. Report the exact unresolved rows and do not
  substitute project judgment.

A positive result is a development answer about the named dev140 artifacts. It
may support the bounded claim that some measured Diagnosis disagreement concerns
annotation multiplicity or representation and that named method conclusions are
or are not stable under the completed views. It cannot establish corrected gold,
clinical validity, test60 performance, or holdout generalization.
