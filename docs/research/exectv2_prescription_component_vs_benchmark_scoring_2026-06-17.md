# ExECTv2 Prescription Component Versus Benchmark Scoring

Date: 2026-06-17

Status: research note and scoring vocabulary. This document records the
deterministic Prescription work completed on the ExECTv2 dev split, the
assumptions made while adding medication component scoring, and the remaining
gap between clinically meaningful extraction and benchmark phrase/CUI matching.
It focuses first on Prescription, then generalizes the terminology to the
broader all-entity scorecard.

## Bottom Line

The current Prescription component result answers a clinical question:

```text
Did the system recover the medication regimen facts: name, dose, and frequency?
```

The benchmark Prescription F1 answers a stricter benchmark-conformance question:

```text
Did the system emit the same ExECT mention key as the gold annotation:
entity + normalized phrase text + all non-ignored attributes, including CUI?
```

Those are not the same task. The deterministic rules now recover medication
regimens well on the dev split: name F1 `0.9257`, dose F1 `0.9343`, frequency
F1 `0.9307`, and complete name+dose+frequency tuple F1 `0.9293`. The
Prescription benchmark item F1 remains `0.3020` because the benchmark key still
depends on phrase-scope and ontology projection choices that are not equivalent
to clinical regimen recovery.

This is not a reason to chase exact raw phrase text. For Prescription, a phrase
such as:

```text
Current antiepileptic medication: Lamotrigine 125 milligrams twice a day
```

should be represented clinically as:

```text
Lamotrigine 125 milligrams twice a day
```

The section/list prefix is context, not part of the medication regimen. If the
gold phrase includes or omits that prefix inconsistently, exact phrase matching
is measuring annotation/projection convention, not medication understanding.

## What Has Been Done So Far

The deterministic all-9 baseline now scores all nine ExECTv2 entities on the dev
split and has active deterministic extraction for Prescription, Investigations,
Diagnosis, and SeizureFrequency. Its current artifact is:

```text
experiments/exectv2_deterministic_all9_dev_20260617.md
```

For Prescription, the machinery added so far is:

- A richer anti-seizure medication vocabulary with brand/generic mappings and
  common spelling variants, including examples such as `Keppra` to
  levetiracetam, `Lamictal` to lamotrigine, `Epilim`/`Eplim`/`Episenta` to
  sodium valproate, and `Tegretol`/`Tegretaol` to carbamazepine.
- Regimen extraction that emits complete medication facts rather than every
  isolated medication-name mention.
- Dose and unit parsing for common clinical forms such as `mg`, `mgs`, `mgms`,
  `milligrams`, `milligrammes`, `g`, and `grams`.
- Frequency parsing for schedule forms such as `bd`, `twice daily`, `od`,
  `daily`, `mane`, `nocte`, `morning`, `evening`, `tds`, and rescue/PRN forms
  such as `as required`.
- Split-dose handling such as morning/evening regimens and multiple dose slots.
- Suppression of planned/titration doses and weight-based `mg/kg/day` mentions
  where those should not become current regimen tuples.
- A Prescription component scorer that evaluates medication name, dose,
  frequency, and complete regimen tuple separately from phrase text and CUI.

The current all-entity dev scorecard reports:

| Surface | Per-item F1 | Per-letter F1 |
| --- | ---: | ---: |
| Overall phrase_only | 0.3789 | 0.6210 |
| Overall semantic | 0.3119 | 0.5625 |
| Overall benchmark | 0.2985 | 0.5528 |
| Prescription benchmark | 0.3020 | 0.5223 |
| Prescription name component | 0.9257 | n/a |
| Prescription dose component | 0.9343 | n/a |
| Prescription frequency component | 0.9307 | n/a |
| Prescription complete tuple component | 0.9293 | n/a |

## Assumptions Made

These assumptions are now explicit and should be tested or ablated rather than
left implicit.

1. Prescription is fundamentally a regimen extraction task.

   The clinical object is the drug regimen: drug name, dose, dose unit, and
   frequency. The exact surrounding phrase is evidence/provenance and benchmark
   projection, not the core clinical endpoint.

2. Medication name equivalence should be clinical, not literal.

   Brand names, generic names, and common spelling variants should match when
   they refer to the same drug. `Keppra 500 mg BD` and
   `levetiracetam 500 mg twice daily` are the same clinical regimen, even if the
   exact `DrugName`, phrase text, and CUI strings differ.

3. Dose and frequency should be scored as components before requiring the full
   tuple.

   A single aggregate Prescription F1 hides whether the system missed the drug,
   the dose, the unit, the schedule, or only the benchmark projection. Separate
   name/dose/frequency scoring makes the error analysis actionable.

4. Phrase scope should be source-near but clinically bounded.

   The preferred Prescription phrase should be the medication regimen span, not
   the whole list heading or surrounding clinical sentence. For example,
   `Lamotrigine 125 milligrams twice a day` is a better clinical phrase than
   `Current antiepileptic medication: Lamotrigine 125 milligrams twice a day`.

5. CUI attachment is benchmark-format projection.

   CUI is important for the benchmark-with-CUI surface, but it is not the same
   as identifying the medication regimen. CUI improvements should be reported as
   ontology/projection improvements, not as pure clinical extraction gains.

6. Dev split iteration is not a final benchmark claim.

   These results are ExECTv2 dev results. A full benchmark-comparable audit
   requires a frozen policy, frozen code, and the planned held-out evaluation
   protocol.

## The Current Gap

The high Prescription component F1 and low Prescription benchmark F1 expose a
projection gap:

```text
clinical regimen fact  ->  ExECT mention phrase  ->  attributes  ->  CUI
```

The current component scorer evaluates mostly the first part. The benchmark key
evaluates the whole chain at once. A prediction can therefore be clinically
right and still be counted as a benchmark false positive plus false negative.

The major gap families are:

- Phrase-scope mismatch: the system emits the regimen span while the gold span
  may include a heading, list marker, wider sentence, or different normalization.
- Brand/generic surface mismatch: clinical synonyms are equivalent in the
  component scorer but not necessarily in the exact benchmark key.
- CUI convention mismatch: the system may attach a generic-drug CUI while the
  gold annotation uses a brand, product, or differently scoped concept CUI.
- Attribute-bundle mismatch: exact benchmark scoring requires the full
  non-ignored attribute set to match on the same mention key.
- Split/merge mismatch: one clinical regimen can be annotated or emitted as one
  combined mention or multiple dose-slot mentions.
- Over-emission and under-emission: component scoring can reveal that the system
  found most facts, while benchmark scoring penalizes extra unsupported regimen
  mentions and missed gold mentions simultaneously.

The next research task is not to make the extractor memorize gold phrase text.
It is to define a benchmark projection policy that maps clinically extracted
regimens into the expected ExECT mention representation, then ablate that policy
separately from clinical extraction.

## Scoring Vocabulary

The table below defines the F1 terms used in current ExECTv2 work. These terms
should be used consistently in scorecards, reports, and project status.

| Term | Unit | Match key | What it answers | Main limitation |
| --- | --- | --- | --- | --- |
| Precision | Items or letters | TP / predicted positives | Of what we emitted, how much matched gold? | High precision can still miss many facts. |
| Recall | Items or letters | TP / gold positives | Of what gold contains, how much did we recover? | High recall can over-emit. |
| F1 | Items or letters | Harmonic mean of precision and recall | Single balance between precision and recall. | Hides which subproblem failed. |
| Per-item F1 | Mentions/facts | Multiset of mention keys within each letter | How well every individual annotation item was matched. | Sensitive to duplicate, split, and merge conventions. |
| Per-letter F1 | Entity presence per letter | Whether an entity has any matched item in the letter | How well the system detects entity presence at letter level. | Does not prove all items or attributes are correct. |
| phrase_only F1 | ExECT mention | `entity + normalized phrase` | Whether the phrase basis is close under exact phrase normalization. | Ignores all attributes, so it can overstate clinical correctness. |
| semantic F1 | ExECT mention | `entity + normalized phrase + non-CUI semantic attributes` | Whether phrase and clinical attributes match when CUI is dropped. | Still depends on exact phrase scope. |
| benchmark F1 | ExECT mention | `entity + normalized phrase + all non-ignored attributes`, keeping CUI | Benchmark-conformance under the current with-CUI scorer. | Collapses clinical extraction and ontology projection into one number. |
| Prescription name component F1 | Medication component | Canonicalized `DrugName` per letter | Did we recover medication identities? | Ignores dose/frequency and phrase/CUI. |
| Prescription dose component F1 | Medication component | `DrugDose + DoseUnit` per letter | Did we recover dose magnitudes and units? | Does not bind dose to a specific drug unless complete tuple also matches. |
| Prescription frequency component F1 | Medication component | Normalized `Frequency` per letter | Did we recover schedule frequency? | Does not bind schedule to a specific drug unless complete tuple also matches. |
| Prescription complete tuple F1 | Medication regimen | Canonicalized `DrugName + DrugDose + DoseUnit + Frequency` | Did we recover the full regimen fact? | Ignores exact phrase scope and CUI by design. |
| Source-near overlap | Diagnostic mention overlap | Same entity with substring/source-near phrase overlap | Whether a miss is near the gold phrase rather than unrelated. | Not benchmark-comparable and can be too lenient. |
| Attribute agreement on overlap | Diagnostic attributes | Non-ignored attributes on overlapped mention pairs | Whether near-matched phrases carry correct features. | Depends on the overlap pairing heuristic. |
| Evidence validity rate | Reliability gate | Predicted evidence is a source substring | Whether predictions are grounded in the letter text. | Not a correctness metric by itself. |
| Schema validity rate | Reliability gate | Prediction satisfies the ExECT contract | Whether output is structurally legal. | Legal output can still be clinically wrong. |

## Three Prescription Examples

### Example 1: Section Prefix Versus Regimen Phrase

Source text:

```text
Current antiepileptic medication: Lamotrigine 125 milligrams twice a day
```

Clinically preferred Prescription mention:

```text
text = "Lamotrigine 125 milligrams twice a day"
DrugName = "lamotrigine"
DrugDose = "125"
DoseUnit = "mg"
Frequency = "2"
```

If gold uses the full section-prefixed phrase, exact phrase-only, semantic, and
benchmark matching can fail despite correct medication extraction. The component
scorer should count this as correct because the regimen fact is correct. The
benchmark scorer may count it as one false positive and one false negative
until phrase projection is policy-aligned.

### Example 2: Brand Versus Generic

Source text:

```text
Keppra 500 mg BD
```

Equivalent clinical prediction:

```text
text = "Keppra 500 mg BD" or "levetiracetam 500 mg twice daily"
DrugName = "levetiracetam"
DrugDose = "500"
DoseUnit = "mg"
Frequency = "2"
```

The component scorer maps `Keppra` to levetiracetam and treats the regimen as a
match. The benchmark scorer can still fail if the gold annotation uses a brand
phrase, brand `DrugName`, or a different CUI convention. That failure is useful,
but it is an ontology/projection failure, not evidence that the medication was
clinically missed.

### Example 3: Split Dose Schedule

Source text:

```text
Epilim 300 mg in the morning and 600 mg in the evening
```

Clinically meaningful representation:

```text
sodium-valproate 300 mg Frequency=1
sodium-valproate 600 mg Frequency=1
```

The component scorer can count both medication-dose-frequency tuples if both
slots are recovered. The benchmark scorer may still fail if the gold represents
the whole schedule as one phrase, chooses the brand CUI for `Epilim`, or uses a
different split/merge convention. This is exactly why split/merge behavior needs
to be reported separately from clinical component recovery.

## Broader Entity Implications

Prescription is the clearest example because medication regimens decompose into
obvious clinical components. The same evaluation split applies across ExECTv2:

- Diagnosis: clinical diagnosis category and certainty/negation can be right
  even when phrase basis or CUI differs.
- Investigations: test performed/result/type can be right while the phrase
  target differs between `EEG`, `abnormal EEG`, and the result-bearing clause.
- SeizureFrequency: the clinically important fact is the seizure type plus
  frequency attributes, but the benchmark phrase often wants the seizure-type
  anchor rather than the whole frequency sentence.
- PatientHistory, Onset, WhenDiagnosed, BirthHistory, and EpilepsyCause:
  temporal and assertion attributes need to be separated from the exact phrase
  span and CUI attachment so error analysis can say whether the clinical fact,
  time projection, assertion, or benchmark formatting failed.

The scorecard should therefore keep a layered readout for every entity family:

1. Clinical component or attribute recovery, where the entity has meaningful
   decomposable attributes.
2. Source-near phrase diagnostics, to detect phrase-scope problems without
   turning them into the headline scorer.
3. Semantic exact F1, to measure phrase plus non-CUI attributes.
4. Benchmark with-CUI F1, to measure final benchmark-conformant output.
5. Reliability gates: evidence validity, schema validity, parse/call failures,
   repairs, drops, routing, and CUI attachment rate.

## Recommended Next Steps

1. Define a Prescription phrase projection policy.

   The likely policy is: emit the clinically bounded medication regimen phrase,
   excluding list headings and section labels. Document this as a deliberate
   benchmark-format choice and compare it with raw-gold exact phrase behavior.

2. Build a Prescription CUI projection table as a benchmark-format component.

   Keep this separate from medication extraction. Report benchmark F1 with and
   without CUI projection so CUI gains are not mistaken for clinical gains.

3. Add a Prescription error ledger with counts by gap family.

   Minimum families: phrase-scope mismatch, brand/generic mismatch, CUI mismatch,
   attribute mismatch, split/merge mismatch, false current regimen, missed
   current regimen, and PRN/rescue convention mismatch.

4. Generalize component scoring where clinically meaningful.

   Investigations should have performed/result/type component scores. Diagnosis
   should have phrase/category/assertion/CUI layers. SeizureFrequency should keep
   its phrase-only, semantic, and benchmark surfaces, plus attribute-family
   diagnostics for count/range/time-period/time-since/frequency-change.

5. Keep the headline benchmark score honest.

   The benchmark score should remain the final benchmark-conformance number, but
   it should never be the only number used to explain progress. Otherwise, a
   clinically correct system can look broken, and a benchmark-projected system
   can look clinically stronger than it is.

