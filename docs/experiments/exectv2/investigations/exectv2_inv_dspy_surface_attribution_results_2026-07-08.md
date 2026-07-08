# Investigations dspy surface attribution — results (pathway #3)

Date: 2026-07-08. Owner: ExECTv2 workstream.
Hypothesis: `inv_dspy_surface_attribution_2026-07-08` — **CONFIRMED: dspy's
90.4% is extractor-derived (category b), not annotation-derived.** It comes from
a single-call LLM extractor + a thin note-text-only bridge, with no gold
adjudication layer. This closes the "likely" deferred by the 07-06 Inv oracle
doc and validates the Inv cross-family comparison.
Predeclaration:
`docs/experiments/exectv2/investigations/exectv2_inv_dspy_surface_attribution_predeclaration_2026-07-08.md`.
Cost: **zero LLM calls; zero scorer runs** (the 07-06 numbers were re-confirmed;
the rest is a cross-codebase read).

## Headline

**dspy's near-ceiling Investigations number is extractor-derived, and its
extractor is a single-call LLM program — not an oracle, and not an
adjudication stack.** The 07-06 oracle doc's deferred speculation ("likely
includes their adjudication/lens layer") is **refuted**: dspy's 90.4% test /
96.7% validation (GPT-4.1-mini) comes from a DSPy `OutputField` prediction
scored by exact set-F1 against annotation-derived gold, with only a conservative
note-text bridge that *removes* unsupported labels and never reads gold.

This has two consequences for our manuscript, both sharp:

1. **The Inv cross-family comparison is valid.** dspy's number and our hybrid
   number (0.9132 dev / 0.9213 full) are commensurable: both are
   extractor-derived set-F1 on the same corpus. Our −0.40 deterministic-vs-hybrid
   gap is **not** an artifact of comparing an oracle to an extractor — it is the
   real, measured contribution of our hybrid lane's lenses + LLM over our bare
   deterministic extractor.
2. **Our Inv story is the contribution-bearing family and should be foregrounded
   — but with one honest caveat.** dspy reaches ~0.90 with a *single LLM call*;
   our hybrid reaches 0.91 with deterministic extractor + lens + verifier + LLM
   arbitration. The architectures differ: dspy front-loads the reasoning into one
   prompt; we decompose it across deterministic + LLM stages. The manuscript
   must state both numbers and the architectural difference, not claim our hybrid
   "beats" a single-call system on Inv by the raw gap (the single-call dspy
   number is already near-ceiling).

## The verdict, by the frozen criteria

The predeclaration named three independently-checkable properties. All three
verified against the sibling repo:

### 1. Does dspy inject gold as prediction? — NO

There is **no `gold_as_prediction`, oracle, or copy-gold construction for the
investigation family** anywhere in `dspy-extraction/src`. Oracle / ceiling
machinery exists in the codebase but is confined to **seizure-frequency**
(`exect_frequency_candidate_selection_probe.py`'s
`_oracle_prediction_set_from_e1_payload` / `"candidate_constrained_oracle"`,
explicitly labeled "uses gold labels" and "not deployable") and **medication**
(`exect_medication_current_rx_ceiling_probe.py`). Investigation has none.

**Decisive evidence:** the stored runs that produce 90.4% carry genuine FP/FN
errors. A gold-as-prediction oracle produces zero mismatches by construction.
The GPT-4.1-mini test holdout run
(`test_holdout_exect_s5_..._20260527T055059Z/metrics.json`) reports
`field_f1.investigation = 0.9041` with **TP=33 / FP=4 / FN=3** — real errors,
documented in the E12 ceiling doc (EA0102: `eeg abnormal` predicted vs
`eeg normal` gold, a clinical-negation miss; EA0015: gold omission → model FP).
These are extractor errors, not oracle artifacts.

### 2. Does a real extractor emit the scored predictions? — YES

`dspy-extraction/src/clinical_extraction/programs/exect_s2.py` declares the DSPy
signature with `investigation: list[str] = dspy.OutputField(...)` (lines 276,
315, 350). In `_predict_s2_record` (line 528), the LM is actually called
(`pred = module(note_text=record.text)`) and the resulting `pred.investigation`
list flows through the bridge into `ExtractedValue` entries that are scored.

The scorer
(`dspy-extraction/src/clinical_extraction/evaluation/exect.py`, S5 mode
`exect_s5_core_field_family_deterministic_v1`) computes standard micro-F1 over
the `investigation` family: gold values from `gold.investigations`, predicted
values from `prediction.values` normalized via
`normalize_investigation_phrase` to `"{modality} {result}"` strings, TP/FP/FN by
set membership. Nothing injects gold into the prediction slot.

### 3. Is there an adjudication layer between extractor and score? — A thin
   note-text-only bridge; NO gold adjudication

Two bridge functions sit between the raw LM output and the scored prediction:

- **S2 bridge** — `exect_s2.py::_recover_s2_investigation_raw_values` (line 1016):
  drops ECG modality outputs and removes `"{modality} unknown"` labels **unless
  the note text actually contains the word "unknown"** (a substring check
  against `record.text`, lines 1036–1044).
- **S4/S5 bridge** — `investigation_primitives.py::recover_exect_s4_investigation_benchmark_values`
  (line 20): blocks "unknown" labels when the note shows the scan is merely
  *planned* ("will arrange", "plan to"), keeping "unknown" only when the note
  literally says results are unavailable.

**Both bridges read only `record.text` (the source note), never
`gold.investigations`.** They are conservative precision guards — they only
*remove* unsupported labels; they never inject, copy, or look up gold. There is
no CUI projection, no learned verifier, no gold de-dup, and no lens on the
investigation path. (The only `_dedupe` in the path is ordinary same-string
dedup.)

This lands in the predeclaration's **fourth band: extractor-derived, light
bridge** — the sharpest outcome.

## The numbers, side by side

| System | Surface | dev140 / validation F1 | full-200 / test F1 | What it is |
| --- | --- | ---: | ---: | --- |
| **Our deterministic-only** | `_extract_investigations` alone | **0.5116** (88/120/48) | **0.4858** (111/163/72) | Our no-model extraction ceiling |
| **Our hybrid (cited)** | v08 Inv lane | **0.9132** (121/8/15) | **0.9213** (164/9/19) | Deterministic + lens + verifier + LLM |
| **dspy GPT-4.1-mini** | single-call LLM + note-text bridge | **0.967** (val, 29/1/1) | **0.904** (test, 33/4/3) | One DSPy call + conservative bridge |
| **dspy Qwen-35B** | single-call LLM + note-text bridge | **0.949** (val, 28/1/2) | **0.972** (test, 35/1/1) | Same architecture, different model |
| **Our `gold_as_prediction`** | gold copied through | 1.0000 | 1.0000 | Scorer integrity ceiling (not extraction) |

> **Split labels differ.** dspy's "validation" / "test" (holdout) correspond to
> our dev140 / full-200-test surfaces in role (development vs frozen holdout),
> but the literal splits are not identical (dspy uses its own ExECT split). The
> comparison is **directionally valid** (both are extractor-derived set-F1 on the
> same ExECTv2 corpus), not numerically identical. The manuscript must label
> dspy's numbers as sibling-repo figures from a different split, re-verified as
> extractor-derived here but not re-run on our split.

The corroborating `dissertation-recursive` repo independently arrives at
near-ceiling Inv numbers (EEG 0.90–0.975, MRI 0.825–0.90 across systems) via a
*different* metric (per-modality accuracy, not set-F1) and a *different*
extractor path, with only a keyword normalizer (`canonical_investigation_result`,
no gold). Two independent codebases, same conclusion: a real LLM extractor
reaches ~0.90+ on Inv without any gold adjudication.

## What this revises (vs the 07-06 oracle doc)

The 07-06 doc stated, as a deferred speculation:

> *"dspy's strong Inv number likely includes their adjudication/lens layer, not
> just the bare extractor. Our analogue of 'dspy's near-ceiling' is the hybrid
> lane (0.9132), not the deterministic extractor."*

This probe **refines** that statement:

- **Refuted:** the "likely includes their adjudication/lens layer" clause.
  dspy's number has no adjudication layer; it is a single-call extractor + a
  note-text precision guard.
- **Confirmed and sharpened:** the "our analogue is the hybrid lane, not the
  deterministic extractor" clause. The reason is now known — it is **not** that
  dspy hides an adjudication stack; it is that **dspy front-loads the clinical
  reasoning into a single LLM call**, whereas our architecture decomposes it
  across deterministic extractor + lens + verifier + LLM arbitration. The two
  architectures reach the same ceiling (≈0.90–0.92) by different routes. Our
  deterministic extractor alone (0.51) is the bottom layer of a decomposed
  pipeline; dspy's single call does in one step what our full stack does across
  several.

## Implications for the manuscript (feeds pathway #4)

1. **The Inv attribution row is now unambiguous.** Investigations is
   lens+LLM-owned: our deterministic extractor alone is 0.51; our hybrid
   (deterministic + lens + LLM) is 0.91; dspy's single-call LLM is ~0.90. The
   deterministic layer is a recall scaffold (88 of 121 hybrid TP), not a
   solution. This is the contribution-bearing family — the place our
   architecture's LLM lane does irreplaceable work — and the comparison to dspy
   is valid.
2. **State the architectural difference, not just the gap.** The honest framing
   is: both architectures reach near-ceiling on Inv; dspy does it in one LLM
   call, ours does it across a deterministic + LLM decomposition. Our hybrid's
   value on Inv is **not** "beats single-call by X" (the single-call is already
   near-ceiling); it is that the decomposition lets the deterministic layer
   carry Prescription and SF to their ceilings *without* an LLM call, while
   reserving the LLM for Inv where it is genuinely needed. The cross-family
   attribution picture (Rx/SF deterministic-owned, Inv LLM-owned) is the
   contribution thesis, and Inv being the LLM-bearing family is now
   cross-validated against the sibling repo.
3. **The `gold_as_prediction` ceiling (1.0000) is ours, not dspy's.** We built
   the oracle surface to test scorer integrity; dspy did not build one for Inv.
   Our 1.0000 confirms our scorer preserves gold; it is not a competing Inv
   number. Do not confuse the two in the manuscript.
4. **Label dspy's numbers as sibling-repo, different-split, extractor-derived.**
   The literal splits differ; the numbers are re-verified here as
   extractor-derived (not oracle) but not re-run on our split.

## Limitations and honest caveats

- **The splits are not identical.** dspy's validation/test and our dev140/full-200
  are both ExECTv2 development/holdout pairs, but the literal letter sets differ
  (dspy uses its own split manifest). The comparison is directional
  (extractor-derived vs extractor-derived), not numerically exact.
- **dspy's bridge is not zero.** The note-text-only bridge removes some
  unsupported "unknown" labels and ECG outputs, which is a small precision
  effect. It is conservative (removes only; never injects) and reads no gold,
  so it does not change the extractor-derived verdict — but it means dspy's
  number is "extractor + light bridge," not "bare extractor." Our hybrid's
  lens+verifier stack is a heavier post-processing layer; the architectural
  difference is real.
- **This probe cannot separate lens from LLM within our hybrid lane.** The
  07-06 doc's caveat stands: "deterministic ≪ hybrid" is measured; the
  within-hybrid lens-vs-LLM split would need a lens-only ablation (out of scope
  here).
- **`dissertation-recursive` uses a different metric** (per-modality accuracy,
  not set-F1). Its near-ceiling Inv numbers corroborate the direction but are
  not directly commensurable with either our F1 or dspy's F1.

## What this is NOT

- **Not a re-run of dspy's system.** dspy's numbers are taken from its stored S5
  runs and its E12 ceiling doc; we did not re-execute dspy's pipeline. We read
  its scorer, its bridge, and its stored metrics to classify the surface.
- **Not a claim that our hybrid "beats" dspy on Inv.** Both reach ~0.90–0.92;
  the architectural difference (decomposed vs single-call) is the finding, not a
  ranking.
- **Not a gold or scorer change.** Read-only cross-codebase read + re-confirmed
  07-06 numbers; nothing in this repo's gold, scorer, or production wiring moved.

## Artifacts / provenance

- This repo (re-confirmed 2026-07-08):
  `experiments/exectv2_investigations_no_model_oracle_2026-07-06.py` + `.json`
  (dev140: deterministic_only 0.5116, gold_as_prediction 1.0000; full-200:
  deterministic_only 0.4858, gold_as_prediction 1.0000).
- Sibling repo (read, not modified):
  - E12 ceiling doc:
    `dspy-extraction/docs/experiments/exect/exect_investigation_isolated_ceiling_e12_20260529.md`
    (the 90.4–96.7% source).
  - S5 scorer: `dspy-extraction/src/clinical_extraction/evaluation/exect.py`
    (`exect_s5_core_field_family_deterministic_v1`).
  - S2 bridge: `dspy-extraction/src/clinical_extraction/programs/exect_s2.py`
    (`_recover_s2_investigation_raw_values`, line 1016; reads `note_text` only).
  - S4/S5 bridge:
    `dspy-extraction/src/clinical_extraction/exect/investigation_primitives.py`
    (`recover_exect_s4_investigation_benchmark_values`, line 20; reads
    `note_text` only).
  - Stored metrics: GPT-4.1-mini test holdout
    `runs/test_holdout_exect_s5_..._20260527T055059Z/metrics.json`
    (`field_f1.investigation = 0.9041`, TP 33 / FP 4 / FN 3).
- Corroborating repo: `dissertation-recursive/src/core/raw_output_scoring.py`
  (per-modality Inv accuracy; independent codebase, same direction).
- Comparison anchors (cited hybrid Inv):
  `docs/experiments/exectv2/investigations/exectv2_inv_llm_vs_hybrid_comparator_2026-07-03.md`.
- Umbrella: PROJECT_STATUS.md `Next`, 2026-07-08 queue, pathway #3.
