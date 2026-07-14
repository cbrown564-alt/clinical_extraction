# ExECTv2 Diagnosis interpretation audit: substrate result

Date: 2026-07-14  
Status: substrate complete; adjudication and clinically equivalent sensitivity views open  
Protocol: [Diagnosis interpretation audit protocol](exectv2_diagnosis_interpretation_audit_protocol_2026-07-14.md)

## Answer at this stage

The no-call dev140 substrate is complete for rules-only, the retained GEPA
LLM-only comparator, and the retained v08 hybrid control. It produces 246 unique
Diagnosis review targets across 104 letters. Every method-specific missed and
spurious count reproduces the current `concept_only` scorer exactly.

The three completed fixed views preserve the same ordering:

`LLM with rules > rules only > LLM only`

This is an automated development result, not the final annotation sensitivity
answer. Multiplicity-insensitive and clinically equivalent views remain
uncomputed until their review decisions exist.

## Fixed-view results

| Method | Concept only F1 | Concept + negation F1 | Concept + assertion F1 | Missed | Spurious |
| --- | ---: | ---: | ---: | ---: | ---: |
| Rules only | 0.8599 | 0.7812 | 0.6622 | 45 | 37 |
| LLM only | 0.6861 | 0.6624 | 0.5322 | 84 | 101 |
| LLM with rules | 0.8984 | 0.8853 | 0.7943 | 21 | 41 |

The hybrid-minus-LLM-only F1 difference is 0.2123 for concept only, 0.2229 for
concept plus negation, and 0.2620 for concept plus full assertion. Requiring
attributes therefore does not explain away the hybrid advantage in these fixed
views; it increases it. The hybrid-minus-rules-only difference is much smaller
for concept identity (0.0385) and increases for negation and assertion, so the
review should distinguish concept recovery from context-dependent attributes.

## Union review population

- 246 unique `letter + direction + normalized concept` rows.
- 104 of 140 dev letters contain at least one union disagreement.
- 94 review rows are missed concepts; 152 are spurious concepts.
- Exclusive method membership:
  - LLM only: 120
  - LLM with rules: 31
  - rules only: 28
  - LLM only plus rules only: 36
  - LLM only plus LLM with rules: 13
  - LLM with rules plus rules only: 2
  - all three: 16

The large LLM-only-only group means a review of only shared disagreements would
misstate the comparison. The 16 all-method rows are the cleanest first hard
slice for finding benchmark-wide interpretation issues, while the method-only
rows test method-specific failure mechanisms.

## Provenance finding

The older retained row analysis reports Diagnosis F1 0.6617 with 209
disagreements for the historical
`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628` run under its
2026-06-30 scorer. The current retained LLM-only comparator is the separate
`exectv2_gepa_dedup_gpt41mini_h2mb8_20260628` artifact. On 2026-07-02, the D1
scorer correction added parent/child Diagnosis hierarchy matching; the current
registry records this selected artifact moving from 0.6624 to 0.6861, with
`concept_only` 0.6861 and `concept_negation` 0.6624.

The new substrate correctly uses the current fixed scorer and yields 185
LLM-only disagreements: 84 missed plus 101 spurious. Therefore:

- the former 209-row adjudication remains historical evidence about a different
  GEPA output and the former scoring surface;
- its 0.9501 internally adjusted F1 must not be presented as an adjustment to
  the current 0.6861 score;
- the current 246-row three-method union needs its own adjudication;
- the paper's limited qualitative claim may remain, but its numerical support
  must distinguish historical and current scorer versions.

This is scorer/provenance drift in the documentation, not a new scorer defect.
The registry already contains the corrected LLM-only value; the Diagnosis
canonical summaries did not.

## Reproducibility and attribution

- Dataset and split: ExECTv2 dev140; test60 was not read.
- Calls: none.
- Rules-only predictions: regenerated deterministically from current code.
- LLM-only and hybrid predictions: saved JSONL replay.
- Primary scorer: current Diagnosis `score_concept_identity(...).concept_only`,
  including entity-agnostic recall, home-tagged precision, de-duplication,
  specificity collapse, and hierarchy reconciliation.
- Artifact decomposition self-check: per-method missed equals scorer FN and
  spurious equals scorer FP; the build fails otherwise.
- The JSON summary records working-tree byte hashes for both saved prediction
  files and a canonical digest for regenerated deterministic predictions.

Artifacts:

- `experiments/exectv2_diagnosis_interpretation_audit_dev140_20260714.jsonl`
- `experiments/exectv2_diagnosis_interpretation_audit_dev140_20260714.json`

## Claim boundary

This is a pre-adjudication development substrate. It establishes the current
scorer populations and stability across three already-defined views. It does
not establish that any disagreement is a gold defect, that two diagnoses are
clinically equivalent, that the benchmark should be changed, or that the result
transfers to test60.

## Next action

Review the 246 rows under the protocol's observable fields, beginning with the
16 rows shared by all methods and then a stratified sample from each exclusive
method group. Measure agreement per field before consensus. Calculate the two
clinically interpreted sensitivity views only for decisions supported by that
record; send unresolved equivalence judgments to an independent neurologist or
epileptologist.
