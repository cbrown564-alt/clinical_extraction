# Qwen ExECTv2 LLM-Only Error Analysis

Date: 2026-06-23

Scope: attribution-clean Qwen `llm_only` ExECTv2 key-entity experiments where
Qwen must generate the scored facts and Qwen-owned finalization must select
among those model-generated facts. Candidate-backed and rescue-backed results
are discussed only as diagnostics.

Primary protocol:

- `docs/design/llm_repair_attribution_protocol_2026-06-22.md`
- `docs/experiments/exectv2/key_entities/qwen_protocol_clean_attribution_2026-06-23.md`

Primary on-target artifact (full dev, added 2026-06-23 revision):

- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_clean_render_ids_full_examples_dev140_qwen36_live_20260623.jsonl`
- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_clean_render_ids_full_examples_dev140_qwen36_live_20260623.md`

Earlier small-sample row-level artifacts (now known to be optimistic; see
Revision Note):

- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_mentions_full_examples_dev5_qwen36_live_20260623.jsonl`
- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_mention_ids_full_examples_dev5_qwen36_live_20260623.jsonl`
- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_clean_render_ids_full_examples_dev5_qwen36_live_20260623.jsonl`
- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_per_entity_clean_render_ids_full_examples_dev1_qwen36_live_20260623.jsonl`

## Revision Note (2026-06-23): Full-Dev Measurement Supersedes dev5

The first edition of this analysis read the clean generation route almost
entirely off `dev5` (five letters) and a recurring `0.842` "first-row" figure.
The clean-render route has now been run on the **full dev split (140 letters)**.
The dev5 headlines were not merely noisy; they were systematically optimistic.
Every favorable small-sample number shrank at scale:

| Surface | dev5 (old) | dev140 (measured) |
| --- | ---: | ---: |
| strict `model_preserving_canonical` F1 | 0.517 | **0.339** |
| phrase_only (item) | 0.607 | 0.446 |
| source_near (item) | 0.854 | 0.716 |
| evidence validity | 1.0000 | 0.9623 |
| Prescription clinical-recovery | 1.000 | 0.839 |
| Diagnosis clinical-recovery | 0.783 | 0.592 |
| SeizureFrequency clinical-recovery | 0.750 | 0.512 |
| Investigations clinical-recovery | 1.000 | 0.919 |

The qualitative failure taxonomy below (rendering friction, de-duplication,
companion-concept inventory, SF operand policy) still holds and is, if anything,
strengthened. But two conclusions change: (1) the absolute strict ceiling of
free-form Qwen generation is ~`0.34`, not ~`0.52`; and (2) the "mostly
annotation friction, the model is clinically strong" framing is too generous —
SF attribute agreement is `0.242` and within-letter over-emission is large
(per-item precision `0.352` vs per-letter precision `0.813`), both genuine model
failures rather than scoring artifacts. The candidate-backed `0.89`–`0.92`
diagnostics are now confirmed to be **deterministic-rule candidates**
(`hybrid_rules_candidates_llm_selector`) and are off-target for the gate; they
bound the selector, not the generator. The sections below are revised
accordingly; the original dev5/first-row figures are retained only where they
are labeled as such.

## Executive Read

The Qwen failures are not primarily evidence-span failures and are not well
explained by a wholly incompetent clinical model: at full dev there are no call
or blocking schema failures, evidence validity is `0.9623`, and Prescription
(`0.839`) and Investigations (`0.919`) clinical-recovery are strong. But the
favorable dev5 readout overstated the case. At dev140, source-near overlap is
`0.716`, not `0.854` — so roughly 28% of the mention inventory is missed or
spurious even under generous source-near matching, and there is now a real
~3.8% hallucinated-span rate (34 evidence-invalid mentions). Qwen *often* finds
the right source-near facts on the easy families; it does not reliably do so on
Diagnosis and SeizureFrequency.

The strict score collapses to `0.339` for two reasons that the dev5 view
conflated. First, the current `model_preserving_canonical` target is
much closer to "reconstruct the ExECTv2 annotation inventory exactly" than to
"recover the clinically important facts." It requires:

- exact mention multiplicity, including duplicate diagnosis and frequency rows
  for repeated source events;
- benchmark-specific mention text, often including source-section labels,
  hyphenated forms, or compact gold strings that are not natural clinical prose;
- complete entity-specific attributes, including certainty, negation, seizure
  count operands, time anchors, and investigation CUI distinctions;
- ontology companion concepts such as epilepsy syndromes plus named seizure
  types, including singular/plural variants;
- preservation of some annotation conventions that are clinically debatable,
  such as counting multiple diagnosis rows for the same seizure type.

Second — and this is the correction the full-dev run forces — part of the loss
is genuine model failure, not target construction. Even the generous source-near
layer is only `0.716`, SeizureFrequency clinical-recovery is `0.512` with
attribute agreement `0.242` (31/128 correct), and the model over-emits: at the
strict item level it produces `562` false positives against `629` false
negatives, with per-item precision (`0.352`) far below per-letter precision
(`0.813`), meaning most false positives are within-letter duplicate, attribute,
or multiplicity noise the model itself introduced. The annotation-target story
explains the gap between strict (`0.339`) and source-near (`0.716`); it does not
explain why source-near itself is only `0.716` or why SF operands are wrong
three times in four.

This explains why the result can look implausibly low relative to Gan
seizure-frequency Qwen work or a separate repo evaluation. Gan frequency was a
single-label selection problem; this ExECTv2 surface is a multi-entity,
multi-mention, exact inventory reconstruction problem.

## Headline Results

### Primary: Attribution-Clean Free-Form Generation At Full Dev (dev140)

This is the on-target number for the LLM-attributed claim: the `full_examples`
`single_call_clean_render_ids` route, which gives the model only the letter,
family guidance, attribute vocabulary, clinical rules, and worked examples, and
explicitly forbids any precomputed span list, regex hit list, or upstream
target. Qwen generates its own mention pool and selects from it by ID. Full dev,
140 letters, live `qwen3.6:35b`:

| Surface | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical (strict) | 0.339 | 0.352 | 0.327 | 305 | 562 | 629 |
| phrase_only | 0.446 | 0.464 | 0.430 | 402 | 465 | 532 |
| source_near | 0.716 | 0.745 | 0.690 | 645 | 222 | 289 |

Gate summary: 0 generation/selection call failures, 0 parse/schema failures,
evidence validity `0.9623` (34 evidence-invalid mentions dropped of 901).
Per-letter strict benchmark F1 is `0.617` (P=0.813, R=0.498), confirming that
most of the precision loss is within-letter multiplicity/attribute noise rather
than whole-letter false alarms.

Per-family, clinical-recovery and source-near layers (the report does not expose
a strict per-family split):

| Family | Clinical-recovery F1 | Source-near F1 | Source-near attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.839 | 0.715 | 0.741 (120/162) |
| Diagnosis | 0.592 | 0.657 | 0.869 (205/236) |
| SeizureFrequency | 0.512 | 0.690 | 0.242 (31/128) |
| Investigations | 0.919 | 0.919 | 0.966 (115/119) |

The standout technical signal is SeizureFrequency: source-near overlap is a
respectable `0.690` (Qwen finds the seizure anchor), but attribute agreement is
`0.242` — the operands (count, period, since/last-event state, dates) are wrong
about three times in four. That is a model-policy failure, not a rendering or
projection artifact.

### Diagnostic: Compact Repair-Attribution With A Deterministic Evidence Ledger

This is a **different architecture** from the primary route above and must not be
read as the free-form generation ceiling. The compact run
(`llm_only_key_entities_structured.py`) feeds the model a deterministic
`candidate_evidence_ledger` plus a `high_priority_evidence_ledger` built from
`standard_dictionary` residual additions — evidence spans, anchor hints, and
lane hints that point directly at the residual target facts (though they
deliberately omit scorer-ready attributes). The declared compact dev140 run:

| Surface | Overall F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw_model | 0.6975 | 0.6840 | 0.7116 | 565 | 256 | 229 |
| schema_format | 0.6975 | 0.6840 | 0.7116 | 565 | 256 | 229 |
| model_preserving_canonical | 0.7821 | 0.8285 | 0.7406 | 588 | 119 | 206 |
| hybrid_full_stack | 0.8483 | 0.8251 | 0.8728 | 693 | 145 | 101 |

Per-family clean dev140 F1:

| Family | F1 |
| --- | ---: |
| Diagnosis | 0.7637 |
| SeizureFrequency | 0.6813 |
| Prescription | 0.8721 |
| Investigations | 0.8155 |

The hybrid stack gains many true positives through rescue additions, which do
not count for an LLM-attributed claim. More importantly, the gap between the
free-form route (`0.339`) and this ledger-scaffolded route (`0.782`) is almost
entirely produced by the deterministic evidence ledger telling the model where
the residual targets live. That is a strong retrieval aid that sits at the edge
of the attribution protocol's "retrieval aids only when they do not encode a
complete target fact" allowance: it does not hand over attributes, but it does
hand over family, location, and lane for the exact residual facts. The `0.782`
should therefore be read as **ledger-assisted generation**, not as evidence that
Qwen recovers the strict inventory on its own. The honest free-form number is
`0.339`.

### Off-Target: Deterministic-Rule-Candidate Selector Routes

These runs supply the model with candidate facts generated by **deterministic
rules**, then let Qwen keep or reject them:

| Candidate source | Surface | F1 | Attribution label |
| --- | --- | ---: | --- |
| strict keep/reject actions dev140 | model_preserving_canonical | 0.8977 | `hybrid_rules_candidates_llm_selector` |
| default-keep action replay dev140 | model_preserving_canonical | 0.9155 | `candidate_passthrough_or_default_keep` |

Per the attribution protocol (`llm_repair_attribution_protocol_2026-06-22.md`,
"Candidate-Backed Routes"), these scores **must not** satisfy the
`model_preserving_canonical` promotion gate, because the prediction-bearing
target facts were not generated by Qwen. They are reported here only as a
component-interaction diagnostic.

The first edition treated these as "the strongest evidence that Qwen is not
useless on the domain." That inference does not hold: the candidates are
deterministic-rule outputs that already encode the strict text, multiplicity,
and ontology policy, so preserving them measures the **selector** (Qwen as a
keep/reject filter over a clean inventory), not the **generator**. They say
nothing about whether Qwen can produce the strict inventory itself — which is
the entire question, and which the primary route answers at `0.339`. With these
rows correctly classified as off-target, the free-form dev140 result carries the
full empirical weight of the "Qwen cannot generate the strict inventory"
conclusion.

### Attribution-Clean Generation-Selection Branches

All "first row" figures are single letters and all "devN" figures are 1–5
letters; only the bolded full-dev cell is statistically meaningful. The dev5
column was consistently optimistic relative to full dev (clean-render 0.517 dev5
vs 0.339 dev140), so the small-sample readings in this table should be treated as
upper-bound anecdotes, not estimates.

| Branch | Best small result | Larger result | Full dev (140) | Main observed failure |
| --- | ---: | ---: | ---: | --- |
| two-stage generation then finalization | 0.267 first row | not promoted | not run | finalizer moved/misplaced attributes |
| single-call inventory | 0.632 first row | 0.427 dev5 | not run | event-to-mention rendering drift |
| single-call final mentions | 0.778 first row | 0.506 dev5 | not run | natural renders, duplicate misses, weak Diagnosis/SF |
| generated mention IDs plus selected IDs | 0.842 first row | 0.483 dev5 | not run | finalization fixed, generation still weak |
| clean-render selected IDs | 0.842 first row | 0.517 dev5 | **0.339** | within-letter over-emission + weak Diagnosis/SF at scale |
| per-entity clean-render selected IDs | 0.737 first row | not run | not run | slower and worse than single-call clean-render |
| Qwen pool adjudication | 0.842 first row | 0.722 dev2 | not run | duplicate precision collapse |
| Qwen group adjudication | 0.842 first row | 0.588 dev2 | not run | picked weak representatives |
| typed mentions | 0.737 first row | not run | not run | typed fields did not fix generation policy |

The repeated pattern is clear: constraining finalization helps one cherry-picked
row, but does not make Qwen emit the full strict annotation inventory across
rows. The one branch carried to full dev landed at `0.339`, roughly `0.18` below
its own dev5 reading.

## Score-Layer Audit

Measured layers for `single_call_clean_render_ids` at **full dev (140)**:

| Layer | Item F1 | Interpretation |
| --- | ---: | --- |
| strict reported benchmark | 0.339 | Actual promotion surface |
| phrase_only | 0.446 | Text/multiplicity is ~`0.11` of the loss |
| source_near (generous overlap) | 0.716 | Even forgiving overlap matching is far below `0.900` |

The dev5 oracle ladder (concept-style `0.697`, attribute-only `0.719`, generous
entity-fact `0.787`) was a separate n=5 analysis and has **not** been recomputed
at full dev; given that every other dev5 surface fell ~`0.15`–`0.18` at scale,
those ceilings are almost certainly optimistic and should not be cited as the
projection ceiling until recomputed. The measured dev140 `source_near` layer
(`0.716`) is the more reliable generous-matching readout and already makes the
point: even forgiving overlap matching cannot approach `0.900`, so
projection-only work cannot rescue this artifact.

The decomposition: strict (`0.339`) → phrase_only (`0.446`) attributes ~`0.11` of
loss to text/multiplicity rendering; phrase_only → source_near (`0.716`)
attributes a further ~`0.27` to strict-vs-overlap matching of exact spans and
attributes; and the residual `0.284` below source_near is the model simply
missing or fabricating facts. SeizureFrequency is the clearest true failure: its
source-near attribute agreement is `0.242` (31/128), so even when Qwen lands the
seizure anchor, the operands are usually wrong. Some losses are annotation
friction, but seizure frequency and diagnosis still contain large, genuine
policy/attribute failures that no amount of text normalization will fix.

## Row-Level Error Analysis

The following rows are the first five dev letters used in the clean
generation-selection ladder. They are development rows, not holdout rows. They
are retained as qualitative illustrations of the failure *modes* — rendering
friction, de-duplication, companion-concept gaps, SF operand policy — all of
which the full-dev aggregate (above) confirms. Note, however, that these five
letters were the optimistic tail: their per-row strict F1 (clustered near the
dev5 `0.517`) is well above the dev140 mean of `0.339`, so they understate the
over-emission and SF-attribute failures seen across the full split.

### EA0002

Source facts:

- Diagnosis heading: focal epilepsy, probable temporal.
- Current medications: carbamazepine 400 mg twice a day; Topiramate 100 mg BD.
- Seizure-frequency facts: 2 to 3 focal seizures in March; four secondary
  generalised seizures since last clinic.
- Investigation: previous MRI scan in 2012 with abnormal temporal signal.

Qwen gets right clinically:

- Finds focal epilepsy and temporal lobe epilepsy.
- Finds both medications with dose/frequency.
- Finds focal-seizure range and secondary-generalised count.
- Finds abnormal MRI.

Strict clean-render misses:

| Entity | FN | FP | What happened |
| --- | ---: | ---: | --- |
| Prescription | 1 | 1 | Gold text is `carbamazepine-`; Qwen emits natural `carbamazepine 400 mg twice a day`. Attributes are correct. |
| Diagnosis | 1 | 0 | Gold has a second `focal-seizures` diagnosis row from the frequency sentence; Qwen emits one focal-seizures diagnosis only. |

Why:

- Qwen follows a clinically natural unique-fact policy. ExECTv2 scores repeated
  diagnosis rows when the seizure type appears in multiple source events.
- Qwen renders medications as clinically readable regimen phrases. Gold
  prescription text may be a compact medication span, sometimes with section
  punctuation.

Direct interventions tried:

- Selected-ID finalization prevented finalizer rewriting. First-row F1 improved
  to `0.842`.
- Clean-render IDs introduced `source_text` and `clean_text`. The first-row
  v02 also scored `0.842`, but still missed the duplicate focal-seizures
  diagnosis and the carbamazepine text convention.
- Per-entity clean-render dropped to `0.737` and did not solve the duplicate
  policy.

Implication:

EA0002 is not a clinical extraction failure. It is mostly a strict annotation
inventory and text-rendering failure.

### EA0004

Source facts:

- Diagnosis: epilepsy, probable focal.
- Medication: Lamotrigine 125 milligrams twice a day.
- Frequency: uncertain, several seizures since last clinic; a few seizures per
  year.
- Investigations: previous MRI normal; EEG in 2014 with temporal slowing.

Qwen gets right clinically:

- Finds epilepsy/focal epilepsy.
- Finds lamotrigine with dose/frequency.
- Finds both seizure-frequency statements.
- Finds MRI and EEG results.

Strict clean-render misses:

| Entity | FN | FP | What happened |
| --- | ---: | ---: | --- |
| Prescription | 1 | 1 | Gold preserves full section phrase with `milligrams`; Qwen normalizes to `Lamotrigine 125 mg twice a day`. |
| SeizureFrequency | 2 | 2 | Gold expects numeric `3 since last clinic` and `2 per year`; Qwen emits `several` and `few` as values. |
| Investigations | mostly text/CUI | mostly text/CUI | Qwen finds MRI/EEG, but rendered text and projected CUI phrase do not match strict benchmark objects. |

Why:

- Qwen preserves vague quantifiers semantically. The benchmark expects those
  vague quantifiers converted to particular numeric operands.
- This conversion is prediction-bearing if deterministic code supplies it after
  Qwen did not emit the numeric value. It cannot be credited under the current
  llm_only protocol.
- Medication and investigation losses are mostly render/canonical-form
  mismatches.

Direct interventions tried:

- Typed fields asked Qwen to use explicit seizure-frequency operands; first-row
  smoke remained `0.737` and did not justify escalation.
- Clean-render policy told Qwen to put counts/dates in attributes; dev5
  SeizureFrequency strict F1 remained `0.476`.
- Per-entity prompting did not improve first-row performance and would be too
  slow for broad iteration.

Implication:

EA0004 is the clearest example where ExECTv2 asks for an annotation policy, not
only clinical understanding. Qwen understands "several" and "few"; it does not
consistently map them to the benchmark's preferred operands.

### EA0005

Source facts:

- Diagnosis heading: genetic generalised epilepsy; epilepsy with generalised
  tonic clonic seizures alone. The source contains a typo, `tonic chronic`.
- Medication: sodium valproate 500 mg twice a day; carbamazepine 200 mg twice a
  day.
- Seizure type/frequency: last GTCS July 2016; previous December 2015; roughly
  two seizures per year.
- Investigations: MRI 2012 normal; EEG 2012 generalised spike and wave.

Qwen gets right clinically:

- Finds both medications.
- Finds genetic generalised epilepsy and a GTCS-related epilepsy syndrome.
- Finds MRI and EEG results.
- Finds seizure dates and annual seizure-rate evidence in some branches.

Strict clean-render misses:

| Entity | FN | FP | What happened |
| --- | ---: | ---: | --- |
| Prescription | 1 | 1 | Sodium valproate text uses natural regimen phrase; gold has section-prefixed compact phrase. |
| Diagnosis | 2 | 0 | Clean-render misses singular GTCS diagnosis and the singular epilepsy-with-GTCS-alone variant. Earlier branches missed more companion concepts. |
| SeizureFrequency | 1 | 2 | Gold expects a `0 since July 2016` last-event state; Qwen emits dated one-event occurrences in July 2016 and December 2015. |
| Investigations | 1 | 1 | MRI fact clinically correct, strict text/CUI phrase differs. |

Why:

- The diagnosis annotation policy expands a compact heading into multiple
  companion concepts and singular/plural variants. Qwen usually emits a
  clinically plausible subset.
- Qwen interprets "last event July 2016; previous event December 2015" as two
  dated events. The benchmark wants the last-event state rendered as zero events
  since July 2016.
- Qwen tends to correct or normalize source typos such as `tonic chronic` to
  `tonic clonic`, which is clinically sensible but can perturb strict text
  matching.

Direct interventions tried:

- Prompt rules explicitly asked for singular/plural seizure-type distinctions
  and companion diagnosis rows. They improved first-row behavior but did not
  stabilize dev5.
- Render-ID and clean-render variants separated evidence from rendered text.
  That helped some text choices but did not make Qwen reliably emit all
  companion concepts.
- Pool/group adjudication over Qwen-generated mentions showed Qwen can choose
  among alternatives, but when the pool lacks the exact companion concept or
  contains weaker event-flattened variants, selection cannot recover it.

Implication:

EA0005 is a true ontology-policy failure. This is not merely CUI projection; the
model has to know how many benchmark concepts to emit from one diagnosis
heading.

### EA0006

Source facts:

- Diagnosis: epilepsy unclassified, possibly generalised.
- Medication: levetiracetam 500 mg twice a day.
- Seizure type/frequency: 2 generalised tonic clonic seizures in 2014; absence
  like seizures in 2014.
- Investigations: MRI 2015 normal; EEG 2015 normal.

Qwen gets right clinically:

- Finds levetiracetam.
- Finds epilepsy/generalised epilepsy and seizure-type mentions.
- Finds MRI/EEG normal.
- Finds absence-like and GTCS seizure-frequency evidence in some branches.

Strict clean-render misses:

| Entity | FN | FP | What happened |
| --- | ---: | ---: | --- |
| Prescription | 1 | 1 | Natural regimen text instead of full section-prefixed gold text. |
| Diagnosis | 2 | 2 | Qwen emits absence-like seizures as a Diagnosis, while gold's diagnosis inventory emphasizes epilepsy/generalised epilepsy/GTCS duplicates. It also changes certainty for epilepsy in clean-render. |
| SeizureFrequency | 1 | 0 | GTCS 2014 frequency state not rendered with all strict attributes. |
| Investigations | 2 | 2 | MRI/EEG facts are found, but text/CUI conventions differ from gold. |

Why:

- Qwen treats named seizure types as diagnosis-like clinical entities when they
  appear in the seizure type/frequency section. The gold policy is inconsistent
  across rows: some seizure types are diagnosis rows, some are only frequency
  rows, and some appear duplicated.
- Certainty is a strict attribute. Changing epilepsy certainty from `5` to `3`
  creates a strict false positive/false negative pair even when the clinical
  concept is present.
- Investigation projection/text loss is again mostly benchmark convention.

Direct interventions tried:

- Clinical rules told Qwen to emit both Diagnosis and SeizureFrequency when a
  frequency sentence names a seizure type. This helped EA0002 but causes
  over-emission risk in rows like EA0006.
- Per-entity prompting did not solve this tension; it can even encourage each
  entity prompt to over-assert its own entity.

Implication:

EA0006 shows why a simple prompt rule cannot fix the benchmark policy. The
right action depends on annotation conventions that are not always clinically
obvious from the source text.

### EA0007

Source facts:

- Diagnosis: epilepsy unclassified; possible focal onset.
- Medication: levetiracetam 750 mg mane and 500 mg nocte; phenytoin 75 mg tds.
- Frequency: seizures every 3 to 4 weeks, possibly focal onset.
- Investigation: MRI 2011 normal.

Qwen gets right clinically:

- Finds both levetiracetam dose slots and phenytoin.
- Finds epilepsy/focal seizure context.
- Finds seizure interval and MRI normal.

Strict clean-render misses:

| Entity | FN | FP | What happened |
| --- | ---: | ---: | --- |
| Prescription | 3 | 3 | Gold has two `levetiracetam-` rows and one `Phenytoin-`; Qwen emits natural regimen text, and one clean-render row combines the two levetiracetam dose slots. |
| Diagnosis | 2 | 1 | Gold counts duplicate `epilepsy` and `focal-onset-epilepsy`; Qwen emits `epilepsy` and `focal seizures` or `focal onset seizures`. |
| SeizureFrequency | 2 | 1 | Gold has two identical seizure-frequency rows with `NumberOfSeizures=1`; Qwen emits one row and sometimes omits the count or adds illegal certainty. |
| Investigations | 1 | 1 | MRI fact present, strict text differs. |

Why:

- Qwen naturally collapses split-dose medication regimens and duplicate seizure
  frequency rows. The benchmark counts them separately.
- "Possibly focal onset" is clinically uncertain. Qwen chooses a human-readable
  seizure-type label, while gold wants `focal-onset-epilepsy` with
  `DiagCategory=MultipleSeizures` and certainty `3`.
- The seizure-frequency interval requires an implicit count of one seizure per
  interval. Qwen often preserves the interval but omits `NumberOfSeizures=1`.

Direct interventions tried:

- The prompt explicitly asked to keep repeated source-supported mentions and
  split medication dose slots. Qwen still merged or naturalized them on dev5.
- Typed fields and per-entity prompts were meant to improve attribute discipline
  but did not solve the missing implicit count or duplicate-row policy.

Implication:

EA0007 is the best example of why clinical competence can coexist with low
strict F1. Qwen understands the regimen and interval, but not the exact
annotation multiplicity and implicit operand policy.

## What Qwen Is Getting Wrong

### 1. Natural Clinical Rendering Instead Of ExECTv2 Text Rendering

This is the dominant Prescription and Investigations failure. Qwen emits:

- `Lamotrigine 125 mg twice a day`
- `sodium valproate 500 mg twice a day`
- `MRI`
- `EEG`

Gold may expect:

- `Current-antiepileptic-medication:-Lamotrigine-125-milligrams-twice-a-day`
- `Current-medication:-sodium-valproate-500-mg-twice-a-day`
- `MRI-2012-normal`
- `EEG-2015-normal`

This is not a clinical extraction failure. It is an annotation-rendering
failure. However, under the current protocol, deterministic code cannot freely
rewrite model text to the gold string if that rewrite changes the scored fact
inventory or hides model false positives.

### 2. De-Duplicating Repeated Source-Supported Facts

Qwen repeatedly collapses clinically duplicate facts:

- EA0002 has two gold `focal-seizures` diagnosis rows; Qwen emits one.
- EA0007 has duplicate `epilepsy` and seizure-frequency rows; Qwen emits one.
- Split levetiracetam dosing can be merged into one regimen phrase.

This is a sensible clinical behavior, but a strict ExECTv2 error.

### 3. Companion Diagnosis Inventory Failure

Qwen tends to emit a clinically natural diagnosis subset. Gold often requires
multiple related concepts:

- syndrome or epilepsy type;
- seizure type;
- singular seizure event;
- plural seizure type;
- generic epilepsy rows;
- duplicate rows when mentioned in separate sections.

EA0005 is the clearest example. A single heading can imply several gold
diagnosis annotations, and Qwen does not consistently reproduce that expansion.

### 4. Seizure-Frequency Operand Policy Failure

This is the largest single genuine failure, and full dev quantifies it: SF
source-near overlap is `0.690` (Qwen lands the anchor) but source-near attribute
agreement is `0.242` — only 31 of 128 overlapping SF mentions carry the right
operands. Strict SF clinical-recovery is `0.512`. Qwen often finds the correct
source span but does not express the benchmark state in the expected operands:

- `several` and `few` remain as vague values instead of numeric approximations.
- last-event statements become dated one-event facts rather than zero-since
  states.
- interval statements preserve `3 to 4 weeks` but omit implicit
  `NumberOfSeizures=1`.
- some rows include extra illegal or irrelevant attributes such as certainty on
  SeizureFrequency.

This is a genuine model-policy failure for the strict target. It is not solved
by CUI projection, and the `0.242` attribute agreement shows it is not a
rendering or scoring artifact either.

### 4b. Within-Letter Over-Emission (Precision Loss)

The first edition framed the failure as mostly recall-side (missed duplicates
and companions). Full dev shows over-emission is roughly equal in size: strict
`562` false positives against `629` false negatives. Per-item precision is
`0.352` while per-letter precision is `0.813`, so the bulk of the false
positives are *within-letter* — Qwen emits the right letter-level facts but adds
duplicate, mis-attributed, or multiplicity-inflated mentions around them.
Diagnosis (P `0.612`, FP `113`) and SeizureFrequency (P `0.506`, FP `85`) carry
most of the spurious mass. Any future intervention must improve precision, not
just recall; prompt edits that push the model to "enumerate more" risk making
this worse.

### 5. JSON Dialect Noncompliance

Many Qwen outputs require Python-literal JSON repair. This has not been a
blocking problem because schema repair recovers the objects, but it is a sign
that Qwen is not following the output contract as tightly as GPT-style hosted
models usually do.

### 6. Selector Success Over Deterministic Candidates Does Not Transfer To Generation

Qwen can preserve a clean inventory it is handed: the default-keep
deterministic-rule-candidate dev140 diagnostic reaches `0.9155`, and strict
keep/reject actions reach `0.8977`. But those candidates are produced by
deterministic rules and already carry the strict rendering, multiplicity, and
ontology policy, so the result measures Qwen-as-filter, not Qwen-as-generator.
Free-form Qwen generation — the only attribution-clean route — reproduces that
inventory at `0.339`. The selector competence and the generation deficit are
not in tension; they are answers to two different questions.

## What We Tried And What Happened

| Problem targeted | Intervention | Outcome |
| --- | --- | --- |
| Two-call finalizer drift | Single-call inventory with generated and final events | first-row `0.632`, dev5 `0.427`; event-to-mention drift remained |
| Finalizer rewriting final facts | Generated mention table plus selected IDs | first-row `0.842`, dev5 `0.483`; generation quality still weak |
| Natural text versus final render | `source_text` plus model-owned `clean_text` | first-row `0.842`, dev5 `0.517`; first-row render improved, dev5 still weak |
| Attribute dictionary looseness | Typed mention fields | first-row `0.737`; typed schema did not fix policy |
| Entity interference | One call per entity | first-row `0.737`; slower and not better |
| Cross-run duplicate variants | Qwen pool/group adjudication | first-row `0.842`, dev2 `0.588-0.722`; duplicate/representative selection still weak |
| Projection suspicion | Concept/attribute/entity-fact oracle audit (dev5 only) | generous dev5 ceiling about `0.787`; measured dev140 source_near is `0.716`; not enough for target |
| Small-sample optimism | Carry clean-render route to full dev (140) | strict `0.339` vs dev5 `0.517`; every favorable surface fell ~`0.15`-`0.18` at scale |

## Why This Looks Worse Than Expected From Gan Frequency Work

The Gan seizure-frequency task and this ExECTv2 surface stress different
competencies.

Gan frequency asks for one final seizure-frequency label per note. A model can
be clinically right by finding the decisive current frequency and mapping it to
one label.

This ExECTv2 key-entity task asks for a complete mention inventory across four
entity families. It scores exact entity, text, multiplicity, and attributes.
The model must decide not only the clinical answer but also the annotation
policy:

- how many diagnosis rows to emit;
- whether to emit companion concepts;
- whether a seizure type is diagnosis, frequency, or both;
- whether repeated source events count as duplicate annotations;
- which exact text string should represent a medication or investigation;
- which implicit seizure-frequency operands should be filled.

So the current results do not imply that Qwen is poor at epilepsy clinical
reasoning. They imply that free-form llm_only generation — Qwen *and*
GPT-4.1-mini alike (see the GPT-4.1-mini Control) — is poor, under these prompts,
at emulating the strict ExECTv2 annotation/rendering policy without candidate
facts or prediction-bearing deterministic repair. The apples-to-apples control
confirms this is a route-level limit, not a model-specific one.

## Implications

1. The `>0.900` Qwen llm_only target is not reachable by more small prompt edits
   in the current free-form generation family. At full dev the route scores
   strict `0.339`; the failure has replicated across event, mention,
   selected-ID, typed-field, clean-render, per-entity, and Qwen-pool variants,
   and the one branch carried to full dev fell ~`0.18` below its own dev5
   reading. Small-sample tuning on this family is now actively misleading.

2. Projection-only work cannot rescue the artifact. The measured dev140
   `source_near` layer is `0.716`; even forgiving overlap matching is far below
   `0.900`. (The dev5 entity-fact oracle of `0.787` is unrecomputed and, given
   the scale gap on every other surface, likely optimistic.) SeizureFrequency
   attribute agreement of `0.242` is a model failure no projection can touch.

3. The deterministic-rule-candidate selector routes (`0.8977`/`0.9155`) are
   off-target hybrid evidence per the attribution protocol. They measure Qwen as
   a filter over a clean inventory, not as a generator, and must not be cited as
   evidence that Qwen recovers the scored facts. With them set aside, the
   free-form `0.339` is the sole on-target Qwen number.

4. The apples-to-apples GPT-4.1-mini control — the same attribution-clean route,
   profile, temperature, and token budget, swapping only the model — has now
   been run (the prior GPT v08 control was not comparable, benefiting from mature
   assembly and deterministic lenses). See the **GPT-4.1-mini Control** addendum
   below for the result and what it implies about whether `0.339` is a
   Qwen-specific limit or a property of the llm_only route itself.

5. If the objective remains strict llm_only `model_preserving_canonical` F1 above
   `0.900`, the next route is not another prompt variant. Note the precision
   finding (4b): "enumerate more" prompting is counterproductive. The credible
   routes are:

   - supervised or optimizer-driven learning of the ExECTv2 annotation policy
     on development/training examples;
   - a model-generated claim table followed by Qwen self-query where the claim
     table is trained or heavily exemplified on exact annotation multiplicity;
   - a deliberately hybrid architecture that owns strict rendering and ontology
     expansion deterministically, while reporting Qwen clinical-generation
     quality on source-near and clinical-recovery surfaces.

6. If the scientific question is "does Qwen recover clinically important epilepsy
   facts," strict ExECTv2 F1 is too harsh as the only readout — but the
   clinical-recovery story is weaker than the dev5 view implied. At full dev only
   Prescription (`0.839`) and Investigations (`0.919`) clear a plausible bar;
   Diagnosis (`0.592`) and SeizureFrequency (`0.512`) do not. The "Qwen recovers
   the clinical facts" claim holds for two of four families, not all four.

## Recommended Stop Rule

Do not run more attribution-clean Qwen generation-selection experiments from this
prompt family on any sample size. The family's true full-dev strict result is
`0.339`, and dev5 readings have proven systematically optimistic by ~`0.15`-`0.18`,
so a dev5 smoke gate is no longer a trustworthy filter. A new experiment in this
space should only proceed if it changes the *method* (supervised/optimizer policy
learning, trained claim table, or an explicitly hybrid architecture per
Implication 5), and it must report on **dev25 or larger** — never dev5 — with:

- strict F1 at least `0.75-0.80` on dev25+;
- SeizureFrequency strict F1 materially above `0.70` with attribute agreement
  well above the current `0.242`;
- no call or blocking schema failures and evidence validity at least `0.96`;
- per-item precision approaching per-letter precision (the over-emission in 4b
  closed), not just improved recall.

## GPT-4.1-mini Control (Apples-To-Apples)

To separate "Qwen specifically cannot do this" from "the attribution-clean
llm_only route cannot do this," `openai/gpt-4.1-mini` was run through the
**identical** `single_call_clean_render_ids` / `full_examples` route on the same
140 dev letters, with the same temperature (`0.0`) and token budget (`5000`).
Only the model and endpoint changed.

| Surface | Qwen 3.6 (dev140) | GPT-4.1-mini (dev140) |
| --- | ---: | ---: |
| strict `model_preserving_canonical` F1 | 0.339 | 0.334 |
| phrase_only (item) | 0.446 | 0.447 |
| source_near (item) | 0.716 | 0.712 |
| per-letter benchmark F1 | 0.617 | 0.630 |
| evidence validity | 0.9623 | 0.9607 |
| Prescription clinical-recovery | 0.839 | 0.846 |
| Diagnosis clinical-recovery | 0.592 | 0.580 |
| SeizureFrequency clinical-recovery | 0.512 | 0.551 |
| Investigations clinical-recovery | 0.919 | 0.863 |
| SF source-near attribute agreement | 0.242 (31/128) | 0.318 (40/126) |
| strict FP / FN | 562 / 629 | 597 / 629 |

The two models are statistically indistinguishable on the strict surface
(`0.339` vs `0.334`) and track each other on every layer, both strong families,
both weak families, the same over-emission signature (GPT-mini actually emits
*more* false positives), and the same catastrophic SF attribute agreement
(GPT-mini `0.318` is marginally better than Qwen's `0.242` but still wrong two
times in three). GPT-mini is even slightly worse on Investigations.

This is the single most important result in the revised analysis, and it
overturns the first edition's central attribution. **The `0.339` ceiling is not
a Qwen limitation; it is a property of the attribution-clean free-form llm_only
route on this benchmark surface.** A stronger, hosted, tightly
instruction-following model reaches the same wall. Two consequences follow:

1. The target-construction critique is vindicated — two independent models hit
   the same `~0.34` strict / `~0.71` source-near wall, which is what you expect
   when a large share of the loss is exact-inventory reconstruction friction
   rather than model competence.

2. The genuine-model-failure findings (SF operand policy, within-letter
   over-emission) are *also* model-independent — they are failures of the
   free-form generation *paradigm* against this annotation policy, not of any
   one model's clinical reasoning.

Practically: swapping in a better base model is not a route to `0.900`. The
only credible routes remain the method changes in Implication 5
(supervised/optimizer policy learning, a trained claim table, or an explicitly
hybrid architecture). And any future model-quality comparison on this surface
should expect models to cluster near `0.34` strict regardless of capability,
so the discriminating readouts are the source-near and clinical-recovery layers,
not strict F1.

Artifacts:
`experiments/exectv2_llm_only_key_entities_generation_selection_single_call_clean_render_ids_full_examples_dev140_gpt41mini_live_20260623.{jsonl,md}`

