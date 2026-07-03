# Predeclaration — Inv LLM-vs-hybrid full-200 (frozen aggregate-only protocol)

Date: 2026-07-03. Owner: ExECTv2 workstream.
Hypothesis: `inv_llm_precision_vs_hybrid_inversion_2026-07-03` (PENDING).
dev140 results doc: `exectv2_inv_llm_vs_hybrid_comparator_2026-07-03.md`.
Driver: `scripts/run_exectv2_v08_inv_llm_vs_hybrid.py full200 --allow-non-dev140 --cache`.

## Why this predeclaration exists

The dev140 run (Phase A1) passed its gate and reproduced the predicted
inversion's first half: the hybrid Inv lane beats the LLM-tuned precision
extractor on dev140 (0.9132 vs 0.8949, Δ −0.0183). The LLM raised precision
(FP 8→6) but lost recall (FN 15→21) — the precision instruction dropped some
completed investigations the hybrid captures. The full-200 run is needed to
test the inversion's second half: does the LLM's contextual precision
judgment beat the hybrid on the broader test surface (where incidental /
planned investigation mentions are plausibly more prevalent)?

## dev140 result (the basis for the full-200 predeclaration)

| Producer (dev140 Inv `clinical_headline`, v08 assembly) | F1 | P | R | TP/FP/FN |
| --- | ---: | ---: | ---: | --- |
| **Hybrid Inv lane (baseline)** | **0.9132** | 0.9380 | 0.8897 | 121/8/15 |
| LLM-tuned (precision-completed-only) | 0.8949 | 0.9504 | 0.8456 | 115/6/21 |

Overall dev140: hybrid **0.9130** → treatment **0.9100** (Δ −0.0030).
Diagnosis/SF/Prescription byte-identical to baseline (clean isolation confirmed
— only the Inv producer was swapped, same-day same-scorer).

The dev140 loss is recall-driven (the precision probe over-dropped 6 completed
investigations: TP 121→115, FN 15→21). The safety clause did not fully prevent
the over-drop, mirroring the Rx probe #3 over-drop pattern that needed the
emit-if-unsure fix. Precision improved (FP 8→6).

## What the full-200 run will measure (aggregate-only)

Aggregate-only inspection per the standing protocol (no full-200 row
inspection). Two headlines:

1. **Inv `clinical_headline` F1** — does the LLM beat the hybrid on full-200?
2. **Overall `clinical_headline` F1** — the aggregate effect.

## Predeclared outcomes (the inversion test)

The inversion CONFIRMS only if the LLM-tuned Inv F1 > hybrid Inv F1 on
full-200. The mechanism would be: precision failures (incidental / planned /
non-neuro investigation mentions) are more prevalent on the 60 test letters
than on dev140, so the LLM's contextual completion judgment yields a larger
precision gain that outweighs its recall cost.

| Outcome | Verdict | Action |
| --- | --- | --- |
| LLM Inv F1 > hybrid on full-200 (and > the dev140 LLM 0.8949) | **Inversion CONFIRMED** | Write generalization synthesis doc; the split-dependent inversion generalizes from Rx to Inv |
| LLM Inv F1 ≤ hybrid on full-200 | **Inversion REFUTED** | The Rx inversion is Prescription-specific; document the negative cleanly |

## Cost and isolation

- ~60 fresh LLM calls (dev140's 140 are cached), gpt-4.1-mini temp 0.
- Same-day baseline+treatment isolation (P7 audit method): both arms read the
  same base manifest, same gold letters, same scorer; only the Inv producer
  artifact differs.
- The dev140 cached file (`exectv2_llm_inv_tuned_extractor_dev140_20260703.jsonl`)
  is reused unchanged for the first 140 letters; only letters 141–200 fire
  fresh calls.

## Honest caveats

- The dev140 loss (−0.0183) consumed 92% of the −0.02 gate budget. If the
  precision instruction's over-drop scales to full-200, the LLM could lose
  full-200 outright rather than win it — the inversion is plausible but not
  guaranteed.
- Full-200 overall F1 deltas within ~±0.005 should not be over-claimed
  (run-to-run variance band), consistent with the Rx comparator's disclosure.
- This is comparison evidence for the paper, not a promotion attempt — the v08
  architecture's hybrid Inv lane stays unless the LLM wins decisively AND the
  promotion is separately gated.
