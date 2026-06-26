# ExECTv2 Deterministic All-9 Layered Error Analysis

Date: 2026-06-17

Status: research note and diagnostic error analysis for the ExECTv2 `dev`
split. This report explains the current deterministic all-9 scorecard, the
difference between `phrase_only`, `semantic`, and `benchmark` scoring, and the
main row-level failure modes across all nine ExECTv2 entities.

Revision (deep pass): the original note read the score ladder at face value. This
version adds a code-backed "Deep Structural Findings" section showing that a large
share of the measured error is an artifact of how the benchmark target is
constructed (phrase-target altitude, multiset duplicates, context-dependent
attributes, in-sample CUI lookup), and reorganizes the architecture priorities
around a representation-bound vs. recall-bound regime split.

Revision (2026-06-17, root-cause pass): two corrections from re-reading the gold
JSON against the raw MarkupOutput CSVs. (1) Finding 1's `col5`/`col6` labels were
fixed — the column order is per-entity-file; the stable facts are `text`=raw span,
`CUIPhrase`=clean concept (see `contract/evaluation.py`, discoveries D16).
(2) Finding 3 was rewritten: the duplicate-key gold copies are distinct-offset
mentions the benchmark counts twice, so the fix is extractor-side per-occurrence
emission, **not** gold de-duplication; it was implemented for PatientHistory
(`contract.evaluation.EntityEvaluationPolicy`), shifting the numbers below. Diagnosis/
Investigations are unchanged (per-occurrence over-emits their prose repetitions).

Primary artifact:

```text
experiments/exectv2_deterministic_all9_dev_20260617.md
experiments/exectv2_deterministic_all9_dev_20260617.json
```

This is not a frozen full-200 benchmark audit. It is a dev-split diagnostic for
architecture planning, projection-gap accounting, and deciding where GPT-first
and hybrid work should focus next. **Note:** the cited artifact files and their
registry entry predate the 2026-06-17 Finding 3 fix and still show the pre-fix
PatientHistory numbers; regenerate with
`python -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.cli.deterministic_all9_scorecard`
to refresh them. The numbers in this note are the post-fix values.

## Bottom Line

The first version of this note read the three-layer ladder at face value and
concluded that "phrase basis and attribute bundles, not CUI" dominate the loss.
That is directionally true but shallow: it takes the scorer's denominators as
ground truth. They are not. A deeper read of the gold labels, the loader, and the
scorer shows that **a large share of the measured "error" is an artifact of how
the benchmark target is constructed, not of what the extractor can recover.** The
architecture implications change once that is separated out.

Four structural findings, each measured directly against the dev gold (numbers
reproduced under "Deep Structural Findings" below):

1. **There is no coherent phrase target, so `phrase_only` F1 is largely a
   measurement artifact.** The loader keeps the raw covered span (gold `text`) for
   seven entities and the clean canonical term (`CUIPhrase`) for two, by heuristic.
   Re-scoring `phrase_only` against `CUIPhrase` instead of the raw span swings
   entity F1 by up to ±60 points (Investigations `0.60 → 0.06`, Prescription
   `0.31 → 0.01`, WhenDiagnosed `0.82 → 0.00`, but Onset `0.40 → 0.63`). The
   extractor's emission, the raw span, and `CUIPhrase` sit at three different
   altitudes — regimen span vs. raw covered span vs. ontology concept — so the
   "phrase floor" mostly measures altitude alignment, not extraction quality.

2. **A third of all benchmark "misses" are representation mismatches, not missed
   facts.** Of 1021 benchmark false negatives, 340 (33%) fall in letters where
   the gold mention's CUI is *already present* among predictions — the clinical
   concept was found, only the exact mention key differs. This splits the nine
   entities into a representation-bound regime and a recall-bound regime that the
   old phrase-coverage taxonomy conflated.

3. **A concept-de-duplicating extractor caps recall against genuine duplicate
   gold.** 83/466 PatientHistory gold mentions (18%) and 48/405 Diagnosis (12%) are
   exact duplicate-key copies within a single letter — at **distinct offsets**,
   i.e. genuinely separate textual mentions the offset-based benchmark counts
   twice, not annotation artifacts. The old extractor de-duplicated by concept and
   emitted one, forcing the second to a false negative (PatientHistory ceiling
   ≈ 0.82, Diagnosis ≈ 0.88). The fix is per-occurrence emission, **not** gold
   de-duplication (which would be easier than the benchmark). Measured, it is
   net-positive only for PatientHistory (`0.212 → 0.240`); for Diagnosis/
   Investigations naive per-occurrence emission turns prose repetitions into false
   positives and crushes precision, so their ceiling is real but not cheaply
   recoverable (Finding 3).

4. **Attribute bundles are not a function of the phrase, so the `semantic` layer
   has a built-in ceiling for any phrase-keyed (deterministic) architecture.**
   Corpus-wide, the same phrase maps to conflicting attribute bundles for 58% of
   SeizureFrequency phrases (21/36), 32% of Diagnosis (23/73), and 13% of
   PatientHistory (18/144). Certainty, negation, and temporal anchoring are
   context-determined, not lexically determined. The "attribute bundle mismatch"
   family is therefore quantified evidence *for* an LLM-read architecture, not a
   rule-tuning backlog.

Overall dev performance:

| Layer | Per-item F1 | Per-letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| `phrase_only` | 0.4627 | 0.7526 | 576 | 434 | 904 |
| `semantic` | 0.3815 | 0.6814 | 475 | 535 | 1005 |
| `benchmark` | 0.3687 | 0.6747 | 459 | 551 | 1021 |

(These reflect the Finding 3 per-occurrence fix for PatientHistory, landed
2026-06-17; the pre-fix headline was `phrase_only` 0.4571 / `semantic` 0.3754 /
`benchmark` 0.3625. Per-letter F1 is unchanged — duplicates do not affect presence.
Only PatientHistory cells moved; all other entities are identical.)

The per-letter column deserves more weight than the headline gives it. For a
phenotyping task ("does this patient have diagnosis X / investigation Y"),
per-letter presence is the decision-relevant unit, and it is far healthier than
per-item: Diagnosis is `0.32` per-item but `0.75` per-letter, Investigations
`0.32`/`0.58`, SeizureFrequency `0.69`/`0.92`. Leading with the most compressed,
most pessimistic number understates the clinically usable signal.

The layer transition is still useful, but must be read knowing the denominators
above are soft:

| Transition | TP loss | Interpretation |
| --- | ---: | --- |
| `phrase_only` to `semantic` | 101 | Phrase matched, attribute bundle did not — and 13–58% of that is structurally unlearnable by a phrase-keyed system (finding 4). |
| `semantic` to `benchmark` | 16 | Fact matched after dropping CUI, but failed the with-CUI key — scored against a lookup table hand-fit to this same dev gold (in-sample; see below). |

The biggest problem is therefore neither "attach more CUIs" nor simply "improve
phrase basis." It is that the benchmark mention key fuses (a) a phrase target
with no stable altitude, (b) a multiset cardinality the extractor cannot
observe, (c) context-dependent attributes a rule cannot assign, and (d) an
in-sample CUI projection. Separating those four is the real work.

The strongest clinical caveat remains `Prescription`: exact benchmark item F1 is
only `0.3020`, while the clinical Prescription headline is `0.9072`. The deep
read sharpens why — **126 of Prescription's 145 benchmark false negatives (87%)
are letters where the correct drug concept is already emitted.** The benchmark
loss is almost entirely phrase altitude (the extractor's full regimen span vs. the
gold `text` drug fragment) and exact `DrugName` casing, not medication recovery.

## Deep Structural Findings

All figures below are computed directly from the dev gold (`load_letters_for_split("dev")`,
140 letters) and the deterministic predictions (`run_all9_on_letters`). They are
reproducible from `scoring.py` + `benchmark_projection.py` and do not depend on
any sampled row reading.

### Finding 1: the phrase target has no stable altitude

The gold JSON carries two phrase fields from the benchmark MarkupOutput CSVs:
the raw covered span (offset-drift corrupted: truncations, over-captures,
spelling) → `text`, and the clean canonical term → `CUIPhrase`. `data.py` repairs
`text` to `CUIPhrase` for **only** SeizureFrequency and Diagnosis; the other seven
entities are scored on the raw span. That choice is load-bearing, and it is a
heuristic, not a benchmark fact.

(A provenance note, corrected 2026-06-17: which physical CSV column holds each
field varies per entity file — `CUIPhrase` is col6 for SeizureFrequency but col5
for the other entities, and Prescription's `text` is a separate col10 regimen
span. The invariant is `text`=raw span, `CUIPhrase`=clean concept; the column
index is not stable, so this note refers to the fields, not col5/col6. See
`contract/evaluation.py` and discoveries-log D16.)

Two measurements expose how unstable it is. First, how often the raw `text` span
even differs from the clean `CUIPhrase` for each entity (dev):

| Entity | gold w/ CUIPhrase | `text != CUIPhrase` | divergence | loader repairs? |
| --- | ---: | ---: | ---: | --- |
| Investigations | 136 | 123 | 90% | no |
| WhenDiagnosed | 11 | 9 | 82% | no |
| Prescription | 206 | 143 | 69% | no |
| EpilepsyCause | 21 | 12 | 57% | no |
| Onset | 17 | 8 | 47% | no |
| SeizureFrequency | 187 | 74 | 40% | **yes** |
| BirthHistory | 31 | 11 | 35% | no |
| Diagnosis | 404 | 95 | 24% | **yes** |
| PatientHistory | 465 | 99 | 21% | no |

Second, what `phrase_only` F1 becomes if you score against `CUIPhrase` instead of
the current target — i.e. how much the floor is just altitude alignment:

| Entity | `phrase_only` F1 (raw `text`, current) | `phrase_only` F1 (`CUIPhrase`) | Δ |
| --- | ---: | ---: | ---: |
| Investigations | 0.6006 | 0.0619 | −0.54 |
| Prescription | 0.3069 | 0.0149 | −0.29 |
| WhenDiagnosed | 0.8182 | 0.0000 | −0.82 |
| BirthHistory | 0.8852 | 0.6230 | −0.26 |
| EpilepsyCause | 0.6222 | 0.4444 | −0.18 |
| PatientHistory | 0.3183 | 0.3495 | +0.03 |
| Onset | 0.4000 | 0.6286 | +0.23 |
| Diagnosis / SF | unchanged (already `CUIPhrase`) | — | — |

The extractor emits at a third altitude again: for Prescription it emits the full
regimen span (`carbamazepine 400 mg twice a day`), which matches neither the gold
`text` (`carbamazepine-`, a drift-truncated regimen fragment) nor `CUIPhrase` (the
bare drug concept). So the `phrase_only` floor is not a clean "did we find the
span" signal — it is "did our emission altitude happen to match the loader's
per-entity field choice." Any paper claim built on `phrase_only` as a transparent
floor needs this caveat.

### Finding 2: a third of benchmark "misses" are representation, not recall

For each entity, of the benchmark-layer false negatives, how many fall in a
letter where the gold mention's CUI is *already present* among the predictions
(the concept was found; only the exact mention key — phrase scope / attribute
bundle / duplicate cardinality — failed):

| Entity | benchmark FN | of which gold CUI already in preds | share | regime |
| --- | ---: | ---: | ---: | --- |
| WhenDiagnosed | 2 | 2 | 100% | representation-bound |
| Prescription | 145 | 126 | 87% | representation-bound |
| BirthHistory | 14 | 12 | 86% | representation-bound |
| EpilepsyCause | 9 | 6 | 67% | representation-bound |
| Onset | 12 | 7 | 58% | mixed |
| SeizureFrequency | 51 | 28 | 55% | mixed |
| Investigations | 84 | 24 | 29% | recall-bound |
| PatientHistory | 390 | 82 | 21% | recall-bound |
| Diagnosis | 314 | 53 | 17% | recall-bound |
| **Total** | **1021** | **340** | **33%** | — |

This is the single most important reframing. The representation-bound entities
(Prescription, BirthHistory, WhenDiagnosed, EpilepsyCause) are **not** candidate-
generation problems — the clinical concept is recovered in the large majority of
their misses, and the remaining work is projecting the right mention key (phrase
altitude + casing + attribute bundle). The recall-bound entities (Diagnosis,
PatientHistory, Investigations) are the genuine candidate-generation gaps. The old
"phrase coverage miss" family lumped both regimes together and pointed every
entity at "broaden the lexicon," which is the wrong instruction for half of them.

### Finding 3: a concept-de-duplicating extractor caps recall against duplicate gold

Scoring is an exact multiset match per letter. Two gold mentions with the same
`(entity, phrase, attributes)` key require a cardinality of 2 — but the extractor
de-duplicated by concept and emitted 1, so the second copy was an unavoidable
false negative. Exact within-letter benchmark-key duplicate copies in the dev gold:

| Entity | gold mentions | exact duplicate copies | forced-FN share |
| --- | ---: | ---: | ---: |
| PatientHistory | 466 | 83 | 18% |
| Diagnosis | 405 | 48 | 12% |
| Investigations | 136 | 8 | 6% |
| SeizureFrequency | 187 | 5 | 3% |
| Prescription | 206 | 1 | <1% |

PatientHistory's recall ceiling from this effect alone was ≈ `(466−83)/466 = 0.82`;
Diagnosis ≈ `0.88`. The first version of this note proposed de-duplicating the gold
within a letter before the match. **That is wrong, and the deeper read says why.**
All 131 PatientHistory + Diagnosis duplicate copies sit at **distinct offsets** —
they are genuinely separate textual mentions (e.g. "epilepsy" in the opening line
*and* in the history), not identical-span annotation artifacts. The published,
offset-based benchmark counted each one, so de-duplicating the gold would make our
recall *easier than the benchmark* — not benchmark-faithful. The root cause is on
the **extractor** side: it de-duplicated by concept. Fixing that (emit one mention
per textual occurrence) is the faithful move — but only where it pays.

Measured: making de-dup offset-aware (preserve distinct-offset occurrences,
collapse only true same-span re-emissions) is net-positive **only for
PatientHistory** (semantic per-item `0.212 → 0.240`, overall floor `0.375 → 0.382`
at unchanged precision; gold annotates each historical assertion). Applying it to
**Diagnosis/Investigations instead crushes precision** (Diagnosis `0.60 → 0.41`):
their rules match the bare concept word in running prose — "epilepsy" appears 8×
in one letter where gold annotates it once — so every prose token becomes a false
positive. The benchmark annotates distinct clinical *assertions*, not prose tokens,
and the deterministic rules cannot make that distinction. So the per-occurrence fix
is gated to PatientHistory (`EntityEvaluationPolicy`); for Diagnosis
and Investigations the duplicate ceiling is real but **not cheaply recoverable** —
recovering it needs per-entity occurrence selection (a candidate-generation problem,
consistent with their recall-bound regime in Finding 2), and the ceiling must be
stated alongside their per-item recall until then.

### Finding 4: attributes are context-determined, capping the rule architecture

The `semantic` layer requires the full non-CUI attribute bundle. But the bundle
is not a function of the phrase. Counting distinct phrases (corpus-wide) whose
semantic attribute bundle is not unique — i.e. the same phrase legitimately
carries different Certainty/Negation/temporal attributes in different contexts:

| Entity | distinct phrases | phrases w/ conflicting bundle | share |
| --- | ---: | ---: | ---: |
| SeizureFrequency | 36 | 21 | 58% |
| WhenDiagnosed | 2 | 2 | 100% |
| Diagnosis | 73 | 23 | 32% |
| Investigations | 23 | 6 | 26% |
| PatientHistory | 144 | 18 | 13% |
| Prescription | 146 | 11 | 8% |

A phrase-keyed deterministic system assigns one bundle per phrase by
construction, so it cannot satisfy these without reading context. The
`phrase_only → semantic` loss of 101 TP is therefore not all "tune the rules" —
a structural floor of it requires reading the surrounding sentence (uncertainty
hedges, "for 16 years" vs "at age 16", drug-change anchors). This is the cleanest
quantitative argument in the substrate for routing attribute assignment to an LLM
while keeping deterministic candidate generation.

### Finding 5: the CUI projection is in-sample and near-deterministic

Two facts about `benchmark_projection.py` that the layer ladder hides:

- **It is hand-fit to the dev gold.** The lookup tables enumerate the exact
  concepts/CUIs observed in dev (e.g. PatientHistory's ~40 hand-entered concepts,
  the BirthHistory preterm-severity CUIs). The dev with-CUI benchmark numbers are
  therefore in-sample. On the locked test split, coverage holes will appear and
  the with-CUI headline will drop relative to the CUI-dropped `semantic` layer.
  This must be stated before any frozen-test read.
- **Where it underperforms, the gold is genuinely non-functional.** Gold CUI is
  near-deterministic from the phrase for most entities (0–2 ambiguous phrases),
  which is why a lookup works at all. The residual is either context/result-keyed
  (Investigations `eeg` → 3 CUIs by Normal/Abnormal/Unknown, handled correctly by
  result-keying) or true annotator inconsistency no phrase map can satisfy:
  `diabetes` → `C0011847` vs `C0011849`, `born prematurely` → `C0151526` vs
  `C3829315`, plus a literal `null` CUI and one missing CUI in Diagnosis gold. The
  16-TP `semantic → benchmark` loss is mostly this irreducible inconsistency, not
  a fixable projection convention.

## Scoring Contract

The ExECTv2 scorer reduces each mention to a match key and scores by exact
multiset match inside each letter. Counts are then micro-averaged across
letters and entities.

The three score layers differ only in which fields are included in the match
key.

| Layer | Match key | Question answered | What it ignores |
| --- | --- | --- | --- |
| `phrase_only` | `entity + normalized phrase` | Did the system emit the same entity phrase basis? | All attributes, including CUI. |
| `semantic` | `entity + normalized phrase + clinical attributes`, dropping `CUI` | Did the system emit the same clinical fact, assuming CUI is only projection? | `CUI`; always ignores redundant `CUIPhrase`; for `SeizureFrequency`, also ignores guideline-out-of-scope `Certainty` and `Negation`. |
| `benchmark` | `entity + normalized phrase + all benchmark-scored attributes`, keeping `CUI` | Did the system emit the benchmark-comparable mention key? | Redundant `CUIPhrase`; for `SeizureFrequency`, guideline-out-of-scope `Certainty` and `Negation`. |

Phrase normalization lowercases, strips quote characters, converts hyphens to
spaces, and collapses whitespace. It does not do fuzzy matching or substring
matching. For example, `carbamazepine-` and `carbamazepine 400 mg twice a day`
do not match as phrases even when they describe the same medication regimen.

Semantic scoring is not a loose clinical preference metric. It is still exact
on the normalized phrase and on the non-CUI attribute bundle. It only removes
CUI from the attribute key. A correct phrase with `Certainty=5` instead of
gold `Certainty=4`, or age duration encoded as `Age=16` rather than
`NumberOfTimePeriods=16`, will pass phrase-only scoring but fail semantic
scoring.

Benchmark scoring is the final with-CUI exact key. A row can be semantically
correct and still fail benchmark scoring when the CUI convention differs.

## Per-Entity Layer Gap

| Entity | Phrase F1 | Semantic F1 | Benchmark F1 | Phrase to semantic TP loss | Semantic to benchmark TP loss | Main gap |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| BirthHistory | 0.8852 | 0.6230 | 0.5574 | 8 | 2 | Assertion certainty and CUI projection after high phrase recall. |
| Diagnosis | 0.3958 | 0.3428 | 0.3216 | 15 | 6 | Low phrase recall, certainty/category exactness, and CUI convention. |
| EpilepsyCause | 0.6222 | 0.5333 | 0.5333 | 2 | 0 | Cause-context over-emission and certainty mismatch. |
| Investigations | 0.6006 | 0.3653 | 0.3220 | 38 | 7 | Result/type attributes are the dominant loss; CUI adds a smaller projection gap. |
| Onset | 0.4000 | 0.2857 | 0.2857 | 2 | 0 | Temporal representation, especially age versus duration. |
| PatientHistory | 0.3183 | 0.2402 | 0.2371 | 25 | 1 | Very large phrase coverage gap plus temporal/assertion bundle mismatch. |
| Prescription | 0.3069 | 0.3020 | 0.3020 | 1 | 0 | Exact phrase basis is the dominant benchmark gap; clinical components are much stronger. |
| SeizureFrequency | 0.7430 | 0.6921 | 0.6921 | 10 | 0 | Good phrase basis, remaining frequency-attribute failures. |
| WhenDiagnosed | 0.8182 | 0.8182 | 0.8182 | 0 | 0 | Small residual phrase spelling/projection issue; no layer-specific attribute/CUI loss. |

## Entity-Level Error Analysis

### BirthHistory

Current benchmark item F1: `0.5574`.

BirthHistory has a strong phrase-only score (`0.8852`), so the deterministic
rules often find the right birth-history phrase. The major score drop is from
phrase-only to semantic, where assertion certainty and related attributes must
match exactly. A smaller CUI projection gap remains.

Row-level examples:

| Break | Row | Gold | Prediction | Reading |
| --- | --- | --- | --- | --- |
| Phrase miss | `EA0010` | `perinatal-insult` | none | The note contains "probable perinatal insult"; the extractor missed the BirthHistory mention in phrase-only scoring. |
| Attribute mismatch | `EA0010` | `perinatal-insult`, `Certainty=4`, `Negation=Affirmed` | `perinatal-insult`, `Certainty=5`, `Negation=Affirmed` | Phrase-only counts this as correct, but semantic scoring fails because uncertainty is stronger in gold than in the prediction. |
| CUI mismatch | `EA0137` | `perinatal-injury`, `CUI=C0005604` | `perinatal-injury`, `CUI=C0456798` | Clinical assertion matches, but benchmark CUI projection differs. |

Representative evidence:

```text
symptomatic structural focal epilepsy (probable perinatal insult)
```

```text
changes in the left fronto-temporal region consistent with a perinatal injury
```

Interpretation: BirthHistory should not be optimized by adding broad phrase
rules alone. The near-term gain is assertion calibration and CUI projection for
a small set of birth-history concepts.

### Diagnosis

Current benchmark item F1: `0.3216`.

Diagnosis is low at all layers. The phrase-only score (`0.3958`) shows that the
deterministic diagnosis surface list captures some diagnoses, but it misses or
collapses many specific gold diagnosis phrases. Semantic scoring then loses
additional rows to certainty and category exactness. Benchmark scoring loses a
smaller but visible set to CUI projection.

Row-level examples:

| Break | Row | Gold | Prediction | Reading |
| --- | --- | --- | --- | --- |
| Phrase miss / over-broad phrase | `EA0002` | `temporal-lobe-epilepsy`, `focal-seizures`, `secondary-generalised-seizures` | `epilepsy` | The rule found a broad diagnosis but not the benchmark's specific diagnosis/seizure-type phrases. |
| Attribute mismatch | `EA0025` | `jme`, `Certainty=3`, `DiagCategory=Epilepsy`, `Negation=Affirmed` | `jme`, `Certainty=5`, `DiagCategory=Epilepsy`, `Negation=Affirmed` | Phrase and category match, but "possible JME" needs lower certainty. |
| CUI mismatch | `EA0008` | `symptomatic-structural-focal-epilepsy`, `CUI=C0472349` | same phrase and semantic attrs, `CUI=C0014547` | A benchmark projection failure after semantic agreement. |

Representative evidence:

```text
Diagnosis: focal epilepsy-Probable temporal
```

```text
Diagnosis: generalised tonic clonic seizures with myoclonic jerks, possible JME
```

Interpretation: Diagnosis needs entity-specific phrase policy and certainty
logic before more CUI work. The extractor often recognizes epilepsy but not the
gold's level of diagnostic specificity.

### EpilepsyCause

Current benchmark item F1: `0.5333`.

EpilepsyCause loses mostly through phrase/context selection and a small
attribute-certainty gap. There was no semantic-to-benchmark CUI mismatch in the
sampled dev analysis; benchmark equals semantic for this run.

Row-level examples:

| Break | Row | Gold | Prediction | Reading |
| --- | --- | --- | --- | --- |
| Phrase / context false positive | `EA0008` | no matched EpilepsyCause for `meningioma` | `meningioma-`, `CUI=C0349604` | "Previous meningioma resection" is historical context, but the rule over-projects it as an epilepsy cause. |
| Attribute mismatch | `EA0059` | `meningitis`, `Certainty=4`, `Negation=Affirmed` | `meningitis`, `Certainty=5`, `Negation=Affirmed` | "secondary probably caused by early life meningitis" should preserve uncertainty. |
| CUI mismatch | none found in sampled layer-difference scan | n/a | n/a | CUI projection is not currently the main EpilepsyCause issue. |

Representative evidence:

```text
Previous meningioma resection 3rd January 2005
```

```text
Symptomatic structural epilepsy secondary probably caused by early life meningitis
```

Interpretation: EpilepsyCause needs better causal-context gating and uncertainty
calibration. Avoid broadening cause lexicons without stronger context logic.

### Investigations

Current benchmark item F1: `0.3220`.

Investigations has one of the largest layer gaps. Phrase-only F1 is `0.6006`,
but semantic F1 drops to `0.3653`, losing 38 true positives. That means many
test phrases are found, but result/type attributes are wrong or incomplete.
Benchmark CUI projection loses another 7 true positives.

Row-level examples:

| Break | Row | Gold | Prediction | Reading |
| --- | --- | --- | --- | --- |
| Phrase/projection mismatch | `EA0002` | `MRI-scan`, `MRI_Performed=Yes`, `MRI_Results=Abnormal`, `CUI=C1319851` | `MRI`, `MRI_Performed=Yes`, `CUI=C0436539` | The note states a prior MRI abnormality and repeat MRI plan. The prediction captures MRI performed but misses abnormal-result projection. |
| Attribute mismatch | `EA0004` | `EEG-`, `EEG_Performed=Yes`, `EEG_Results=Abnormal` | `EEG-`, `EEG_Performed=Yes` | Phrase matches, but "temporal slowing" is not encoded as an abnormal result. |
| CUI mismatch | `EA0040` | `EEG`, normal result, `CUI=C0560017` | `EEG`, normal result, `CUI=C0744602` | Semantic attributes match; result-specific benchmark CUI differs. |

Representative evidence:

```text
previous MRI scan in 2012. It does show a subtle high intensity signal in the left temporal lobe
```

```text
An EEG in 2014 did show some temporal slowing.
```

```text
EEG 1st of February 2018 - Essentially normal
```

Interpretation: Investigations should get component diagnostics: test performed,
result, test subtype, and CUI projection. A single exact mention F1 hides the
fact that result extraction is the main bottleneck.

### Onset

Current benchmark item F1: `0.2857`.

Onset is small-count and brittle. Phrase-only F1 is `0.4000`; semantic and
benchmark are both `0.2857`. The main failure is temporal representation,
especially confusing age-at-onset and duration-since-onset.

Row-level examples:

| Break | Row | Gold | Prediction | Reading |
| --- | --- | --- | --- | --- |
| Phrase false positive | `EA0007` | no matched Onset for the extracted phrase | `seizures`, `Age=13`, `AgeUnit=Year` | A seizure-frequency context was apparently interpreted as onset context. |
| Attribute mismatch | `EA0057` | `epilepsy`, `NumberOfTimePeriods=16`, `TimePeriod=Year` | `epilepsy`, `Age=16`, `AgeUnit=Year` | The phrase matches, but "has been ... for 16 years" style duration should not become age-at-onset. |
| CUI mismatch | none found in sampled layer-difference scan | n/a | n/a | Benchmark equals semantic for Onset in this run. |

Representative evidence:

```text
seizures every 3 to 4 weeks, possibly focal onset
```

Interpretation: Onset should be treated as a temporal-anchor problem, not a
simple phrase problem. The next diagnostic should separate age-at-onset,
duration-since-onset, and date/year onset patterns.

### PatientHistory

Current benchmark item F1: `0.2371` (post per-occurrence fix; was `0.2087`).

PatientHistory is the largest all-9 bottleneck. It has 466 gold mentions and
175 predicted mentions (up from 157 once per-occurrence emission recovers the
distinct-offset repeat assertions, Finding 3). Phrase-only F1 is `0.3183`, so
recall and phrase scope are still poor before attributes are considered. Semantic
F1 drops to `0.2402`, mostly through temporal, certainty, and negation bundle
mismatches. CUI contributes one additional true-positive loss in this run, but it
is not the central problem.

PatientHistory ledger from the scorecard:

| Gap family | Count |
| --- | ---: |
| Gold mentions | 466 |
| Predicted mentions | 175 |
| Predicted mentions with CUI | 175 |
| Predicted mentions with temporal attributes | 9 |
| Predicted negated mentions | 36 |
| Phrase-scope/missing FN | 364 |
| Phrase-scope/over-emission FP | 73 |
| Additional attribute-bundle FN versus phrase | 25 |
| Additional attribute-bundle FP versus phrase | 25 |
| Additional CUI FN versus semantic | 1 |
| Additional CUI FP versus semantic | 1 |

Row-level examples:

| Break | Row | Gold | Prediction | Reading |
| --- | --- | --- | --- | --- |
| Phrase miss | `EA0002` | `convulsive-seizures` | none | The note mentions "bigger convulsive seizures"; conservative PatientHistory rules miss the gold historical concept. |
| Attribute mismatch | `EA0009` | `febrile-seizures`, `AgeLower=2`, `AgeUpper=34`, `AgeUnit=Month` | `febrile-seizures`, `Age=2`, `AgeUnit=Year` | Phrase matches, but the age range "2 months and 34 months" is badly projected. |
| CUI mismatch | `EA0073` | `diabetes`, `CUI=C0011847` | `diabetes`, `CUI=C0011849` | Semantic assertion matches, but benchmark CUI differs. |

Representative evidence:

```text
before one of her have bigger convulsive seizures
```

```text
2 febrile seizures at the age of 2 months and 34 months
```

```text
background of ischaemic heart disease, hypertension, and diabetes
```

Interpretation: PatientHistory needs a deliberately broader candidate strategy,
probably LLM-first or hybrid candidate assessment. Deterministic regex coverage
alone is unlikely to recover enough long-tail historical concepts without
over-emission unless paired with strong context and assertion gates.

### Prescription

Current benchmark item F1: `0.3020`.

Prescription is the clearest case where the benchmark score and clinical
utility diverge. Exact phrase-only F1 is `0.3069`, semantic F1 is `0.3020`, and
benchmark F1 is also `0.3020`. The layer transition loss is tiny after phrase
matching: only one true positive is lost from phrase-only to semantic, and no
additional true positives are lost to CUI in this run. The main benchmark
problem is phrase basis.

The clinical component readout tells a different story:

| Prescription component | Item F1 | Precision | Recall |
| --- | ---: | ---: | ---: |
| Clinical headline | 0.9072 | 0.9293 | 0.8860 |
| Medication name | 0.9257 | 0.9444 | 0.9078 |
| Dose | 0.9343 | 0.9536 | 0.9158 |
| Frequency | 0.9307 | 0.9495 | 0.9126 |
| Complete tuple | 0.9293 | 0.9485 | 0.9109 |
| Ordinary complete tuple | 0.9096 | 0.9326 | 0.8877 |
| Rescue regimen | 0.8333 | 0.8333 | 0.8333 |
| Future medication diagnostic | 0.2609 | 0.2143 | 0.3333 |
| Weight-based dosing diagnostic | 0.0000 | 0.0000 | 0.0000 |

Row-level examples:

| Break | Row | Gold | Prediction | Reading |
| --- | --- | --- | --- | --- |
| Phrase mismatch | `EA0002` | `carbamazepine-`, `DrugDose=400`, `DoseUnit=mg`, `Frequency=2` | `carbamazepine 400 mg twice a day`, same clinical regimen attrs | Clinically correct regimen, benchmark phrase mismatch. |
| Attribute mismatch | `EA0167` | `sodium-valproate-400mg-twice-a-day`, `DrugName=SodiumValproate` | same phrase, `DrugName=sodium-valproate` | This is a `DrugName` spelling/projection mismatch inside the exact semantic key. |
| CUI mismatch | none found in sampled layer-difference scan | n/a | n/a | Prescription's current benchmark gap is phrase and exact attribute convention, not CUI loss after semantic match. |

Representative evidence:

```text
Current antiepileptic medication: carbamazepine 400 mg twice a day Topiramate 100 mg BD
```

```text
sodium valproate 400mg twice a day
```

Interpretation: Prescription should not be optimized by chasing raw gold phrase
text. The right paper-facing story is a projection-gap story: medication
regimens are recovered well, while exact benchmark mention representation
remains weak. Keep the clinical headline and projection table side by side.

### SeizureFrequency

Current benchmark item F1: `0.6921`.

SeizureFrequency is the strongest high-support entity in the deterministic
all-9 run. Phrase-only F1 is `0.7430`; semantic and benchmark are both
`0.6921`. There is no additional CUI gap after semantic matching because the
shared lexicon currently assigns the correct CUI for semantically matching
mentions.

The remaining gap is mostly frequency-attribute logic and over-emission.

Row-level examples:

| Break | Row | Gold | Prediction | Reading |
| --- | --- | --- | --- | --- |
| Phrase/over-emission | `EA0005` | no matched gold for several extra emitted mentions | `seizures`, `absences`, `Generalised tonic clonic seizure` | The extractor over-emits multiple frequency mentions in a complex seizure history. |
| Attribute mismatch | `EA0022` | `focal-seizures`, `NumberOfSeizures=0`, `PointInTime=DrugChange` | `focal-seizures`, `NumberOfSeizures=0` | Phrase and seizure-free state match, but the drug-change anchor is missing. |
| CUI mismatch | none found in sampled layer-difference scan | n/a | n/a | Benchmark equals semantic for SF in this run. |

Representative evidence:

```text
focal seizures are completely under control on the dose of lamotrigine 200 mg twice a day
```

Interpretation: The next SF gains are likely from temporal anchor completion,
competing-mention selection, and over-emission controls rather than CUI.

### WhenDiagnosed

Current benchmark item F1: `0.8182`.

WhenDiagnosed has the highest exact all-layer score among the small structured
entities. Phrase-only, semantic, and benchmark are identical, so the remaining
errors are not layer-specific attribute or CUI failures. The sampled failure is
a phrase spelling/projection mismatch.

Row-level examples:

| Break | Row | Gold | Prediction | Reading |
| --- | --- | --- | --- | --- |
| Phrase mismatch | `EA0075` | `Epilepsy`, `Age=18`, `AgeUnit=Year`, `CUI=C0014544` | `epileps`, same attributes and CUI | Attributes and CUI are right, but the predicted phrase is truncated. |
| Attribute mismatch | none found in sampled layer-difference scan | n/a | n/a | No separate semantic loss after phrase matching. |
| CUI mismatch | none found in sampled layer-difference scan | n/a | n/a | Benchmark equals semantic for this run. |

Interpretation: WhenDiagnosed mainly needs a small phrase projection fix and
continued pattern coverage. It is not a priority bottleneck compared with
PatientHistory, Investigations, Diagnosis, or benchmark-shaped Prescription.

## Cross-Entity Failure Taxonomy

The current all-9 deterministic errors fall into seven reusable failure
families.

| Failure family | Entities most affected | Description | Example |
| --- | --- | --- | --- |
| Phrase coverage miss | Diagnosis, PatientHistory, Prescription, Investigations | The gold mention phrase is absent from predictions, or the prediction uses a broader/narrower phrase. | `EA0002` Diagnosis predicts broad `epilepsy` instead of specific diagnosis phrases. |
| Phrase over-emission | EpilepsyCause, Onset, SeizureFrequency, Investigations | The system emits an entity mention that gold does not contain. | `EA0008` EpilepsyCause emits `meningioma-` from historical resection context. |
| Attribute bundle mismatch | BirthHistory, Diagnosis, Investigations, Onset, PatientHistory, SeizureFrequency | Phrase matches, but certainty, negation, temporal, result, or frequency attributes differ. | `EA0009` PatientHistory converts `2 months and 34 months` to `Age=2 Year`. |
| Temporal representation mismatch | Onset, WhenDiagnosed, PatientHistory, SeizureFrequency | The fact is located but encoded as the wrong temporal type. | `EA0057` Onset duration becomes age-at-onset. |
| Result/type under-specification | Investigations | Test phrase is found, but result or subtype is missing. | `EA0004` EEG phrase found but abnormal temporal slowing not encoded. |
| Benchmark CUI projection mismatch | BirthHistory, Diagnosis, Investigations, PatientHistory | Semantic fact matches after dropping CUI, but with-CUI benchmark key fails. | `EA0040` normal EEG has result-compatible attributes but different CUI. |
| Clinical component versus benchmark phrase mismatch | Prescription | The clinical regimen is right, but exact mention phrase/key is wrong. | `EA0002` `carbamazepine-` versus `carbamazepine 400 mg twice a day`. |

These seven families are a vocabulary, not a priority list. Finding 2 supplies
the priority axis the families lacked — the regime each entity is actually in:

| Regime | Entities | What the misses are | Right move |
| --- | --- | --- | --- |
| Representation-bound | Prescription, BirthHistory, WhenDiagnosed, EpilepsyCause | Concept found ≥67% of misses; loss is phrase altitude + casing + bundle | Fix the projection (cheap, near-free F1); do **not** broaden lexicons |
| Mixed | SeizureFrequency, Onset | ~55% concept-found; split between bundle and over/under-emission | Attribute/anchor logic + emission control |
| Recall-bound | Diagnosis, PatientHistory, Investigations | <30% concept-found; the concept is genuinely absent | Real candidate generation (LLM-first/hybrid) |

## What This Means For Architecture

The deterministic all-9 substrate is useful as a transparent floor and candidate
source, not as a freeze-ready benchmark solution. The deep findings change the
priority order, and add a class of work the first version missed entirely:
fixing the *evaluation*, not just the extractor.

Extractor priorities, by regime (Finding 2):

1. **Recall-bound — needs candidate generation, not rule tuning.**
   `Diagnosis` (17% concept-found), `PatientHistory` (23%), `Investigations`
   (29%) are where the clinical fact is genuinely absent. These justify a
   GPT-first or hybrid candidate assessor. `Investigations` additionally needs
   the performed/result/subtype component split — but note 29% of its misses are
   representation, so component projection buys part of it too.
2. **Representation-bound — fix projection, do not broaden lexicons.**
   `Prescription` (87% concept-found), `BirthHistory` (86%), `WhenDiagnosed`
   (100%), `EpilepsyCause` (67%) already recover the concept. Their benchmark F1
   moves by aligning the emitted phrase altitude to the gold column the loader
   chose and matching `DrugName`/attribute casing — not by adding rules.
3. **Mixed — attribute/anchor logic.** `SeizureFrequency` and `Onset`: temporal
   anchor completion, age-vs-duration disambiguation, and over-emission control.

Evaluation-side priorities (these gate the validity of every number above):

4. **Decide the phrase target deliberately (Finding 1).** The per-entity raw-span
   vs `CUIPhrase` choice swings F1 by up to ±60 points and is currently a loader
   heuristic. Pick the benchmark-faithful target per entity, document it, and
   report `phrase_only` against a single declared target — or stop using
   `phrase_only` as a "floor" at all.
5. **Emit per textual occurrence; do NOT de-duplicate gold (Finding 3).** The
   PatientHistory/Diagnosis duplicate copies are distinct-offset mentions the
   benchmark counts twice, so collapsing the gold would be easier than the
   benchmark. The faithful fix is extractor-side per-occurrence emission — done for
   PatientHistory (`0.212 → 0.240`). For Diagnosis/Investigations it over-emits
   prose repetitions, so publish their ≈0.88 ceiling next to per-item recall until
   per-entity occurrence selection exists. This is an extractor decision, not a
   scorer one.
6. **Treat the with-CUI benchmark layer as in-sample on dev (Finding 5).** The
   CUI lookup is hand-fit to dev concepts; its dev benchmark numbers will not
   transfer to the locked test. Report `semantic` as the architecture-comparable
   layer and `benchmark` with an explicit in-sample flag until a test read.

## Recommended Next Work

1. Add a reusable all-entity projection-gap ledger.

   Minimum columns: row id, entity, gold phrase, predicted phrase, phrase match,
   semantic match, benchmark match, gap family, evidence, gold attributes,
   predicted attributes, and whether the miss is a candidate-source miss or a
   projection miss.

2. Add per-entity component diagnostics where clinically meaningful.

   Good candidates: `Investigations` performed/result/type, `Diagnosis`
   phrase/category/assertion, `SeizureFrequency` count/range/period/anchor
   families, and `Prescription` split/merge, rescue, future medication, and
   weight-based dosing.

3. Use deterministic outputs as candidate sources, not hidden final truth, in
   all-entity hybrid work.

   The deterministic layer is high-value for `Prescription`, `SeizureFrequency`,
   and some structured entities. It is not sufficient for `PatientHistory` and
   broad diagnosis specificity.

4. Keep CUI projection explicit.

   CUI improvements should be reported as benchmark-format projection gains
   unless they change the clinical concept selected. Do not describe CUI
   projection as clinical extraction improvement by itself.

5. Require all future all-entity scorecards to show the three-layer ladder.

   Every run should report phrase-only, semantic, and benchmark scores, plus
   reliability gates. A single benchmark F1 is too compressed to support
   architecture decisions.

6. Do not run a new full-200 audit yet.

   Per current project status, full-200 ExECTv2 audits remain blocked until
   dev-split evidence beats the benchmark target with a predeclared readout.

7. Emit per textual occurrence, not gold de-duplication (Finding 3).

   The duplicate gold copies are distinct-offset mentions, so gold de-duplication
   would be easier than the offset-based benchmark. The extractor now keys its
   de-dup on the source span for PatientHistory (offsets are reliable as relative
   instance identifiers even though they drift in absolute terms), recovering the
   genuine duplicate assertions. For Diagnosis/Investigations, where per-occurrence
   emission over-emits prose repetitions, publish the ≈0.88 duplicate ceiling next
   to per-item recall until per-entity occurrence selection exists.

8. Declare one phrase target per entity and flag the CUI layer as in-sample
   (Findings 1, 5). Stop reporting `phrase_only` as a transparent floor against
   an undocumented raw-span/`CUIPhrase` mixture, and mark the with-CUI benchmark
   layer in-sample on dev until a locked-test read exists.

## Claim Language

Safe claim:

```text
On the ExECTv2 dev split, the deterministic all-9 substrate reaches 0.3687
benchmark / 0.3815 semantic per-item F1, 0.6747 benchmark per-letter F1, and a
higher 0.75/0.92 per-letter F1 on Diagnosis/SeizureFrequency. A structural read of
the gold shows that 34% of benchmark false negatives are representation mismatches
in letters where the correct concept was already emitted; that PatientHistory and
Diagnosis carry duplicate-key gold mentions at distinct offsets (genuine repeat
assertions the benchmark counts twice), which per-occurrence emission recovers for
PatientHistory but not for the prose-repetition entities (a ≈0.88 Diagnosis
ceiling); and that 13–58% of attribute-bundle loss is context-determined and
structurally outside a phrase-keyed rule system.
```

Unsafe claims:

```text
The deterministic all-9 system is close to benchmark quality after CUI fixes.
Phrase basis is the dominant, uniform bottleneck across the nine entities.
```

Why unsafe: (1) semantic-to-benchmark CUI loss is only 16 TP, and that CUI layer
is in-sample on dev. (2) "Phrase basis" is not one bottleneck — for four entities
the concept is already recovered and the loss is cosmetic key projection
(representation-bound), while for three it is genuine recall; treating them
uniformly points half the entities at the wrong fix. (3) Part of the phrase and
multiset loss is a scorer/target-construction artifact, not extractor capability.

## Appendix: Per-Entity Counts

| Entity | Layer | Item F1 | TP | FP | FN |
| --- | --- | ---: | ---: | ---: | ---: |
| BirthHistory | phrase_only | 0.8852 | 27 | 3 | 4 |
| BirthHistory | semantic | 0.6230 | 19 | 11 | 12 |
| BirthHistory | benchmark | 0.5574 | 17 | 13 | 14 |
| Diagnosis | phrase_only | 0.3958 | 112 | 49 | 293 |
| Diagnosis | semantic | 0.3428 | 97 | 64 | 308 |
| Diagnosis | benchmark | 0.3216 | 91 | 70 | 314 |
| EpilepsyCause | phrase_only | 0.6222 | 14 | 10 | 7 |
| EpilepsyCause | semantic | 0.5333 | 12 | 12 | 9 |
| EpilepsyCause | benchmark | 0.5333 | 12 | 12 | 9 |
| Investigations | phrase_only | 0.6006 | 97 | 90 | 39 |
| Investigations | semantic | 0.3653 | 59 | 128 | 77 |
| Investigations | benchmark | 0.3220 | 52 | 135 | 84 |
| Onset | phrase_only | 0.4000 | 7 | 11 | 10 |
| Onset | semantic | 0.2857 | 5 | 13 | 12 |
| Onset | benchmark | 0.2857 | 5 | 13 | 12 |
| PatientHistory | phrase_only | 0.3183 | 102 | 73 | 364 |
| PatientHistory | semantic | 0.2402 | 77 | 98 | 389 |
| PatientHistory | benchmark | 0.2371 | 76 | 99 | 390 |
| Prescription | phrase_only | 0.3069 | 62 | 136 | 144 |
| Prescription | semantic | 0.3020 | 61 | 137 | 145 |
| Prescription | benchmark | 0.3020 | 61 | 137 | 145 |
| SeizureFrequency | phrase_only | 0.7430 | 146 | 60 | 41 |
| SeizureFrequency | semantic | 0.6921 | 136 | 70 | 51 |
| SeizureFrequency | benchmark | 0.6921 | 136 | 70 | 51 |
| WhenDiagnosed | phrase_only | 0.8182 | 9 | 2 | 2 |
| WhenDiagnosed | semantic | 0.8182 | 9 | 2 | 2 |
| WhenDiagnosed | benchmark | 0.8182 | 9 | 2 | 2 |
