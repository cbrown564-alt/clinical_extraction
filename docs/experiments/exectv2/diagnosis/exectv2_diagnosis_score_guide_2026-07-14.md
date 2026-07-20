# Guide to the ExECTv2 Diagnosis F1 scores

Date: 2026-07-14  
Status: discussion document; interpretations are not settled paper decisions

## Purpose

Several Diagnosis F1 values appear in the current paper and the completed
dev140 Diagnosis review. They measure different outputs with different matching
rules. This document records how they relate without treating disputed
interpretations as decided.

F1 combines precision and recall. It is comparable only when the evaluated
rows, output unit, matching policy, attributes, and aggregation method are the
same. A higher number under a more permissive interpretation is not necessarily
a better extraction system.

## Score map

| Scores | Evaluated output | Scoring role | Current paper role |
| --- | --- | --- | --- |
| Rules `0.6020` | All nine entity types; all-feature macro per-item F1 | Paper-derived development metric | Selected headline result |
| LLM only `0.7393`; LLM with rules `0.9189` | Four main entity types; internal clinical-fact F1 | Architecture-level development comparison | Selected headline results |
| Rules `0.8599`; LLM only `0.6861`; LLM with rules `0.8984` | Diagnosis concepts only on dev140 | Fixed baselines for the completed review | Not currently presented in the paper |
| Rules `0.9344`; LLM only `0.8499`; LLM with rules `0.9789` | Same saved Diagnosis outputs under the conservative sensitivity interpretation | Diagnostic sensitivity analysis | Not a replacement benchmark result |
| Rules `0.9520`; LLM only `0.9056`; LLM with rules `0.9950` | Same saved Diagnosis outputs under the widest reviewed interpretation | Diagnostic upper sensitivity view | Not a replacement benchmark result |
| Rules `0.8926`; LLM only `0.6210`; LLM with rules `0.9034` | New candidate Diagnosis outputs against unchanged gold and scorer | Candidate implementation results | Candidates are not promoted into the paper reference table |
| Historical DeepSeek `0.8708`; GPT-4.1-mini `0.8397`; Qwen `0.8307` | Diagnosis within full200 model runs | Development-inclusive model comparison; historical DeepSeek runtime metadata is incomplete | DeepSeek result is audit-only; final paper row is pending |

The rows in this table must not be collapsed into one ranking. In particular,
the paper's rules-only `0.6020` and its LLM results `0.7393` and `0.9189` do not
use the same entity coverage or score definition.

## 1. Current paper headline results

The paper's main ExECT table currently reports:

- rules only: `0.6020` paper-derived all-features macro per-item F1 across all
  nine entity types;
- LLM only: `0.7393` internal clinical-fact F1 across the four main entity
  types;
- LLM with rules: `0.9189` internal clinical-fact F1 across the four main
  entity types.

These are selected architecture-level development results. They are not three
values from one common scorer. The paper already states that they cannot prove
strict benchmark superiority.

The completed Diagnosis work did not promote a new reference architecture.
Consequently, it does not automatically replace these three headline values.

## 2. Fixed Diagnosis-only baselines

The completed review starts from one comparable Diagnosis-only concept score
for each architecture on dev140:

| Architecture | Fixed Diagnosis concept F1 |
| --- | ---: |
| Rules only | 0.8599 |
| LLM only | 0.6861 |
| LLM with rules | 0.8984 |

These scores compare normalized Diagnosis concepts while leaving the existing
gold and scorer unchanged. They are the appropriate baseline for asking how
the 246 reviewed Diagnosis disagreements affect interpretation and whether a
candidate fixes genuine extraction errors.

They are not directly comparable with the paper's `0.6020`, `0.7393`, or
`0.9189` because those are architecture-level scores with different entity
coverage and, for rules only, a different metric family.

## 3. Sensitivity views

The final review classified the 246 disagreement rows as:

| Review decision | Rows |
| --- | ---: |
| Representation/evaluation issue | 173 |
| Extraction error | 72 |
| Uncertain | 1 |

The sensitivity views keep the saved predictions fixed and ask how the measured
Diagnosis result changes if specified reviewed representation differences are
treated as acceptable.

| Architecture | Fixed score | Conservative sensitivity | Widest reviewed interpretation |
| --- | ---: | ---: | ---: |
| Rules only | 0.8599 | 0.9344 | 0.9520 |
| LLM only | 0.6861 | 0.8499 | 0.9056 |
| LLM with rules | 0.8984 | 0.9789 | 0.9950 |

These numbers describe sensitivity to evaluation interpretation. They are not
new model outputs, official corrected scores, independent clinical validation,
or evidence that the hybrid is `99.5%` clinically correct.

Exactly how the paper should characterize the 173 representation/evaluation
decisions remains open for discussion. Possible descriptions include gold-label
problems, annotation conventions, clinically acceptable alternatives, scoring
strictness, or a mixture of these. This document does not choose among them.

## 4. Candidate implementation results

The implementation candidates were also scored against the original gold and
fixed Diagnosis concept scorer:

| Architecture | Fixed baseline | Candidate | Change | Decision |
| --- | ---: | ---: | ---: | --- |
| Rules only | 0.8599 | 0.8926 | +0.0327 | Retain as an opt-in development candidate |
| LLM only | 0.6861 | 0.6210 | -0.0652 | Reject prompt v0.2 |
| LLM with rules | 0.8984 | 0.9034 | +0.0051 | Retain as an opt-in development candidate |

The rules boundary candidate resolved 21 reviewed rows, including 17 labelled
extraction errors, and introduced one new residual. The hybrid candidate
resolved three reviewed extraction errors and introduced no new residuals. The
broad rules residual dictionary was rejected because it introduced 30 new
residuals. All candidate Diagnosis mentions had exact source evidence in the
saved comparison.

These results measure changes to the extraction systems. They should not be
confused with the larger increases in the sensitivity views, which change the
interpretation of disagreements rather than the predictions.

## 5. Diagnosis commentary in the current paper

The paper-derived rules-only replay provides another Diagnosis score ladder:

| Diagnosis view | Per-item F1 |
| --- | ---: |
| Normalized phrase | 0.6977 |
| CUI | 0.7332 |
| All evaluated features | 0.3010 |

This is the basis for the paper's statement that CUI matching recovers some
surface-form variation while feature agreement remains a large limitation,
especially for Diagnosis. The all-feature view includes Diagnosis attributes
such as certainty and category.

The completed review focused primarily on Diagnosis concept identity,
multiplicity, and clinical granularity. It therefore does not directly test or
remove the attribute-level loss behind the fall from `0.7332` to `0.3010`.
Whether the paper should retain, qualify, or reframe its current attribute
commentary is a question for the follow-up discussion.

## 6. Other Diagnosis numbers that must remain separate

- The original ExECT publication reports Diagnosis per-item F1 `0.85` as part
  of its original full200 evaluation. The current repository has implemented
  the metric family but has not reproduced that system or result.
- The historical internally adjusted Diagnosis F1 `0.9501` belongs to a
  different pre-D1 GEPA run and scorer. It must not be transferred to the
  current three-architecture review.
- The DeepSeek, GPT-4.1-mini, and Qwen Diagnosis scores use full200 and different
  runtime conditions. They do not answer the dev140 review question.

## 7. Facts established versus interpretations reserved

The following are direct study records:

- the fixed and candidate scores in the tables above;
- the `173 / 72 / 1` review distribution;
- the changed-row and new-residual counts;
- exact-evidence validity of the saved candidates;
- unchanged gold and fixed scorer;
- dev140-only row inspection, with no test60 inspection;
- no candidate promotion.

The following remain interpretive questions for a separate session:

1. How much of the 173-row group should be described as defective gold, an
   annotation convention, evaluation strictness, or legitimate ambiguity?
2. Should the paper report either sensitivity view, and if so, as a table,
   limitation, or annotation-analysis result?
3. Does the completed review strengthen, qualify, or conflict with the current
   claim that Diagnosis attributes are the main remaining paper-derived loss?
4. Should the deterministic candidates remain supporting evidence or enter a
   future selected reference after an appropriate frozen evaluation?
5. What independent clinical review is needed before making a clinical-validity
   claim about the reviewed equivalences?

## Claim boundary

All new review and candidate results are development evidence from inspected
ExECTv2 dev140. They do not correct the published gold, establish clinical
validity, measure test60 performance, demonstrate holdout generalization, or
replace the retained paper reference.

## Source records

- [Current manuscript](../../../research/paper_manuscript_2026-06-26.md)
- [Diagnosis component comparison](exectv2_diagnosis_component_comparison_2026-07-14.md)
- [Diagnosis resolution protocol](exectv2_diagnosis_resolution_protocol_2026-07-14.md)
- [ExECT scoring and annotation evidence](../../../canon/04_scoring.md)
- [Paper claim status](../../../canon/10_paper_provenance.md)
