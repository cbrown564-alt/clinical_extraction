# SF `changed`-class: row-by-row adjudication — why two LLMs plateau, and what is actually irreducible

> **SUPERSEDED (2026-06-29) by the canonical whole-corpus analysis:**
> `exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`. This report covered only the `changed`
> slice (42 letters) and reported ~52% genuine model error. The canonical analysis adjudicates **all
> 140 dev rows** on the **exact `state_profile` metric** (both LLM stages) and finds genuine model
> error is **28%** corpus-wide — the changed class is the *worst* slice, not representative. Its
> dominant whole-corpus finding (gold=[] over-emission = mostly **gold under-annotation**, not model
> error) is invisible from the changed-only slice. Read the canonical report for current conclusions;
> this one stands only as the `changed`/direction-axis deep dive.

Date: 2026-06-29
Scope: every dev140 letter where gold OR the model emits a SeizureFrequency `changed` state
(42 letters: 14 recall misses / 15 over-calls / 13 agreements).
Run analysed: `exectv2_gepa_sf_verify_gpt41mini_20260628` (P2 mini — best LLM-only SF verify,
state_profile 0.741 / clinical_headline 0.597; the same plateau Phase 5's reasoner arms reproduced at ~0.78).
Method: a zero-LLM quantitative skeleton (`scratchpad/quant_skeleton.py` logic — adjacency lexeme
scan + FC composition) + five parallel sub-agent clinical adjudications reading each full letter.

This report **revises** two prior conclusions:
- Plan §6c / Phase 4: "change-class precision is curated-precision territory, **not a learnable boundary**."
- The interactive claim that the plateau is "the label is underdetermined / irreducible."

Both were over-stated. The row evidence shows the `changed` plateau is **~⅔ a fixable representation
defect and ~⅓ genuine annotation ambiguity** — not a single irreducible wall.

---

## 1. The question

The SF `changed` class sits at F1 **0.473** (P 0.46 / R 0.48) while the rest of SF is ~0.80 and the
hybrid reaches 0.85R/1.00P. Two different task models (gpt-4.1-mini, deepseek-chat/-reasoner) plateau
at the same place. Is this an unlearnable boundary (the label is a convention coin-flip), or something
more specific? And does optimising toward gold here trade away clinically useful information?

## 2. Inter-annotator agreement — the premise, corrected

The ExECTv2 paper (Fonferko-Shadrach 2024, Table 1) reports human IAA per entity. Seizure Frequency
is the **second-weakest-agreed entity in the whole corpus**, not the strongest:

| Annotation | Human IAA F1 | ExECTv2-vs-gold per-item F1 |
| --- | ---: | ---: |
| Prescription | 0.87 | 0.87 |
| Diagnosis | 0.83 | 0.85 |
| Investigations | 0.82 | 0.95 |
| Birth History | 0.69 | 0.97 |
| Epilepsy Cause | 0.67 | 0.90 |
| Onset | 0.61 | 0.96 |
| Patient History | 0.57 | 0.78 |
| **Seizure Frequency** | **0.47** | **0.66** |
| When Diagnosed | 0.45 | 0.91 |
| **All** | **0.73** | 0.87 |

So two trained annotators, working from the v9 guidelines, agreed on SF at **F1 0.47** — they
disagreed roughly half the time. Our verifier's `changed`-class F1 (0.473) is essentially the
human-vs-human agreement ceiling for the entity. That establishes a genuine ambiguity floor, but —
per §6–7 — it accounts for only ~⅓ of our errors, not all of them.

## 3. The schema/metric finding — direction is neither modelled nor scored

The verify program's event schema (`gepa/program_sf_verify.py:58-75`) offers:

```
"kind": "frequency_rate | cluster_frequency | seizure_free | changed"
```

There is **no direction field**. The model can flag "something changed" but cannot express
`Increased / Decreased / Frequent / Infrequent / Same`. `events_to_sf_facts` maps `changed → state="changed"`,
and the downstream adapter fills `FrequencyChange="Same"` as the default representative value. So
**every `FC=Same` on a prediction is a pipeline default, not the model's clinical judgment.**

Both SF metrics then erase direction anyway:
- `state_profile` (`frequency_state_faithful`) collapses the five-way FC vocab into one `changed` bucket — presence only.
- `clinical_headline` `_frequency_state` is FC-blind (`changed → unknown`).

**Consequence (confirmed on the TP batch): across all 13 letter-level agreements the model emitted
`Same`; gold was directional in 12 of them; the model recovered the true direction in 0/12.** The
"13 true positives" are coincidental — they match only because the metric ignores direction. The
clinically actionable signal (is the patient getting better or worse?) is neither produced by our
system nor measured by the benchmark.

## 4. Quantitative skeleton (model-independent)

For each changed-involved letter, does an explicit change/band lexeme sit **within 50 chars of a
seizure term** (the deterministic-whitelist-recoverable signal), and what FC values are involved?

| group | n | adjacent change-lexeme present | FC composition |
| --- | ---: | ---: | --- |
| Recall misses (FN) | 14 | **14/14 (100%)** | gold: Frequent×6, Infrequent×5, Increased×1, Decreased×1, Same×2 |
| Over-calls (FP) | 15 | 10/15 (67%) | pred: **Same×16** (i.e. every FP is the default flag) |
| Agreements (TP) | 13 | 11/13 (85%) | gold: Increased×6, Frequent×6, Decreased×3, Infrequent×2, Same×1; **pred: Same×13** |

Over the 27 *genuine* gold `changed` facts (FN+TP), the signal source is **LEXICAL 23/27 (85%),
RELATIONAL 4/27 (15%), unsupported 0**.

## 5. Per-row adjudication

Axis A = signal source (LEXICAL / RELATIONAL / RATE-REDUNDANT / NONE).
Axis B = who is clinically right (GOLD_RIGHT / BOTH_DEFENSIBLE / MODEL_DEFENSIBLE).
Axis C = clinical-utility cost of matching gold (GAIN/REDUNDANT/NEUTRAL for recall; LOSE/NO-LOSS/NEUTRAL for precision).

### 5a. Recall misses (FN, 14) — gold has `changed`, model missed it

| letter | gold FC | phrase | A | B | C |
| --- | --- | --- | --- | --- | --- |
| EA0011 | Infrequent | "infrequent focal to bilateral convulsive seizures" | LEXICAL | GOLD_RIGHT | GAIN |
| EA0025 | Frequent | "very frequent myoclonic jerks" (whole type missed) | LEXICAL | GOLD_RIGHT | GAIN |
| EA0068 | Infrequent | "Diagnosis: Infrequent focal seizures" | LEXICAL | GOLD_RIGHT | GAIN |
| EA0108 | Increased | "seizures returning" (baseline "well controlled until last December") | RELATIONAL | GOLD_RIGHT | GAIN |
| EA0121 | Frequent | "continues to get frequent seizures" / "clusters very frequently" | LEXICAL | GOLD_RIGHT | GAIN |
| EA0123 | Decreased(+Infrequent) | "frequency has reduced from once a year to 1 every 2–3 years" | LEXICAL | GOLD_RIGHT | GAIN |
| EA0022 | Infrequent | "well controlled" / "completely under control" | LEXICAL | BOTH_DEF | NEUTRAL |
| EA0059 | Infrequent | "His seizures are also well controlled" | LEXICAL | BOTH_DEF | NEUTRAL |
| EA0106 | Frequent | "still having fairly frequent seizures" (rate already emitted) | LEXICAL | BOTH_DEF | REDUNDANT |
| EA0169 | Frequent | "frequent focal dyscognitive seizures in clusters" (rate 10–15/2d) | LEXICAL | BOTH_DEF | REDUNDANT |
| EA0181 | Frequent | (same patient/text as EA0169) | LEXICAL | BOTH_DEF | REDUNDANT |
| EA0082 | Frequent | "absences continue fairly frequent… 2–3 per day" (rate emitted) | LEXICAL | MODEL_DEF | REDUNDANT |
| EA0136 | Same | "seizures remain well controlled" (already captured seizure-free) | LEXICAL | MODEL_DEF | REDUNDANT |
| EA0128 | Same | "continues to get myoclonic jerks" (GTC 7yr free) | RELATIONAL | MODEL_DEF | NEUTRAL |

FN tally — A: LEXICAL 12, RELATIONAL 2, unsupported 0. B: GOLD_RIGHT 6, BOTH_DEF 5, MODEL_DEF 3.
C: GAIN 6, REDUNDANT 5, NEUTRAL 3.

### 5b. Over-calls (FP, 15) — model emits `changed` (`Same`), gold has none at letter level

| letter | model keyed on | A | B | C |
| --- | --- | --- | --- | --- |
| EA0092 | "make no changes to her **medication**" (not seizures) | NONE | GOLD_RIGHT | NO-LOSS |
| EA0104 | a diagnosis header, no frequency statement | NONE | GOLD_RIGHT | NO-LOSS |
| EA0124 | "valproate dose **unchanged**" (medication) | NONE | GOLD_RIGHT | NO-LOSS |
| EA0139 | "**medications** should remain the same" | NONE | GOLD_RIGHT | NO-LOSS |
| EA0172 | "most days" (no stability cue; the "rare" is SUDEP risk) | NONE | GOLD_RIGHT | NO-LOSS |
| EA0173 | seizure-free patient; "worse" was historical re: contraception | NONE | GOLD_RIGHT | NO-LOSS |
| EA0109 | "rare in the past but have become **more frequent**" — an INCREASE, flagged Same | LEXICAL | GOLD_RIGHT | NO-LOSS |
| EA0151 | "well controlled" baseline, but current event is an "unusual" cluster of 5 (deterioration) | RELATIONAL | GOLD_RIGHT | NO-LOSS |
| EA0186 | a resolution + a new recurrence, both collapsed to flat Same | RELATIONAL | GOLD_RIGHT | NO-LOSS |
| EA0007 | "best it's ever been" | RELATIONAL | BOTH_DEF | NEUTRAL |
| EA0010 | "Things are quite stable" (already seizure-free) | LEXICAL | BOTH_DEF | NEUTRAL |
| EA0040 | "this has helped his seizures" | LEXICAL | BOTH_DEF | NEUTRAL |
| EA0067 | "brivetiracetam seems to have helped her seizures" | LEXICAL | BOTH_DEF | NEUTRAL |
| EA0079 | "His epilepsy has been stable over the last few years" | LEXICAL | MODEL_DEF | LOSE |
| EA0166 | "jerks have improved significantly… once a month" (gold dropped the type) | LEXICAL | MODEL_DEF | LOSE |

FP tally — A: NONE 6, LEXICAL 6, RELATIONAL 3. B: GOLD_RIGHT 9, BOTH_DEF 4, MODEL_DEF 2.
C: NO-LOSS 9, NEUTRAL 4, LOSE 2.

### 5c. Agreements (TP, 13) — direction is lost in all but one

| letter | gold FC | model FC | phrase | A |
| --- | --- | --- | --- | --- |
| EA0049 | Frequent | Same | "infrequent at first… now happening frequently" | LEXICAL |
| EA0050 | Decreased | Same | "improved since reducing the lamotrigine" | LEXICAL |
| EA0087 | Increased | Same | "more generalised tonic clonic seizures" | LEXICAL |
| EA0096 | Frequent | Same | "frequent drops and absences" | LEXICAL |
| EA0111 | Increased | Same | "an increase in her seizures" | LEXICAL |
| EA0119 | Frequent | Same | "fairly frequent seizures" | LEXICAL |
| EA0125 | Increased | Same | "increasing seizures" | LEXICAL |
| EA0131 | Increased | Same | "seizures have been worse in the last year" | LEXICAL |
| EA0161 | Decreased | Same | "seizure frequency has improved" | LEXICAL |
| EA0178 | Decreased | Same | "improved her seizures" | LEXICAL |
| EA0198 | Increased | Same | "this increase in seizures frequency" | LEXICAL |
| EA0008 | Increased | Same | "seizures have returned" (after a period of seizure freedom) | RELATIONAL |
| EA0184 | Same | Same | "more typical absences since the last appointment" (only FC match) | RELATIONAL |

TP tally — A: LEXICAL 11, RELATIONAL 2. **Direction recovered: 1/13 (only EA0184); 0/12 of the directional cases.**

## 6. Aggregate adjudication (29 error cases)

| Axis B | FP | FN | total | share |
| --- | ---: | ---: | ---: | ---: |
| GOLD_CLEARLY_RIGHT (genuine error) | 9 | 6 | **15** | **52%** |
| BOTH_DEFENSIBLE (IAA-0.47 ambiguity) | 4 | 5 | **9** | **31%** |
| MODEL_DEFENSIBLE (gold convention friction) | 2 | 3 | **5** | **17%** |

Clinical-utility cost of forcing the model to match gold: on precision, **9/15 over-calls are
NO-LOSS** (the suppressed fact was noise) and only **2/15 LOSE** real information; on recall, **6/14
misses are GAIN**, 5/14 REDUNDANT (a band stacked on a rate already emitted), 3/14 NEUTRAL.

## 7. The decomposition — what is fixable vs irreducible

The 29 errors split into three mechanisms, and only the last is irreducible:

1. **Representation defect — fixable (the bulk of the 52% genuine-error bucket).**
   - *Direction-blindness.* The model has no way to say Increased/Decreased and defaults to `Same`,
     so it stamps `Same` on clear deteriorations (EA0109 "more frequent", EA0151 cluster, EA0186
     recurrence) and recovers direction in 0/12 agreements. A five-way `kind` matching the gold FC
     vocab removes this.
   - *No seizure-adjacency.* 6/15 over-calls lift `Same` from **medication** language ("dose
     unchanged", "medications should remain the same") or unrelated tokens (SUDEP "rare", a diagnosis
     header). A "change lexeme must attach to a seizure term" rule removes these.
2. **Lexical recall gap — fixable.** 12/14 misses (and 11/13 agreements) have an explicit band/change
   word adjacent to a seizure term. A recall-additive band-lexeme whitelist recovers them — exactly
   what the hybrid's `deterministic/rules/change.py` does and what Phase 3b's +18 facts demonstrated.
   (~5 of these are clinically redundant with a rate the model already emitted; recovering them lifts
   the score but adds little clinical information.)
3. **Genuine IAA-0.47 ambiguity — irreducible (the 31% BOTH_DEFENSIBLE).** "well controlled" =
   seizure-free or Infrequent? a Frequent band on top of a cluster rate — one fact or two? "best it's
   ever been" — a change or just a steady good rate? These are the calls two human annotators split on,
   and no model or rule can be "right" because gold itself is a coin-flip here.

**Why two different LLMs plateaued at the same 0.47:** not because the boundary is intrinsically
unlearnable, but because **both runs inherited the same representation defect** — a direction-blind
schema, a `Same` default, no seizure-adjacency, and letter-level feedback. The hybrid reaches
0.85R/1.00P precisely by fixing all three (direction-mapped whitelist + seizure-adjacency +
recall-additive extraction); its 1.00 precision is partly genuine discipline and partly in-sample
fitting to this gold (the whitelist was tuned against it), so on held-out data it too would settle
toward the IAA ceiling on the ambiguous slice.

## 8. Does optimising toward gold trade away clinical usefulness?

Mostly **no on precision, partly yes on recall, and yes at the metric level**:

- **Precision:** the over-calls are 60% genuine noise (default-`Same` misattributing medication
  language, flattening real deteriorations). Only 2/15 are useful information gold dropped. Suppressing
  the model's `Same`-spam to match gold costs almost no clinical information. The model here is *worse*
  than the disciplined hybrid, not a nuanced expert being penalised.
- **Recall:** ~36% of misses are gold double-tagging a qualitative band on top of a numeric rate it
  already records; the model emitting one fact per type is arguably the cleaner clinical representation
  and gold's redundancy is the artefact. But ~43% are genuine misses of real information (an
  unrecorded worsening, a whole missed seizure type).
- **Metric level:** the `changed` class is (a) the second-worst-agreed construct in the corpus (IAA
  0.47) and (b) **mis-operationalised** — the metric scores presence-of-a-band-token, not direction.
  Optimising hard on it pushes toward matching a noisy, direction-stripped flag while the genuinely
  actionable signal (Increased vs Decreased) sits unmodelled and unscored. That is a poor optimisation
  target — not because the model is superior, but because the target measures the wrong thing.

## 9. Corrections to prior conclusions

- **Phase 4 ("not a learnable boundary; curated-precision territory")** — over-stated. ~52% of the
  errors are genuine but trace to a fixable representation defect, not a curated-convention wall; only
  ~31% is the irreducible IAA slice. The Phase-4 forensic ("9/16 over-calls are active-rate-vs-changed
  convention") was reading the *ambiguity slice* and generalising it to the whole class.
- **The interactive "the label is underdetermined / two LLMs can't do it because it's irreducible"** —
  over-stated for the same reason. The irreducible part is real but a minority; the dominant cause is
  a shared schema defect both runs had.
- This is the same pattern as the rest of the workstream: a declared ceiling dissolved on inspection
  into an unwired/mis-specified component (here: direction never modelled, direction never scored)
  plus a smaller genuine floor.

## 10. Recommended next experiment

Test the representation fix directly, on the clinically meaningful signal:

- **Direction-aware SF schema:** replace `kind=changed` with a five-way `kind`/direction matching the
  gold FC vocab (`increased/decreased/frequent/infrequent/same`), so the model emits direction instead
  of the adapter defaulting `Same`.
- **Seizure-adjacency discipline** in the prompt/feedback: a change lexeme only counts when it attaches
  to a seizure term, not a medication or diagnosis token.
- **Direction-sensitive metric:** score the FC direction (not just `changed` presence), so the
  optimiser is rewarded for the actionable distinction and the 0/12 direction-recovery failure becomes
  visible. Report it alongside `state_profile`/`clinical_headline`.

This isolates whether the LLM-only route can reach the hybrid's 0.85R/1.00P on *direction*, which is
the part of seizure frequency a clinician actually acts on — and which the current benchmark and
schema both throw away.

## 11. Artifacts

- Substrate (full letter + gold/pred SF + lexeme scan, one md per letter):
  `experiments/exectv2_sf_changed_class_substrate.py` (regenerable from `gepa.data.load_dev_letters`
  + the P2 run jsonl; writes per-letter md + `_index.json` to an output dir).
- Quantitative skeleton (adjacency lexeme scan + FC composition):
  `experiments/exectv2_sf_changed_class_quant.py` (zero-LLM, prints the §4 / §6 numbers).
- Per-row clinical adjudication: five parallel sub-agent passes over FN/FP/TP batches (this report).
- Source numbers: `exectv2_sf_verify_error_analysis.py` (the 74-error decomposition this refines);
  paper Table 1 IAA from `data/ExECTv2 (2025)/Annotation of Epilepsy Clinic Letters for NLP (Fonferko-Shadrach 2024).pdf`.
- Prior context: `exectv2_sf_verify_error_analysis_2026-06-29.md`, plan
  `docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md` §6c/Phase 4–5.
