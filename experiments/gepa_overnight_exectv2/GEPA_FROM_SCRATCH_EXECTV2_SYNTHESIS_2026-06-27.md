# DSPy-native GEPA from-scratch on ExECTv2 de-dup facts — synthesis (2026-06-27)

Question driving the work (operator): *the Gan GEPA-from-scratch was a success;
repeat it for ExECTv2 — the ultimate goal is simplification, the ideal goal is
better performance with a single prompt.*

Target surface: the 4-family de-duplicated `clinical_headline` (clinical-recovery)
F1 — Diagnosis=`concept_negation`, SeizureFrequency/Investigations/Prescription=
`clinical_headline` — the designated headline per plan 13 / decision 0027. This is
the exact surface plan 13 chased *by hand* and where it plateaued.

## TL;DR

- **The "ideal goal" was not met.** From-scratch GEPA on a single prompt reached
  **~0.63 clinical_headline F1 on dev140** (mini 0.628, deepseek-reasoner 0.636),
  which is **below** the hand-tuned single-prompt plateau (**0.710**, plan 13) and
  far below the **v08 hybrid (0.9155)**.
- **GEPA barely beat its own lean seed.** The untuned 121-token seed already scores
  **0.619** on dev140; ~940 metric calls of optimization bought only **+0.01 to
  +0.02** F1, entirely in Prescription/Investigations. **Diagnosis (~0.45) and
  SeizureFrequency (~0.52) did not move** — the same two families that cap every
  prior result.
- **The length-penalty mechanism replicated the Gan finding cleanly.** With the
  penalty ON the evolved instruction is ~555–590 tokens; with it OFF it bloats to
  **1930 tokens (3.3×)** for **no accuracy gain** (0.636 vs 0.628 — within
  seed-level noise). So the penalty buys a 3× shorter prompt for free. That is the
  one unambiguous "simplification" win.
- **Net:** on ExECTv2, automated prompt optimization is *not* a path past the
  Diagnosis/SF ceiling. This triply confirms (hand-tuning, penalized GEPA,
  unconstrained GEPA all plateau there) that the gap is a prediction-bearing
  structural limit, not a prompt-wording deficiency.

## Results (dev140, canonical clinical_headline)

| Config | headline F1 | instr tok | Dx | SF | Rx | Inv | strict | wall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Seed (untuned, lean)** | **0.6188** | 121 | 0.453 | 0.548 | 0.761 | 0.781 | 0.130 | — |
| GEPA mini (penalized) | 0.6283 | 590 | 0.456 | 0.539 | 0.815 | 0.792 | 0.123 | 34 min |
| GEPA deepseek-reasoner | 0.6363 | 555 | 0.435 | 0.524 | 0.892 | 0.825 | 0.136 | 71 min |
| GEPA mini (no length penalty) | 0.6363 | **1930** | 0.454 | 0.572 | 0.839 | 0.777 | 0.129 | 27 min |
| *hand-tuned single prompt (plan 13)* | *0.710* | — | *0.672* | *0.558* | *0.814* | *0.832* | *0.13* | — |
| *v08 hybrid (multi-component)* | *0.9155* | — | *0.909* | *0.905* | *0.936* | *0.913* | *~0.37* | — |

Artifacts: `experiments/exectv2_gepa_from_scratch_dedup_{gpt41mini,deepseek_reasoner,gpt41mini_nolengthpenalty}_20260627.{json,md,jsonl,instruction.txt}`.

Caveat: the full-dev headline is mildly optimistic (the 50-letter valset GEPA
selected on is a subset of the 140-letter eval). It still lands below the
hand-tuned 0.710 — so the optimistic number loses, which only strengthens the
negative conclusion. Development surface only; `test` (60) never touched.

## Why ExECTv2 differs from Gan (the interesting contrast)

On Gan, from-scratch GEPA *matched/edged* the hand-tuned prompt because the
hand-tuned advantage was ~25 rules GEPA could rediscover from a lean seed under a
length penalty. On ExECTv2 the hand-tuned de-dup prompt carried richer scaffolding
(worked examples + decision tables) that encode the Diagnosis-enumeration and
SF-state distinctions; from a lean seed GEPA did **not** rediscover that signal —
the biggest shortfall is Diagnosis (GEPA ~0.45 vs hand-tuned ~0.67). Crucially the
**unconstrained** ablation (1930 tokens, penalty off) also failed to close it
(Dx 0.454), so this is not the length penalty starving useful content — single-
instruction evolution simply doesn't recover the per-family decision structure the
hybrid (and, partially, the hand prompt) supply with dedicated components.

## What the length penalty mechanism is (ported from Gan)

`metric.py` returns `dspy.Prediction(score, feedback)`:
- `score = per-letter clinical_headline F1 − length_penalty`, clamped to [0,1].
- `length_penalty` over soft budgets: instruction 600 tok, demos 800, output 2000
  (β=0.25/0.25, α=0.05; capped 0.6). Output α is small/budget generous because
  ExECTv2 output length is data-driven (number of facts), not a bloat surface.
- `feedback` names the Diagnosis/SF gap families + per-family P/R/F1 + live token
  count vs budget, so reflection is told in words to stay concise.
- The program stamps `instruction_tokens`/`demo_tokens` onto the prediction so the
  penalty enters GEPA's *selection* score (the Gan bug-fix). Confirmed working: the
  1930-vs-590-token gap between ablation and penalized arms is the direct evidence,
  and during the run GEPA was repeatedly seen skipping longer proposals that did not
  beat a leaner candidate.

Quality reuses the existing de-dup stack unchanged: `parse_dedup_clinical_facts_json`
→ evidence-gated, attribution-clean `to_predicted_letter_from_dedup_facts` → the
four canonical `clinical_headline` scorers. The GEPA number is computed exactly as
the dedup runner's canonical headline overall, just per-letter for a dense gradient.

## Protocol & provenance

- ExECTv2 split has only dev(140)/test(60); dev is sub-split deterministically
  (seed 20260627) into trainset 90 (optimizer-only) + valset 50 (Pareto). `test`
  never touched. Final eval on full dev.
- Task models: `openai/gpt-4.1-mini`, `deepseek/deepseek-reasoner`. Reflection
  (teacher) = `deepseek/deepseek-reasoner`. GEPA `auto="medium"` (~940 metric
  calls), temperature 0 task, `use_cloudpickle` checkpoints.
- Registration was **skipped** for all arms by the known malformed
  `experiments/registry.jsonl:63` (`primary_metrics` nested dict) — same blocker the
  Gan synthesis flagged; artifacts are written regardless. Fix line 63 to re-enable.

## Follow-up: per-family multi-signature GEPA (refutes the decomposition hypothesis)

Hypothesis: a single instruction can't carry the per-family decision structure, so
give each family its own evolvable instruction (the hybrid's per-component shape).
Built `gepa/program_multifamily.py` — four `dspy.Predict` (diagnosis,
seizure_frequency, prescription, investigation), each instruction evolved
independently by GEPA; `forward` merges their facts so metric/adapter/scorers are
reused unchanged. mini, auto="medium" (GEPA auto-scaled to ~2705 metric calls = 4
predictors × budget; ~10.8k mini calls, finished in ~45 min wall via 12-thread
parallelism).

**Result: no improvement.** dev140 clinical_headline **0.631** vs monolith 0.628 —
statistically identical. The two gap families did **not** move: **Diagnosis 0.426**
(monolith 0.456), **SeizureFrequency 0.523** (monolith 0.539); the only gain was
Prescription (0.891). And this was not under-investment: GEPA grew an **829-token
Diagnosis** and **603-token SeizureFrequency** instruction (1902 tok total) and
still got nothing on those families.

| Config | overall | Dx | SF | Rx | Inv |
| --- | ---: | ---: | ---: | ---: | ---: |
| GEPA monolith (mini) | 0.628 | 0.456 | 0.539 | 0.815 | 0.792 |
| **GEPA multi-family (mini)** | **0.631** | **0.426** | **0.523** | **0.891** | **0.800** |
| hand-tuned single prompt | 0.710 | 0.672 | 0.558 | 0.814 | 0.832 |
| v08 hybrid | 0.9155 | 0.909 | 0.905 | 0.936 | 0.913 |

**Sharpened conclusion.** The Diagnosis/SeizureFrequency clinical_headline ceiling is
not reachable by prompt optimization in *any* shape tested — monolith or per-family,
hand-tuned or GEPA-evolved, penalized or unconstrained. What the v08 hybrid does for
those families (0.91 vs ~0.45/0.52) is the actual multi-stage machinery — diagnosis
enumeration, candidate adjudication, verifier filtering — not per-family prompt
scaffolding. The gap is prediction-bearing structural work, exactly as plan 13
posited; decomposing the *prompt* does not substitute for decomposing the *pipeline*.

Artifacts: `experiments/exectv2_gepa_multifamily_dedup_gpt41mini_20260627.{json,md,jsonl,instruction.txt}`.
Implementation note: a transient Windows checkpoint-write `OSError [Errno 22]` on the
rapidly-rewritten `gepa_state.bin` crashed the first attempt at 65%; the run is
checkpoint-resumable, so a resume-retry loop completed it on the 2nd attempt with no
wasted spend.

## Follow-ups for the operator

1. **Accept the negative result.** "Better performance with a single prompt" on the
   ExECTv2 de-dup surface is not reachable by GEPA from scratch; the Dx/SF ceiling
   is structural. The reportable wins are (a) the length-penalty simplification
   mechanism (3× shorter prompt, no loss) and (b) corroboration of plan 13's
   plateau by a second, automated method.
2. **If pursuing further:** the natural next experiment is GEPA over a *small
   multi-signature* program (per-family predictors for Diagnosis + SeizureFrequency,
   the two gap families) rather than one instruction — i.e. let GEPA evolve the
   hybrid's per-family scaffolding, not replace it with a monolith.
3. **Seed-as-baseline is informative on its own:** the 121-token lean seed already
   reaches 0.619, ~87% of the hand-tuned 0.710 at zero optimization — most of the
   single-prompt headline is "free," and neither hand-tuning nor GEPA closes the
   remaining gap.
