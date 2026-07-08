# Results — SF `FrequencyChange` magnitude gold-annotation audit (2026-07-08)

Date: 2026-07-08. Owner: ExECTv2 workstream.
Hypothesis: `sf_magnitude_gold_audit_2026-07-08` — **MAGNITUDE LABELS ARE
GENUINE** (Band 3: 1/17 = 5.9% mislabeled, robust to ambiguous handling).
Predeclaration:
`docs/experiments/exectv2/seizure_frequency/exectv2_sf_magnitude_gold_audit_predeclaration_2026-07-08.md`.
Driver: `scripts/run_exectv2_sf_magnitude_gold_audit.py` (zero LLM calls, zero
scorer calls; read-only gold inspection).
Substrate: `experiments/exectv2_sf_magnitude_gold_audit_20260708.jsonl` (the 19
rows + ±220-char context emitted by the driver).
Summary: `experiments/exectv2_sf_magnitude_gold_audit_summary_20260708.json`.

## Verdict

**MAGNITUDE LABELS ARE GENUINE — conflation is by design (Band 3).**

Of 19 dev140 `Frequent`/`Infrequent` gold annotations, **16 are genuine
magnitude**, **1 is mislabeled direction**, and **2 are ambiguous**. The
headline mislabeled share is **1/17 = 5.9%** (ambiguous excluded), far below the
predeclared 30% threshold. The verdict is **robust to ambiguous handling**: even
counting both ambiguous rows as mislabeled direction (the adversarial upper
bound) the share is **3/19 = 15.8%**, still below 30%.

This answers the deconflation probe's (entry 38) deferred question: the
`FrequencyChange` magnitude sub-vocab is **not** a gold-annotation
representational defect. The conflation of change-direction and frequency-
magnitude on a single attribute is by annotation-guideline design (Appendix L987,
"Aligned"). Consequently the deconflation probe's residual direction gap
(**+0.0226**) is a **pure model gap**, not a gold artifact — the closed-option
selector genuinely trails the deterministic rules on the direction axis itself.

| Category | Count | Share (non-ambiguous) |
| --- | ---: | ---: |
| `GENUINE_MAGNITUDE` | 16 | 94.1% |
| `MISLABELED_DIRECTION` | 1 | 5.9% |
| `AMBIGUOUS` (excluded) | 2 | — |
| **Total** | **19** | — |

## Per-row classification

The classification taxonomy and decision rules are frozen in the predeclaration
(three categories: `MISLABELED_DIRECTION`, `GENUINE_MAGNITUDE`, `AMBIGUOUS`;
ties broken toward `GENUINE_MAGNITUDE`). Each row is classified by reading the
±220-char context window the driver emits around the annotation span (span
fenced `>>…<<`). Gold `start_index`/`end_index` drift against `note_text`
(spelling was corrected in the `.txt` files post-annotation without updating
offsets); the window is deliberately generous and the raw `text`/`cuiphrase`
are printed alongside, so the classification does not depend on the exact slice.

| # | Letter | FC | Annotation | Category | Source phrase |
| ---: | --- | --- | --- | --- | --- |
| 1 | EA0025 | Frequent | myoclonic-jerks | GENUINE_MAGNITUDE | "very frequent myoclonic jerks" |
| 2 | EA0049 | Frequent | myoclonic-jerks | GENUINE_MAGNITUDE | "frequently gets myoclonic jerks" |
| 3 | EA0049 | Frequent | generalised-tonic-clonic-seizures | **MISLABELED_DIRECTION** | "were infrequent at first they are now happening frequently" |
| 4 | EA0082 | Frequent | absences | GENUINE_MAGNITUDE | "continue fairly frequent, 2-3 per day" |
| 5 | EA0096 | Frequent | absences | GENUINE_MAGNITUDE | "frequent drops and absences throughout the day" |
| 6 | EA0106 | Frequent | seizures | GENUINE_MAGNITUDE | "still having fairly frequent seizures" |
| 7 | EA0119 | Frequent | seizures | GENUINE_MAGNITUDE | "still seems to be getting fairly frequent seizures" |
| 8 | EA0119 | Frequent | seizures | GENUINE_MAGNITUDE | "still having fairly frequent seizures" |
| 9 | EA0121 | Frequent | seizures | GENUINE_MAGNITUDE | "continues to get frequent seizures" |
| 10 | EA0161 | Frequent | tonic-clonic-seizures | GENUINE_MAGNITUDE | "relatively frequent … in the last few years" |
| 11 | EA0169 | Frequent | dyscognitive-seizures | GENUINE_MAGNITUDE | "frequent focal dyscognitive seizures in clusters" |
| 12 | EA0181 | Frequent | dyscognitive-seizures | GENUINE_MAGNITUDE | "frequent focal dyscognitive seizures in clusters" |
| 13 | EA0011 | Infrequent | focal-to-bilateral-convulsive-seizures | GENUINE_MAGNITUDE | "infrequent … having around two in the year" |
| 14 | EA0022 | Infrequent | seizures | **AMBIGUOUS** | "seizures seems to be well controlled on lamotrigine" |
| 15 | EA0049 | Infrequent | absence | GENUINE_MAGNITUDE | "Occasional absences" |
| 16 | EA0050 | Infrequent | absences | GENUINE_MAGNITUDE | "Occasional absences" |
| 17 | EA0059 | Infrequent | seizures | **AMBIGUOUS** | "seizures are also well controlled" |
| 18 | EA0068 | Infrequent | focal-seizures | GENUINE_MAGNITUDE | "Infrequent focal seizures" (Diagnosis line) |
| 19 | EA0123 | Infrequent | generalized-tonic-clonic-seizures | GENUINE_MAGNITUDE | "longstanding infrequent" |

### Row 3 — the single `MISLABELED_DIRECTION` (EA0049 GTCS)

EA0049's `generalised-tonic-clonic-seizures` is labeled `Frequent` despite the
text reading *"Although the generalised tonic clonic seizures were **infrequent
at first** they are **now happening frequently**."* This is an explicit
before/after change construction — the clinically load-bearing claim is
"direction of change" (increased), not "absolute rate." A `FrequencyChange =
Increased` label would capture the clinical claim more faithfully; the
annotator labeled the *current magnitude* (`Frequent`) rather than the *change*.
This is the single clearest candidate for mislabeling the pre-audit flagged, and
it is the only row that lands in `MISLABELED_DIRECTION`.

### Rows 14 & 17 — the two `AMBIGUOUS` ("well controlled" ⇒ Infrequent)

EA0022 and EA0059 both annotate `seizures` as `Infrequent` with the text
*"[seizures] seems to be **well controlled**"* (EA0022) and *"seizures are also
**well controlled**"* (EA0059). "Well controlled" is the guideline's List 11
(L877–L879) mapping ⇒ `FrequencyChange = Infrequent`. It sits at the boundary of
two readings: a **magnitude** reading ("is at a low rate") and a **direction**
reading ("has come under control" — a change to low frequency, often via
treatment). Neither reading decisively dominates in context (EA0022 adds "on
lamotrigine," which weakly supports the change-to-low reading, but the sentence
is present-tense and could equally be a steady-state rate). Per the frozen
tie-break these are reported as `AMBIGUOUS` and excluded from the headline
denominator; their sensitivity bounds are below.

## Sensitivity checks (predeclared secondary metrics)

**Ambiguous handling (the headline robustness check):**

| Handling | Mislabeled | Genuine | Denominator | Mislabeled share |
| --- | ---: | ---: | ---: | ---: |
| Ambiguous excluded (headline) | 1 | 16 | 17 | **5.9%** |
| Ambiguous → mislabeled (upper bound) | 3 | 16 | 19 | **15.8%** |
| Ambiguous → genuine (lower bound) | 1 | 18 | 19 | **5.3%** |

The verdict (Band 3, < 30%) is robust across all three handlings. The
adversarial upper bound (15.8%) stays well inside Band 3.

**Co-annotation cross-tab (the mechanism check):**

Four letters carry *both* a magnitude label and a direction label on different
seizure types (the annotator demonstrably knew and used the direction vocab):

| Letter | Magnitude annotation | Direction annotation | Magnitude category |
| --- | --- | --- | --- |
| EA0050 | Infrequent (absences) | Decreased (seizures) | GENUINE_MAGNITUDE |
| EA0123 | Infrequent (GTCS) | Decreased (seizure) | GENUINE_MAGNITUDE |
| EA0161 | Frequent (TCS) | Decreased (seizure) | GENUINE_MAGNITUDE |
| EA0049 | Frequent (GTCS), Infrequent (absence), Frequent (myoclonic) | (none) | 1 mislabeled / 2 genuine |

The pattern is the expected one and corroborates the verdict: when the annotator
used the direction vocab elsewhere on the same letter, the magnitude labels are
deliberate (genuine), not direction mislabels. The single mislabel (EA0049
GTCS) is on a letter where the annotator did *not* use a direction label
elsewhere — consistent with the annotator defaulting to the magnitude slot when
the change construction was not the focus of the annotation pass. This is a
mechanism check, not a verdict driver; it aligns with the headline share.

## Reproduction / contract checks

- **Count reproduction:** the driver emits **19 rows** (Frequent 12 / Infrequent
  7), matching the pre-audit tally from the 200 gold files exactly. No gold or
  scorer state changed.
- **Zero calls:** 0 LLM calls, 0 scorer calls. Pure read + classify.
- **Split discipline:** dev140 only. test59 / full-200 were not inspected (the
  frozen protocol authorizes dev140 row inspection only).
- **Scoring surface unchanged:** no metric, key builder, or prediction artifact
  was touched. The deconflation probe's projected metrics
  (`state_profile_direction_deconf`, `state_profile_magnitude`) stand as-is.

## Interpretation

This audit is the gold-side complement to the deconflation probe's scoring-side
finding. Together they triangulate the conflation from two directions:

- **Scoring-side (entry 38):** projecting the vocab onto two orthogonal axes
  shrinks the rules-vs-selector integration gap 60% (conflated +0.0564 →
  direction-deconflated +0.0226); the magnitude axis carries ~two-thirds of the
  gap, a real direction residual ~one-third.
- **Gold-side (this audit):** the magnitude labels the deconflation projected
  are **genuine magnitude in 16/19 cases** (94.1% non-ambiguous). The
  conflation is by annotation-guideline design, not a gold defect.

The synthesis: the `FrequencyChange` attribute *deliberately* conflates two
clinical notions (absolute rate + change-direction) per the guideline, and the
deterministic `rules/change.py` faithfully implements that conflated vocab. The
closed-option selector, asked a plain-English "direction" question over all five
labels, correctly treats the genuine-magnitude labels as out-of-scope for the
direction question — which is *why* it drops them on the conflated metric and
*why* the deconflation's `same` projection is the honest direction-axis
encoding. The residual +0.0226 direction gap is a genuine model gap (the
selector misses ~4 direction facts the rules' regexes catch), unattributable to
gold noise.

This **closes pathway #2** of the 2026-07-08 SF follow-up queue. Pathway #1
(the magnitude complement, entry 39) already closed as a negative; the remaining
two pathways (#3 the Inv dspy near-ceiling question; #4 the manuscript
attribution-discipline deliverables) are independent of this result.

## Manuscript implication (predeclared Band 3)

No gold-defect caveat is warranted for the magnitude sub-vocab. The manuscript
§4.2 / gold-quality passage states plainly that the `FrequencyChange` magnitude
labels (`Frequent`/`Infrequent`) are a deliberate (if conflation-prone) part of
the guideline's `FrequencyChange` semantics — the field mixes absolute-rate and
change-direction notions by design — and that the deconflation probe's residual
direction gap (+0.0226) is a pure model gap, not a gold artifact. The
deconflation's `same` projection for magnitude labels (entry 38) stands as the
faithful direction-axis encoding of genuinely-magnitude labels.

The single mislabel (EA0049 GTCS) and the two ambiguous "well controlled" rows
are noted as documented gold-noise at known low prevalence (1/17 mislabeled;
2/19 ambiguous) — consistent with the gold-noise surface the `/gold-noise`
frontend tab already exposes, not rising to a representational-defect claim.
They do not move any cited number and require no scorer change.

## What this does NOT change

- No cited headline number (the audit does not score anything).
- No gold annotation (frozen; test59 locked, dev140 inspected read-only).
- No scorer / metric / key builder / prediction artifact.
- No production wiring (this is a documentation deliverable).
- The deconflation probe's verdict (entry 38: MAGNITUDE IS PART OF THE GAP, NOT
  ALL OF IT) — this audit confirms the magnitude labels the deconflation
  projected are real magnitude labels, so the deconflation's attribution stands
  unchanged. The residual direction gap is reaffirmed as a genuine model gap.
