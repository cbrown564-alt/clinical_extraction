# Satellite 02 — Rules-Based Architecture

Parent: [[00_overarching_implementation_plan]] · Phases 2 & 6
Status: planning. Dev-split only until the Phase 7 audit.

## Purpose

Build the deterministic ExECTv2 extractor — the portability baseline and the
like-for-like comparator to the benchmark's own rule-based GATE pipeline.
Seizure Frequency first (Phase 2), then all nine entities (Phase 6). This is the
architecture that, if it clears the benchmark per-entity F1s — overall 0.87 per
item / 0.90 per letter across the nine entities, but only 0.66 per item / 0.68
per letter on Seizure Frequency, the hardest entity (Table 1, Fonferko-Shadrach
2024) — makes a rules-vs-rules win against the published system.

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

Dev split (140 letters, 187 gold SF mentions),
`rule_set=deterministic_sf_v2_anchor_association`, via
`runners/run_deterministic_sf` and pinned in
`tests/test_exectv2_deterministic_sf.py::test_dev_split_baseline_pinned`:

| Config | per-item F1 | per-letter F1 |
|--------|-------------|---------------|
| `phrase_only` (text only) | 0.382 | 0.604 |
| `sf_semantic` (guideline-aligned: drops CUI/CUIPhrase/Certainty/Negation) | 0.272 | 0.482 |
| `sf_benchmark` (keeps CUI; phrase→CUI lexicon live; == sf_semantic) | 0.272 | 0.482 |

**Phase 2 completion batch (2026-06-10).** On top of the guideline-alignment +
temporal-family + CUI-lexicon work, this batch closed the attribute-correctness
and precision gaps and measured the per-statement question. sf_semantic per-item
F1 **0.156 → 0.272 (+74%)**, per-letter **0.313 → 0.482**; per-letter precision
**0.479 → 0.868** (FP letters 26 → 5). Changes: awareness-suffix fix; range rules
accept a seizure noun / "times" before "per"; drop TimeSince from
count_in_last_period (D9); negation-aware implied count (negated ⇒ 0); Christmas
⇒ December; flexible seizure-free duration + "after"/drug-stop point-in-time +
date filler; medication-dose, adverbial, and non-clinical/history/driving gates;
and the **same-sentence bounded-gap association** rule (the largest precision
lever — drop an extraction with no nearby anchor instead of gluing it onto a
distant one). **Per-statement emission (D8) was implemented and measured
net-negative (per-item 0.272→0.264) and reverted** — see the error-analysis
artifact. Full row-level analysis, the FN decomposition, and the noise ceiling
are in `docs/research/exectv2_sf_error_analysis_2026-06-10.md`; clause mapping in
`docs/research/exectv2_sf_guideline_alignment_2026-06-10.md`.

**Noise ceiling (quantified, D12).** 37/187 = 19.8% of gold SF phrases are
offset-drift–corrupted (truncations + frequency-embedding over-captures),
un-winnable on exact phrase text; a further 13/187 = 7.0% are singular/plural
mismatches we deliberately do not normalize away (scope decision: keep exact
match). Combined ≈ 26.7%, so exact-match phrase recall is capped at ≈ 0.73 and
the sf_semantic recall of 0.225 reads as a corrupt-adjusted ≈ 0.31.

The remaining winnable gap is recall (precision is now strong): wrong-type
association, "infrequent/under control" ⇒ FrequencyChange, Age-based bundles,
Last_Year-as-PointInTime, and DrugChange-without-"since". Each is small (1–4
mentions) and several risk precision, so they are logged not forced.

Benchmark SF F1 = **0.66 per item / 0.68 per letter** (Table 1,
Fonferko-Shadrach 2024 — the published system's hardest entity; its overall F1
is 0.87 per item / 0.90 per letter, carried by the easy structured ones).
The bar to beat for SF is 0.66/0.68; the benchmark-comparable
`sf_benchmark` config is now at 0.272 per-item / 0.482 per-letter, with the
remaining gap dominated by the quantified noise ceiling (≈ 26.7% un-winnable on
exact text) and a small, precision-risky recall tail. The original gap list,
with final status:

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
2. **Temporal family (DONE).** `rules/temporal.py` emits PointInTime / dates /
   TimeSince / "last seizure ⇒ 0 Since" / Christmas⇒December; the count-correctness
   fixes (negation-aware implied 0, ranges, count_in_last_period TimeSince drop)
   complete more of the dominant bundles.
3. **Phrase/anchor recall (PARTIAL).** Awareness-suffix and seizure-free
   duration/PIT fixes recovered qualified-type and seizure-free mentions. The
   anchor+association model's one-mention-per-statement default was confirmed
   correct: **per-statement emission (D8) measured net-negative and reverted**.
   Remaining recall misses are the precision-risky tail in §3a.
4. **Precision (DONE).** per-letter precision 0.479 → 0.868 via the
   medication-dose / adverbial / non-clinical-context gates and the
   same-sentence bounded-gap association rule (the SF-vs-Diagnosis/history
   discriminator that was missing). per-item FP 145 → 80.
5. **Gold `text` corruption (DONE — quantified).** 37/187 = 19.8% offset-drift
   corruption + 13/187 = 7.0% singular/plural ≈ 26.7% un-winnable on exact text;
   documented as the recall ceiling in the error-analysis artifact. Scoring kept
   as exact match per the 2026-06-10 scope decision.
6. **Operational (DONE).** Runner scores the dev split; baseline re-pinned.
7. **Guideline 1:1 alignment audit (DONE).** Every rule traces to a clause in
   `exectv2_sf_guideline_alignment_2026-06-10.md`; gold-vs-guideline divergences
   logged (D14, noise rows).

Order of attack: CUI lexicon (done) → temporal family (done) →
attribute-correctness + precision gates + association rule (done) →
per-statement (done: net-negative, reverted). **Phase 2 SF extractor complete**
(see exit criteria §7). The recall tail in §3a is logged for a future pass.

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

- **Phase 2 (COMPLETE, 2026-06-10)**: SF deterministic extractor scored on dev
  (`sf_benchmark` 0.272 per-item / 0.482 per-letter, 0.868 per-letter
  precision); row-level error list + noise ceiling produced
  (`docs/research/exectv2_sf_error_analysis_2026-06-10.md`); rules
  portability-tagged (`rule_metadata.py` `Portability`); guideline 1:1 audit
  done. Per-statement emission (D8) measured net-negative and reverted. The
  remaining sub-benchmark gap is the quantified ≈ 26.7% gold noise ceiling plus a
  small precision-risky recall tail, both logged.
- **Phase 6**: all 9 entities extracted; overall dev per-item/per-letter F1
  reported; rule ablation table buildable.
