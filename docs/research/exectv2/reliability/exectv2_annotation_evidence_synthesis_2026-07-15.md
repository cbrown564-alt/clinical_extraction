# ExECTv2 annotation-evidence synthesis

Date: 2026-07-15  
Status: complete retained-development synthesis; independent clinical review open  
Protocol: [annotation-evidence synthesis protocol](exectv2_annotation_evidence_synthesis_protocol_2026-07-15.md)  
Machine-readable result: `experiments/exectv2_annotation_evidence_synthesis_20260715.json`

## Answer

The retained evidence supports a bounded annotation-analysis claim: some
measured ExECT disagreements arise from mechanically identifiable annotation
defects, documented annotation conventions, multiplicity or representation
choices, genuine ambiguity, and scorer behavior. These mechanisms are now
traceable without changing gold or any scorer.

The synthesis does not establish clinical validity. Most clinical-equivalence
decisions were made within the project, 197 of the current 246 Diagnosis rows
were pattern-assisted, and the blind re-review used LLM sub-agents rather than
independent clinicians. Independent clinical review remains required before
describing the reviewed alternatives as clinically valid.

## What was combined

The generated artifact hash-checks 13 retained sources and contains 584 evidence
records:

| Record type | Records | Role |
| --- | ---: | --- |
| Historical four-family ledgers | 334 | Defect, convention, ambiguity, multiplicity, scorer-artifact, and model-error cases from the earlier internal reviews |
| Completed Diagnosis review | 246 | Current dev140 review decisions with mechanism, sensitivity treatment, provenance, and unresolved clinical fields |
| Direct gold issues | 4 | Three open score-bearing mechanical defects and one fixed closed-vocabulary formatting defect |

These records overlap. The count of 584 is neither a number of unique letters
nor a prevalence denominator. Across the three retained narrative reports, all
57 explicitly cited letter IDs map to at least one taxonomy record.

One historical limitation remains visible rather than repaired by inference:
the 2026-06-30 Diagnosis narrative reports 209 concept disagreements, but the
selected generated Diagnosis ledger contains 199 rows. The ten unavailable
concept rows remain aggregate-only historical evidence. This does not affect
the completed 246-row review, which uses a later three-method disagreement
substrate and is the current Diagnosis interpretation result.

## Evidence by mechanism

| Evidence type | Retained finding | Handling |
| --- | --- | --- |
| Mechanical defect | `gold_data_issues.jsonl` records four field-level issues: three remain open in frozen gold and one TimePeriod normalization issue is fixed in scoring | Cite the individual defect; do not extrapolate a corpus-wide clinical error rate |
| Annotation convention | The primary guideline permits one phrase to carry multiple concepts in different contexts, retains multiple time periods, and maps phrases such as “well controlled” to `Infrequent` | Treat convention mismatch separately from a defective annotation |
| Multiplicity and representation | The historical ledgers and current Diagnosis review contain consolidated-versus-atomic, same-CUI, clinical-granularity, and accepted-equivalence cases | Keep the original score primary; report only in a named sensitivity view |
| Ambiguity | The Seizure Frequency review records temporal and interpretation ambiguity; the current Diagnosis review retains one unresolved row | Do not force an inferred gold correction |
| Scoring | Diagnosis concept scoring, Seizure Frequency `state_profile`, and paper-derived phrase/CUI/full-attribute scoring answer different questions | Never collapse the scores into one accuracy claim |
| Model-error control | Both historical ledgers and the current review retain genuine extraction errors alongside annotation findings | Do not forgive model errors in annotation sensitivity views |

The source guideline matters to interpretation but does not prove that a
particular reviewed alternative is clinically equivalent. Conversely, the
three direct open defects are mechanical field conflicts and do not depend on
a clinical-equivalence judgment.

## Current Diagnosis result

The completed review classifies the 246 current dev140 disagreements as:

| Review decision | Rows | Sensitivity handling |
| --- | ---: | --- |
| Representation/evaluation issue | 173 | 133 enter the conservative view; another 40 enter only the widest reviewed interpretation |
| Extraction error | 72 | Not forgiven |
| Uncertain | 1 | Not forgiven; remains unresolved |

Review provenance is 197 pattern-assisted decisions and 49 manual decisions;
one manual decision is the unresolved row. The structured clinical-adjudication
fields in the ledger remain `unreviewed`, so “completed review” means completed
project triage, not completed independent clinical adjudication.

The scoring layers remain separate:

| Architecture | Fixed Diagnosis F1 | Conservative sensitivity | Widest reviewed interpretation |
| --- | ---: | ---: | ---: |
| Rules only | 0.8599 | 0.9344 | 0.9520 |
| LLM only | 0.6861 | 0.8499 | 0.9056 |
| LLM with rules | 0.8984 | 0.9789 | 0.9950 |

The sensitivity values reinterpret fixed saved outputs. They are not corrected
benchmark scores, new predictions, independent clinical accuracy, or promoted
paper headline results. The separate extraction candidates were scored against
unchanged gold: rules and hybrid fixes remain development candidates, while the
LLM-only prompt candidate was rejected after regression.

## Historical family evidence and review reproducibility

The historical Seizure Frequency internal review assigned 15 of 53
disagreements to model error, 22 to annotation mismatch or redundant
annotation, and 16 to ambiguity or temporal convention. Exact per-letter
agreement was 62.1%; the internally defensible view was 89.3%. Keep the latter
as historical sensitivity evidence, not clinical validation.

The historical Diagnosis review reported 31 of 209 disagreements as model
error, 167 as model-defensible annotation mismatch, and 11 as ambiguous. Its
0.6617-to-0.9501 adjustment belongs to a different run and scorer. It remains
mechanism evidence but is superseded for the current Diagnosis magnitude by the
completed 246-row review.

The blind LLM re-review is a necessary negative result. Across 40 sampled cases,
raw agreement was 60.0% and pooled unweighted kappa was 0.397. Aggregate
reweighting was more stable for Seizure Frequency than Diagnosis, but individual
borderline verdicts were not highly reproducible. This supports cautious
wording and an independent-clinician follow-up; it does not validate the
project's clinical judgments.

## Decision and claim boundary

The annotation package is consolidated for reproducibility and paper handling:

- keep original benchmark and internal scores primary;
- label the two current Diagnosis sensitivity views explicitly;
- keep the historical Diagnosis adjustment superseded and separate;
- cite mechanical defects individually;
- distinguish documented conventions from claimed clinical equivalence;
- retain extraction-error controls rather than treating every disagreement as
  annotation noise; and
- require independent clinical review for clinical-validity language.

This is development evidence from retained, permitted ExECT records. It does
not edit gold, change a scorer, inspect test60, measure holdout generalization,
or establish how common these mechanisms are outside the inspected records.
