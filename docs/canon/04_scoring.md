# 04 — ExECT scoring and annotation evidence

Last updated: 2026-07-14

| Score | Question | Use |
| --- | --- | --- |
| Clinical fact recovery (`clinical_headline`) | Were the right facts recovered across the four main entity types? | Primary internal comparison |
| Entity-specific score | Was the entity's clinical object recovered? | Entity analysis |
| Seizure-frequency state profile | Was the combined seizure-burden state recovered? | Seizure-frequency development |
| Phrase, CUI, and full attributes | Does the output match the published representation? | Published-metric comparison |
| Evidence groundedness | Is the cited text present after neutral text repair? | Evidence fidelity |

Do not describe `clinical_headline` as the published strict benchmark. The
repository now implements the paper-derived normalized-phrase, CUI, and
full-attribute views, but it has not reproduced the paper's original system or
reported validation scores.

| Method | Split | Selected result |
| --- | --- | ---: |
| Rules only, all nine entities | dev140 | strict item F1 0.3548 |
| Rules only, all nine entities | dev140 | published-view macro item F1: phrase 0.5687, CUI 0.7144, all features 0.6020 |
| GEPA LLM only | dev140 | clinical fact F1 0.7393 |
| LLM with rules (`v08`) | dev140 | clinical fact F1 0.9189 |

The published-view replay is a no-call development result over all nine entity
types. Its per-letter macro F1 is 0.7518 for normalized phrase, 0.8534 for CUI,
and 0.7922 for all features. CUI matching recovers many surface-form misses;
attribute agreement, especially for Diagnosis, is the main remaining loss. The
paper's original 0.87 per-item and 0.90 per-letter results are reference values,
not reproduced scores.

The selected annotation records include diagnosis and seizure-frequency row
analyses, a blind replication report, four entity ledgers,
`experiments/gold_data_issues.jsonl`, and the extracted annotation guidelines.
The same team produced and reviewed these records. They support limited claims
about multiplicity, representation, ambiguity, and specific defects; they are
not independent clinical validation.

The current hierarchy-aware Diagnosis audit substrate reports dev140 concept F1
of 0.8599 for rules-only, 0.6861 for LLM-only, and 0.8984 for LLM-with-rules. It
contains 246 unreviewed union disagreements. The former 0.6617 to 0.9501
Diagnosis adjustment belongs to a different historical GEPA run under the
pre-D1 scorer and cannot be transferred to the current artifact or scoring
surface.

Open work: adjudicate the current Diagnosis union under the predeclared
observable fields, check the published inter-annotator agreement method against
its primary source, and combine cited annotation issues with their scoring
effects and review status.
