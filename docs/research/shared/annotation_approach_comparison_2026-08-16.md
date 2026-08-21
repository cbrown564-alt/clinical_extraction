# Why Gan and ExECT annotated so differently

Date: 2026-08-16

Status: source-backed literature synthesis; diagnostic, not a new experiment.
The paper-source writing brief is
[what the two golds already decided](../paper/what_the_two_golds_already_decided_2026-08-17.md).

Question: why did the two programmes take their particular annotation
approaches, what challenges shaped those choices, and what did that do to
the gold labels this project scores against?

## Sources

Primary:

- Fonferko-Shadrach et al., *Annotation of epilepsy clinic letters for
  natural language processing*, J Biomed Semantics 2024; 15:17
  (`data/ExECTv2 (2025)/Annotation of Epilepsy Clinic Letters for NLP
  (Fonferko-Shadrach 2024).pdf`)
- *ExECT V2.1 — What and How of annotating with Markup*, v9, 09.09.2023
  (`data/ExECTv2 (2025)/ExECT V2 .1- What and How of annotating_v9.docx`;
  extract:
  [annotation_guidelines_v9_extracted.md](../exectv2/annotation_guidelines_v9_extracted.md))
- Fonferko-Shadrach, PhD thesis, Swansea University, October 2022 / 2023
  (`literature/Epilepsy Extraction/Rules-Based/2023_Fonferko-Shadrach_B.final.65061.pdf`),
  especially Chapters 1.4.2, 2.2, 3, and 8.1
- Gan et al., *Reproducible Synthetic Clinical Letters for Seizure
  Frequency Information Extraction*, arXiv:2603.11407v1, 12 Mar 2026
  (`data/Gan (2026)/Synthetic Clinical Letters for Seizure Frequency.pdf`)

Secondary (this project's later reading of the same gold, not author
intent):

- [task-shape framework](task_shape_framework_2026-08-06.md)
- [Gan gold taxonomy](../gan2026/gold_task_taxonomy_2026-08-06.md)
- [ExECT gold taxonomy](../exectv2/gold_task_taxonomy_2026-08-06.md)
- [clinical selection policy catalog](clinical_selection_policy_catalog_2026-07-31.md)

## Claim boundary

This is a **diagnostic** reading of published methods, guidelines, and
the thesis. It does not change gold, scorers, or selected scores.

Two corpus distinctions matter:

1. The ExECT thesis gold was 100 **real** Swansea Neurology Biobank
   letters. The public set this project uses is the later 200
   **clinician-written synthetic** letters from the 2024 paper. The
   guidelines and Markup configuration are the same lineage (v7 in the
   thesis appendix; v9 for the synthetic validation).
2. Gan's published real-letter gold is 1,781 King's College Hospital
   letters, of which 300 were double-reviewed. The public set this
   project uses is the 1,500-row **synthetic** subset. Real-letter
   annotation guidelines were not released.

Where the Gan paper is silent on a selection rule, this note says so.
It does not treat this project's later policy catalog as Gan's published
annotation manual.

## Short answer

The two programmes were not solving the same annotation problem.

**ExECT annotated to validate a rule-based inventory extractor.** The
gold had to look like GATE output: every mention, every attribute, every
UMLS CUI, in a closed feature vocabulary. That choice came from the
research aim (enrich routinely collected data with a wide epilepsy
variable set) and from the evaluation method (automated feature-identical
match). The cost was a hard, fatiguing task with low human agreement,
especially on seizure frequency. Consensus after review became the gold,
not either annotator's first pass.

**Gan annotated to train and evaluate a single current-frequency
endpoint.** The gold had to be one normalised label per letter that
could be mapped to seizures per month. That choice came from a different
aim (privacy-preserving LLM training for a temporally complex outcome)
and from a different bottleneck (scale, leakage, and output
representation). The cost is that competing true statements must lose,
that real-letter gold was collapsed to a number, and that the published
structured dialect lives mainly on the synthetic side.

The gold labels we score are therefore not two encodings of the same
clinical question. They are two different answers to “what should count
as correct?”

## What each programme was trying to do

ExECT's thesis aim is explicit: routinely collected data lack the detail
needed to study interactions among aetiology, comorbidity, and
treatment, so NLP should create **detailed disease-specific datasets**
from clinic letters (thesis Abstract; Ch. 1). ExECT v1 already extracted
nine epilepsy categories. v2 widened the variable set and
**synchronised feature format** so outputs could be linked and
validated automatically (thesis 3.1, 8.2). The 2024 paper then needed a
**shareable** annotated corpus: no public epilepsy letter set with a
full concept-and-relation guideline existed, mainly because of
identifiable data (2024 Introduction).

Gan's aim is also explicit, and different. Seizure frequency is “one of
the most frequently used indicators of disease control and treatment
response,” but it is “intrinsically more temporally complex than many
discrete epilepsy attributes (e.g., medication lists)” (Gan 1.1, 4.2).
High-performing extractors need large training sets; real letters cannot
be shared at LLM scale without privacy and memorisation risk (Gan 1.1).
The paper therefore builds a **task-faithful synthetic framework** and a
**structured label scheme** so models can be trained without
distributing patient text (Gan 1.2, 2.6).

The 2024 ExECT paper itself names the contrast that later became Gan's
design problem: seizure frequency “relays a story,” is recorded in a
wide variety of formats, often covers multiple seizure types, and is
“a significant disadvantage of annotating text for a rule-based system
as compared to classifying phrases for a machine learning model”
(2024 Discussion, citing Xie et al. 2023). Gan took the second path.

## Why ExECT annotated as an inventory

### The gold had to match the pipeline

Thesis 3.1 is the governing sentence. ExECT v1 was scored by clinicians
who could accept equivalent meaning (“dates could be expressed in
different way as long as the meaning was the same”). Automated GATE
evaluation cannot do that. “Annotation features and formats have to be
identical.” The standard specification therefore “centred not only on
the entity and feature recognition but also reflected the format of the
output produced by the ExECT v2 pipeline.”

Chapter 8.1.1 repeats the split of labour: annotators asked for
clarifications and examples; algorithm developers “had to ensure that
the format of the annotations created was in line with that produced by
the algorithm, to allow for validation.” Markup was chosen over BRAT
because it supplied UMLS lookups and produced standoff files GATE could
score (thesis 2.3, 8.1.3).

That is why gold is mention-level, attribute-rich, and CUI-aligned.
It is not because the authors thought a clinician's summary of a letter
should look like that. It is because the thing being validated was a
gazetteer-and-JAPE extractor.

### The inventory is the research object

The 2024 entity list is the v2 research object: Birth History,
Diagnosis, Epilepsy Cause, Investigations, Onset, Patient History,
Prescriptions, Seizure Frequency, When Diagnosed. Certainty 1–5 is
assigned to diagnosis and patient history; other families get closed
attributes (dose, result, time window, frequency change). The
guidelines say a phrase may belong to more than one concept, and “all
possible contexts should be annotated” (v9 Appendix A). Combined
seizure and epilepsy phrases are split when they have separate CUIs
(“partial seizures with secondary generalisation”; “refractory focal
epilepsy”) and kept together when they have one CUI (“focal to
bilaterally convulsive seizure”; “symptomatic focal epilepsy”).

This is ontology-first annotation. The gold is a coded inventory, not a
clinical paraphrase.

### Guidelines evolved because humans could not agree

The thesis treats guideline writing as an iterative reliability process
(Ch. 2.2.1, citing Artstein and Poesio). Two 10-letter tests on real
letters, then a 20-letter pairwise F1 test, then a 100-letter gold set
reviewed as a group (Ch. 3.2–3.3). The 2024 synthetic set reused that
method: four trained annotators, 100 letters each, two combined sets of
200, IAA, then consensus meetings to form gold.

Early real-letter agreement was poor. Fleiss' kappa on the first
10-letter test was 0.159 for seizure frequency and 0.001 for patient
history; the second test improved SF to 0.429 and investigations to
0.627, but diagnosis fell to 0.097 and patient history stayed slight
(thesis Table 3.1). The 20-letter pairwise F1 with all features was
0.72 micro; without features it rose to 0.84, which the authors read as
evidence that **feature assignment**, not only span choice, was a
disagreement source (thesis 3.2.2).

The 2024 synthetic IAA is the number attached to the gold this project
uses:

| Entity | Human IAA F1 | Gold mentions | ExECTv2 per-item F1 |
| --- | ---: | ---: | ---: |
| Prescription | 0.87 | 290 | 0.87 |
| Diagnosis | 0.83 | 572 | 0.85 |
| Investigations | 0.82 | 183 | 0.95 |
| Birth History | 0.69 | 47 | 0.97 |
| Epilepsy Cause | 0.67 | 36 | 0.90 |
| Onset | 0.61 | 22 | 0.96 |
| Patient History | 0.57 | 620 | 0.78 |
| Seizure Frequency | 0.47 | 260 | 0.66 |
| When Diagnosed | 0.45 | 17 | 0.91 |
| All | 0.73 | 2047 | 0.87 |

CUIs were dropped from IAA because missing or misassigned CUIs were
judged to be tool error, not annotator choice (2024 Discussion). Gold
still required them.

The authors' own conclusion: clinical text annotation is difficult;
gold must be “arranged by researcher consensus”; the pipeline was more
accurate than the annotators (2024 Abstract and Conclusion). Thesis
3.3 is more cautious: after group correction “it was impossible to
guarantee that some errors were not still present,” and later
validation found some.

## Why Gan annotated as one current label

### The endpoint is one number, used as an outcome

Gan starts from seizure frequency as a **research and clinical
endpoint**, not as one field among nine. Letters contain rates, ranges,
vague quantifiers, seizure-free durations, clusters, and statements
anchored to implicit reference points (“since I last saw the patient”)
(Gan 1.1). Prior KCH work had already treated this as harder than
epilepsy type, seizure classification, or medication lists (Gan 2.3,
citing Fang 2025 and Holgate 2025).

The published evaluation therefore collapses everything to **seizures
per month**, then into Purist (fine) and Pragmatic (coarse) bands, with
`ε = 1000` for unknown and `ε = 0` for no seizure (Gan Table 1). That
is a modelling and comparability choice: it lets structured labels,
numeric regression, and four-way classes share one score.

### Real letters were annotated as categories, then converted to a number

Section 2.5 is the only published real-letter annotation method. Each
of 1,781 (text also says 1,791) clinic letters was marked for a
predefined set of frequency **categories** as present or absent.
A data-science step then converted those categories into one monthly
number. Three hundred letters were double-reviewed by two senior
epilepsy clinicians to form the held-out gold test.

The paper does **not** publish:

- the category list used at the clinician stage
- the rule for choosing among several present categories
- how “current” was defined when a letter also had history
- inter-annotator agreement on the 1,481 training letters
- a Markup-style mention guideline

It does say why expert annotation was required: frequency is often
implicit or highly variable (2.5). It also says the real gold exists
**only as a number**. That mismatch later blocked joint training of
the structured label formats on real letters (2.8, 4.5).

Two classing decisions were made for comparability with Holgate 2025:
“unknown frequency” and “no seizure information” were merged into one
Unknown class; a distinct “No seizure” class was added for explicit
absence, including seizure-free presentations (2.5). On the Real(300)
test set that produced a heavy unknown mass: 163/300 unknown, 33 no
seizure, 72 frequent, 32 infrequent (Table 3). The gold is therefore
not only a rate dialect. It is also an abstention dialect, and
abstention is the majority class on the real test they report.

### Synthetic gold was built label-first, then filtered

The public synthetic scheme is the opposite of ExECT's letter-first
annotation.

1. Ten privacy-checked base letters preserve NHS style.
2. GPT-5 writes 500 short frequency descriptions.
3. **Humans** read those descriptions, assign a canonical label, and
   rewrite the text as a parametric template.
4. Templates are instantiated to 17,315 (description, label) pairs.
5. GPT-5 lifts each pair into a full letter.
6. GPT-5 is asked to re-infer the label. Only exact matches are kept
   (15,099 letters). Failures concentrate on complex narratives; chain-
   of-thought exemplars reduce discards (2.6.3–2.6.4).

The label scheme is a closed linguistic dialect, not a mention
inventory:

- `unknown`
- `no seizure frequency reference`
- `seizure free for <value|multiple> <month|year>`
- `<value|multiple> per <value|multiple> <day|week|month|year>`
- two-part cluster grammar
- `unknown, <value|multiple> per cluster`

`multiple` is a first-class token, later mapped to 3 for the monthly
scale (2.6.1). Ranges are kept in the label and only later mid-pointed
for banding. The authors chose this representation because a single
numeric target “inevitably discards uncertainty” and forces the model
to “pick a number,” while a four-way class is stable but loses ranges,
durations, and cluster structure (2.7). Structured labels
outperformed both on real letters (Abstract; 4.1–4.2).

So Gan's published gold has two layers. The **real** gold is a
clinician-then-numeric endpoint. The **synthetic** gold, which this
project scores, is a human-normalised dialect that letters were
generated to match.

## Challenges and how they changed the gold

### ExECT: boundary, features, fatigue, and the gazetteer

The thesis and 2024 paper name the same failure modes.

**Entity boundaries were unstable.** Non-specific seizures were
assigned to Diagnosis by some annotators and to Patient History by
others. Compound phrases were split by some and kept whole by others.
Medication *changes* were annotated as current prescriptions. Onset
was confused with a current frequency window (“frequent complex
partial seizures for the last 1 year” was removed from Onset after
review because it did not prove first occurrence; it was kept as
seizure frequency) (thesis 3.2.1, 3.3; 2024 Discussion).

Those disagreements produced durable coding rules:

- generic “seizure / absence / myoclonic jerk” is not Diagnosis; it
  is Patient History, unless a person trigger and frequency statement
  move it to Seizure Frequency
- hypothetical, driving-advice, and “epilepsy point of view” mentions
  are out
- past-tense diagnosis is in; “should they return” is out
- negated “no further GTCS since August” is still an **affirmed**
  diagnosis (history of that seizure type) and a **zero** frequency
- last seizure on a date is `NumberOfSeizures = 0` with
  `TimeSince_or_TimeOfEvent = Since`, even if the preposition is “in”
- both time windows are annotated when a letter gives two (“two
  seizures in March” and “since last being seen”)
- “well controlled” / “under control” map to `Infrequent`;
  “completely under control” maps to 0 (v9 List 11)
- a bare plural “seizures” with no number is 2
- word numbers are closed: couple/few/number/multiple → 2; several → 3

**Feature assignment was as hard as span choice.** Missing CUIs,
certainty levels, prescription dose, and SF since/during were the
common 20-letter errors (thesis 3.2.2). The 2024 paper adds annotator
fatigue from the range of features and UMLS matching, “reflecting the
complexity of the rule-based system.” IAA therefore ignored CUIs;
gold still required them. Certainty was used only for Diagnosis and
Patient History in the synthetic validation, because other families'
certainty was inherited from those terms and sometimes mismatched
(v9 General points).

**The gazetteer limited what gold could contain.** During validation,
“we should only annotate terms with the UMLS match, whilst collecting
the terms we feel are important” (v9). Investigations without a
stated result are ignored. Drugs without a dose are ignored except
rescue midazolam/diazepam. If frequency is missing, gold writes
once daily, or `As Required` for clobazam and rescue drugs. Those
defaults are annotation conventions, not source-stated schedules
([Decision 0021](../../decisions/0021-prescription-missing-frequency-defaults-are-benchmark-projection.md)).
Seizure semiology, family history, and most negation are out of
scope (2024 Discussion). Empty gold in a family therefore means
**not annotated under the guideline**, not “clinically false.”

**Consensus replaced dual annotation as truth.** The 2024 gold is
“the final corrected set, representing consensus opinion.” The thesis
gold was reviewed by the whole team, with developers checking format
and “troublesome” cases (8.1.3). That raises reliability relative to
a single annotator. It also means gold is a negotiated coding
standard, not an independent second reading.

### Gan: temporal complexity, privacy, representation, and imbalance

Gan names a different stack of problems.

**Temporal interpretation is the task.** Ranges, clusters, implicit
windows, missing data, and ambiguous expressions are “common in
real-world clinical correspondence” (1.1). Even GPT-5 in reasoning
mode discarded a substantial fraction of complex synthetic letters
until CoT exemplars were added (2.6.4). The response was not a
nine-entity guideline. It was a **closed label dialect** that keeps
range, cluster, duration, and unknown as first-class forms, plus
evidence spans so a reviewer can see which sentence was treated as
current.

**Privacy blocked letter-first gold at training scale.** De-identified
real text still carries leakage and membership-inference risk for
LLMs (1.1). Gan therefore inverted ExECT's 2024 solution. ExECT had
clinicians write 200 synthetic letters and then annotate them. Gan
had humans label short descriptions, generate 15k letters around
those labels, and keep only letters the teacher could re-derive.
The synthetic gold is faithful to the dialect by construction. It is
less faithful to the mess of a real letter that was not written to
match a template. The authors say so: ten base letters and templated
descriptions limit diversity and may explain diminishing returns at
larger scale (4.4–4.5).

**The useful representation and the published real gold are not the
same object.** Structured labels were the best training target, but
real letters only have numeric gold, so Formats 3 and 4 could be
trained only on synthetic data (2.8). Future work would need
“efficient annotation or semi-automated conversion” of real letters
into the label scheme (4.5). That is an admission that the
clinically richer gold was not the gold they could collect on real
notes.

**Unknown is a designed class, not a leftover.** Merging “unknown
frequency” with “no seizure information,” while splitting out “no
seizure,” was done to stay comparable with prior KCH work and to
score explicit absence separately (2.5). On Real(300), unknown is
54%. On this project's 1,500-row synthetic subset the unknown-like
mass is smaller (200 unknown + 86 unresolved multiple + 54 no
reference = 340/1500, 22.7%), because the generation process
controlled the mix. The public gold therefore under-represents the
real-letter abstention rate the authors themselves report.

**How one current winner is chosen is only partly published.** The
paper says annotators marked categories present or absent “based
solely on information contained in the text,” then a conversion
produced one monthly number (2.5). It does not say what happens when
a usual monthly rate and a year-to-date total are both present, or
when episodes are “under review.” Those selection rules exist in
this project's later catalog as observed gold behaviour
([policies A1–A13](clinical_selection_policy_catalog_2026-07-31.md)).
They are not Gan's released annotation manual. The honest statement
is: Gan decided that one current label was the scientific object,
and left the published method thinner than ExECT's v9 on the
decision that makes that object hard.

## Impact on the gold labels this project scores

### What one correct answer is

On ExECT, a letter is correct only if the **set** of coded mentions
matches. EA0012 gold is not “this patient has epilepsy on three
ASMs.” It is one Diagnosis mention (`epilepsy`, CUI C0014544,
DiagCategory Epilepsy, Certainty 5) plus three Prescription mentions
with dose, unit, frequency, and CUI, including the brand `tegretol`
rather than a substituted generic. EA0177 gold keeps both
`seizure-free` since last clinic (`NumberOfSeizures = 0`) and a
Patient History `seizures` mention. Missing either is a miss;
merging them is a miss; adding a rate the guideline did not code is
an extra.

On Gan, a letter is correct only if the **one** canonical string
maps to the right monthly band. A development example in the 1,500
subset is `2 cluster per month, 6 per cluster`, with the quote
“Cluster days twice this month; typically six seizures in 24 h.”
A clinically adequate “about twelve a month” is the wrong dialect.
A second true historical rate in the same letter is not a second
gold answer.

### What silence means

ExECT empty gold is “not annotated.” Fifty-eight of 200 letters have
no Seizure Frequency mention; three have no four-family gold at all
([ExECT taxonomy](../exectv2/gold_task_taxonomy_2026-08-06.md)).
Extracting a defensible rate from those letters can still score as a
false positive. The guideline also forbids inventing investigation
results and current doses that are only implied.

Gan silence is an explicit label: `unknown`, `no seizure frequency
reference`, or, on the real-letter scheme, Unknown versus No
seizure. Abstention is a scored class, not an empty cell.

### What defaults and closed maps do

ExECT gold contains values the letter did not say. Missing ASM
frequency becomes 1 or `As Required`. “A few” becomes 2. “Teenager”
becomes age 13–19. “Last clinic” becomes the PointInTime token
`LastClinic`. “Well controlled” becomes `Infrequent`. Those tokens
are the gold. A system that quotes the source phrase and stops is
not yet right.

Gan gold contains a different closed map. `multiple` becomes 3 on
the monthly scale. Cluster answers need both sides. Unresolved
“multiple per week” is a sentinel, not an ordinary rate. The
synthetic generation process then **writes letters to those tokens**,
so the public gold is cleaner than a real clinic letter that was
never forced through the template.

### What consensus and conversion do to error

ExECT's published human IAA of 0.47 on seizure frequency means the
pre-consensus SF gold was already the least stable family. Consensus
removed some of that noise and, by the authors' account, also
removed CUI and feature slips that did not reflect clinical choice.
Residual gold defects remain possible; the thesis says so, and this
project's later annotation-evidence synthesis found mechanical
defects and representation disagreements without treating them as a
licence to change frozen gold
([synthesis](../../experiments/exectv2/reliability/exectv2_annotation_evidence_synthesis_2026-07-15.md)).

Gan's real test gold was double-reviewed by two senior clinicians,
which is a stronger endpoint check than ExECT's mixed
clinician/researcher IAA on SF. The conversion to a single number,
however, **destroys** the range, cluster, and duration structure
that the authors later argue is the right supervision. The public
synthetic gold keeps that structure, but only because the letter was
generated from it. The two Gan golds are not interchangeable, which
is why the paper could not train structured formats on real letters.

### Why the two scores cannot be compared

ExECT F1 asks: did you recover the coded inventory? Gan Purist
accuracy asks: did you emit the one current label? A system can be
clinically reasonable on both and still fail both, for opposite
reasons: too few facts on ExECT, the wrong winner or the wrong
dialect on Gan. That is the same conclusion as the
[task-shape framework](task_shape_framework_2026-08-06.md), now
traced to the authors' own annotation history rather than only to
the labels we inherited.

## What this does not show

- It does not show that either gold is clinically invalid.
- It does not recover unpublished Gan real-letter guidelines or IAA.
- It does not re-annotate either corpus.
- It does not authorise changing gold, scorers, or selected scores.
- Thesis IAA figures are from real SNB letters during guideline
  development, not from the 200 synthetic letters. The 2024 table is
  the IAA for the public ExECT set.

## Decision and next action

The annotation difference is explained by research object, evaluation
method, and the problems each team hit. ExECT needed a
feature-identical inventory to validate a rule-based linker. Gan
needed a single normalised endpoint that could be generated at LLM
scale without sharing patient text. Both choices are still visible
in the gold this project scores.

No gold or scorer change follows. The useful next use of this note
is interpretive: when a residual looks like a model failure, check
whether it is actually a guideline convention (ExECT split concepts,
defaults, empty-gold) or an unpublished current-state choice (Gan
one-winner, unknown-versus-rate). Those remain the live reading
problems on each track. The ExECT placement of those conventions —
closed tables in hybrid rewrite, a few selection cues in the prompt —
is recorded in Decision 0055 / prompt-variant slots (guideline rule-vs-prompt note pruned).

A scoped scan of the June reviews in `docs/literature` asked whether
annotation-convention as a cause of IAA is already a surveyed theme
there. It is named, not surveyed
([theme scan](annotation_iaa_literature_theme_2026-08-16.md)). The
broader review, starting from `literature/` and the methods papers
that tree already cites, finds the theme is common once reliability
engineering, scheme choice, and disagreement-as-signal are kept
apart. Owner:
[annotation convention IAA literature review](annotation_convention_iaa_literature_review_2026-08-16.md).
