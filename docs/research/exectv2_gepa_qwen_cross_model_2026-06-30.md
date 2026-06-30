# Cross-model GEPA on ExECTv2 de-dup `clinical_headline` — Qwen 3.6 35B (local)

Status: **CLOSED (bounded negative).** Date: 2026-06-30.
Owner: ExECTv2 GEPA workstream.

Companions:
- `docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md` (the plateau this extends)
- `experiments/gepa_qwen_cross_model_exectv2.py` (the orchestrator), `experiments/gepa_overnight_exectv2/run_qwen_overnight.ps1` (overnight driver)

## 1. Question

Every single-pass GEPA result to date used **GPT-4.1-mini** as the task model (with a
deepseek-reasoner transfer arm); the local **Qwen 3.6 35B** was skipped for practicality.
This run closes that gap: replay the two *best* mini configurations — the H2 single-prompt
monolith (0.719) and the per-family 4-signature program (0.731) — with Qwen 3.6 35B as the
task model and deepseek-reasoner as the reflection model, changing **only** the task model
and the local-hardware knobs. Does a different single-pass base model move the plateau?

## 2. Result: Qwen lands *below* mini — and below its own hand-tuned baseline

| configuration | task model | dev140 headline F1 |
| --- | --- | ---: |
| hand-tuned single prompt (plan 13) | Qwen 3.6 35B | 0.694 |
| hand-tuned single prompt (plan 13) | GPT-4.1-mini | 0.710 |
| **GEPA single-prompt monolith** | **Qwen 3.6 35B** | **0.607** |
| **GEPA per-family (4 instr)** | **Qwen 3.6 35B** | **0.654** |
| GEPA single-prompt monolith | GPT-4.1-mini | 0.719 |
| GEPA per-family (4 instr) | GPT-4.1-mini | 0.731 |
| v08 multi-stage hybrid | GPT-4.1-mini | 0.9155 |

Two findings:

1. **Qwen + GEPA underperforms mini + GEPA by ~0.08–0.11** on both program shapes
   (single 0.607 vs 0.719; multi 0.654 vs 0.731). The per-family > monolith ordering holds
   for Qwen too (0.654 > 0.607), as it did for mini.
2. **GEPA did not lift Qwen above its own hand-tuned plateau (0.694)** — both Qwen GEPA arms
   land *below* it. On mini, GEPA (0.719/0.731) *beat* hand-tuned (0.710). So the
   instruction-tuning lift that the H1+H2 fixes unlocked on mini does not reproduce on the
   weaker base model; here GEPA's length-penalized search settled on a lean 247-token
   monolith instruction (seed 121) that is *worse* than the hand-written prompt.

These are genuine model-quality numbers, not formatting artifacts: **0 unscorable letters**
on both arms (Qwen emitted valid JSON for all 140 letters).

## 3. Why — Diagnosis retrieval, not representation

The gap is upstream extraction quality, localized by evidence-presence recall (the fraction
of gold facts for which the program retrieved *any* overlapping-text prediction, keying aside):

| family | Qwen single F1 / ev-recall | Qwen multi F1 / ev-recall | mini GEPA ref |
| --- | ---: | ---: | ---: |
| Diagnosis | 0.530 / **0.395** | 0.553 / **0.378** | F1 0.66 |
| SeizureFrequency | 0.391 / 0.604 | 0.506 / 0.663 | F1 0.59 |
| Prescription | 0.759 / 0.806 | 0.730 / 0.835 | — |
| Investigations | 0.788 / 0.882 | 0.932 / 0.919 | — |
| **overall ev-recall** | **0.599** | **0.615** | 0.694 (hybrid 0.883) |

- **Diagnosis is the drag:** Qwen retrieves only ~38–40% of gold diagnosis evidence (vs
  mini's stronger Dx and the hybrid's 0.883 overall). Diagnosis F1 0.53–0.55 vs mini's 0.66.
- **SeizureFrequency** is also weaker (0.39/0.51 vs mini's 0.59) — consistent with the
  known SF gold-quality ceiling, just hit lower by a weaker producer.
- **Investigations / Prescription** are close to mini (Inv even 0.93 on the multi arm); the
  cross-model loss is concentrated in the two hard families (Dx, SF).
- The multi-family arm over-emits (1357 facts emitted, 796 scored, vs single's 863/844) yet
  still scores higher — more producers surface more, echoing the
  `exectv2_gepa_vs_hybrid_evidence_decomposition` "multi-lane extraction" mechanism.

## 4. Interpretation

This **reinforces, not overturns**, the plateau synthesis. The path to the hybrid's 0.9155
is **multi-stage architecture, not a different single-pass base model**: swapping in a smaller
local model makes the single-pass ceiling *worse* (~0.61–0.65), and the architectural gap is
*larger* for Qwen, not smaller. The cross-model arm was the last open lever in the
"is the gap reachable by a single model?" investigation; it is now closed negative across two
models (mini, Qwen) and every architecture/objective tried.

## 5. Provenance & method

- **Surface:** dev140 `clinical_headline` (Diagnosis = concept_negation), micro-averaged.
  GEPA trained on the deterministic optimizer-only dev sub-split; `test` never touched.
  Development-surface number, NOT paper-comparable; strict benchmark reported beside it
  (single 0.122, multi 0.132 — diagnostic only).
- **Config (both arms):** task `ollama_chat/qwen3.6:35b` (temp 0, max_tokens 6000), reflection
  `deepseek/deepseek-reasoner`, `reflection_minibatch_size=8` (H2 fix), H1 diff-feedback metric
  (default), `auto="medium"`. Local single-GPU: `num_threads=1`, `num_ctx=16384` (OOM-safe;
  dev letters max ~1071 tok so input never starved). Length penalty: single = default
  (instr 600 / out 2000); multi = instr 2000 / out 2000.
- **Budget realized:** single ~940 metric calls, 3.4 h; multi 7.7 h. Run end-to-end on the
  local 35B with **no OOM** (the Gan-run failure mode for this model).
- **Operational note:** the first launch (Bash `run_in_background` + a session `! ollama serve`)
  was reaped on Claude-session teardown ~17 min in. The run was relaunched under a Windows
  Scheduled Task wrapping a self-contained driver (ensures its own ollama, runs the resumable
  orchestrator) and completed unattended overnight. See the overnight-runs memory.
- **Registry:** registration into `experiments/registry.jsonl` had been silently failing since
  2026-06-12 — a malformed record (`evidence_grounded_by_grade` stored as a nested dict) broke
  `load_run_registry`, so `_register` skipped every exectv2 GEPA run. Fixed by flattening the 12
  affected records; the two Qwen runs and the two mini H2 comparators are now registered.
  (Separately, the whole-registry artifact validation still fails on ~dozens of June-17/18
  entries pointing to archived `.md` paths — pre-existing, left for a dedicated cleanup.)
