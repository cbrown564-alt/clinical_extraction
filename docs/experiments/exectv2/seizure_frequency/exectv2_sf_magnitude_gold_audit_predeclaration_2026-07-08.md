# Predeclaration — SF `FrequencyChange` magnitude gold-annotation audit (2026-07-08)

Date: 2026-07-08. Owner: ExECTv2 workstream.
Hypothesis: `sf_magnitude_gold_audit_2026-07-08` (PENDING).
Driver: `scripts/run_exectv2_sf_magnitude_gold_audit.py` (zero LLM calls;
read-only inspection of dev140 gold + source text; no scorer/gold change).
Prior art: `sf_direction_vocab_deconflation_2026-07-08` (registry entry 38,
MAGNITUDE IS PART OF THE GAP — conflation explains ~60% of the integration gap,
a +0.0226 direction residual remains) and `sf_magnitude_complement_2026-07-08`
(registry entry 39, COMPLEMENT TRAILS RULES — the magnitude recall gap is a
genuine capacity gap no contract design recovers).
Umbrella: pathway #2 of the 2026-07-08 SF follow-up queue (Next in
`PROJECT_STATUS.md`).

## Purpose (the question)

The vocab-deconflation probe (entry 38) asked a **scoring-side** question:
does the +0.0564 rules-vs-selector integration gap survive projecting the
`FrequencyChange` vocab onto two orthogonal axes (direction, magnitude)? It
found the gap shrinks 60% (to +0.0226) but does not collapse — magnitude is
~two-thirds of the gap, a real direction residual is ~one-third. The
magnitude-complement probe (entry 39) then showed the LLM's magnitude
precision edge does *not* transfer to the no-match letters, closing pathway #1.

This audit asks the orthogonal, **gold-side** question the deconflation probe
explicitly deferred: **are the magnitude labels (`Frequent`/`Infrequent`)
themselves predominantly mislabeled direction (a gold-annotation
representational defect), or are they genuine magnitude (the conflation is by
design)?** The deconflation predeclaration froze the scope: "the conflation is
baked into the frozen gold … the annotation guideline … §2 even maps
`'under control'/'well controlled' ⇒ FrequencyChange=Infrequent` … by guideline
design," and treated the gold as "Aligned" (guideline design, not a defect).
This audit tests that treatment empirically, row by row, rather than asserting
it.

Either outcome resolves the ambiguity the deconflation probe surfaced:

- If the magnitude labels are **predominantly mislabeled direction**, the gold
  schema has a representational defect worth a manuscript caveat (the
  guideline's Appendix L987 "Aligned" mapping is itself a representational
  error — it puts a magnitude reading into a change-direction field). The
  frozen corpus cannot be re-annotated, so it is documented, not fixed, and
  filed as a candidate guideline-correction note.
- If they are **genuinely magnitude**, the conflation is by design (the field
  deliberately mixes two clinical notions), and the residual direction gap the
  deconflation probe isolated is a pure model gap, not a gold artifact.

This is the gold-noise inspection surface the `/gold-noise` frontend tab (item 1
of the predecessor-synthesis follow-ups) was built to support, and the row-level
dev140 inspection the standing protocol permits.

## Why a gold inspection, not a scorer change (scope freeze)

This audit **does not touch gold or the scorer**. It reads the dev140 gold
annotations and their source text, classifies each magnitude label, and
aggregates the verdict. There is no re-scoring, no rekey, no prediction
artifact consumed. The output is a classification table + an aggregate share.
The frozen benchmark key (`frequency_state_directional`, the deconflated
companions) is unchanged; this is a documentation/interpretation deliverable,
exactly as the `Next` entry frames it ("Free (dev140 gold audit, no LLM calls)").

## The classification taxonomy (frozen before any row is classified)

Each of the 19 dev140 `Frequent`/`Infrequent` gold annotations is classified
into exactly one of three mutually exclusive categories by reading the source
letter text around the annotation span. The decision rule is stated per
category; ties are broken toward `GENUINE_MAGNITUDE` (the conservative call —
the annotator's literal label stands unless the text clearly contradicts it).

### Category A — `MISLABELED_DIRECTION` (the annotation expresses a change-direction, not a magnitude)

The source text for the annotated seizure type states a **change in frequency
over time** (worsening / improving / now-happening-vs-before) or a
relative-temporal framing that is fundamentally about direction, such that the
clinically load-bearing claim is "this has changed," not "this is at a high/low
absolute rate."

Decision rule — assign `MISLABELED_DIRECTION` when **either**:

1. The sentence contains an explicit before/after or change-of-frequency
   construction tied to the annotated type — e.g. "were infrequent at first,
   they are now happening frequently," "frequency has improved," "deteriorated,"
   "begun to slip," "increased," "decreased," "control had been good until …"
   — where the *change* is the point, and a direction label
   (`Increased`/`Decreased`) would capture the clinical claim more faithfully
   than a magnitude label.
2. The magnitude word ("frequent," "infrequent," "occasional," "well
   controlled") is being used as a *post-hoc characterization of a change*
   rather than an absolute rate — e.g. "well controlled" meaning "has come
   under control" (a change to low frequency) rather than "is at a low rate"
   (a static magnitude).

The signature: the reader's clinical takeaway is "direction of change," not
"absolute frequency level."

### Category B — `GENUINE_MAGNITUDE` (the annotation expresses an absolute frequency level, no change-direction claim)

The source text states the **absolute rate/frequency** of the annotated seizure
type with no change-over-time framing — the magnitude word is a static
descriptor of how often the seizures occur in the current clinical picture.

Decision rule — assign `GENUINE_MAGNITUDE` when **all** hold:

1. The magnitude word ("frequent," "infrequent," "occasional," "well
   controlled" used as "is controlled," "rare") is an absolute-rate descriptor
   of the current state.
2. There is no before/after, worsening/improving, or change-of-frequency
   construction tied to the annotated type in the same sentence (a *separate*
   `Increased`/`Decreased` annotation on a *different* seizure type in the
   same letter does NOT reclassify this one — the annotator distinguished the
   two types deliberately).
3. The reader's clinical takeaway is "absolute frequency level," not
   "direction of change."

The signature: removing the magnitude word would lose information about *how
often*, not about *which way it changed*.

### Category C — `AMBIGUOUS` (the text supports both readings; cannot classify confidently)

The source text is compatible with either a direction reading or a magnitude
reading, and no single clinical claim dominates.

Decision rule — assign `AMBIGUOUS` when the magnitude word appears in a context
where a reasonable clinician could read it either way (e.g. "well controlled"
in a follow-up letter where it is unclear whether "controlled" implies a change
to that state or simply a steady low rate), AND neither A nor B's decision rule
fires decisively. These are reported separately and excluded from the headline
share; they do not count toward either the "mislabeled" or "genuine" totals.

## The outcome bands (frozen before classification)

Headline share = `MISLABELED_DIRECTION / (MISLABELED_DIRECTION + GENUINE_MAGNITUDE)`,
excluding `AMBIGUOUS` from the denominator (sensitivity to whether ambiguous
rows are included is reported as a secondary check).

| Outcome | Verdict | Manuscript implication |
| --- | --- | --- |
| `MISLABELED_DIRECTION` share **≥ 60%** (≥ ~10 of the non-ambiguous rows) | **MAGNITUDE LABELS ARE PREDOMINANTLY MISLABELED DIRECTION — gold representational defect** | Manuscript carries a gold-quality caveat: the guideline's Appendix L987 mapping puts a magnitude reading into a change-direction field, and the majority of dev140 magnitude annotations are better read as direction. File a candidate guideline-correction note (frozen corpus → documented, not re-annotated). The deconflation probe's `same` projection for magnitude labels is reaffirmed as the honest encoding. |
| `MISLABELED_DIRECTION` share **30–60%** (a real mix) | **CONFLATION IS PARTLY BY DESIGN, PARTLY ARTIFACT — mixed gold** | Manuscript carries a softer caveat: some magnitude labels are genuine, a meaningful minority are mislabeled direction. The deconflation's `same` projection holds for the genuine ones; the mislabeled ones are a documented gold-noise source. |
| `MISLABELED_DIRECTION` share **< 30%** (≤ ~5 of the non-ambiguous rows) | **MAGNITUDE LABELS ARE GENUINE — conflation is by design** | No gold-defect caveat. The field deliberately mixes two clinical notions (absolute rate + change-direction) per the guideline; the deconflation probe's residual direction gap (+0.0226) is a pure model gap, not a gold artifact. The `same` projection stands as the faithful direction-axis encoding of genuinely-magnitude labels. |

The expected outcome is genuinely uncertain. Arguments for "genuine magnitude":
the guideline explicitly defines the 5-value closed vocab and maps "well
controlled"⇒`Infrequent`; some letters carry *both* a magnitude label and a
direction label on different seizure types (the annotator distinguished them).
Arguments for "mislabeled direction": the guideline's own mapping
("under control"⇒`Infrequent`) is itself a change-framing ("has come under
control") put into a magnitude slot; several magnitude words ("well
controlled," "occasional") are inherently ambiguous between rate and change.

### Sensitivity / secondary checks (reported regardless of band)

1. **Ambiguous-inclusive share:** recompute the headline share with `AMBIGUOUS`
   rows counted as `MISLABELED_DIRECTION` (upper bound) and as
   `GENUINE_MAGNITUDE` (lower bound). The verdict band must be robust to the
   ambiguous handling or the sensitivity is reported as a caveat.
2. **Cross-tabulation with the co-annotation pattern:** for letters that carry
   *both* a magnitude label and a direction label (EA0050, EA0123, EA0161
   observed in the pre-audit), report whether the magnitude label on those
   letters classifies as genuine (expected: if the annotator used the direction
   vocab elsewhere, a magnitude label is more likely deliberate). This is a
   mechanism check on the headline share, not a verdict driver.
3. **EA0049 GTCS special case:** the pre-audit flagged that EA0049's
   `generalised-tonic-clonic-seizures` is labeled `Frequent` despite the text
   reading "were infrequent at first they are now happening frequently" — an
   explicit change. This is the single clearest candidate for
   `MISLABELED_DIRECTION` and is called out individually in the results.

## Frozen contract

| Field | Value |
| --- | --- |
| Driver | `scripts/run_exectv2_sf_magnitude_gold_audit.py` (read-only; emits the 19 rows + context to `experiments/exectv2_sf_magnitude_gold_audit_20260708.jsonl`) |
| Gold | dev140 only (frozen; test59/full-200 locked, not inspected) |
| Surface | All SeizureFrequency mentions with `FrequencyChange ∈ {Frequent, Infrequent}` (19 rows: Frequent 12 / Infrequent 7 — reproduced by the driver in-run) |
| Scorer | Unchanged. No scoring; no prediction artifact consumed. |
| Call count | **0 LLM calls. 0 scorer calls.** Pure read + classify. |
| Row inspection | dev140 only (the 19 magnitude annotations across 16 letters). |
| Classification source | The driver's emitted `context` window (±220 chars, span fenced) + the raw annotation `text`/`cuiphrase`. The full letter text is available via the `/gold-noise` tab for any row needing wider context. |

## What this is NOT

- **Not a gold re-annotation.** Gold is frozen; this classifies the existing
  labels, it does not change them.
- **Not a scorer or metric change.** No scoring surface is touched; the
  deconflation probe's projected metrics stand as-is.
- **Not a re-test of the deconflation probe.** That probe measured a scoring-
  axis gap; this measures a gold-label property. They are complementary — the
  deconflation asked "does the gap survive separating the axes?" and this asks
  "are the magnitude labels even on the right axis?"
- **Not a claim about test59/full-200.** Dev140 only; any statement about the
  wider corpus is bounded by the dev140 prevalence measured here.
- **Not a promotion gate.** No production wiring follows from the verdict; the
  output is a documentation/attribution deliverable (a manuscript caveat or the
  absence of one).

## Provenance / artifacts (produced)

- Driver: `scripts/run_exectv2_sf_magnitude_gold_audit.py`.
- Substrate: `experiments/exectv2_sf_magnitude_gold_audit_20260708.jsonl`
  (the 19 rows + context emitted by the driver).
- Results doc:
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_magnitude_gold_audit_results_2026-07-08.md`.
- Hypothesis registry entry: `sf_magnitude_gold_audit_2026-07-08`.

## Pre-declaration of the manuscript implication (frozen before classification)

- **Band 1 (≥60% mislabeled):** the manuscript §4.2 / gold-quality passage
  gains a caveat that the `FrequencyChange` magnitude sub-vocab is itself a
  gold-annotation defect — the majority of magnitude labels are better read as
  change-direction, and the guideline's "well controlled ⇒ Infrequent" mapping
  is a representational error (a change-to-low reading encoded as a magnitude).
  This strengthens the deconflation probe's finding (the conflation is not just
  a scoring artifact but a gold property) and reframes the residual direction
  gap as partly gold-attributable. Filed as a candidate guideline-correction
  note for the corpus authors; the frozen corpus is documented, not fixed.
- **Band 3 (<30% mislabeled):** no gold-defect caveat; the manuscript states
  the magnitude labels are a deliberate (if conflation-prone) part of the
  guideline's `FrequencyChange` semantics, and the deconflation probe's
  residual direction gap is a pure model gap. The `same` projection stands.

Either way the audit converts the deconflation probe's deferred "by guideline
design" assertion into a measured property, which is the discipline this
workstream requires before the gold-framing can support a claim.
