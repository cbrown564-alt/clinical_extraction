# ExECTv2 Gold Representation & Scoring — Principles

Date: 2026-06-17

Status: synthesis note. Steps back from the row-level error analysis to record the
*durable principles* about how ExECTv2 gold is loaded, represented, and scored —
the structural facts that survive any particular extractor, and that should shape
evaluation design and architecture decisions going forward.

This is the conceptual companion to three working documents, which carry the
counts and row-level evidence this note only summarizes:

- `exectv2_deterministic_all9_layered_error_analysis_2026-06-17.md` — the
  layered (phrase/semantic/benchmark) error analysis these principles generalize.
- `exectv2_data_discoveries_log.md` — the append-only evidence log (D11, D16,
  D17, D18 are the load-bearing entries here).
- `exectv2_gold_schema_profile_2026-06-09.md` — the raw schema/attribute profile.

Code touchpoints: `contract/evaluation.py` (`EntityEvaluationPolicy`),
`data.py` (`ExectAnnotation`), `scoring.py` (`match_key`, multiset scoring,
`*_config_for`), and `deterministic/mention_identity.py` (`dedupe_mentions`).

## Bottom Line

A benchmark F1 on ExECTv2 is not a clean read of extractor quality. It is the
product of three independent layers that the headline number fuses together:

1. **the target** — which of two gold phrase representations a mention is scored
   against, a choice that is per-entity and was partly undocumented;
2. **the scorer** — an offset-free exact multiset match, whose design decisions
   (drop CUI? keep duplicates? which attributes?) silently move the denominator;
3. **the extractor** — what it emits, and crucially what *unit* it emits in.

Most of what looked like "model error" in the first read of the all-9 scorecard
was actually a mismatch *between these layers*: an emission altitude that did not
match the chosen target, a multiset cardinality the extractor could not observe, a
CUI key fit in-sample. The single most useful move is to stop reading the fused
number and instead attribute every gap to one of the three layers.

The principles below are what made that attribution possible. Each is stated as a
claim, then *how it was found* (because several were found by distrusting a
plausible-sounding statement and going back to the raw source), then *the
implication*.

## The two representations (the foundational picture)

The gold lives in two places: the per-entity benchmark CSVs in
`MarkupOutput_200_SyntheticEpilepsyLetters/` (the source) and the `Json/` files the
loader reads (derived). Every gold mention carries **two** phrase strings:

- a **raw covered span** — the phrase sliced out of the letter by the annotation
  offsets. It is what `data.py` stores as `text`. It is corrupted by offset drift
  (truncations like `epileps`, `…awarenes`; over-captures like
  `Current-antiepileptic-medication:-sodium-valproate-600-mg-bd-(to-reduce`).
- a **clean canonical concept** — the normalized ontology term. It is stored as
  the `CUIPhrase` attribute, which the scorer *ignores* by default.

Everything downstream follows from the fact that these are two different things at
two different altitudes, and that the gold, the loader, and the extractor each sit
at a *third* altitude in places. The principles formalize that.

## Principles

### P1 — Gold carries two phrase representations at different altitudes, and the choice between them is load-bearing

**Claim.** "Did the extractor find the phrase" has no single answer, because gold
offers two phrases per mention (raw span vs. clean concept) that disagree on
21–90% of mentions depending on entity. Scoring against one vs. the other swings
per-entity `phrase_only` F1 by up to ±60 points. The loader's per-entity decision
(repair `text := CUIPhrase` for SeizureFrequency and Diagnosis only; keep the raw
span for the other seven) is therefore not a detail — it sets the target.

**How found.** Re-scoring `phrase_only` against `CUIPhrase` instead of the stored
`text` for every entity and watching the F1 move (Investigations `0.60 → 0.06`,
WhenDiagnosed `0.82 → 0.00`, Onset `0.40 → 0.63`). A floor that moves that much
under a representation swap is measuring representation, not recall.

**Implication.** `phrase_only` is not a transparent "did we find it" floor unless
the target is declared per entity and held fixed. Either declare one target per
entity and document it, or stop quoting `phrase_only` as a floor. The
architecture-comparable layer is `semantic` (attributes minus CUI), not
`phrase_only`.

### P2 — Provenance is per-file; there is no universal column schema

**Claim.** The mapping from CSV column to JSON field is **not** the same across the
nine markup files. The clean concept (`CUIPhrase`) is col5 for most entities but
col6 for SeizureFrequency; the raw span (`text`) is col6 for most but col5 for SF;
and Prescription is a third layout entirely (col5 = `CUIPhrase`, col6 = `DrugName`,
and a 10th regimen-span column → `text`). The invariant that holds everywhere is at
the *field* level — `text` = raw span, `CUIPhrase` = clean concept — never at the
*column index* level.

**How found.** A plausible, widely-cited statement ("col5 is the raw span, col6 is
the clean concept") was in `data.py`, the error analysis, and the discoveries log.
Matching JSON rows back to CSV rows by offset/CUI showed it was correct for
SeizureFrequency and *reversed* for BirthHistory, Diagnosis, and the rest, with
Prescription different again. The claim had propagated across three documents while
being half-wrong, because it was true for the one entity (SF) under active work
when it was written.

**Implication.** Two implications, one technical and one methodological. Technical:
reason about gold in field terms (`text` / `CUIPhrase`), never column indices; the
loader reads named JSON fields, so the per-file column variation never reaches the
code, but it does reach anyone reasoning from the CSVs. Methodological: a provenance
claim is only as good as a check against the raw source; "true for the entity I was
looking at" silently generalizes into "true," and numbers/labels ossify across docs.

### P3 — Offsets are unreliable for matching but reliable as relative instance identifiers

**Claim.** "Score on labels, not offsets" (D11) is correct but over-broad as
usually stated. Offset drift makes the *absolute* position wrong, so offsets cannot
locate or align a mention. But two distinct mentions still carry *distinct* offsets
regardless of drift, so offsets remain a sound way to tell "the same concept,
twice" from "one concept, emitted twice." Absolute position is corrupt; relative
distinctness is intact.

**How found.** The duplicate-FN problem (P5) needed a way to keep two genuine
occurrences of one concept apart without trusting the offsets for matching. The
realization that drift is a *shift*, not a *scramble*, means distinctness survives
it. This is now the basis of the offset-aware de-dup in `dedupe_mentions`
(`evidence_span.start_char` keys instance identity; it is never compared to gold).

**Implication.** "Don't use offsets" should be scoped to "don't use offsets for
matching or alignment." They are still usable — and useful — as within-letter
instance identifiers, which is exactly what per-occurrence emission needs.

### P4 — A benchmark number fuses target + scorer + extractor; error attribution requires separating them

**Claim.** The three score layers (`phrase_only` → `semantic` → `benchmark`) are not
just increasing strictness; they isolate *where* a gap lives. A `phrase_only`
miss is a target/recall issue (P1); a `phrase_only → semantic` loss is an attribute
issue; a `semantic → benchmark` loss is a CUI-projection issue. Without the ladder,
a single benchmark F1 cannot distinguish "missed the fact" from "found the fact,
wrong key."

**How found.** Decomposing the all-9 scorecard by layer showed that a third of
benchmark false negatives sat in letters where the correct concept was *already
emitted* (the CUI was present) — i.e. the fact was found and only the exact key
differed. A flat F1 had been reading those as missed facts.

**Implication.** Always report the three-layer ladder, never a lone benchmark F1.
Treat `benchmark` (with-CUI) as in-sample on dev (the CUI lookup is hand-fit to dev
concepts, D5/Finding 5) and read `semantic` as the comparable layer until a locked
test. The same discipline splits entities into representation-bound (concept found,
key wrong → fix projection) vs. recall-bound (concept absent → fix candidate
generation) regimes, which point at opposite fixes.

### P5 — An apparent recall ceiling is recoverable only where the extractor's unit of extraction matches the annotator's unit of annotation

**Claim.** The gold annotates a concept once per distinct *clinical assertion*, and
the same concept can be asserted twice in one letter (e.g. "epilepsy" in the
problem list and again in the history) — at distinct offsets, counted twice by the
offset-based benchmark. A concept-de-duplicating extractor emits one and takes a
forced false negative. This looks like a cheap recall ceiling ("just emit per
occurrence"). It is only cheap where the extractor's notion of "an occurrence"
coincides with the annotator's notion of "an assertion." Where the extractor matches
bare words in prose, per-occurrence emission turns every prose token into a false
positive instead.

**How found.** All 131 PatientHistory + Diagnosis duplicate-key gold copies were
verified to sit at *distinct* offsets (genuine repeat assertions, not annotation
artifacts), which rules out the tempting "de-duplicate the gold" fix — that would
make recall *easier* than the published benchmark. The faithful fix (extractor
emits per occurrence) was then measured per entity: net-positive for PatientHistory
(semantic `0.212 → 0.240`, precision held) but precision-destroying for Diagnosis
(`0.60 → 0.41`, "epilepsy" emitted 8× in one letter where gold annotates it once).
So the fix is gated to PatientHistory by `EntityEvaluationPolicy`.

**Implication.** The unit of extraction is an architecture decision, not a free
parameter. Recovering duplicate-gold recall requires *assertion-level* occurrence
selection (which span constitutes a distinct clinical assertion), which is a
candidate-generation problem — consistent with Diagnosis/Investigations being
recall-bound (P4). Until that exists, their duplicate ceiling is real and should be
published next to per-item recall, not "recovered."

### P6 — Per-entity heterogeneity is the rule, not the exception

**Claim.** Nearly every load/score policy that one is tempted to set globally is
actually per-entity: the phrase target (P1), the column provenance (P2), the
attribute scope (Certainty/Negation apply to all entities *except* SeizureFrequency,
D18), the duplicate semantics (P5), and the CUI projection. A single global rule is
wrong for some entity in every one of these dimensions.

**How found.** Every attempt at a blanket policy broke on at least one entity:
blanket `text := CUIPhrase` is wrong for Investigations (CUIPhrase encodes the
finding, `EEG → abnormal-eeg`); blanket per-occurrence emission is wrong for
Diagnosis; a blanket CUI/Certainty scope is wrong for SF. The exceptions are not
noise — they are the structure.

**Implication.** Loader, scorer, and extractor occurrence semantics should all
read `EntityEvaluationPolicy`: a small explicit per-entity policy set with a
documented measured rationale. Prompts/eval for the LLM family must be per-entity,
not one schema for nine.

### P7 — Measure the obvious fix per entity before shipping it; it is often net-negative

**Claim.** The intuitive fix to a structural problem frequently trades one
entity's gain for another's loss, and the aggregate can move the wrong way. The
gain is only real once it is measured at the level the heterogeneity lives (P6),
i.e. per entity.

**How found.** Disabling de-dup entirely (the "obvious" fix for P5) raised
PatientHistory and Diagnosis recall but *lowered* overall precision and barely
moved overall F1, because it surfaced large prose-repetition over-emission in
Diagnosis/Investigations that the de-dup had been masking. Only the per-entity
before/after table revealed that the right scope was PatientHistory-only.

**Implication.** Structural fixes to load/score/extract should be accompanied by a
per-entity before/after read, not just an overall delta. An overall F1 that barely
moves can hide a large precision/recall reshuffle that matters for the architecture
choice.

## How these were found (method)

The investigation was deliberately bottom-up and source-grounded, and the method is
as reusable as the findings:

1. **Read the loader and scorer before trusting any number.** The match key,
   normalization, and ignore-sets in `scoring.py` define what the F1 *means*; the
   per-entity repair in `data.py` defines the target. Neither is visible in a
   results table.
2. **Go back to the raw source and match it against the derived artifact.** Joining
   `Json/` rows to `MarkupOutput/*.csv` rows by offset/CUI is what exposed the
   per-file column variation (P2) and Prescription's anomalous `text` column. A
   derived artifact's documentation describes intent; the source describes fact.
3. **Reproduce the quantitative claims directly from gold.** The duplicate-FN
   counts, the divergence rates, the "concept already emitted" share were all
   recomputed from the gold rather than taken from the prior note — which is how the
   distinct-offset nature of the duplicates (P5) surfaced.
4. **Distrust a plausible statement that is load-bearing.** The col5/col6 claim
   sounded right and was cited everywhere; checking it against more than one entity
   file is what broke it (P2).
5. **Measure candidate fixes at the grain of the heterogeneity.** Every fix was run
   as a per-entity before/after on the dev split before being committed or gated
   (P7).

## Implications for the project

**Evaluation.** Report the three-layer ladder always; lead with `semantic` as the
architecture-comparable layer; flag `benchmark` (with-CUI) as in-sample on dev;
declare and document one phrase target per entity, or drop `phrase_only` as a
"floor." Carry the representation-bound vs. recall-bound regime split (P4) into any
architecture comparison, because it points different entities at opposite fixes.

**Representation / loader.** The core abstraction is `text` (raw span) vs.
`CUIPhrase` (clean concept), not any column index (P2). Keep per-entity policy
explicit and documented in code. `raw_text` provenance is worth preserving even
though it is corrupt, because it is the only link back to what the offsets covered.

**Extractor.** The unit of extraction must be chosen to match the annotator's unit
of annotation (P5). Per-occurrence emission is correct only with assertion-level
occurrence selection; absent that, concept-level emission plus a published ceiling
is the honest operating point for the prose-repetition entities.

**Research hygiene.** Provenance and numeric claims propagate across documents and
ossify; a load-bearing claim deserves a check against source before it is reused
(P2), and a structural fix deserves a per-entity measurement before it is shipped
(P7).

## Claim Language

Safe:

```text
On ExECTv2 the benchmark F1 fuses three separable layers — the per-entity phrase
target, the offset-free multiset scorer, and the extractor's unit of emission.
Attributing a gap requires the phrase/semantic/benchmark ladder: a third of
benchmark false negatives are letters where the concept was already emitted (key,
not recall), and duplicate-gold recall ceilings are recoverable only where the
extractor's occurrence unit matches the annotator's assertion unit. Gold offsets
are unusable for matching but sound as relative instance identifiers.
```

Unsafe:

```text
The gold has a single phrase target and a uniform column schema; offsets are
simply unusable; the benchmark F1 measures extractor quality; the duplicate-FN
ceiling is a cheap recall win.
```

Why unsafe: the phrase target and column provenance are per-entity (P1, P2, P6);
offsets are unusable only for matching, not for instance identity (P3); the
benchmark number fuses target + scorer + extractor (P4); and the duplicate ceiling
is recoverable only where extraction and annotation share a unit (P5, P7).
