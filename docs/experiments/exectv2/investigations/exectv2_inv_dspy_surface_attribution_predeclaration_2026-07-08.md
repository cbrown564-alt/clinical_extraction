# Predeclaration — Investigations dspy surface attribution (pathway #3)

Date: 2026-07-08. Owner: ExECTv2 workstream.
Hypothesis: `inv_dspy_surface_attribution_2026-07-08` (PENDING → CONFIRMED).
Umbrella: PROJECT_STATUS.md `Next`, 2026-07-08 queue, **pathway #3** — the open
follow-up to the Investigations no-model oracle
(`docs/experiments/exectv2/investigations/exectv2_investigations_no_model_oracle_2026-07-06.md`).

## Purpose (the question)

The 07-06 Inv no-model oracle found our deterministic-only Inv extractor scores
**0.5116 dev140 / 0.4858 full-200** vs the cited hybrid **0.9132 / 0.9213** — a
−0.40 / −0.44 gap, the contribution-bearing family. The oracle doc noted dspy
reports **90.4–96.7%** near-ceiling Inv performance and flagged that this *"does
NOT transfer to our deterministic extractor,"* but **deferred the reason** to a
sibling-repo read it did not perform:

> *"dspy's strong Inv number likely includes their adjudication/lens layer, not
> just the bare extractor. … (Label the dspy number honestly as a sibling-repo
> figure not re-verified in this checkout.)"*

That "likely" is the unmeasured assumption this probe closes. The fork in the
road, as stated in PROJECT_STATUS.md pathway #3:

- **(a) Annotation-derived** — dspy's 90.4% corresponds to a
  `gold_as_prediction`-style oracle (predictions reconstructed from gold). If so,
  the Inv comparison is apples-to-oranges and our −0.40 is the honest "LLM
  contributes here" number, *but* the comparison itself is invalid.
- **(b) Extractor-derived** — dspy's 90.4% comes from a real extractor (LLM /
  DSPy program / rules) producing predictions scored against gold. If so, the Inv
  finding is the single place our architecture's LLM lane is doing irreplaceable
  work, and the manuscript should foreground it — *and* the comparison is valid.

The two outcomes diverge sharply on what the manuscript should claim, so the
distinction is worth measuring rather than assuming.

## What "surface" means here

Two scoring surfaces, both already built by the 07-06 Inv oracle driver, frame
the comparison:

| Surface | What it tests | dspy analogue |
| --- | --- | --- |
| `gold_as_prediction` | Scorer integrity: gold copied through the pipeline | An oracle / ceiling probe that injects gold |
| `deterministic_only` | Our no-model extraction ceiling (`_extract_investigations` alone) | The analogue of dspy's *bare extractor*, if dspy reports one |
| cited hybrid (0.9132) | Our full v08 Inv lane (deterministic + lens + verifier + LLM) | The analogue of dspy's number *if* it includes adjudication |

The question is **which of these dspy's 90.4% corresponds to.** This is not a
question we can answer by running our own code — it requires reading dspy's
evaluation harness. The probe is therefore a **cross-codebase read**, not a
costed experiment: zero LLM calls, zero scorer runs beyond the already-confirmed
07-06 numbers.

## Frozen decision criteria (the verdict bands)

The verdict turns on three independently-checkable properties of the dspy
Investigations evaluation, read from the sibling repo at
`C:\Users\cbrow\Code\dspy-extraction` (and corroborated against
`dissertation-recursive`):

1. **Does dspy inject gold as prediction?** Search for any `gold_as_prediction`,
   oracle, copy-gold, or from-gold construction on the *investigation* family.
2. **Does a real extractor emit the scored predictions?** Confirm the prediction
   path is a DSPy/LLM `OutputField` or rules module producing novel values, scored
   against annotation-derived gold.
3. **Is there an adjudication layer between extractor and score?** Identify any
   lens / verifier / bridge / CUI projection / de-dup against gold / learned
   arbiter on the Inv path, and determine whether it reads gold.

| Finding | Verdict |
| --- | --- |
| Gold injected as prediction (oracle) OR no real FP/FN in the run | **(a) ANNOTATION-DERIVED** — comparison invalid; manuscript says so |
| Real extractor + no adjudication layer (bare extractor scored) | **(b) EXTRACTOR-DERIVED, BARE** — dspy's extractor is genuinely near-ceiling; our −0.40 gap is a deterministic-extractor gap, not an architecture gap; the LLM lane comparison is valid and Inv should be foregrounded |
| Real extractor + adjudication layer that reads gold | **(b) EXTRACTOR-DERIVED, ADJUDICATED** — comparison is to our hybrid, not our deterministic extractor; our −0.40 is the deterministic-vs-adjudicated gap and the manuscript must state the surface |
| Real extractor + post-processing that reads note-text only (not gold) | **(b) EXTRACTOR-DERIVED, LIGHT BRIDGE** — the bridge is a precision guard, not an oracle; the near-ceiling is attributable to the extractor + a conservative note-text repair; comparison to our hybrid is valid with a caveat about the bridge |

The fourth band is the sharpest and the one the reading tests for.

## Scope freeze

- **No new code in this repo.** The 07-06 Inv oracle driver and its JSON are
  reused unchanged; the numbers are re-confirmed, not regenerated.
- **No LLM calls.** A cross-codebase read of the sibling repo + a re-confirmation
  run of the deterministic replay.
- **No gold, scorer, metric, or production-wiring change.** Read-only.
- **Split discipline unchanged.** dev140 + full-200 aggregate-only; the dspy
  numbers are taken from their stored S5 runs (validation + test holdout) and are
  not re-run.

## Provenance / artifacts

- This repo: `experiments/exectv2_investigations_no_model_oracle_2026-07-06.py`
  (the two-surface driver) + its JSON (re-confirmed 2026-07-08).
- Sibling repo: `C:\Users\cbrow\Code\dspy-extraction` — the E12 ceiling doc, the
  S5 scorer, the S2/S4 Inv recovery bridges, the stored `metrics.json` runs.
- Corroborating repo: `C:\Users\cbrow\Code\dissertation-recursive` — its
  per-modality Inv accuracy (independent codebase, same conclusion).
- Results doc:
  `docs/experiments/exectv2/investigations/exectv2_inv_dspy_surface_attribution_results_2026-07-08.md`.
- Registry entry: `inv_dspy_surface_attribution_2026-07-08`.
