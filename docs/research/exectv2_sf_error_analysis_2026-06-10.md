# ExECTv2 SeizureFrequency — Deterministic Extractor Error Analysis (2026-06-10)

Row-level error analysis and noise-ceiling quantification for the deterministic
SeizureFrequency extractor on the **dev split** (140 letters, 187 gold SF
mentions), the Phase 2 milestone deliverable (plan 02 §6, exit criterion §7).

Regenerate with:

```
uv run python -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_deterministic_sf
```

Pinned as a regression test in
`tests/test_exectv2_deterministic_sf.py::test_dev_split_baseline_pinned`.

## 1. Headline scores

`rule_set = deterministic_sf_v2_anchor_association`. Three match configs (see
`scoring.py`); `sf_benchmark` is the benchmark-comparable one (keeps `CUI`,
ignores `CUIPhrase`/`Certainty`/`Negation` per guideline L17/L19).

| Config | per-item P / R / F1 | per-letter P / R / F1 |
|--------|---------------------|-----------------------|
| `phrase_only` | 0.484 / 0.316 / **0.382** | 0.900 / 0.455 / **0.604** |
| `sf_semantic` | 0.344 / 0.225 / **0.272** | 0.868 / 0.333 / **0.482** |
| `sf_benchmark` | 0.344 / 0.225 / **0.272** | 0.868 / 0.333 / **0.482** |

Predicted 122 mentions vs 187 gold. Benchmark SF F1 to beat = **0.66 per item /
0.68 per letter** (Table 1, Fonferko-Shadrach 2024 — the published system's
hardest entity; overall 0.87/0.90).

### Trajectory (the two 2026-06-10 batches)

| Milestone | sf_semantic per-item | sf_semantic per-letter | per-letter precision |
|-----------|----------------------|------------------------|----------------------|
| Guideline-align + temporal + CUI (prior) | 0.156 | 0.313 | 0.479 |
| **Phase 2 completion (this)** | **0.272** | **0.482** | **0.868** |

sf_semantic per-item F1 +74%; per-letter +54%; per-letter precision +0.39 (FP
letters 26→5). phrase_only per-letter F1 0.575→0.604 at 0.90 precision.

## 2. What changed in this batch

Attribute-correctness (convert FP+FN pairs → TP):
1. **Awareness suffix without "of"** — `rules/anchor.py`: "focal seizures with
   altered awareness" (6 gold) now captured (was truncated to "focal seizures",
   breaking phrase match and CUI lookup).
2. **Range accepts a seizure noun / "times" before "per"** — `rules/rate.py`:
   "1 to 2 seizures a year", "2 to 3 times per month" now read as ranges, not a
   collapsed single count.
3. **`count_in_last_period` drops `TimeSince=Since`** (D9) — "in the last N
   months" is a period, not a date/point-in-time.
4. **Negation-aware implied count** — `pipeline.py`: a negated frequency ("no
   further seizures since …") implies `NumberOfSeizures=0`, not the default
   plural=2 (the single largest count-value miss on temporal mentions).
5. **Christmas ⇒ December** — `rules/temporal.py`: gold reads "since (before)
   Christmas [<year>]" as `MonthDate=12` (+`YearDate`) + Since.
6. **Flexible seizure-free duration / point-in-time** — "seizure free for more
   than five years"; "remains seizure free after his surgery" (after ⇒
   Since+Surgery); drug-stop point-in-time triggers; "since the beginning of
   <month>" date filler.

Precision (cut FP):
7. **Medication-dose gate widened** — `_DOSE_UNIT` now covers
   `milligram(me)s`/`mgs`/`gram(me)s`/`units`; "250 milligrams twice a day" no
   longer leaks in as seizure frequency.
8. **Adverbial seizure-context gate** — a bare "daily"/"weekly" fires only near
   a seizure noun (kills "daily headaches", "daily living", titration "daily").
9. **Non-clinical / history / driving zero gate** — `rules/seizure_free.py`:
   "no history of febrile seizures", "no significant seizure markers", "free of
   seizures before … allowed to drive" no longer emit a spurious 0.
10. **Same-sentence, bounded-gap association** (largest precision lever) —
    `association.py`: an attribute extraction binds only to an anchor in its
    sentence within 80 chars, and is dropped otherwise instead of being glued
    onto a distant seizure anchor. This killed the dominant cross-context FP
    ("migraine episodes once a month", "4 to 5 episodes a month" borrowing a
    seizure anchor elsewhere in the letter). FP letters 17→5.

Net-negative, reverted:
11. **Per-statement emission (D8)** — splitting a co-located numeric statement
    from a FrequencyChange into two mentions was implemented and measured
    **net-negative** on dev (per-item 0.272→0.264, per-letter 0.482→0.471): the
    ~11-mention upside is outweighed by split-induced FP (lone change mentions
    gold had merged, or whose direction is wrong). Reverted; rationale recorded
    in `association.py`. This is the honest de-overfitting result, not a
    deferral — the anchor+association model's single-merged-statement default is
    the better operating point on dev.

## 3. FN decomposition (sf_semantic: 187 gold, 42 TP, 145 FN)

| Bucket | Count | Winnable? |
|--------|------:|-----------|
| **TP** | 42 | — |
| Right phrase, wrong attribute bundle (`attr_miss`) | 21 | Partly (hard tail: DrugChange-without-"since", "used to" historical reframing, Age-based bundles, Last_Year-as-PointInTime) |
| Singular/plural phrase mismatch only | 13 | **Not on exact match** (see §4) |
| Other no-phrase-match (clean gold phrase) | 74 | Partly (wrong-type association, uncovered statement forms, "infrequent/under control") |
| Offset-drift–corrupted gold phrase | 37 | **No** (see §4) |

## 4. Noise ceiling (D12) — quantified

**Corrupt slice: 37 / 187 = 19.8%.** Gold SF `text` values that do not normalize
to a clean seizure-term phrase, because spelling was corrected in the letters
after annotation without updating offsets (D11/D12). Two kinds:

- *Truncations* (un-winnable on exact phrase text): `'seizur'`, `'eizures'`,
  `'absenc'`, `'ocal seizures with altered awarenes'`, `'yoclonic jerks.'`,
  `'convulsive seizur'`, `'seizrue free'` (also a misspelling).
- *Over-captures embedding frequency* (violate D7 "text is the seizure term
  only"): `'2 generalised tonic clonic seizures in 2014'`, `'seizures since the
  last clinic appointment'`, `'not had any further seizures since increasing the
  levetiracetam'`, `'seizure frequency has reduced'`.

**Singular/plural mismatch: 13 / 187 = 7.0%.** Gold annotates the singular form
("generalised tonic clonic seizure", "secondary generalised seizure", bare
"seizure" for a multi-event count) where the extractor emits the plural the
letter actually uses (or vice versa). `normalize_phrase` lowercases and strips
hyphens/quotes but does not singularize. Singularizing the match key would
recover these for **both** architectures and the benchmark comparison, but it
changes the reported phrase metric and the cross-architecture contract; per the
2026-06-10 scope decision we **keep exact match** and report this as a ceiling
component rather than altering scoring. Many of the 13 are themselves
offset-drift artifacts (gold truncated "seizures" → "seizure").

**Combined un-winnable-on-exact-text ceiling ≈ 50 / 187 = 26.7%.** The
`sf_semantic` recall of 0.225 should be read against an effective gold of ~137
clean, exact-matchable mentions, i.e. a corrupt-adjusted recall ≈ 0.31.

## 5. Remaining winnable work (next, if pursued)

Ranked by the §3 buckets, recall-side (precision is now strong at 0.87
per-letter):

1. **Wrong-type association** — when a letter has several seizure types, a
   frequency clause sometimes associates to the wrong anchor (e.g. emits
   "myoclonic jerks" where gold wants "generalised tonic clonic seizure"). Needs
   type-aware association, not just nearest.
2. **"Infrequent / under control" ⇒ FrequencyChange** — "well controlled" /
   "under control" ⇒ Infrequent (guideline List 11 L877–L879) is still
   unmodeled; appears in several no-phrase misses.
3. **Age-based bundles** (`AgeLower`/`AgeUpper`/`AgeUnit`) — a small gold family
   ("seizures between the ages of 13 and 19") with no rule.
4. **`PointInTime=Last_Year` vs period `Year`** — "5 seizures in the last year"
   is gold `Last_Year`+During, we emit period `Year`.
5. **DrugChange without "since"** — "stopped her medication 2 months ago" ⇒
   DrugChange+Since is inferred by gold without a "since/after" cue.

These are individually small (1–4 mentions each) and several risk precision, so
they are logged rather than forced. The corrupt + plural ceiling (§4) caps any
exact-match approach at ≈ 0.73 phrase recall regardless.
