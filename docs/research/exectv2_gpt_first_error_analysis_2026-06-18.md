# ExECTv2 GPT-First — Item-Level Error Analysis (dev140)

Date: 2026-06-18 · Parent: [[09_gpt_first_execution_plan]] ·
Subject of analysis: `experiments/exectv2_hybrid_all_entities_dev140_gpt41mini_20260617.jsonl`
(the bare-union GPT-only hybrid, Phase C headline **0.220 semantic item F1**).

This is the deep item-by-item analysis the Phase C/E gate read demanded before any
architecture change. It is read on the **deterministic-replay-free** GPT-only
hybrid (no rule augmentation), so every number is the LLM candidate set assembled
by a bare union of the nine focused per-entity passes.

## Headline: the gap is assembly, not candidate recall

Decomposing every gold mention by whether its concept was surfaced by a candidate
(substring-overlap, format-blind):

| Read | Overall | Diagnosis | PatientHistory | Prescription | SeizureFreq | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **anyEnt** overlap recall (some pass surfaced it) | **0.84** | 0.84 | 0.73 | 0.94 | 0.91 | 0.94 |
| **corrEnt** overlap recall (the *correct-entity* pass surfaced it) | 0.68 | 0.49 | 0.56 | 0.94 | 0.84 | 0.94 |
| **exactCorr** (correct pass, exact normalized phrase) | 0.38 | 0.26 | 0.33 | 0.32 | 0.51 | 0.71 |

Reads:

1. **Candidate generation is not the binding constraint.** The union of the nine
   passes already surfaces **0.84** of all gold concepts somewhere. The ceiling a
   pure selection/assembly stage can reach on recall is 0.84 — far above the 0.22
   the bare union scores.
2. **Entity misassignment costs ~16 recall points overall** (anyEnt 0.84 →
   corrEnt 0.68) and is catastrophic on **Diagnosis (0.84 → 0.49, −35 pts)** and
   **PatientHistory (0.73 → 0.56, −17 pts)**: the concept is in the pool, but the
   *wrong* per-entity pass emitted it, so it both misses the correct entity and
   over-emits on the wrong one.
3. **Phrase altitude costs ~30 more points** (corrEnt 0.68 → exactCorr 0.38): even
   when the right pass surfaces the concept, the model's phrase boundary rarely
   equals gold's canonical phrase.

## Per-entity FN decomposition (semantic key, CUI-dropped)

Every gold mention missed at the semantic key, classified:

| Entity | gold | TP | attr-mismatch | entity-confusion | altitude | true-miss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PatientHistory | 466 | 68 | 86 | 98 | 87 | 127 |
| Diagnosis | 405 | 68 | 38 | 184 | 51 | 64 |
| Prescription | 206 | 38 | 28 | 0 | 127 | 13 |
| SeizureFrequency | 187 | 23 | 70 | 22 | 54 | 18 |
| Investigations | 136 | 86 | 11 | 2 | 29 | 8 |

(`entity-confusion` = the gold phrase appears in predictions under a *different*
entity; `altitude` = same entity, overlapping but non-exact phrase.)

## The four structural failures, ranked by leverage

1. **Entity confusion from nine independent passes (no arbitration).** The
   assembler (`hybrid/all_entity_assessment.py`) is a bare union + faithfulness
   gate + CUI projection — there is no joint entity assignment. The same span is
   independently claimed by multiple passes and scattered. Top confusion pairs
   (gold-entity → predicted-as): Diagnosis→PatientHistory **70**, Diagnosis→Onset
   **69**, PatientHistory→SeizureFrequency **51**, Diagnosis→SeizureFrequency
   **31**. **Diagnosis loses 184/405 golds to this alone.** This is the #1 lever
   and is recoverable on existing candidates by a selection stage.

   *Worked case (EA0002):* the Diagnosis pass emitted only `focal epilepsy`; the
   seizure-type diagnoses `focal seizures` / `secondary generalised seizures`
   (gold Diagnosis, DiagCategory=MultipleSeizures) were emitted by the
   *PatientHistory* pass — simultaneously a Diagnosis recall miss and a
   PatientHistory false positive.

2. **Phrase altitude.** Prescription is the textbook case (127 altitude FNs): gold
   `text` is inconsistent (≈70% full regimen span `Topiramate-100-mg-BD`, ≈30%
   bare drug name), so a single predicted altitude cannot match. For the CUIPhrase
   entities (Diagnosis, SeizureFrequency) gold `text` is the clean concept and the
   model emits a longer descriptive span (`focal seizures without change in
   awareness` vs `focal seizures`). WhenDiagnosed is the extreme: source-near
   recall 1.000, semantic F1 0.073 — pure altitude. Partly a documented
   target-construction artifact ([[project_exectv2_scoring_artifacts]]); the
   honest lever is canonical-phrase *selection* by the model, not gold-fitting a
   lexicon.

3. **Attribute extraction.** SeizureFrequency quantification is the largest
   single-entity attribute gap (NumberOfSeizures 51, NumberOfTimePeriods 30,
   LowerNumberOfSeizures 29, TimePeriod 24, TimeSince 23, PointInTime 16) — the
   Gan unknown-vs-rate residual, reappearing. PatientHistory temporal attributes
   (Age 19, AgeLower 16, AgeUnit 15, YearDate 9) and Diagnosis Certainty (27) are
   the next tier.

4. **Over-emission / spurious.** Investigations 55 spurious FPs, Prescription 42,
   PatientHistory 60 — precision drag on top of the confusion-driven FPs.

## The gold multi-entity reality (why "pick one entity" is wrong)

45 distinct dev phrases legitimately appear under more than one gold entity. The
logic is consistent and must be encoded, not collapsed:

- `epilepsy` → {Diagnosis, Onset (onset age), WhenDiagnosed (diagnosis date)}
- named seizure type (`focal seizures`, `generalised tonic clonic seizures`,
  `complex partial seizures`) → {Diagnosis (DiagCategory), SeizureFrequency when a
  count/rate is stated}
- `seizures` / `seizure` (generic) → {PatientHistory background, SeizureFrequency
  when counted}
- structural aetiology (`stroke`, `traumatic brain injury`, `encephalitis`) →
  {EpilepsyCause, PatientHistory}

So the correct selection stage **replicates a concept across every entity whose
definition it satisfies**, with entity-appropriate attributes — it does not route
a span to a single entity.

## Implication for the plan

The named Phase-C next stage — *a GPT candidate-selection pass, ablation-gated* —
was built as `hybrid/arbitration.py`: one GPT call per letter over the union
candidate pool + the letter, doing entity re-assignment, cross-entity
de-confusion, canonical phrase selection, and attribute finalisation.

## Cycle results (dev140 semantic item F1) and the hard ceiling

| Version | Overall | Diagnosis | Recall | Note |
| --- | ---: | ---: | ---: | --- |
| Bare union (incumbent) | 0.220 | 0.243 | 0.208 | keeps all 9 passes; scattered entities |
| Arbitration v0.1 | 0.195 | 0.227 | 0.155 | over-pruned: silently drops pool concepts |
| Arbitration v0.2 (keep-by-default + forced seizure-type→Diagnosis) | 0.190 | 0.270 | 0.144 | retyping works (EA0002 fixed) but recall still collapses |

**The arbitration-as-regeneration design is structurally recall-limited.** One
combined call cannot reproduce the recall of nine focused single-entity passes
(the attention-dilution Phase A/B documented in reverse). v0.2's entity retyping
is correct — on EA0002 the named seizure types move to Diagnosis(MultipleSeizures)
and replicate into SeizureFrequency — but the call emits ~765 mentions where the
union emits ~1326, so recall falls faster than precision rises.

**Two ceilings now bound any pool-selection approach:**

1. **Altitude ceiling 0.38.** The correct-entity pass produces gold's *exact*
   normalized phrase for only 38% of golds, even though *some* pass overlaps 84%.
   95% of gold phrases ARE verbatim substrings of the letter, so this is **span
   selection**, not gold corruption (only 5% is corrupted/truncated). The misses
   are an **annotation convention**: gold decomposes compound diagnostic clauses
   into atomic mentions (`complex partial seizures with secondary generalised
   tonic-clonic seizures` → two gold mentions) and dual-annotates generic +
   specific (`epilepsy` AND `temporal lobe epilepsy`). The candidate emits the
   verbatim clause. Of Diagnosis-pass altitude misses, 84 are overcapture (cand
   longer than gold), 9 shorter, 0 variant.
2. **Attribute ceiling.** SeizureFrequency quantification and PatientHistory
   temporal coding must match gold values exactly.

**Consequence:** a selection/arbitration stage over the existing pool is capped at
≈0.38 phrase-recall and cannot approach the 0.7–0.9 published cells. Breaking past
it requires changing **candidate generation** to emit the gold altitude convention
plus an attribute reasoning lift — not just re-selecting.

## Deterministic benchmark-altitude projection (Phase F, the chosen path)

Per the user's direction (keep the LLM clinical layer fixed; add a deterministic
projection reported as separate credit), `deterministic/benchmark_altitude.py`
applies three principled, **recall-preserving** transforms to the bare-union
prediction: compound-splitting (Diagnosis/PatientHistory), seizure-type entity
normalization (a named epilepsy seizure type filed as PatientHistory also emits a
Diagnosis(MultipleSeizures) copy), and affirmed-default Certainty/Negation.

| Layer | Bare union | + altitude projection |
| --- | ---: | ---: |
| semantic item F1 | 0.220 | **0.242** |
| Diagnosis semantic F1 | 0.243 | **0.318** (+0.075) |
| PatientHistory semantic F1 | 0.161 | 0.180 |
| benchmark (with-CUI) item F1 | 0.181 | 0.181 |

The Diagnosis lift is the #1 structural bug (entity confusion) fixed
deterministically and recall-preservingly — unlike the GPT arbitration, which
lost recall. Lexicon phrase-snapping was tested and **rejected**: it moved
0.240→0.235 (it disturbs already-correct phrases; coverage-bound, the Phase D
in-sample-lookup finding).

## The honest reachability verdict (oracle decomposition)

An oracle that snaps every prediction's phrase to an overlapping same-entity gold
phrase **when entity + attributes already agree** caps at **F1 0.42** — the most
any phrase-altitude projection can buy. Per-entity oracle ceilings:

| Entity | gold | oracle-ceiling F1 | binding wall above the ceiling |
| --- | ---: | ---: | --- |
| Investigations | 136 | 0.74 | phrase altitude (reachable) |
| Prescription | 206 | 0.70 | inconsistent gold phrase (not deterministically realizable) |
| Diagnosis | 405 | 0.43 | DiagCategory/Certainty attributes + recall |
| PatientHistory | 466 | 0.28 | **recall** (fn≈347 — concepts absent from the pool) |
| SeizureFrequency | 187 | 0.18 | **quantification attributes** (the Gan unknown-vs-rate wall) |

**0.7 on the most-populous entities is not reachable on this metric via
projection.** PatientHistory is recall-bound (the pool misses ~347 golds),
SeizureFrequency is bounded by exact quantification (NumberOfSeizures /
TimePeriod), and Prescription's gold phrase has no single deterministic altitude.
These are the documented clinical-reasoning / target-construction walls
([[project_exectv2_scoring_artifacts]]) — the same verdict the Gan closeout
reached ("0.842 is honest; >0.90 needs a stronger model reading prose directly").
The legitimate gains realized here: Diagnosis 0.243→0.318 and overall 0.220→0.242,
all as transparent, recall-preserving, separately-credited projection.
