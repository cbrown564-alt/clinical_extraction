# Satellite 02 — Rules-Based Architecture

Parent: [[00_overarching_implementation_plan]] · Phases 2 & 6
Status: planning. Dev-split only until the Phase 7 audit.

## Purpose

Build the deterministic ExECTv2 extractor — the portability baseline and the
like-for-like comparator to the benchmark's own rule-based GATE pipeline.
Seizure Frequency first (Phase 2), then all nine entities (Phase 6). This is the
architecture that, if it clears the benchmark per-entity F1s — overall > 0.90
across the nine entities, but only ≈ 0.56 on Seizure Frequency, the hardest
entity for rules — makes a rules-vs-rules win against the published system.

## 1. Shape

Deterministic, staged, every stage named and ablatable (the
`deterministic_canonical_pipeline` discipline from Gan 2026):

```
raw letter text
  → Segment        (section detection: Diagnosis:/Seizure type and frequency:/Investigations: etc.)
  → Extract        (rule families fire → candidate mentions with evidence spans)
  → Normalize      (shared epilepsy normalizer → attribute values)
  → Select/Render  (resolve overlaps; emit PredictedMention per entity)
  → Evidence Trace Check  (every mention's evidence is an exact substring)
```

Output: `PredictedLetter`. No LLM anywhere in this family.

## 2. Rule taxonomy (reused pattern, new instances)

Each rule carries portability metadata, exactly as Gan 2026's
`rule_metadata.py`:

- `general` — dates, durations, section headers, number/word parsing. **Reuse
  Gan 2026 general rules directly** where they already live in a shared/general
  module; lift if still gan2026-local.
- `clinical_epilepsy` — seizure terminology, ILAE seizure types, seizure-free
  phrasing. **Reuse the lifted `tasks/shared/epilepsy/terms.py` + `seizure_free.py`.**
- `seizure_frequency` — rate/count/range/period expressions, current-vs-historical
  selection. **Reuse the shared normalizer; SF selection rules adapted to
  ExECTv2's mention-level output (multiple mentions per letter, not one label).**
- `exectv2_specific` — ExECTv2 synthetic-letter conventions (the
  `Seizure type and frequency:` header line, the structured `Prescription` line
  format, hyphen-joined phrases). New.
- `benchmark_format` — phrase/attribute shaping to match gold annotation
  conventions (how a phrase is delimited, attribute value casing). New, minimal.

Key structural difference from Gan 2026: ExECTv2 is **mention extraction**, so
the deterministic family must produce *all* gold-worthy mentions per letter
(recall across the letter), not select one dominant fact. Selection rules become
*overlap resolution* rules (when two rules fire on the same span, which mention
wins), not *dominance* rules.

## 3. Seizure Frequency first (Phase 2)

Order of work:

1. Section segmentation (the explicit `Seizure type and frequency:` header is a
   high-precision anchor; also scan prose for SF expressions).
2. SF extraction rules → candidate mentions, each with `text` + evidence span +
   raw operands.
3. Shared normalizer → `NumberOfSeizures` / ranges / `TimePeriod` /
   `NumberOfTimePeriods` / temporal anchors / `FrequencyChange`.
4. Seizure-free path: `NumberOfSeizures="0"` mentions (92 in gold) via the
   lifted seizure-free detector.
5. Evidence trace check; emit `PredictedLetter`.
6. Score with `score_entity(..., SEIZURE_FREQUENCY)` on the **dev split**;
   record per-item and per-letter F1.

First milestone: a measured SF per-item/per-letter F1 on dev, with a row-level
error list. This is the first real benchmark signal of the whole task.

## 3a. Measured baseline & gap analysis (2026-06-10)

First real signal, dev split (140 letters, 187 gold SF mentions),
`rule_set=deterministic_sf_v2_anchor_association`, via
`runners/run_deterministic_sf` and pinned in
`tests/test_exectv2_deterministic_sf.py::test_dev_split_baseline_pinned`:

| Config | per-item F1 | per-letter F1 |
|--------|-------------|---------------|
| `phrase_only` (text only) | 0.356 | 0.575 |
| `sf_semantic` (guideline-aligned: drops CUI/CUIPhrase/Certainty/Negation) | 0.156 | 0.313 |
| `sf_benchmark` (keeps CUI; phrase→CUI lexicon now live) | 0.156 | 0.313 |

Numbers as of the 2026-06-10 guideline-alignment + temporal-family work (List 11
counts, SF anchor slang removal, implied-count default, guideline-aligned
scoring, and `rules/temporal.py`: dates/PointInTime/TimeSince, "last seizure was
<date> ⇒ 0 Since", bare-count + SF-context gate + bare-nonzero-count filter).
Trajectory: phrase per-item 0.313→0.332→0.356, semantic per-item 0.123→0.132→
0.156, semantic per-letter 0.238→0.313. See
`docs/research/exectv2_sf_guideline_alignment_2026-06-10.md`. The earlier
`full_features` config (requiring Certainty/Negation) was retired — guideline
v9 L17/L19 say those are not SF features. With the phrase→CUI lexicon now live
(gap 1, `sf_benchmark` == `sf_semantic` = 0.156), the remaining gap is recall and
precision shared across both configs: SF-vs-Diagnosis discrimination,
per-statement emission, and the missing temporal/phrase coverage (gaps 2–4).

Benchmark SF F1 ≈ 0.56 (the published system's hardest entity; its overall
F1 across the nine entities is > 0.90, carried by the easy structured ones).
So the bar to beat for SF specifically is ≈ 0.56 — but we are at 0.000 on the
benchmark-comparable `full_features` config. Major gaps, ranked by impact:

1. **CUI assignment (DONE).** All 187/187 gold SF mentions carry `CUI` (16
   distinct); the benchmark config required it and rules emitted none, pinning
   `sf_benchmark` at 0. `deterministic/lexicon.py` is the finite phrase→CUI map:
   it keys the 16 gold CUIs on their normalized `CUIPhrase` variants (44 keys,
   2 dominance-resolved collisions — bare `seizure`→C0036572, `focal`→C0877017),
   and `pipeline._with_cui` attaches the CUI to every anchor whose phrase is in
   the lexicon. Result: `sf_benchmark` 0.000 → 0.156, now exactly equal to
   `sf_semantic` — the lexicon assigns the correct CUI to *every*
   semantically-matching mention, so CUI no longer caps the headline. Further
   `sf_benchmark` gains now require lifting phrase/attribute recall (gaps 2–4),
   not the lexicon.
2. **Exact attribute-set match + missing temporal family caps `no_ref` at
   62.6%.** `match_key` requires the full attribute set to agree. No rule emits
   `PointInTime` (33), `YearDate` (28), `MonthDate` (25), `DayDate` (5);
   `TimeSince_or_TimeOfEvent` (71) only partially. A temporal-anchoring rule
   family ("since the last clinic" → Since+LastClinic; "in March 2018" → dates)
   is the biggest winnable lift.
3. **Phrase/anchor recall 0.30, compounded by architecture.** Association drops
   any anchor with no nearby frequency attribute, so bare `seizures`/`seizure`
   (most common gold phrases) annotated with only a change/temporal attribute
   are lost — gaps 2 and 3 multiply. The anchor+association model also emits one
   mention per seizure-type phrase, but gold annotates one per frequency
   statement.
4. **Precision 0.33 (115 FP).** Anchor rule fires on Diagnosis-style seizure
   phrases; loose attribute rules attach spuriously. No real SF-vs-Diagnosis
   discriminator.
5. **Gold `text` corruption from offset drift.** Many gold SF phrases are
   themselves truncated/shifted (`'seizures e'`, `'convulsive seizur'`,
   `'ocal seizures with altered awarenes'`) and some embed temporal context
   (`'2 generalised tonic clonic seizures in 2014'`). A portion of phrase recall
   is therefore unwinnable; quantify and document as a noise ceiling.
6. **Operational (DONE).** Milestone runner fixed (was `NameError` on
   `load_letters`) and now scores the dev split; baseline pinned as a regression
   test.

7. **Annotation-guideline 1:1 alignment audit.** We hold the exact ExECT v2.1
   guidelines (`data/ExECTv2 (2025)/ExECT V2 .1- What and How of
   annotating_v9.docx`). Every rule and normalization decision should trace to a
   guideline clause; where gold contradicts the guideline (known noise rows:
   `TimePeriod="days"`, stray `DiagCategory`, offset-drift truncations) or the
   guideline is under-specified, log it as an explicit divergence rather than
   silently fitting it. Doubles as a paper-grade transparency artifact and the
   spec source for the phrase/attribute normalization above.

Order of attack: (1 done) → temporal family (done) → CUI lexicon (done) →
precision / per-statement mention model, with the guideline audit feeding each.

Firm, cross-architecture findings about the data/schema/scoring (the things that
constrain *both* the rules and the LLM prompts/eval) are logged separately and
append-only in `docs/research/exectv2_data_discoveries_log.md` — consult it
before adding rules or designing LLM prompts so the same ground truth drives both.

## 4. All entities (Phase 6)

Generalize the same staged pipeline to the other eight. Most are *more*
tractable than SF (the paper notes Prescriptions/Investigations/Diagnosis are
the easiest, structured entities; SF/Patient History the hardest). Bring them up
roughly in benchmark-difficulty order so each adds a known increment:

Prescription → Investigations → Diagnosis → Onset → When Diagnosed → Epilepsy
Cause → Birth History → Patient History.

Each entity gets its own rule set under the taxonomy, its own tests, and its own
dev-split score. The runner aggregates to the overall per-item/per-letter F1
that the benchmark headline uses.

## 5. De-overfitting discipline

The benchmark scored on all 200 synthetic letters; deterministic rules will be
tempted to fit their phrasing. Apply the Gan 2026 Phase 2 method:

- Classify each rule family as general / format / validation-phrase-shaped.
- Rewrite validation-phrase-shaped rules to anchor on source-backed structure,
  not literal phrase lists.
- Accept dev-score regressions when they remove dataset-specific notation —
  generalizability is the goal, not dev-score max. Report both.

## 6. Deliverables & tests

- `deterministic/` staged modules + `rule_metadata.py` with portability tags
- Per-entity rule sets, each separately testable and ablatable
- Unit tests per rule family; corpus-level dev-split score test with a pinned
  expected range (updated deliberately, like Gan 2026's pipeline_v1 tests)
- Row-level error-analysis artifact per entity

## 7. Exit criteria

- **Phase 2**: SF deterministic extractor scored on dev, error list produced,
  rules portability-tagged.
- **Phase 6**: all 9 entities extracted; overall dev per-item/per-letter F1
  reported; rule ablation table buildable.
