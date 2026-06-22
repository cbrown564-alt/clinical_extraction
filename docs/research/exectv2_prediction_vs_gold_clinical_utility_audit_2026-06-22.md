# ExECTv2 Prediction vs Gold Clinical Utility Audit

Date: 2026-06-22

## Executive Answer

This audit supports the concern that the current scoring view is too narrow.
Across a 20-letter dev140 sample, the final architecture predictions are often
clinically more useful than the gold labels in two specific ways:

1. They usually preserve exact source evidence with enough sentence context to
be reusable downstream.
2. They often normalize awkward or drift-corrupted gold spans into cleaner
clinical facts, especially for medication regimens, investigations, and
seizure-frequency statements.

That does not mean the predictions are simply "better than gold" as benchmark
answers. The gold labels remain the target for ExECT-style scoring. The better
claim is narrower but important: the model-plus-assembly outputs frequently
perform a richer clinical evidence extraction task than the benchmark labels
measure.

The second question also has a clear answer: yes. The current prompt, scoring,
normalization, and repair stack sometimes improves F1 by moving predictions
toward ExECT conventions in ways that can make the output less clinically useful
or less attribution-clean. The most important examples are benchmark-format
diagnosis companions, residual dictionary additions, duplicate seizure-frequency
projections, and active-rate seizure-frequency repair that raises the headline
score while leaving a large clinical-fidelity gap.

## Scope

This is a dev140 audit only. It does not inspect ExECTv2 holdout rows, full-200
row-level failures, or any locked benchmark surface.

Architectures audited:

| Short name | Artifact | Model role |
|---|---|---|
| v08 | `exectv2_holistic_finding_assembly_v08_dev140` | GPT-4.1 mini performance control |
| v09 | `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | GPT-4.1 mini simplification control |
| DeepSeek | `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | diagnostic comparator |
| Qwen | `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | local diagnostic comparator |

The fixed sample was `EA0044` from the frontend screenshot plus 19
hash-sampled letters from the shared dev140 set:

`EA0044`, `EA0171`, `EA0189`, `EA0033`, `EA0046`, `EA0057`, `EA0132`,
`EA0050`, `EA0047`, `EA0034`, `EA0027`, `EA0030`, `EA0074`, `EA0004`,
`EA0020`, `EA0139`, `EA0067`, `EA0063`, `EA0110`, `EA0168`.

The sample has 113 gold target-family mentions across Diagnosis,
SeizureFrequency, Prescription, and Investigations.

## Evidence Sources

Frontend-facing final artifacts:

- `frontend/public/mock-data/artifacts/exectv2_holistic_finding_assembly_v08_dev140.json`
- `frontend/public/mock-data/artifacts/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140.json`
- `frontend/public/mock-data/artifacts/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140.json`
- `frontend/public/mock-data/artifacts/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140.json`

Assembly and source artifacts:

- `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.json[l]`
- `experiments/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.json[l]`
- `experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.json[l]`
- `experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.json[l]`
- `experiments/exectv2_llm_only_key_entities_structured_v09_dev140_gpt41mini_20260621.jsonl`
- `experiments/exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl`
- `experiments/exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl`

Scoring was replayed with the repo ExECTv2 scorer and the existing assembly
report machinery. No new model calls were made.

## Raw-Surface Caveat And Fix

The original audit found that v08 and v09 assembly JSONL rows contained usable
`raw_lane_mentions`, while DeepSeek and Qwen preserved raw model payloads only
in source key-entity JSONL fields such as `raw_output`, `structured_events`,
and source `predicted_mentions`. That made their assembly `raw_lane_score`
appear as zero even though the models had emitted predictions.

Phase 5 fixes this reporting surface: when a structured-event `raw_output` does
not expose top-level `mentions`, the assembly raw lane is populated from the
source `predicted_mentions`. The preserved `raw_output` and `structured_events`
remain untouched as the deeper raw model surface.

## Quantitative Readout

Full dev140 final metrics:

| Run | Raw lane F1 | Evidence-valid F1 | Headline F1 | Dx | SF | Rx | Inv |
|---|---:|---:|---:|---:|---:|---:|---:|
| v08 | 0.8328 | 0.8872 | 0.9155 | 0.9090 | 0.9053 | 0.9357 | 0.9132 |
| v09 | 0.8231 | 0.8778 | 0.9061 | 0.9090 | 0.9053 | 0.9357 | 0.8549 |
| DeepSeek | 0.7498 | 0.8728 | 0.9174 | 0.8898 | 0.9017 | 0.9415 | 0.9658 |
| Qwen | 0.6406 | 0.8567 | 0.9001 | 0.8563 | 0.8908 | 0.9343 | 0.9579 |

20-letter sample metrics:

| Run | Surface | Overall F1 | Dx | SF | Rx | Inv | Pred | Gold | Exact evidence |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| v08 | raw lane | 0.8376 | 0.7711 | 0.8400 | 0.9388 | 0.9167 | 121 | 113 | 1.000 |
| v08 | final/repaired | 0.8870 | 0.9114 | 0.8400 | 0.9388 | 0.9167 | 117 | 113 | 1.000 |
| v09 | raw lane | 0.7170 | 0.7711 | 0.8400 | 0.9388 | 0.0000 | 99 | 113 | 1.000 |
| v09 | final/repaired | 0.8870 | 0.9114 | 0.8400 | 0.9388 | 0.9167 | 117 | 113 | 1.000 |
| DeepSeek | final/repaired | 0.8739 | 0.8500 | 0.8444 | 0.9545 | 0.9388 | 109 | 113 | 1.000 |
| Qwen | final/repaired | 0.8616 | 0.8981 | 0.8085 | 0.8936 | 0.8936 | 111 | 113 | 1.000 |
| GPT key v09 | source scored | 0.7257 | 0.6098 | 0.6667 | 0.8511 | 0.9167 | 113 | 113 | 1.000 |
| DeepSeek key v0910 | source scored | 0.7619 | 0.6588 | 0.7500 | 0.8696 | 0.9167 | 118 | 113 | 1.000 |
| Qwen key v0910 | source scored | 0.6548 | 0.6346 | 0.5217 | 0.8889 | 0.6383 | 98 | 113 | 1.000 |

The exact-evidence rate is the easiest result to underestimate. In this sample,
the final predictions are not merely cleaner labels. They are exact substrings
from the letters, usually full clauses or full sentences.

## Finding 1: Predictions Are Often Clinically Better Than Gold

### Evidence Context

The gold labels usually encode the benchmark fact, but not reusable evidence.
They are often hyphenated, span-drifted, truncated, or concept-only:

- `seizures`
- `EEG-`
- `Medication:-lamotrigine-75mg-twice-a-day`
- `focal-to-bilateral-convulsive-seizures`
- `MRI-`

The predictions usually attach the source sentence or a compact clinical clause:

- `she has not had any further seizures since her last clinic appointment and since starting the lamotrigine`
- `EEG 2019: generalised spike and wave with photosensitivity`
- `Levetiracetam 750mg bd`
- `Focal to bilateral convulsive seizures, last event October 2019`
- `A MRI two years ago showed an area of gliosis in the right frontal lobe secondary to his previous surgery`

For downstream clinical use, this is materially better. It tells a reviewer
why the fact was extracted, whether it is current/historical/negated, and
whether the evidence is strong enough to reuse.

### EA0044: The Frontend Example Is Real

Gold:

- Diagnosis: `epilepsy-with-generalised-tonic-clonic-seizures-alone`
- SeizureFrequency: two separate `seizures` labels for zero seizures since
  last clinic and since drug change.
- Investigations: `MRI`, `EEG`, and duplicate `EEG-`.

The model outputs are more clinically useful:

- Diagnosis evidence preserves the heading: `Diagnosis: Generalised Epilepsy
  with tonic-clonic seizures alone`.
- Prescription evidence is the clean current regimen: `Medication:
  lamotrigine 75mg twice a day`.
- Investigation evidence preserves the result-bearing phrases: `MRI 2019
  normal` and `EEG 2019: generalised spike and wave with photosensitivity`.
- Seizure frequency evidence preserves the full statement connecting both
  temporal anchors: no further seizures since last clinic and since starting
  lamotrigine.

The gold labels are adequate for a benchmark match. The predictions are better
for a clinician or downstream extraction consumer.

### Medication And Investigation Spans Are Consistently Cleaner

The sample repeatedly shows prescription predictions choosing the exact regimen
span rather than the drifted markup span:

- EA0033: `sodium valproate 1 g twice a day`; `Clobazam 10 mg as required`.
- EA0030: `lamotrigine 250 milligrams twice a day`; `Keppra 1000 milligrams
  twice a day`.
- EA0046: `Levetiracetam 750mg bd`; `Phenytoin 100mg od`.
- EA0057: `Levetiracetam 1000mg bd`.

Investigation predictions similarly preserve result-bearing clauses:

- EA0030: `EEG 1992: frequent bursts of spike and wave and polyspike`; `MRI
  1993: mild cerebellar atrophy`.
- EA0046: MRI gliosis and EEG right-sided sharp-wave evidence.
- EA0171: one shared `MRI and EEG normal 2018` evidence clause cleanly supports
  both investigations.

This is a clinically meaningful improvement over scoring-only label text.

### Gold Omissions Can Make Correct Clinical Output Look Wrong

EA0171 has no gold SeizureFrequency mention, but the letter states that since
starting lamotrigine the patient has had no further episodes. v08/v09/DeepSeek
capture a zero-seizure state after drug change. That is clinically useful, but
it is a false positive against the gold label set.

EA0074 has only a gold diagnosis for juvenile myoclonic epilepsy, while v08/v09
also capture increasing seizure frequency in the note. Again, this is clinically
useful extraction that the current target surface may punish.

This matters because it means the model can be doing a useful clinical task
which the benchmark does not credit.

## Finding 2: Some Constraints Improve F1 But Reduce Clinical Usefulness

### Deterministic Repair Is Prediction-Bearing

The repairs are not just format cleanup. In the 20-letter sample, final mentions
carry many deterministic provenance actions:

- v08/v09: diagnosis convention cleanup, diagnosis alias repair, residual
  benchmark concepts, deterministic prescription repair, deterministic SF union
  arbitration, and deterministic investigation arbitration.
- DeepSeek/Qwen: standard dictionary diagnosis/SF/prescription/investigation
  repair; residual diagnosis, SF, investigation, and prescription additions.

This improves the headline score. It also means the system is no longer just
scoring what the model said. It is scoring a hybrid clinical-and-benchmark
projection.

### Diagnosis Repair Can Add Benchmark Companions That Are Not Clinically New

Diagnosis repair often adds generic `epilepsy` companions or rewrites
convention aliases to improve ExECT agreement. This helps recall because gold
often contains both a syndrome-specific diagnosis and generic `epilepsy`.

Clinically, however, duplicating `epilepsy` beside a more specific diagnosis is
not always adding new information. It can clutter downstream displays and make
the prediction set look more redundant than the clinical record.

EA0046 shows this pattern clearly: the useful clinical fact is symptomatic
structural focal epilepsy secondary to traumatic brain injury with focal to
bilateral convulsive seizures. The benchmark-aligned output also contains
generic epilepsy companions to match ExECT conventions.

### Seizure-Frequency Headline Repair Can Hide A Fidelity Gap

The full dev140 v08 score has SeizureFrequency headline F1 0.9053, but the
active-rate fidelity companion in the same report is much lower. In the sample,
Qwen's SeizureFrequency final score is 0.8085 while the active-rate fidelity
companion is 0.2963.

That is the sharpest warning in this audit. The repaired headline score can
credit a clinically plausible state projection while still failing to preserve
the detailed burden/rate information that would matter clinically.

### Benchmark Labels Encourage Duplicate Or Compressed Temporal States

EA0044 illustrates a useful zero-seizure sentence being rendered as two
benchmark states: since last clinic and since drug change. That may be correct
for ExECT scoring, but downstream clinical use would probably prefer one
evidence-backed event with both temporal anchors rather than duplicate mentions.

EA0171 has the opposite problem: a clinically useful zero-seizure statement is
not in gold, so extracting it can hurt precision. This creates pressure to
suppress clinically useful statements when they are not benchmark-supported.

### Evidence Repair Can Improve Exactness While Changing What The Output Means

The non-GPT runs show many `repaired_evidence_from_mention_text` and
`dropped_evidence_not_substring` warnings. Exact evidence is valuable, but if
repair replaces a longer model rationale with a shorter mention text, the final
artifact may become easier to score while losing context the model originally
selected.

That tradeoff is acceptable for benchmark replay, but it should be reported as
repair, not as raw model evidence selection.

### Prompt And Schema Constraints Favor Compact ExECT Mentions

The prompt/schema asks the model to render legal target-family mentions with
finite attributes. That is necessary for scoring, but it constrains the model
away from richer clinical summaries such as:

- active versus historical seizure burden;
- whether a medication is current, planned, reducing, or rescue-only;
- whether a diagnosis is family history, possible patient diagnosis, or
  clinician impression;
- whether an investigation is historical, planned, repeated, or result-bearing.

The structured events retain some of this state, but the scored mention surface
collapses much of it.

## Row-Level Examples

| Letter | What The Predictions Do Better | What Still Hurts Clinical Usefulness |
|---|---|---|
| EA0044 | Full evidence for generalized epilepsy, lamotrigine regimen, MRI normal, EEG abnormal/photosensitivity, and zero seizures since clinic/drug change. | Benchmark-style duplicate zero-seizure states are less natural than one clinical event with two anchors. |
| EA0171 | Captures normal MRI/EEG and current lamotrigine cleanly; captures no further episodes after lamotrigine. | Gold has no SF mention, so useful seizure-free/current-state evidence can become a false positive. |
| EA0189 | Correctly captures normal CT. Qwen/DeepSeek notice possible myoclonic seizures. | DeepSeek also extracts maternal childhood absence seizures, a family-history fact, as patient diagnosis. Qwen/DeepSeek may overcall uncertain myoclonic events. |
| EA0033 | Medication and investigation spans are cleaner than gold; EEG evidence includes the abnormal pattern. | Diagnosis convention still needs benchmark normalization for JME/generalized tonic-clonic seizure companion facts. |
| EA0046 | Predictions preserve cause, seizure type, last-event timing, medication, MRI gliosis, and EEG sharp-wave evidence. | Generic epilepsy companions and repeated MRI evidence improve benchmark matching but add redundancy. |
| EA0057 | Captures structural epilepsy, focal motor seizures, focal-to-bilateral convulsive seizures, zero-frequency statements, levetiracetam, and abnormal MRI evidence. | Single-vs-multiple seizure category and historical/current framing remain fragile. |
| EA0030 | Clean regimen and investigation evidence; JME abbreviation normalized to juvenile myoclonic epilepsy. | Normalization is helpful, but benchmark projection owns much of the win. |
| EA0074 | Models capture JME with source sentence; v08/v09 also capture increasing near-daily seizures absent from gold. | Clinically useful SF extraction is uncredited or penalized when gold omits it. |
| EA0004 | Predictions preserve uncertain seizure-frequency wording and annual estimate better than a bare `seizures` label. | The benchmark still prefers compact count/period labels over a richer uncertainty state. |

## Sample Ledger

Counts are ordered Diagnosis/SeizureFrequency/Prescription/Investigations.

| Letter | Gold | v08 final | v09 final | DeepSeek final | Qwen final | Main review signal |
|---|---:|---:|---:|---:|---:|---|
| EA0044 | 1/2/1/3 | 3/2/1/2 | 3/2/1/3 | 2/1/1/2 | 2/1/1/2 | Gold labels are compact/duplicated; predictions preserve sentence-level seizure-free and investigation evidence. |
| EA0171 | 4/0/1/2 | 3/1/1/2 | 3/1/1/2 | 3/1/1/2 | 3/0/1/2 | Gold omits SF despite no-further-episodes evidence after lamotrigine. |
| EA0189 | 1/0/0/1 | 0/0/0/1 | 0/0/0/0 | 2/0/0/1 | 1/0/0/1 | Overcall risk: uncertain myoclonic events and family history can become patient diagnosis. |
| EA0033 | 4/0/2/2 | 3/0/2/2 | 3/0/2/2 | 3/0/2/2 | 3/0/2/2 | Cleaner medication and EEG/MRI evidence than gold spans. |
| EA0046 | 4/1/2/4 | 4/2/2/3 | 4/2/2/3 | 5/1/1/4 | 3/1/2/2 | Rich cause/seizure/investigation context; generic companions add redundancy. |
| EA0057 | 7/2/1/1 | 5/2/1/1 | 5/2/1/1 | 5/2/1/1 | 4/4/1/1 | Historical/current boundary stress case for seizure types and zero-frequency states. |
| EA0132 | 6/1/0/4 | 6/2/1/2 | 6/2/1/2 | 6/1/0/2 | 6/3/0/2 | Medication/currentness and investigation result normalization stress case. |
| EA0050 | 3/4/2/2 | 3/5/2/2 | 3/5/2/2 | 3/4/2/2 | 2/4/3/2 | Compact ExECT labels versus fuller clinical evidence. |
| EA0047 | 3/2/4/0 | 2/3/5/0 | 2/3/5/0 | 3/1/2/0 | 1/2/2/0 | Diagnosis convention repair and SF normalization pressure. |
| EA0034 | 4/1/1/1 | 4/2/1/1 | 4/2/1/1 | 5/2/1/1 | 4/1/1/1 | Source-near regimen extraction and evidence context. |
| EA0027 | 1/0/0/0 | 1/0/0/0 | 1/0/0/0 | 1/0/0/0 | 1/0/0/0 | Uncertain diagnosis language and gold convention pressure. |
| EA0030 | 1/0/2/2 | 1/0/2/2 | 1/0/2/2 | 1/0/2/2 | 1/0/2/2 | Abbreviation/regimen/investigation normalization is clinically helpful. |
| EA0074 | 1/0/0/0 | 1/2/0/0 | 1/2/0/0 | 1/0/0/0 | 1/0/1/0 | Gold underrepresents seizure frequency; predictions find increasing near-daily burden. |
| EA0004 | 2/2/1/2 | 2/2/1/2 | 2/2/1/2 | 3/2/1/2 | 2/2/1/2 | Uncertain SF wording is clinically richer than count-only labels. |
| EA0020 | 1/2/1/0 | 3/3/1/0 | 3/3/1/0 | 2/2/1/0 | 2/4/1/0 | Diagnosis certainty and source-context selection. |
| EA0139 | 1/1/1/0 | 1/2/1/0 | 1/2/1/0 | 2/1/1/0 | 1/1/1/0 | Rescue/current medication and possible dictionary residual behavior. |
| EA0067 | 2/1/2/2 | 3/2/2/2 | 3/2/2/2 | 3/1/2/2 | 3/2/2/2 | Seizure-free/current state versus benchmark projection. |
| EA0063 | 1/2/1/0 | 2/3/1/0 | 2/3/1/0 | 1/1/1/0 | 1/2/1/0 | Clinical evidence context around suspected epilepsy. |
| EA0110 | 3/2/1/0 | 4/2/2/0 | 4/2/2/0 | 3/2/1/0 | 4/2/1/0 | SF and investigation evidence compression. |
| EA0168 | 2/3/1/0 | 3/4/1/0 | 3/4/1/0 | 5/2/1/0 | 2/1/1/0 | Gold omissions versus model-supported facts. |

## Answer To Question 1

Yes, in a meaningful but bounded way.

The predictions are better than the gold labels when the desired output is a
clinically reusable evidence record. They preserve exact evidence, use cleaner
source-near spans, and often carry the surrounding sentence needed to understand
temporality, certainty, and currentness.

The predictions are not universally better as annotations. They sometimes
over-extract uncertain, family-history, historical, or redundant facts. They
also depend on deterministic repair for much of their final benchmark agreement.

The right research claim is:

> ExECTv2 gold labels are a benchmark target, but not a sufficient clinical
> utility target. The model-plus-assembly system often produces a richer
> evidence-backed clinical finding set than the benchmark scoring surface
> measures.

## Answer To Question 2

Yes.

The system is constrained in ways that improve F1 while sometimes reducing
clinical usefulness:

- Prompt/schema constraints push outputs toward legal ExECT mention rows rather
  than richer clinical event records.
- Deterministic normalization and dictionary repair add, rewrite, or drop
  prediction-bearing facts, especially for diagnosis and seizure frequency.
- The clinical headline score can improve after projection even when detailed
  seizure-frequency fidelity remains weak.
- Scoring against omitted or drifted gold labels can penalize clinically useful
  evidence-backed predictions.
- Exact-evidence repair can make an output scoreable while narrowing the
  evidence context the model originally selected.

The constraints are not wrong. Many are necessary to make the benchmark
tractable. But they should be treated as controlled, reportable components, not
as invisible post-processing.

## Recommended Next Artifacts

1. Add a `clinical_utility` companion report for ExECTv2 dev140 that scores or
   audits:
   - exact evidence sentence/clause quality;
   - whether evidence contains the attributes being asserted;
   - current/historical/future/family-history status;
   - duplicate clinical fact compression;
   - gold-omitted but clinically supported facts.

2. Add a same-raw-output repair ablation:
   - source model scored output;
   - evidence-valid only;
   - dictionary normalization only;
   - residual benchmark additions;
   - full final assembly.

3. Split deterministic actions into clinical-useful versus benchmark-format
   buckets:
   - clinical-useful: medication normalization, investigation result
     normalization, exact evidence validation, obvious abbreviation expansion.
   - benchmark-format: generic epilepsy companions, residual ExECT concept
     additions, duplicate temporal-state rendering, CUI projection.

4. Add a row-level `gold_disagreement_review` flag:
   - gold likely incomplete;
   - gold span drift/truncation;
   - prediction clinically correct but benchmark-false-positive;
   - prediction clinically plausible but overcalled;
   - deterministic repair changed clinical meaning.

5. Fix the assembly raw-lane reporting gap for Qwen/DeepSeek so the raw lane in
   final assembly summaries is populated from the source `predicted_mentions`,
   while preserving `raw_output` and `structured_events` as the deeper raw model
   surface.

## Completion: Phases 1-5

Completed on 2026-06-22.

- Phase 1 is implemented in
  `docs/research/exectv2_clinical_utility_companion_dev140_2026-06-22.md`
  and `.json`, with exact evidence, attribute-signal, status, duplicate
  compression, and gold-omitted supported-fact audits.
- Phase 2 is represented as a same-raw-output repair ladder in the companion
  report. Raw/source, evidence-valid, dictionary-only,
  residual-addition/direct-final, and clinical-headline surfaces are now
  materialized and directly scored from assembly `prediction_surfaces`.
- Phase 3 is implemented as deterministic action buckets:
  `clinical_useful`, `benchmark_format`, `seizure_frequency`, and `other`.
- Phase 4 is implemented as row-level `gold_disagreement_review` flags in the
  companion JSON, capped to a 20-row visible sample per run in the markdown.
- Phase 5 is implemented in the assembly replay producer. Structured-event
  artifacts whose `raw_output` does not expose top-level `mentions` now use the
  saved source `predicted_mentions` to populate the raw-lane scoring surface,
  without modifying the preserved `raw_output` or `structured_events`.

After regenerating the final four no-call dev140 assemblies, the DeepSeek raw
lane is populated with 899 raw mentions and raw-lane F1 `0.7498`; Qwen is
populated with 749 raw mentions and raw-lane F1 `0.6406`.

The materialized repair ladder shows the deterministic contribution explicitly:
Qwen moves from source `0.6406` to dictionary-only `0.7526` to
residual-addition/direct-final `0.8567`, then clinical headline `0.9001`.
DeepSeek moves from source `0.7498` to dictionary-only `0.8334` to
residual-addition/direct-final `0.8728`, then clinical headline `0.9174`.

## Bottom Line

The frontend is showing a real phenomenon. The model is not merely approximating
the gold labels; it is often doing a more useful clinical evidence-selection
task. The current architecture already contains the right transparency
materials to study this, but the primary score still rewards benchmark
conformity more than clinical utility.

The next research move should not be "stop repairing." It should be to score
and report repair as its own intervention, and to add a clinical-utility
companion surface so benchmark F1 no longer carries more meaning than it can
support.
