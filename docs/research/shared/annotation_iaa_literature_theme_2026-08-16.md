# Is annotation-convention a surveyed cause of IAA and gold-label noise?

Date: 2026-08-16

Status: scoped literature scan of the local review set; diagnostic, not a
new experiment

Question: the Gan and ExECT golds encode different, partly arbitrary
annotation choices, and ExECT reports low inter-annotator agreement on
some fields. Is that causal story a common theme in the papers already
held in `docs/literature`, or only a local observation?

Companion: [why Gan and ExECT annotated so differently](annotation_approach_comparison_2026-08-16.md)
explains the two programmes' choices. This note asks whether the
*literature those reviews already synthesised* treats guideline choice
as a cause of gold-label disagreement.

## Scope

`docs/literature` is not a pile of primary papers. It holds two
project-authored reviews from June 2026:

- `literature_review.pdf` (7 June 2026; 10 pages). Clinical information
  extraction, epilepsy NLP, hybrid architecture, and uncertainty.
- `llm_reliability_literature_review.pdf` (10 June 2026; 11 pages).
  Definitions and techniques for LLM reliability.

The contrast case named in the query is read from the source papers
those reviews already use, plus the ExECT guideline and thesis the
project holds:

- Fonferko-Shadrach et al., *Annotation of epilepsy clinic letters for
  NLP*, J Biomed Semantics 2024; 15:17
- Gan et al., *Reproducible Synthetic Clinical Letters for Seizure
  Frequency*, arXiv:2603.11407v1, 2026
- *ExECT V2.1 — What and How of annotating*, v9
- Fonferko-Shadrach PhD thesis, 2023, especially Ch. 1.4.2 and 2.2

This scan does not search beyond that set. It does not change gold,
scorers, or selected scores.

## Short answer

The theme is **named once, not surveyed**.

The clinical IE review states the dissertation stance clearly: ExECT
gold is a clinical-linguistic artefact; a system–gold mismatch can be
model error, underspecified annotation, or genuine ambiguity. That is
the user's hypothesis, written as advice. It is not a review of a
literature that already treats annotation convention as a major cause
of low IAA.

The reliability review is silent on gold construction.

The primary epilepsy papers those reviews cite mostly **report** IAA,
annotation cost, or documentation mess. They do not investigate whether
arbitrary coding rules produce the disagreement. The thesis is the
closest local source: it treats guideline writing as an iterative
reliability process and cites the methods literature (Artstein, Teruel,
Roberts/CLEF, Deleger, Hripcsak). Even there, IAA is a tool for
tightening the scheme, not evidence that remaining conventions are
arbitrary and still shape the gold.

A broader investigation is therefore not repeating work already done in
`docs/literature`. It has to leave this folder.

## Coding used here

Each source was scored on what it does with annotation and IAA, not on
whether it mentions the words.

| Code | Meaning |
| --- | --- |
| Silent | No gold-construction, IAA, or guideline discussion |
| Reports | Gives an IAA number, annotation cost, or “experts disagree” as a barrier |
| Names the artefact | Says gold is constructed and can be wrong or underspecified |
| Investigates cause | Asks whether guideline or scheme choices produce the disagreement |
| Compares schemes | Contrasts different annotation philosophies as different scientific objects |

## The two reviews

### Clinical IE review: names the artefact, does not survey it

The review's recurring-challenge list includes one bullet:
clinician annotation is expensive and ambiguous; even experts disagree
on onset, frequency, temporality, and certainty. Adjacent bullets treat
inconsistent documentation, multiple event types, and temporality as
properties of the *letters*, not of the *coding scheme*.

The only sustained treatment is the ExECT 2024 paragraph. The review
calls that paper's deeper contribution epistemic: what it means to
build a clinically credible gold when real letters cannot be shared and
trained annotators disagree. It then says the gold standard is “a
clinical-linguistic artefact, shaped by guideline clarity, concept
boundaries, and adjudication decisions,” and that a sophisticated
dissertation should not treat gold as infallible.

Later it adds the right next question for Gan: not only agreement, but
**label grammar** — what each frequency category means, how ranges map,
how seizure-free duration is treated, and how unknown is separated from
no seizure.

That is the theme. It is a stance drawn from ExECT 2024 and from
reading Gan's schema, not a finding that the cited literature already
explores the cause. Xie, Decker, Holgate, the 2019 ExECT paper, the
2022 EDSS paper, Oh et al., and the 2024 ADL systematic review are
used for extraction performance, generalisability, privacy, or
heterogeneous *outcome* definitions. None is read as a study of
annotation convention as a gold-label mechanism.

### Reliability review: silent

Reliability is defined as a system property given a task: correctness,
groundedness, robustness, calibration, safety, abstention. HELM,
TruthfulQA, FActScore, RAG, and human review appear as ways to judge
*model* output. Healthcare advice is guideline RAG and clinician
oversight. There is no IAA, no annotation manual, and no discussion of
whether the reference label is itself a convention.

Human labels appear only as a calibration target for automated judges.
That assumes the gold is the thing being measured against, not the
thing under investigation.

## What the source papers themselves do

### ExECT 2024 reports IAA and attributes it to task difficulty

Human IAA on the 200 synthetic letters is 0.73 overall, 0.47 on
seizure frequency, 0.45 on when diagnosed, 0.87 on prescriptions.
Consensus after review is the gold. The pipeline beats the annotators
(0.87 per item).

The authors' causal story is:

- identifying and classifying entities is hard
- missing spans, missing attributes, and misclassification (generic
  seizures under diagnosis) were the main errors
- CUI slips were tool error, so IAA ignored CUIs
- feature range and UMLS matching caused fatigue
- structured items (prescriptions) are easier than items that “relay a
  story”
- seizure frequency is written in many formats and often covers
  several event types
- “detailed clear guidelines developed in collaboration with
  annotators and annotation trials reduce errors” (citing Roberts 2007)

They do **not** say that remaining conventions are arbitrary, or that
those conventions are a major cause of the 0.47. Consensus is the
remedy. The scheme's defaults (bare plural = 2; “well controlled” =
Infrequent; missing ASM frequency = once daily) live in the guideline,
not in this causal discussion.

They do cite the methods papers a broader review should open:
Hripcsak and Rothschild 2005 (F-measure as IAA), Deleger et al. 2012
(building medical gold-standard corpora), Roberts et al. 2007 (CLEF
guideline development). Those citations are used as method, not
reviewed as a literature on arbitrary scheme choice.

### Gan 2026 does not report IAA

Real letters: clinicians marked frequency categories present or
absent; a data-science step converted that to one monthly number; 300
letters were double-reviewed. No IAA is published. The category list,
the current-state rule, and the rule for choosing among several
present categories are not published.

Synthetic letters: humans labelled short descriptions, then letters
were generated to match those labels. Agreement is teacher
re-inference, not dual annotation of the same letter.

Gan makes large representation choices (numeric collapse; unknown
merged with no information; `multiple` = 3). The paper defends them as
modelling and comparability decisions. It does not treat them as
annotation conventions that would split two clinicians, because it
never measures that split.

### The thesis treats IAA as a reliability process

Chapter 2.2 is the only local source that reviews annotation
methodology as literature. Gold is expert-annotated entities, features,
and relations (Deleger 2012). Guidelines should be written, tested,
revised until reliability is reached (Artstein 2017). IAA measures
task difficulty, finds problems, and helps create better guidelines
(Teruel et al. 2018). Kappa is for known-category rating; F1 is for
open mention inventories (Hripcsak 2005). Roberts/CLEF is named as a
rare detailed guideline-development account.

That is the standard clinical-NLP methods story: low IAA means the
scheme is unfinished; iteration and consensus finish it. The thesis
then reports that even after iteration, seizure frequency stayed hard
(Fleiss κ 0.159 then 0.429 on real-letter tests; feature assignment
hurt pairwise F1). It does not ask whether the finished conventions
are still arbitrary, or whether a different finished scheme would have
produced a different gold.

## Coverage table

| Source | Code | What it does with the theme |
| --- | --- | --- |
| `literature_review.pdf` | Names the artefact | One ExECT paragraph plus “label grammar”; not a surveyed theme |
| `llm_reliability_literature_review.pdf` | Silent | Reliability of models given gold, not construction of gold |
| ExECT 2024 | Reports | IAA table; difficulty, fatigue, story-like fields; consensus gold |
| Gan 2026 | Silent on IAA | Scheme choices are modelling decisions; no dual-annotation study |
| ExECT v9 guideline | Scheme, not literature | Encodes the conventions (defaults, splits, empty-gold) |
| Thesis Ch. 2.2 | Methods review | IAA as a tool to improve guidelines; cites Artstein, Teruel, Roberts, Deleger, Hripcsak |
| Xie / Decker / Holgate as used in the June review | Reports, if at all | Annotation mentioned as cost or as training labels |
| 2024 ADL systematic review as used in the June review | Reports | “Heterogeneous outcome definitions” as a barrier, not a gold-construction study |

No source in this set **investigates cause** in the sense of the
query: that arbitrary guideline choices are a major, field-wide driver
of low IAA and of the gold labels later treated as truth.

## What this does and does not show

It shows that the user's reading is already latent in the June
clinical IE review and in ExECT's own IAA table, and that the local
review set did not turn that reading into a literature theme.

It does not show that the wider field ignores the theme. The thesis
bibliography already points at the papers that would test that:
Artstein 2017, Teruel 2018, Roberts 2007, Deleger 2012, Hripcsak 2005,
plus Lingren et al. 2014 on pre-annotation bias. Those are the first
doors for the broader investigation.

It does not authorise changing gold or scorers.

## Decision and next action

Start the broader review outside `docs/literature`. The local set has
already done all it can: it named the artefact and left the causal
literature unreviewed.

The broader investigation is now written. It starts from the richer
`literature/` tree, then follows Artstein, Roberts/CLEF, Deleger,
Hripcsak, Teruel, and the disagreement-as-signal literature. Owner:
[annotation convention IAA literature review](annotation_convention_iaa_literature_review_2026-08-16.md).

A useful next pass would separate four questions the June reviews
collapse:

1. Do annotators disagree because the *letter* is ambiguous?
2. Do they disagree because the *guideline* is underspecified?
3. Do they disagree because the guideline is specified, but the
   specification is a convention another expert group would not share?
4. After consensus, does the published gold still carry those
   conventions as if they were clinical facts?

ExECT 2024 answers (1) and part of (2). The v9 guideline and this
project's later residuals make (3) and (4) visible. The field
literature for (3) and (4) is not in `docs/literature`.
