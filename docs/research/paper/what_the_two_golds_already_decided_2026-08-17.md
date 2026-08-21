# What the two golds already decided

Date: 2026-08-17
Revised: 2026-08-19 (golds as evaluation forms, not the task)
Status: literature-grounded paper source; writing brief. The diagnostic
owner remains the annotation comparison.

## The short answer

ExECT and Gan were not annotating the same clinical question.

ExECT annotated a **mention inventory** so a rule-based extractor could
be scored by feature-identical match. Gan annotated **one current
frequency label** so a temporally complex endpoint could be trained and
scored, including on synthetic letters that do not distribute patient
text.

The golds this project scores are those two decisions. They are not two
encodings of one task.

## The gold is an evaluation form, not the task

Neither gold is a neutral copy of facts already sitting in the letter. Each
annotation programme decided what evidence would count, what representation
would be retained, how competing or multiple facts would be handled, and what
unit the evaluator would compare. The proposed method translates letters into
a designed structured form with source text. This paper uses these two golds
as the evaluation forms. That choice is for empirical analysis, not a claim
that gold is the only useful form, or that the gold preserved every clinical
distinction.

| Decision | Gan 2026 | ExECTv2 |
| --- | --- | --- |
| Source information | Temporal seizure-frequency statements, including silence | Mentions and attributes in four scored families |
| Required representation | One canonical current-frequency label | A coded, attribute-bearing mention inventory |
| Selection or assembly | Choose one current state; other true statements are not additional answers | Retain all guideline-supported mentions; preserve multiplicity and family membership |
| Unknown or silence | Explicit `unknown` and no-reference labels | Empty family means not annotated under the guideline |
| Submitted object | One label | One de-duplicated fact set |
| Scored unit | Monthly Purist or Pragmatic band | Feature-defined mention or clinical-fact set comparison |
| Information that may be discarded | Bounds, temporal detail, alternative true statements, and distinctions within a band | Unannotated clinical nuance, hedging or defaults not represented by the scored features |

The paper should therefore treat annotation policy as the evaluation form
used here, not as passive bookkeeping after extraction, and not as the
definition of the method.

## ExECT decided that the inventory is the object

Thesis 3.1 is the governing sentence. ExECT v1 could be scored by
clinicians who accepted equivalent meaning. Automated GATE evaluation
cannot. Annotation features and formats had to be identical to the
pipeline output (Fonferko-Shadrach 2023). Markup and UMLS lookups were
chosen so standoff files could be scored.

That is why gold is mention-level, attribute-rich, and CUI-aligned. It
is not because the authors thought a clinician's summary of a letter
should look like GATE output. It is because the thing being validated
was a gazetteer-and-JAPE extractor.

The 2024 public set reused that method on 200 clinician-written
synthetic letters. A phrase may belong to more than one concept; all
possible contexts should be annotated (v9). Empty gold in a family
means **not annotated under the guideline**, not “clinically false.”
Some gold values are closed maps the letter did not say: a missing
ASM frequency becomes once daily or `As Required`; “a few” becomes 2;
“well controlled” becomes `Infrequent`.

Consensus after review is the published gold, not either annotator's
first pass.

## Gan decided that one current label is the object

Gan starts from seizure frequency as an endpoint, not as one field
among nine (Gan et al. 2026, 1.1). The published evaluation collapses
the letter to seizures per month, then into Purist and Pragmatic bands.

The real-letter method is thinner in public than ExECT's v9. Clinicians
marked frequency categories present or absent; a later conversion
produced one monthly number; 300 letters were double-reviewed (Gan
2.5). The paper does not publish the category list, the rule for
choosing among several present categories, or how “current” was defined
when history was also present. Those selection rules appear later in
this project's policy catalog as observed gold behaviour. They are not
Gan's released annotation manual.

The public synthetic gold, which this project scores, was built
label-first: humans labelled short descriptions, letters were generated
around those labels, and only exact teacher re-inference was kept. The
dialect keeps range, cluster, duration, and unknown as first-class
forms. `multiple` later maps to 3 on the monthly scale. Silence is an
explicit label (`unknown`, `no seizure frequency reference`), not an
empty cell.

So Gan's published gold has two layers. The real gold is a
clinician-then-numeric endpoint. The synthetic gold is a
human-normalised dialect that letters were generated to match. They
are not interchangeable. The paper could not train its structured
formats on real letters for that reason (Gan 2.8, 4.5).

## What one correct answer is

On ExECT, a letter is correct only if the **set** of coded mentions
matches. Missing a fact, merging two facts, or adding a rate the
guideline did not code is an error.

On Gan, a letter is correct only if the **one** canonical string maps
to the right monthly band. A clinically adequate paraphrase in the
wrong dialect is wrong. A second true historical rate is not a second
gold answer.

Gold agreement is a constructed proxy. ExECT reports low human
agreement on story-like fields, especially seizure frequency, and then
takes consensus as gold. Gan does not publish real-letter IAA. The
paper may say that benchmark agreement is not absolute clinical truth.
It should not turn annotation-convention noise into a co-equal topic.
The IAA reviews stay with their owners.

## What this permits the paper to say

| Supported interpretation | Unsupported extension |
| --- | --- |
| The two golds answer different questions: inventory versus one current label. | Either gold is clinically invalid. |
| ExECT gold is a feature-identical coding standard; some values are guideline defaults. | Those defaults may be rewritten for scoring. |
| Gan's public synthetic gold is a closed dialect; the real-letter winner rule is only partly published. | This project's later policy catalog is Gan's annotation manual. |
| The two scores are not numerically comparable. | Performance transfers from one task to the other. |

This source belongs to the literature and dataset lane. It does not
change gold, scorers, or selected scores.

## Sources and owners

The diagnostic owner, with IAA tables, guideline lists, and corpus
distinctions, is
[why Gan and ExECT annotated so differently](../shared/annotation_approach_comparison_2026-08-16.md).

IAA as a literature theme, not a paper topic:

- [scoped scan](../shared/annotation_iaa_literature_theme_2026-08-16.md)
- [convention review](../shared/annotation_convention_iaa_literature_review_2026-08-16.md)

Primary published sources are listed on the annotation comparison and
on the [citation map](related_work_seed_2026-08-17.md).

The project's reading of the inherited labels, without the annotation
history, is
[what the two extraction tasks ask](../shared/task_shape_framework_2026-08-06.md).

## Writing test

**Question:** can the author explain, in one paragraph each, why ExECT
gold is an inventory and Gan gold is one current label?

**Success:** each paragraph names the research object and the
evaluation method that forced that object, says what silence means,
and refuses to treat the two scores as one capability.
