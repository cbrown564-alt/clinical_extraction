# ExECTv2 GPT-First — Selection Pass, Altitude Projection, and the Reachable Ceiling

Date: 2026-06-18 · Parent: [[09_gpt_first_execution_plan]] ·
Companion analysis: [[exectv2_gpt_first_error_analysis_2026-06-18]]

This is the session report for one analyse → build → run → re-analyse cycle on the
ExECTv2 all-entity GPT-first pipeline. It opened from the Phase E gate read (the
bare-union hybrid scored **0.220 semantic item F1** on dev140, far below the gate)
with a mandate to do deep item-level error analysis and make bold architectural
changes toward 0.7 on the most-populous entities. It closes with two new
components, a rejected architecture, an accepted (modest) projection gain, and a
firm, evidence-backed verdict on what this metric can and cannot reach.

**Guardrail note.** All numbers are dev140 (the development split). The locked test
split was never touched. No full-200 audit was run; the Phase E promotion gate
remains NOT met. Gains from deterministic projection are reported as projection
credit, never as LLM clinical reasoning.

---

## 1. The starting picture and the diagnostic question

The Phase C/D/E artifacts left the all-entity hybrid at 0.220 semantic / 0.181
benchmark item F1 — roughly 4× below the published per-item target (0.87). The plan
named over-emission/precision and CUI-projection coverage as the binding
constraints and deferred a "GPT candidate-selection pass." Before building anything
this cycle asked the prior question: **where, item by item, does the 0.220 come
from — is it recall, representation, or assignment?**

## 2. Item-level error analysis (the decisive read)

Decomposing every gold mention on the bare-union GPT-only hybrid by whether a
candidate surfaced its concept (format-blind substring overlap):

| Read | Overall | Diagnosis | PatientHistory | Prescription | SeizureFreq | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| anyEnt overlap recall (some pass surfaced it) | **0.84** | 0.84 | 0.73 | 0.94 | 0.91 | 0.94 |
| corrEnt (the *correct-entity* pass surfaced it) | 0.68 | 0.49 | 0.56 | 0.94 | 0.84 | 0.94 |
| exactCorr (correct pass, exact normalized phrase) | 0.38 | 0.26 | 0.33 | 0.32 | 0.51 | 0.71 |

Three findings, each load-bearing:

1. **Candidate generation is not the binding constraint.** The union of the nine
   focused per-entity passes already surfaces **84%** of all gold concepts. Any
   selection/assembly stage has 0.84 of recall available to it; the 0.220 headline
   leaves most of it on the floor.
2. **Entity misassignment costs ~16 recall points** (0.84 → 0.68) and is
   catastrophic on Diagnosis (**0.84 → 0.49, −35 pts**) and PatientHistory
   (−17 pts). The bare-union assembler is a literal union of nine independent
   passes with no joint entity arbitration, so the same span is claimed by multiple
   passes and scattered. Top confusion pairs (gold → predicted-as):
   Diagnosis→PatientHistory **70**, Diagnosis→Onset **69**,
   PatientHistory→SeizureFrequency **51**, Diagnosis→SeizureFrequency **31**.
   Diagnosis loses **184/405** golds to this alone.
3. **Phrase altitude costs ~30 more points** (0.68 → 0.38): even when the right pass
   surfaces a concept, its phrase boundary rarely equals gold's exact phrase.

The worked case (letter EA0002) makes the mechanism concrete: the Diagnosis pass
emitted only `focal epilepsy`; the seizure-type diagnoses `focal seizures` and
`secondary generalised seizures` (gold Diagnosis, DiagCategory=MultipleSeizures)
were emitted by the *PatientHistory* pass — simultaneously a Diagnosis recall miss
and a PatientHistory false positive.

A separate read established that this is **span selection, not gold corruption**:
95% of gold phrases are exact substrings of the letter; only 5% are
truncated/spelling-drifted. And it established the **gold multi-entity reality** —
45 dev phrases legitimately appear under more than one entity on a consistent
logic (`epilepsy`→{Diagnosis, Onset, WhenDiagnosed}; named seizure type→{Diagnosis,
SeizureFrequency when counted}; generic `seizures`→{PatientHistory, SeizureFrequency}).
The correct stage **replicates a concept across every entity whose definition it
satisfies**; it does not route a span to a single entity.

## 3. Build 1 — GPT Stage-2 arbitration (rejected)

`hybrid/arbitration.py` + `runners/run_arbitration.py` implement the deferred
candidate-selection pass: one GPT call per letter over the union candidate pool +
the letter, doing entity re-assignment, cross-entity de-confusion, canonical-phrase
selection, and attribute finalisation. Replay-first (the pool is the existing
per-entity JSONLs); only the per-letter arbitration call is new. The split of
labor is unchanged from the Gan winner — the LLM owns candidate generation,
reasoning, *and* selection.

| Version | semantic item F1 | Recall | Diagnosis | Note |
| --- | ---: | ---: | ---: | --- |
| Bare union (incumbent) | 0.220 | 0.208 | 0.243 | keeps all nine passes |
| Arbitration v0.1 | 0.195 | 0.155 | 0.227 | over-pruned: silently drops pool concepts |
| Arbitration v0.2 (keep-by-default + forced seizure-type→Diagnosis) | 0.190 | 0.144 | 0.270 | retyping works; recall still collapses |

The **entity retyping is correct** — on EA0002, v0.2 moves the named seizure types
to Diagnosis(MultipleSeizures) and replicates them into SeizureFrequency with the
counts, exactly matching gold. But every version scored **below** the bare union,
because a single combined call cannot reproduce the recall of nine focused
single-entity passes (v0.2 emits ~765 mentions where the union emits ~1326). This
is the attention-dilution finding of Phase A/B in reverse: focused-per-entity beats
one combined pass on recall. **Arbitration-as-regeneration is structurally
recall-limited and was rejected as the headline path.**

## 4. Build 2 — deterministic benchmark-altitude projection (accepted)

Per the chosen direction (keep the LLM clinical layer fixed; add a deterministic
projection reported as separate credit), `deterministic/benchmark_altitude.py` +
`runners/run_benchmark_altitude_projection.py` apply three principled,
**recall-preserving** transforms to the bare-union prediction:

1. **Compound splitting** (Diagnosis, PatientHistory): split a compound clause
   (`complex partial seizures with secondary generalised tonic-clonic seizures`) on
   `with` / `and` / comma into atomic concepts, each inheriting attributes.
   SeizureFrequency is deliberately excluded (its gold anchor keeps a compound type
   as one phrase carrying the count; splitting only fragments correct anchors).
2. **Seizure-type entity normalization**: a named focal/generalised/partial/
   tonic-clonic/myoclonic/absence seizure type filed as PatientHistory also emits a
   Diagnosis(MultipleSeizures) copy (the PatientHistory copy is kept —
   recall-preserving). Non-epilepsy attack types (febrile/dissociative/
   non-epileptic/psychogenic) are excluded.
3. **Affirmed-default attributes**: Certainty=5 / Negation=Affirmed when unstated.

CUI projection runs after, unchanged.

| Layer | Bare union | + altitude projection |
| --- | ---: | ---: |
| semantic item F1 | 0.220 | **0.242** |
| Diagnosis semantic F1 | 0.243 | **0.318** (+0.075) |
| PatientHistory semantic F1 | 0.161 | 0.180 |
| benchmark (with-CUI) item F1 | 0.181 | 0.181 |

The Diagnosis lift is the #1 structural bug (entity confusion) fixed
deterministically **without losing recall** — the property the GPT arbitration
could not hold. Lexicon phrase-snapping (mapping predicted phrases to the existing
lexicon's canonical CUIPhrase) was tested and **rejected**: it moved 0.240→0.235
because it disturbs already-correct phrases — the coverage-bound, in-sample-lookup
limit Phase D already documented.

## 5. The reachable ceiling (the honest verdict)

An oracle that snaps every prediction's phrase to an overlapping same-entity gold
phrase **only when entity + attributes already agree** measures the maximum any
phrase-altitude projection can buy. It caps at **F1 0.42**. Per-entity:

| Entity | gold | oracle-ceiling F1 | binding wall above the ceiling |
| --- | ---: | ---: | --- |
| Investigations | 136 | 0.74 | phrase altitude (reachable) |
| Prescription | 206 | 0.70 | inconsistent gold phrase (not deterministically realizable) |
| Diagnosis | 405 | 0.43 | DiagCategory/Certainty attributes + recall |
| PatientHistory | 466 | 0.28 | **recall** (fn≈347 — concepts absent from the pool) |
| SeizureFrequency | 187 | 0.18 | **quantification attributes** (the Gan unknown-vs-rate wall) |

**0.7 on the most-populous entities is not reachable on this metric via
projection.** The three biggest entities are each blocked by a wall that phrase
projection cannot touch: PatientHistory by candidate recall (the pool simply lacks
~347 of its golds), SeizureFrequency by exact quantification
(NumberOfSeizures / TimePeriod / counts), and Prescription by a gold `text` altitude
that is internally inconsistent (≈70% full regimen span, ≈30% bare drug name, no
deterministic signal which). These are the documented target-construction and
clinical-reasoning walls ([[project_exectv2_scoring_artifacts]]) — the same verdict
the Gan strand reached ("0.842 is honest; >0.90 needs a stronger model reading the
prose directly", [[gan2026_research_closeout_synthesis_2026-06-17]]).

## 6. What this cycle delivered, and the next genuine lever

Delivered:

- A decisive item-level decomposition that re-frames the 0.220 as **assembly-bound,
  not recall-bound** (84% concept overlap; entity confusion and altitude are the
  losses).
- `hybrid/arbitration.py` — the candidate-selection pass; correct on entity
  retyping, rejected on recall grounds, fully documented so the negative result is
  not re-attempted blind.
- `deterministic/benchmark_altitude.py` — a recall-preserving projection that lifts
  Diagnosis 0.243→0.318 and overall 0.220→0.242 as clean, separately-credited
  projection.
- An oracle ceiling (0.42) and a per-entity reachability table that bound the metric
  honestly.

The next genuine lever is **candidate generation, not selection or projection**:
re-running the nine per-entity generators with convention-teaching worked examples
(atomic decomposition, canonical seizure/diagnosis terms) to lift phrase altitude in
the pool itself, plus a SeizureFrequency quantification-reasoning lift. That is a
few-thousand-call effort and was deliberately not taken this cycle (budget capped at
~500 dev calls). Until it is, the honest claim stays the transfer claim: the Gan
architecture and reliability discipline port to broad phenotyping; the broad-entity
benchmark cells remain bounded by recall and clinical-attribute reasoning, not by
the assembly/projection machinery, which this cycle has now characterised and
partially closed.

## Artifacts

- `experiments/exectv2_arbitration_v01_dev140_gpt41mini_20260618.{jsonl,md}`
- `experiments/exectv2_arbitration_v02_dev140_gpt41mini_20260618.{jsonl,md}`
- `experiments/exectv2_altitude_proj_dev140_20260618.{jsonl,md}`
- `src/.../exectv2/hybrid/arbitration.py`, `runners/run_arbitration.py`
- `src/.../exectv2/deterministic/benchmark_altitude.py`,
  `runners/run_benchmark_altitude_projection.py`
- Registered in `experiments/RUN_INDEX.md`.
