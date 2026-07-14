> **Superseded for navigation —** canonical summary: [`DIAGNOSIS_FAMILY_LADDER_CANON.md`](../../../canon/workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md). Full detail retained below.

# Diagnosis canonical row-analysis — the Dx "consolidation" gap is gold quality, not genuine recall

Status: **CLOSED (positive — reframes the manuscript's gap-mechanism claim for Diagnosis).**
Date: 2026-06-30.
Owner: predecessor-lessons application workstream (`docs/research/predecessor_lessons/`).

Companions:
- `docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md` — the doc that
  reopened this question on 2026-06-28 ("the Diagnosis 'consolidation' finding is the same
  mechanism [as SF], so the 'architectural gap' framing is also in question") and never
  followed it up.
- `docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`
  — the SF Phase 7 precedent this analysis mirrors method-for-method.
- `docs/research/paper_drafts/benchmark_reconciliation_sf_gold_quality_revision_2026-06-29.md`
  — the manuscript revision that gave SF the "mechanism B" (gold-quality ceiling) treatment;
  Diagnosis did not get the same treatment and this doc shows it must.

## 1. Question

The GEPA single-model plateau synthesis found Diagnosis genuine-recall-miss F1 0.662 (per-family
run `exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`) and characterized 56 "genuine
misses" as the model failing to enumerate every co-present diagnostic concept the gold tags
(e.g. gold tags both "focal epilepsy" and "temporal lobe epilepsy" from one diagnostic phrase;
the model consolidates to one). That characterization used a simplified, miss-only,
home-tagged-only diagnostic (`experiments/exectv2_genuine_recall_analysis.py`) and never asked
the SF-style question: of the letters scored wrong, how many are genuine model error vs. the
model being clinically right but scored wrong because gold double-tagged or under-annotated?

This analysis answers that question on the **official** Diagnosis `clinical_headline` scorer
(`score_concept_identity(gold, pred, "Diagnosis").concept_only` — entity-agnostic recall pool,
home-tagged precision), reusing the same run's predictions, with zero new LLM calls.

## 2. Method

`experiments/exectv2_dx_canonical_row_analysis.py`: for every dev140 letter, decomposes the
official scorer's per-letter precision/recall contributions into **missed** concepts (gold
concepts with no overlapping prediction anywhere in the letter, any entity — a false negative)
and **spurious** concepts (home-tagged Diagnosis predictions with no matching gold concept — a
false positive). The script **self-validates**: summing the per-letter decomposition reproduces
the official aggregate exactly (P=0.6355, R=0.6902, **F1=0.6617**, matching the registry's
recorded `clinical_headline_diagnosis_f1: 0.6617` for this run bit-for-bit).

88/140 letters (62.9%) carry at least one Diagnosis disagreement: **92 missed + 117 spurious =
209 individual concept-level disagreements.** Per-letter markdown substrate (gold concepts,
predicted concepts, located context snippets, full letter text) was written for all 88 letters
to `_dx_canonical/`.

Five parallel clinical reviewers (general-purpose sub-agents, ~18 letters each, no code access)
read the full letter text for every one of the 209 disagreements and assigned one of three
verdicts, mirroring the SF Phase 6/7 taxonomy:

- **GOLD_RIGHT** — genuine model error (true omission, or a fabricated/over-read diagnosis the
  letter does not support).
- **MODEL_DEFENSIBLE** — the model is clinically correct; the score is wrong because of a gold
  artifact (consolidation/multiplicity, under-annotation, or pure canonicalization/wording
  mismatch of identical text).
- **BOTH_DEFENSIBLE** — genuine ambiguity (hedged/queried diagnoses, differential vs confirmed).

`experiments/exectv2_dx_canonical_adjudication.py` embeds all 209 verdicts verbatim and
**self-validates**: it asserts the embedded set exactly equals the 209 missed/spurious concepts
the row-analysis script enumerated (no missing, no extra) before tallying.

## 3. Result

| | n | share |
| --- | ---: | ---: |
| GOLD_RIGHT (genuine model error) | 31 | 14.8% |
| MODEL_DEFENSIBLE (gold artifact) | 167 | 79.9% |
| BOTH_DEFENSIBLE (genuine ambiguity) | 11 | 5.3% |

By direction:

| direction | n | GOLD_RIGHT | MODEL_DEFENSIBLE | BOTH_DEFENSIBLE |
| --- | ---: | ---: | ---: | ---: |
| MISSED (FN) | 92 | 7 | 80 | 5 |
| SPURIOUS (FP) | 117 | 24 | 87 | 6 |

**Clinically-adjusted aggregate** (treating MODEL_DEFENSIBLE + BOTH_DEFENSIBLE as correct,
recomputing precision/recall from the adjusted tp counts):

| | precision | recall | F1 |
| --- | ---: | ---: | ---: |
| OFFICIAL `concept_only` | 0.6355 | 0.6902 | **0.6617** |
| CLINICALLY-ADJUSTED | 0.9252 | 0.9764 | **0.9501** |

This is a **+0.288 F1** gap between the metric and clinical correctness — larger in absolute
terms than SF's reconciliation (metric 0.621 vs clinically-defensible 0.893 at the letter level,
a +0.27 gap by a different unit of measure, so the two are not directly comparable row-for-row,
but both land in the same place: most of the measured gap is not genuine model error).

## 4. What dominates the 79.9% "model defensible" share

Reading the 167 verdicts, four recurring mechanisms account for nearly all of it (no formal
sub-tagging was kept per-verdict, but the pattern is unambiguous on inspection of the raw list
in `_dx_canonical/_adjudication.csv`):

1. **Gold-multiplicity / consolidation** (the dominant pattern, matching the plateau synthesis's
   original hypothesis). Gold tags both a generic/parent concept and a specific/co-present
   concept — or splits one compound diagnostic phrase into multiple atomic tags (e.g. "Drug
   resistant focal epilepsy" → `drug resistant epilepsy` + `focal epilepsy`) — from a single
   diagnostic statement. The model emits one consolidated tag a clinician would consider
   complete. The JME triad sub-pattern recurs across at least 8 letters: gold tags only
   "juvenile myoclonic epilepsy" while the letter explicitly lists its component seizure types
   (myoclonic jerks, absences, GTCS); the model tagging the named types is treated as spurious.
2. **Pure canonicalization / wording-variant mismatch.** Identical source text produces
   different concept keys because the model and gold's canonicalization dictionaries diverge
   (singular/plural, "secondary" vs "secondarily", a letter's own typo faithfully transcribed,
   old vs new ILAE terminology). Not a clinical disagreement at all — a representation gap.
3. **Gold under-annotation.** The model emitted a diagnosis explicitly stated in the letter
   (frequently under the letter's own "Diagnosis:" header) that gold simply never tagged.
4. **Genuine model error, concentrated in two identifiable patterns** (the 31 GOLD_RIGHT,
   24/31 on the spurious side): **negation-as-diagnosis** (the model tagging an explicitly
   negated finding — "no history of febrile seizures", "no further generalised convulsions" —
   as a positive Diagnosis fact) and **investigation-finding-as-diagnosis** (an EEG finding like
   "generalised spike and wave with photosensitivity" mis-tagged under the Diagnosis entity
   instead of Investigations). These are real, narrow, fixable extraction-discipline bugs, not
   evidence of a broad recall deficit.

## 5. Conclusion and implications

**The Diagnosis "0.66 GEPA ceiling, 0.18 below the LLM-with-rules method" framing in the plateau synthesis
overstates genuine model error in the same way the pre-Phase-7 SF framing did.** Counting only
the 31 genuine errors among the 209 measured disagreements, the model is clinically correct on
the overwhelming majority of what the official scorer counts against it. This is **not** a
"Diagnosis is benchmark-format-fidelity-only" story (mechanism A in the manuscript's current
§4.1.2 framing) — it carries the same **mechanism B (gold-quality/convention ceiling)** that
SF was given in the 2026-06-29 revision, and by this measurement it is *more* lopsided for
Diagnosis (85.2% defensible+ambiguous) than for SF (72% defensible+ambiguous in the Phase 7
doc).

This does not mean Diagnosis extraction is flawless — the negation-handling and
investigation/diagnosis entity-confusion patterns are real, narrow, attributable model bugs
worth a targeted fix — but they account for a small minority of the measured gap.

**Consequence for the manuscript:** §4.1.2's "two distinct mechanisms" framing currently reads
as if SF is the lone gold-quality exception and Diagnosis/Prescription/Investigations are
dominated by closeable format fidelity. That is no longer accurate for Diagnosis. Feed this
result into Phase E as a parallel Diagnosis paragraph alongside the existing SF one, and revise
the "architectural gap is genuine recall" language in the GEPA plateau synthesis's still-active
conclusion (§4–5 of that doc) to note that the genuine-recall component is much smaller than
56/209 once gold-consolidation and canonicalization artifacts are excluded.

**Consequence for the GEPA workstream:** the multi-stage/focused-lanes investigations that
chased Diagnosis "genuine recall" (the exhaustive co-present enumeration schema in
`exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md` Phase 1) were optimizing partly against
a gold-consolidation artifact, not a pure recall deficit — consistent with that plan's own
Phase 3 finding that deterministic Dx convention re-keying (not more retrieval) bought the
larger, cleaner win (0.703 → 0.792).

## 6. Caveats

- This is a **dev140 development-set** analysis on one cached run
  (`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`); `test60` was never touched.
- Adjudication used five independent reviewers with no cross-checking between batches (unlike
  SF Phase 6, which used a single coherent pass); the taxonomy and worked examples were held
  fixed across batches to bound reviewer drift, but inter-reviewer agreement was not separately
  measured. Spot-checking suggests strong internal consistency (the four mechanisms in §4 recur
  identically across all five independent batches without prompting).
- Like SF, this number must be read as a band, not a precise decimal — the 85.2% defensible
  share is large enough that the qualitative conclusion is robust to a few reviewer judgment
  calls going the other way, but the exact percentage is not.
- No deterministic projection or prompt change was made here; this is a pure measurement /
  interpretation result, gated for promotion into the manuscript at Phase E.

## 7. Artifacts

- `experiments/exectv2_dx_canonical_row_analysis.py` — zero-LLM row decomposition + self-validation.
- `experiments/exectv2_dx_canonical_adjudication.py` — embedded verdicts + self-validation + tally.
- `_dx_canonical/_index.json`, `_dx_canonical/_summary.json`, `_dx_canonical/_adjudication.csv`,
  `_dx_canonical/<letter>.md` (88 files) — substrate and outputs (not committed; regenerable).
