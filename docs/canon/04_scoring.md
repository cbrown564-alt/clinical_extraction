# 04 — ExECT scoring and annotation evidence

Last updated: 2026-07-15

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

The [annotation-evidence synthesis](../experiments/exectv2/reliability/exectv2_annotation_evidence_synthesis_2026-07-15.md)
combines the selected row analyses, four family ledgers, direct gold issues,
annotation guidelines, blind re-review, completed Diagnosis review, scoring
effects, sensitivity handling, and review status. Its generated taxonomy
hash-checks 13 retained sources, contains 584 overlapping evidence records, and
maps all 57 letter IDs explicitly cited in the retained narrative reports.
Those counts are evidence records, not unique letters or a prevalence estimate.

The evidence supports different strengths of statement:

- Three open field conflicts and one fixed closed-vocabulary issue are direct
  mechanical defect records. Cite them individually; do not infer a clinical
  error rate from four cases.
- The source guideline documents multiplicity, timing, and qualitative
  frequency conventions. A documented convention does not by itself establish
  that a reviewed model alternative is clinically equivalent.
- Internal project review supports bounded statements about representation,
  ambiguity, and scorer behavior. The blind LLM re-review had 60.0% raw
  agreement and pooled unweighted kappa 0.397, so individual borderline
  verdicts remain weakly reproducible.

The completed current Diagnosis review classifies 246 dev140 disagreements as
173 representation/evaluation issues, 72 extraction errors, and one uncertain
row. Of these, 197 decisions were pattern-assisted and 49 were manual; the
structured clinical-adjudication fields remain unreviewed. Keeping gold and the
fixed scorer unchanged, the conservative sensitivity F1 is 0.9344, 0.8499, and
0.9789 for rules-only, LLM-only, and LLM-with-rules. The wider reviewed
interpretation is 0.9520, 0.9056, and 0.9950. These are sensitivity results, not
corrected benchmark scores or clinical accuracy.

The former 0.6617-to-0.9501 Diagnosis adjustment belongs to a different
historical GEPA run and scorer. It remains mechanism evidence but is superseded
for current magnitude and cannot be transferred to the current artifact. The
historical narrative reports 209 concept disagreements while its selected
generated ledger retains 199 rows; the ten unavailable rows remain
aggregate-only evidence.

Claims of clinical validity still require independent clinical review. No
annotation result changes gold, replaces an original score, authorizes test60
inspection, or establishes holdout generalization.
