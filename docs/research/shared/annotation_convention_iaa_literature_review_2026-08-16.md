# Annotation convention as a cause of IAA and gold-label noise

Date: 2026-08-16

Status: source-backed literature review; diagnostic, not a new experiment

Question: Gan and ExECT encode different, partly arbitrary annotation
choices, and ExECT reports low inter-annotator agreement on some
fields. Is that causal story a common theme in the literature, or only
a local observation?

This is the broader investigation named at the end of the
[scoped `docs/literature` scan](annotation_iaa_literature_theme_2026-08-16.md).
It starts from the richer local `literature/` tree, then follows the
methods papers that tree already cites, then the high-impact work
those papers sit in.

Companion: [why Gan and ExECT annotated so differently](annotation_approach_comparison_2026-08-16.md).

## Scope

Local corpus first (`literature/` plus the ExECT v9 guideline and the
two June reviews in `docs/literature`):

- Epilepsy extraction: ExECT 2019 and 2024, the 2023 thesis, Decker
  2022, Xie 2022 / 2023a / 2023b, Fang et al. 2025, Holgate-style
  fine-tuning, zero-shot GPT seizure outcomes, Gan 2026
- Other clinical IE: CLINES, statin hybrid, open-source LLM extraction,
  SNOW clinician-grade features
- Guidelines: ILAE seizure classification, TRIPOD-LLM, MINIMAR
- Existing project reviews: hybrid seizure-phenotype review; Gan
  critical analysis

Then the methods lineage those sources already name:

- Artstein and Poesio 2008; Artstein 2017
- Hripcsak and Rothschild 2005
- Roberts et al. 2007 / 2009 (CLEF)
- Deleger et al. 2012
- Teruel et al. 2018
- Lingren et al. 2014

Then high-impact connected work that treats disagreement as a property
of the scheme or of the gold, not only of the annotator:

- Aroyo and Welty 2015 (CrowdTruth)
- Plank 2022 (human label variation)
- Uma et al. 2021 (learning from disagreement)
- Cabitza / Zhang et al. 2023 (npj Digital Medicine)
- Xia and Yetisgen-Yildiz on clinical IAA
- Kahneman, Sibony, and Sunstein 2021 (*Noise*)

This review does not change gold, scorers, or selected scores. It does
not re-annotate either corpus.

## Short answer

Yes — but it is three literatures, not one, and the epilepsy papers
mostly inhabit only the first.

**Strand A, reliability engineering.** Low IAA means the guideline is
unfinished. Write, test, revise, then take consensus as gold. This is
the story in Artstein, Roberts/CLEF, Deleger, Hripcsak, the ExECT
thesis, and almost every epilepsy paper that reports agreement.

**Strand B, scheme choice changes the gold.** Some disagreements are
not slips. They are the scheme asking a question another expert group
would not ask, or answering it with a convention. Teruel collapses a
category to raise kappa. Xie calls the one-year seizure-free cutoff
“arbitrary.” Holgate/Fang call the purist band edges arbitrary. ExECT
v9 maps “few” to 2 and missing ASM frequency to once daily. Gan merges
unknown with no information and maps `multiple` to 3. Aroyo and Welty
call “detailed guidelines help” a myth: more instructions can hide
subjectivity rather than remove it.

**Strand C, consensus gold can be the wrong object.** Reliability is
not validity (Artstein and Poesio). Human agreement with an
adjudicated gold is inflated (Xie 2023). Super-expert and majority-vote
golds can fail externally (Zhang / Cabitza 2023). Plank and Uma treat
irreconcilable variation as signal. ExECT 2024’s pipeline beating the
annotators is the same fact read as a success.

The user’s stronger claim — leftover conventions remain arbitrary and
still shape the gold we score — is Strand B plus C. That theme is
common in general annotation theory and in clinical decision-making.
It is only locally visible in epilepsy NLP, where most papers stop at
Strand A.

## Three literatures that rarely cite each other

| Strand | Governing claim | Typical move | What it does with leftover convention |
| --- | --- | --- | --- |
| A. Reliability engineering | Low IAA is a defect in the guideline or the annotator | Iterate, then consensus | Treats the finished scheme as settled |
| B. Scheme as scientific object | The coding question is itself a choice | Collapse, split, default, or refuse a category | Names some choices as arbitrary |
| C. Gold as contested object | A single label can be the wrong scientific object | Keep disagreement, soft labels, learnability | Treats consensus as one operationalisation |

The June clinical IE review named the artefact. It did not separate
these strands. The reliability review never asked the question.

## What the local epilepsy corpus already shows

The `literature/` tree is much richer than `docs/literature`. It
already contains the IAA numbers, the “arbitrary” admissions, and the
ILAE manuals that sit behind both golds.

### ExECT: inventory gold, low IAA on story-like fields

ExECT 2019 used group consensus against pre-defined category
guidelines. The 2023 thesis made guideline writing an iterative
reliability process (Ch. 2.2, citing Artstein, Teruel, Roberts,
Deleger, Hripcsak). Early real-letter Fleiss κ was 0.159 for seizure
frequency and 0.001 for patient history; a later test raised SF to
0.429. Pairwise F1 with features was 0.72, without features 0.84:
feature assignment, not only span choice, was a disagreement source.

ExECT 2024, on the 200 synthetic letters this project scores, reports
human IAA F1 0.73 overall and **0.47 on seizure frequency**. The
authors’ causal story is Strand A: identifying entities is hard;
UMLS/CUI matching caused fatigue; structured items (prescriptions,
0.87) are easier than items that “relay a story”; “detailed clear
guidelines … reduce errors” (citing Roberts 2007). Consensus after
review is the gold. The pipeline beats the annotators (0.87). CUIs
were dropped from IAA as tool error, then required again in gold.

The leftover conventions live in v9, not in that causal paragraph:
bare plural = 2; couple/few/multiple = 2; several = 3; “well
controlled” = Infrequent; “completely under control” = 0; missing ASM
frequency = once daily or As Required; last seizure on a date =
`NumberOfSeizures = 0` with `Since`; generic “seizure” is Patient
History, not Diagnosis. Those are Strand B facts. The 2024 paper does
not investigate them as a cause of the 0.47.

### Xie: high classification IAA, low span IAA, an admitted arbitrary cutoff

Xie et al. 2022 (JAMIA) triple-annotated 1,000 paragraphs, then
majority-voted and adjudicated. Cohen’s κ for seizure-free
classification was **0.82**. Paired span F1 when annotators overlapped
was 0.79; **overall span F1 was 0.44**. Classification and mention
inventory are different annotation objects. That is the same split
ExECT found between prescriptions and seizure frequency.

Xie also names a Strand B choice: the one-year window for “recent
seizure” “was also pragmatic … but from a machine learning perspective
was arbitrary.” All seizure types were lumped. The later longitudinal
papers (2023) convert those adjudicated strings to numbers and say
explicitly that **human agreement with the gold is inflated**, because
the gold was merged from those humans.

Xie 2023a (generalisability) then shows the gold itself moves with
note author: IAA and model agreement drop from epileptologist notes to
neurologist and non-neurologist notes. The annotation protocol was
held constant. The letters were not.

### Fang / Holgate: high kappa on a coarse scheme

Fang et al. 2025 (and the related Holgate fine-tuning paper) report
Cohen’s κ **0.84** between two epileptologists on 280–300 letters.
That is “almost perfect” on Landis and Koch. The object is a closed
set of frequency *categories*, not ExECT’s mention inventory. The same
programme then calls the purist band edges “arbitrary” and prefers a
pragmatic method because “the temporal distinctions are arbitrary.”
High IAA and admitted arbitrariness coexist. Kappa is high because the
scheme is coarse, not because the underlying clinical question is
settled.

### Decker, zero-shot GPT, and Gan: gold without a published IAA

Decker 2022 compares a rule system to “two expert reviewers” and does
not publish IAA in the short paper. The zero-shot GPT seizure-outcome
paper reuses Xie’s protocol: majority vote plus manual adjudication,
and an explicit “seizure free since last visit or within the past
year” rule. Gan 2026 double-reviews 300 real letters, publishes no
IAA, and does not release the category list or the current-state rule.
Synthetic Gan gold is teacher re-inference of a label the letter was
generated to match.

Absence of IAA is not evidence of high agreement. It is evidence that
Strand A was not run in public.

### ILAE manuals: clinical convention before NLP convention

The Fisher 2017 operational classification and the later updated
seizure classification are themselves negotiated coding schemes.
Ambiguous seizures, “unclassified,” and instruction-manual edge cases
are first-class. Annotation guidelines that inherit ILAE categories
inherit those conventions. They are not a natural kind that annotators
would recover without a manual.

### TRIPOD-LLM: report the guideline and the IAA, then stop

TRIPOD-LLM items 8a–8c require annotation guidelines with examples,
the number of annotators, the double-annotated fraction, IAA, and
annotator background. That is Strand A reporting. It does not ask
whether the guideline’s defaults are arbitrary, or whether consensus
gold should remain the only evaluation object.

### Other clinical IE in the local tree

CLINES notes that gold came from different annotators and that IAA
should be quantified later. The open-source LLM extraction paper
reports that some DRAGON tasks had Krippendorff’s α of 0.333. SNOW
treats clinician feature generation as gold and allows case-by-case
revision of interpretation logic when a note is ambiguous — an
adaptive gold, not a frozen scheme. The statin paper is silent on IAA.
These papers confirm that annotation reliability is a known
operational problem. They do not investigate leftover convention.

## Strand A: reliability engineering

This is the literature the thesis already pointed at. It is real, and
it is not the whole story.

**Artstein and Poesio 2008** is the canonical survey. Data are
reliable if coders agree to an extent determined by the study’s
purpose. Reliability is a *prerequisite* for validity, not a proof of
it: if annotators are inconsistent, either some are wrong or the
scheme is inappropriate. High agreement only shows that annotators
internalised a similar reading of the guidelines. It does not show
that the guidelines capture the phenomenon. The paper also shows why
kappa-like coefficients misfire on open mention inventories and why
weighted α-like measures are often more appropriate — and harder to
interpret. Landis and Koch bands are conventions about conventions.

**Hripcsak and Rothschild 2005** explain why ExECT and Xie report F1
rather than kappa for spans: there is no well-defined negative-case
count when the task is “mark the phrases.” Average pairwise F1 is
positive specific agreement. That is a measurement paper, not a
scheme-choice paper.

**Roberts et al. 2007 / 2009 (CLEF)** is the clinical gold-standard
methods account ExECT cites. Guidelines originated in IE templates,
were simplified with clinicians, then iterated on 31 documents until
entity agreement stayed high. They asked the exact boundary questions
ExECT later asked: split “myocardial infarction” into condition plus
locus, or keep it whole? Documents below an 80% entity-agreement
threshold were rejected. Occasional *major* scheme changes were made
when a planned category did not occur or did not fit (lymph-node
involvement dropped; a new Result entity added). That is Strand A
with a Strand B moment: the scheme was changed because the world did
not match the draft, not only because annotators slipped.

**Deleger et al. 2012** report high IAA (F 0.85–0.92) for PHI,
medications, and signs/symptoms after training and iterative
guidelines. The lesson the epilepsy papers take is “this is how you
build gold.” The contrast is also the lesson: those entities are
closer to ExECT prescriptions than to ExECT seizure frequency.

**Teruel et al. 2018** is the paper that uses IAA to change the
*scheme*, not only the wording. Major-claim vs claim had κ 0.48–0.56;
collapsing them raised κ to 0.51–0.64. They treat low IAA as a
symptom of an ill-defined or far-fetched concept and drop it when it
is not central to the application. They also show that automatic
classifiers fail where humans disagree. That is the closest methods
paper to the user’s question, and it is not about clinical text.

**Lingren et al. 2014** tests whether dictionary pre-annotation biases
gold. In their setting it sped work 14–22% and did not change IAA
(93–96%). The paper matters because it treats gold as something that
can be *contaminated by the process*, not only by annotator error.
ExECT’s Markup+UMLS setup is a related process. The 2024 paper
removed CUIs from IAA for that reason, then put them back into gold.

**Xia and Yetisgen-Yildiz** (cited by Zhang / Cabitza): medical
training alone is not sufficient for high IAA (pneumonia from chest
x-ray reports, κ 0.085). Expertise does not dissolve a hard coding
question.

Strand A’s limit: once the guideline is “finished,” leftover
conventions become invisible. Consensus gold is treated as the
phenomenon.

## Strand B: scheme choice changes the gold

This is the strand the user’s Gan/ExECT contrast actually lives in.

The local admissions are already enough to show it is not only a
local hunch:

- Xie 2022: the one-year “recent seizure” window is pragmatic and
  arbitrary.
- Fang / Holgate: purist temporal boundaries are arbitrary; the
  pragmatic method exists because of that.
- ExECT v9: closed maps from vague language to integers and from
  missing frequency to a default schedule.
- Gan 2026: unknown merged with no information; `multiple` = 3; one
  current winner; real-letter current-state rule unpublished.
- ILAE 2017: unclassified and instruction-manual edge cases are
  official clinical convention.

Aroyo and Welty 2015 make the general claim. Myth 1: one truth.
Myth 2: disagreement is bad. **Myth 3: detailed guidelines help.**
When specific cases keep causing disagreement, projects add
instructions that limit interpretation. That raises IAA by forcing a
convention, not by discovering a fact. Myth 7: once annotated, forever
valid. Their medical relation-extraction examples are the same family
of task as ExECT.

Teruel is the worked example: they did not write a longer definition
of “major claim.” They deleted the category. IAA rose because the
scientific object changed.

Artstein and Poesio already warned that a simpler scheme will show
higher chance-corrected agreement. Fang’s 0.84 and ExECT SF’s 0.47
are not two measurements of the same difficulty. They are two
different questions asked of similar letters.

## Strand C: consensus gold can be the wrong object

**Reliability is not validity.** Artstein and Poesio: witnesses who
agree may still be wrong; witnesses who disagree make the event
harder to recover. High IAA can be a consistently applied bad scheme.

**Adjudicated gold inflates human-vs-gold scores.** Xie 2023 says this
in print. ExECT 2024’s “pipeline better than annotators” is the same
arithmetic: the system is scored against consensus, the humans against
each other.

**Super-expert and majority-vote golds can fail.** Zhang, Cabitza and
colleagues (npj Digital Medicine 2023) had 11 ICU consultants label
the same cases (Fleiss κ 0.383). Models trained on each expert
disagreed on an external set (mean Cohen κ 0.255). There was no
stable “super expert.” Majority vote across all experts was worse
externally than majority vote among the *learnable* experts. Kahneman
et al. 2021 (*Noise*) is the background: between-person noise is
normal when the task is a judgment, not a mechanical test.

**Human label variation is a research programme.** Plank 2022:
aggregation assumes a ground truth that often does not exist;
variation can be genuine disagreement, subjectivity, or multiple
plausible answers. Uma et al. 2021 survey how to train and evaluate
without forcing one label. Basile et al. argue for perspectivism.
This literature is mostly toxicity, NLI, and images. It is not yet
the way epilepsy frequency golds are published. It is the literature
that would treat ExECT’s 0.47 and Gan’s unpublished current-state
rule as data, not as a defect to be consensus-smoothed away.

**TRIPOD-LLM and MINIMAR** require reporting how gold was made. They
do not require keeping the pre-consensus labels.

## How the four questions resolve

These are the questions the scoped scan said a broader review should
keep apart.

| Question | Answer in this literature | Strength |
| --- | --- | --- |
| 1. Do annotators disagree because the letter is ambiguous? | Yes. ExECT “relay a story”; Xie contradictory “no convulsions” plus “auras twice per month”; ILAE unclassified; CLINES ambiguous abbreviations. | Strong, local and general |
| 2. Do they disagree because the guideline is underspecified? | Yes, and this is the official fix. Artstein, Roberts, Deleger, thesis 2.2, Teruel. | Strong, Strand A |
| 3. Do they disagree because a finished convention is still arbitrary? | Yes, and this is named more often than the epilepsy papers admit. Xie “arbitrary” year; Holgate “arbitrary” bands; Aroyo Myth 3; Teruel category collapse; ExECT v9 defaults; Gan unpublished winner rule. | Strong as a theme; sparse as an epilepsy result |
| 4. After consensus, does gold still carry those conventions as facts? | Yes in method, rarely in claim. Xie 2023 inflated human-vs-gold; ExECT pipeline > annotators; Zhang/Cabitza majority-vote failure; Plank/Uma against single gold. | Strong outside epilepsy; locally visible, not locally theorised |

So the user’s hypothesis is not a new philosophy of annotation. It is
the reading you get if you refuse to stop at Strand A.

## What this does and does not show

It shows that annotation-convention as a cause of IAA and of gold-label
noise is a common theme once the methods literature and the
disagreement-as-signal literature are included. It is not a common
theme *inside* published epilepsy extraction papers, which mostly
report IAA, iterate, and move on.

It does not show that ExECT or Gan gold is clinically invalid. A
convention can be arbitrary and still be a coherent research object,
if it is named as a convention.

It does not recover unpublished Gan real-letter guidelines or IAA.

It does not authorise changing frozen gold or scorers. The useful
consequence is interpretive, as in the annotation-approach note: when
a residual looks like a model failure, check whether it is a named
convention (ExECT defaults, splits, empty-gold) or an unpublished
current-state choice (Gan one-winner, unknown-versus-rate).

## Decision and next action

The broader investigation is complete enough to state the claim:

Annotation choices are a major, documented cause of low IAA and of
the shape of gold labels. The epilepsy literature reports the
symptoms (field-wise IAA, “story-like” difficulty, occasional
“arbitrary” cutoffs). The methods literature explains the mechanism
(scheme iteration, reliability ≠ validity, guidelines as forced
convention). The disagreement literature refuses the premise that
consensus gold is the only scientific object.

No gold or scorer change follows. If this project wants an empirical
next step, it is not another prompt. It is a predeclared study that
keeps pre-consensus or dual-defensible labels visible on development
letters already in hand — without promoting them into new gold.
That study does not exist yet, and this review does not open it.
