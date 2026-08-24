# How the two tasks are scored

Date: 2026-08-17
Revised: 2026-08-19 (score as how the submitted answer is judged)
Status: paper source; writing glossary extracted from the retired generated
manuscript. Not a scoring authority.

## The short answer

Gan and ExECT do not share a score. When the paper names a result, it must
name the task, the measure, and whether that measure is the project's
internal comparison or a published-benchmark view.

The score is how the submitted answer is judged. It compares a
task-defined object, not the original letter directly. It can therefore
reward gold agreement while discarding distinctions that remain visible
in the source span.

## Gan

Gan scores one rendered seizure-frequency label per letter.

- **Purist** is the primary measure: fine category bands after the label is
  projected to a monthly frequency.
- **Pragmatic** is the coarser companion projection.

The band definitions and the `unknown` / no-seizure sentinels belong to the
Gan dataset paper and to
[Gan clinical policy](../../canon/06_gan_clinical_policy.md). This glossary
does not redefine them. What counts as one correct answer on each gold is
[what the two golds already decided](what_the_two_golds_already_decided_2026-08-17.md).

Purist accuracy cannot show which evidence was selected, whether a competing
statement was also defensible, or which bound or temporal detail was lost when
the label was mapped to a monthly band.

## ExECT

ExECT's primary internal score is 4-family micro F1
(`clinical_inventory_unit_keys`). Diagnosis is
not collapsed to the most-specific concept. De-duplication belongs to
select, not to scoring. Phrase, CUI, evidence-valid, and full-attribute
scores remain separate. Historical Compact/headline cells may still
carry `clinical_headline` (`clinical_headline_unit_keys`). That
Diagnosis-collapse ablation is not the cited primary.

Clinical fact recovery is not the published strict ExECT benchmark.

4-family micro F1 cannot show which upstream component caused an omission or
addition, whether an exact quote was decisive, or whether an unannotated fact
was clinically reasonable. Those questions require the saved translation
trace and development case analysis.

The paper-derived published views score each entity type separately and
report their macro mean:

- **Normalized phrase** compares entity-linked surface forms.
- **CUI** compares entity-linked concept identifiers.
- **All features** adds the entity-specific attributes.

Certainty applies to Diagnosis and PatientHistory. Negation applies only to
PatientHistory. Per-item scoring counts every mention. Per-letter scoring
asks whether a letter contains at least one correct mention and attribute
bundle.

## What this source is for

Use this note when drafting a Methods score paragraph. Do not cite it for
selected fills, holdout limits, or claim strength.

## Evidence owners

- [ExECT scoring](../../canon/04_scoring.md)
- [Gan clinical policy](../../canon/06_gan_clinical_policy.md)
- [Paper claim status](../../canon/10_paper_provenance.md)
- [Decision 0046](../../decisions/0046-exect-primary-method-comparison-boundary.md)

## Writing test

**Question:** can the author name the primary Gan measure, the primary ExECT
internal measure (4-family micro F1 / `clinical_inventory_unit_keys`), and
the one sentence that keeps clinical fact recovery from being called the
published benchmark?

**Success:** those three facts are locatable here without reopening the
scoring canon or a results table.
