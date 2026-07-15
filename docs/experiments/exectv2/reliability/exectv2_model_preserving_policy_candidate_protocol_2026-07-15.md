# ExECTv2 model-preserving deterministic-policy candidate protocol

Date: 2026-07-15  
Status: completed; candidate rejected by the predeclared rescue-retention gate  
Result: [model-preserving candidate result](exectv2_model_preserving_policy_candidate_2026-07-15.md)

## Primary question

Can one bounded, model-preserving deterministic policy reduce the decision-0040
Diagnosis and Prescription correct-to-wrong rows on ExECTv2 dev140 without
discarding the demonstrated deterministic rescues?

This matters because the corrected comparison architecture has the right
family owners, but the current post-model rules still change some already-
correct model outputs into wrong final outputs.

## Data and row policy

- Dataset: ExECTv2.
- Split: the 140 identifiers in the repository's `dev` split manifest.
- Permission: dev140 row inspection was explicitly permitted on 2026-07-15.
- Exclusion: no test60 note, prediction, annotation, identifier, failure, or
  row-level difference may be inspected or retained.
- Replay: saved historical GPT-4.1-mini, historical DeepSeek, and Qwen 3.6 35B
  producer outputs only. No model calls are authorized.
- Filtering: full200 producer blobs must be copied to temporary dev-only JSONL
  files before assembly.

## Candidate and fixed comparator

Comparator: the current decision-0040 model-led policy analyzed in
`experiments/exectv2_model_led_dev140_regression_analysis_20260715.json`.

Candidate identifier: `decision_0040_model_preserving_dev140_v1`.

The candidate is opt-in. The current policy remains the default until the
candidate meets the stop rule. It changes only four boundaries:

1. **Prescription residual additions:** disable all deterministic Prescription
   facts that were not present in the model-owned Prescription output.
2. **Prescription current-versus-future selection:** preserve a complete
   model-owned regimen when its exact evidence, or the immediately preceding
   note context, explicitly marks it as current. A later taper, stop, or
   increase instruction must not turn that current regimen into planned-only
   noise.
3. **Diagnosis residual subsumption:** do not add a broader seizure concept when
   a model-owned Diagnosis concept already contains the same normalized seizure
   concept plus more specific clinical terms. Singular/plural variation is
   ignored for this comparison; epilepsy syndromes and seizure phenotypes are
   not collapsed into each other.
4. **Diagnosis phenotype preservation:** preserve model-owned `absence
   seizures` when the same model output also contains an affirmed absence-
   epilepsy syndrome. This is a clinical-epilepsy hierarchy guard, not a
   letter-specific exception.

Seizure Frequency projection/suppression, Investigations, Prescription
normalization, supported regimen splitting, Diagnosis heading recovery, all
other Diagnosis rewrites/drops/additions, evidence validation, gold, and
scorers remain fixed.

## Ownership and rule categories

All four changes are deterministic semantic policies. Prescription residual
disablement and current-versus-future selection are `clinical_epilepsy` rules.
Diagnosis residual subsumption is a `clinical_epilepsy` selection guard even
when the suppressed addition was labelled `benchmark_format`. Absence-
phenotype preservation is `clinical_epilepsy`. None is credited to the model.

## Metrics

Primary:

- family-local changed-row direction versus model-owned output;
- correct-to-wrong count by family and model;
- wrong-to-correct count by family and model.

Promotion gate for this development candidate:

- Diagnosis correct-to-wrong must fall below 18;
- Prescription correct-to-wrong must fall below 23;
- Seizure Frequency must remain at zero component-local correct-to-wrong;
- total wrong-to-correct must remain at least 150, allowing at most 10 of the
  comparator's 160 rescues to be lost;
- every changed row must retain exact evidence;
- no new schema, parse, call, or fallback failure may be introduced.

Secondary:

- model-owned and final `clinical_headline` F1 by model and family;
- entity-agnostic compatibility view used by the full200 architecture audit;
- changed-row counts by mechanism, first owner, and clinical subproblem.

No scorer threshold, gold annotation, or family assignment may change.

## Required tests and changed-row analysis

Before implementation, add failing tests showing:

- explicit current regimens survive later taper/increase language while
  planned-only regimens remain dropped;
- Prescription residual additions are absent only when the candidate is on;
- broader Diagnosis residual concepts are suppressed by more specific
  model-owned seizure concepts, while distinct syndrome/phenotype facts remain;
- an evidence-backed absence-seizure phenotype is preserved beside an
  absence-epilepsy syndrome only when the candidate is on;
- default policy behavior remains unchanged.

The replay must retain one row per changed dev140 model/family decision with
comparator, candidate, model-owned, and gold keys; both correctness directions;
exact evidence; deterministic actions; first prediction-changing owner; and
source revision.

## Stop rule

- **Accept for the next frozen comparison** only if every promotion gate passes
  and row inspection shows that improvements follow the four predeclared
  mechanisms without a new hidden-family failure.
- **Revise** only for an implementation defect or missing instrumentation. Do
  not add another clinical exception after seeing the candidate rows.
- **Reject** if a gate fails or the apparent gain depends on letter-specific,
  model-specific, or scoring-specific behavior.

Stop after the dev140 decision. Acceptance does not authorize test60 row
inspection or a model call.

## Artifact and claim boundary

Write a machine-readable JSON artifact containing protocol metadata, dependency
and dirty-tree notes, source revisions, score ladders, gate results, mechanism
summaries, and changed-row records. Write a narrative result beside this
protocol.

A positive result is a development decision for the three saved model outputs
on inspected dev140. It is not holdout evidence, clinical validation, proof of
cross-model transfer to the three unrun roster models, or promotion of the
six-model comparison.
