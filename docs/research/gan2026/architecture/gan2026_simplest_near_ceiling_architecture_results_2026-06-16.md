# Gan 2026 — Simplest Near-Ceiling Architecture: Results, Analysis, and Principles

Date: 2026-06-16

Companion results report to the plan
`gan2026_simplest_near_ceiling_architecture_plan_2026-06-16.md`, and follow-on to
the night synthesis `gan2026_f1_dynamic_workflow_night_synthesis_2026-06-16.md`
which accepted **379/450 = 0.842 Purist (test450)** as the honest accuracy ceiling
for the V12 fresh-evidence hybrid and closed the chase for 0.90.

## Headline

After accepting 0.842 as the ceiling, the objective became: **reach as close to it
as possible with the simplest architecture.** The investigation traced the
complexity/accuracy frontier and converged on a clear result:

> **The single GPT structured-event pass — one model, no reasoner, no peer
> ensemble, no guard layer — is the right production architecture. It scores
> 364/450 = 0.809 on test450, just 3.3pp below the full three-model hybrid
> (0.842), and on validation it actually *beats* both the one-model and two-model
> reasoner variants. The entire reasoner + 3-model-ensemble + guard apparatus buys
> only +15 test rows, and that value does not decompose into anything cheaper.**

A material provenance caveat applies (see §6): every hybrid/reasoner run here was
executed on **full `gpt-4.1`**, not `gpt-4.1-mini`. The architecture conclusions
are model-invariant (all rungs used the same model), but the absolute numbers are
full-gpt-4.1 figures and need mini re-validation for the chosen design.

## 1. Objective

The accuracy axis was settled (0.842, structural wall to 0.90). The open axis was
**architectural complexity**, defined as a measurable cost — primarily the number
of distinct model passes, since each upstream model is real operational and
financial weight. Goal: find the knee of the complexity/accuracy frontier, not a
single point.

The V12 hybrid that scores 0.842 is concretely: **three upstream structured-event
extractions** (GPT, Qwen-3.6-35B, DeepSeek) + **a fourth fresh-evidence reasoner
pass** that may keep or replace the GPT answer + **a ~6-rule deterministic guard
layer**. The question was how much of that the score actually needs.

## 2. Method

Discipline carried from the night synthesis: **decompose cheaply first, confirm on
the locked split once.** All development on validation750 + held-out-family CV; the
robustness battery as the transfer gate; test450 touched only as a single
aggregate read of already-saved data.

A complexity ladder was defined, each rung a strict superset of the one below:
- **A0** deterministic floor (0 models) · **A1** naive direct labeler (1) ·
  **A2/A3** single GPT structured-event pass / GPT-only reasoner (1) ·
  **A4** GPT + one peer (2) · **A5** full V12 (3 + reasoner).

## 3. Results

### 3.1 Replay decomposition of the 3-model hybrid (validation750, no model calls)

`gan2026_simplest_arch_decomposition_v1_validation750_2026-06-16.md`

| Layer | Model passes | Purist | Δ |
| --- | ---: | ---: | ---: |
| GPT structured-event pass (`v0_reference`) | 1 | 661/750 = 0.881 | — |
| + fresh-evidence reasoner (raw) | 3+reasoner | 676/750 = 0.901 | +15 |
| + format-only label repair | 3+reasoner | 676/750 = 0.901 | +0 |
| + full deterministic guard layer (`final`) | 3+reasoner | 682/750 = 0.909 | +6 |

The reasoner's net over a single GPT pass is +21, entirely from the replace
mechanism (43 helped / 22 hurt). **The deterministic guard layer is near-inert on
validation: +6 rows, firing on only 8 of 750.**

### 3.2 The reasoner's replace discipline scales with corroboration depth

Three live runs (A3, A4, and the 3-agent baseline) isolate what the peer ensemble
does. The decisive metric is the reasoner's net effect **versus simply keeping the
GPT pass it reviews** (same run, confound-free):

| Reasoner input | Models | Purist (val) | Reasoner net vs own GPT pass | Replace helped / hurt | gap_robust |
| --- | ---: | ---: | ---: | ---: | :---: |
| GPT only (A3) | 1 | 610/750 = 0.813 | **−51** | 28 / 79 | False |
| GPT + DeepSeek (A4) | 2 | 631/750 = 0.841 | **−30** | 34 / 64 | False |
| GPT + Qwen + DeepSeek (A5 baseline) | 3 | 682/750 = 0.909 | **+21** | 43 / 22 | (baseline) |

Replacement improves monotonically with corroboration (−51 → −30 → +21) but only
the **full three-trace ensemble flips it net-positive.** With one peer the reasoner
is still destructive (64 hurt, 67 genuine-rate regressions). A3 (0.813) and A4
(0.841) both land **below the bare one-model GPT pass (0.881)** — adding peers and a
reasoner pass actively hurts until all three traces are present.

Standalone validation strength of the three extractors, for context:
GPT 661/750 = 0.881 · Qwen 638/750 = 0.851 · DeepSeek 622/750 = 0.829. (A4 used the
weaker peer, DeepSeek; GPT+Qwen — the one-peer upper bound — was not run.)

### 3.3 The frontier on the locked test split (test450)

Single-model anchor read by the Freeze Warden as an aggregate-only readout of the
`v0_reference` layer already saved in the frozen v0.4 test artifact (no new run, no
row-level inspection):
`gan2026_single_model_anchor_v0reference_test450_aggregate_readout_2026-06-16.md`.

| Architecture | Model passes | test450 Purist |
| --- | ---: | ---: |
| Deterministic floor | 0 | 343/450 = 0.762 |
| Naive direct labeler (`llm_only`) | 1 | ~323/450 = 0.71 |
| **GPT structured-event pass** | **1** | **364/450 = 0.809** |
| Full V12 hybrid (3 + reasoner + guards) | 3+reasoner | 379/450 = 0.842 |

**The whole apparatus buys +15 rows (+3.3pp) over a single GPT pass on test** —
far less than its 2.8pp validation footprint at a much higher base, and with the
guard layer contributing almost none of it.

## 4. Analysis

**Where the value is, and is not.** The 0.842 hybrid's advantage over one model is
not in its deterministic guards (near-inert, +6/750 val) and not in the reasoner's
raw cleverness. It is in **cross-model agreement disciplining the model's decision
to overwrite its own answer.** The reasoner is a free-to-replace agent; given only
one trace it over-replaces (A3: 79 hurt vs 28 helped), and the over-replacement is
the same failure family as the night synthesis's *unknown-over-reading wall* — the
model converts weak/ambiguous evidence into confident labels. Independent
corroboration from peers is what suppresses bad replacements; it takes **three**
traces, not two, to tip the balance positive.

**Simpler dominates, not merely approximates.** On validation the one-model pass
(0.881) beats the one-model reasoner (0.813) and the two-model reasoner (0.841).
Complexity here is not a monotone ladder toward accuracy — intermediate rungs are
*worse* than the floor of doing less. Only the top rung (3 models) clears the
single pass, and only by +3.3pp on test.

**Validation vs test.** The single pass is 0.881 on val but 0.809 on test (a 7.2pp
gap); the hybrid is 0.909 → 0.842 (6.7pp). The ensemble's validation edge (2.8pp)
shrinks to +3.3pp on test in absolute rows (+15). Validation under-samples the
clinical-wall cases, so guard value and ensemble value can only be trusted from the
locked split — which is exactly why the test anchor was the highest-information
single number in the whole exercise.

**Cost.** The +15 test rows cost two extra upstream models — including a local
35B — plus a fourth LLM pass and a guard layer to maintain. For the project's real
deliverables (KCL transfer, auditability, operational simplicity) that is a poor
trade; a single transparent extraction pass is far more portable to real letters.

## 5. Distilled key principles

1. **Treat simplicity as a measured axis and map the whole frontier.** "Best score"
   and "best architecture" are different optimisations; trace the
   complexity/accuracy curve and pick the knee, don't defend a single point.
2. **Decompose on saved artifacts before spending live calls.** Per-layer scores and
   recorded decisions already on disk answered most questions for free; live runs
   were reserved for prompt-changing rungs; the locked split was read once,
   aggregate-only.
3. **Ensemble value localises to corroboration, not to post-processing.** The
   deterministic guards were near-inert; multi-model *agreement* — not extra rules —
   is what disciplines a free-to-replace agent. When an LLM may overwrite a prior
   answer, the abstain/keep signal must come from an **independent** source, never
   from the model's own confidence (the unknown-over-reading lesson, restated).
4. **Corroboration is non-linear in depth.** Going 1 → 2 → 3 traces moved the replace
   decision −51 → −30 → +21. Two corroborators were not enough; there is no cheap
   2-model middle ground for this mechanism.
5. **Added components can actively hurt.** A simpler architecture out-scoring a more
   complex one (1-model pass > 1- and 2-model reasoners) is a real, common outcome,
   not a measurement artifact — always include the "do less" baseline.
6. **Verify model provenance from artifacts; never inherit "equivalent model"
   assumptions.** The headline numbers were assumed to be on mini and were actually
   on full gpt-4.1 (§6). Read the `model` field, don't trust the comment.
7. **A curated robustness battery passing 100% is necessary but not sufficient**
   (carried forward): the full-distribution held-out-family CV must sit behind it
   before any locked-split run.

## 6. Model provenance and go-forward stack

**What was actually run.** `build_dspy_lm` performs no model aliasing — it passes
the model string straight to the API. Every fresh-evidence/hybrid run in this
investigation, and the v0.4 artifacts behind the 0.842 ceiling and the 0.809
anchor, record `model = openai/gpt-4.1` — i.e. **full gpt-4.1, not gpt-4.1-mini.**
The "gpt-4.1 ≡ gpt-4.1-mini" equivalence is an unverified assumption inherited from
the night synthesis; the only place mini was plausibly the literal model is the
`llm_only` direct-labeler calibration (~0.71). Full gpt-4.1 is also the likely
cause of the OpenAI budget exhaustion seen mid-investigation (one A4 attempt failed
with all 750 calls rate-limited and was re-run after the account was refreshed).

**Go-forward decision (operator directive, 2026-06-16).** The standard model stack
is **`gpt-4.1-mini` as the main closed model** and **Qwen-3.6-35B as the main local
model**; **full `gpt-4.1` is too expensive for routine use.** Consequently the
chosen architecture (single GPT structured-event pass) should be re-validated on
`gpt-4.1-mini` before any production or benchmark claim, and future cost planning
should assume mini + Qwen, not full gpt-4.1.

**Correction — the single GPT pass was already on mini (verified 2026-06-16, no new
calls).** The §6 caveat above conflated two distinct passes. The full-`gpt-4.1`
provenance applies to the **fourth fresh-evidence reasoner pass and the 3-model
hybrid** — *not* to the GPT structured-event extraction that constitutes the chosen
single-pass architecture. Both the validation750 and test450 GPT structured-event
artifacts that supply the `v0_reference` anchor record `model = openai/gpt-4.1-mini`,
mode `live`, temperature 0, prompt `gan2026_hybrid_structured_events_v0.5`:
- `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl` → **661/750 = 0.881 Purist**
- `experiments/gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09.jsonl` → **364/450 = 0.809 Purist**

Scoring these mini artifacts directly reproduces the 0.881 / 0.809 anchors exactly,
and the `v0_reference` layer inside the full-gpt-4.1 v0.4 reasoner artifact is
byte-identical to the mini extraction (0/750 label mismatches). **The single GPT
structured-event pass is therefore already validated on the go-forward stack at
364/450 = 0.809 test; the mini re-validation requested below is satisfied and needs
no new run.** The production path carries no full-`gpt-4.1` dependency. (Principle #6
restated: read the `model` field per pass — the reasoner's model is not the
extraction's model.)

## 7. Recommendation

- **Adopt the single GPT structured-event pass as the production seizure-frequency
  labeler.** One model, no reasoner, no peer ensemble, no guard layer. **364/450 =
  0.809 on the locked split, verified on `gpt-4.1-mini`** (see §6 correction), 3.3pp
  below the hybrid ceiling, maximally simple and transportable to KCL letters.
- **Mini re-validation: DONE.** The chosen pass is already a live `gpt-4.1-mini`
  result on both validation750 (0.881) and test450 (0.809); no new run required. The
  remaining optional item is the **Qwen-3.6-35B local pass** as a fully-local,
  zero-closed-model anchor for portability.
- **Reserve the 3-model hybrid only if +3.3pp is essential to a specific claim** — it
  has no cheaper form; two models do not suffice.
- Optional, to close the frontier: the **GPT+Qwen** two-model rung (stronger peer,
  one live cost, peer trace already saved) as the one-peer upper bound. Expected to
  remain below the one-model pass.

## 8. Reproducibility — artifacts produced

- Plan: `docs/research/gan2026/architecture/gan2026_simplest_near_ceiling_architecture_plan_2026-06-16.md`
- Decomposition driver + report:
  `experiments/build_gan2026_simplest_arch_decomposition_v1.py`,
  `experiments/gan2026_simplest_arch_decomposition_v1_validation750_2026-06-16.md`
- A3 (GPT-only reasoner): prompt version `PROMPT_VERSION_V0_11_GPT_ONLY`,
  `experiments/build_gan2026_fresh_evidence_v0_11_gpt_only_validation750.py` (+ run
  artifacts, registered)
- A4 (GPT + one peer): prompt version `PROMPT_VERSION_V0_12_TWO_MODEL` with
  `set_active_two_model_peer()`,
  `experiments/build_gan2026_fresh_evidence_v0_12_gpt_deepseek_validation750.py`
  (+ run artifacts, registered)
- Test anchor (Freeze Warden, aggregate-only):
  `experiments/gan2026_single_model_anchor_v0reference_test450_aggregate_readout_2026-06-16.md`
- All prompt variants are additive; the fresh-evidence module default remains v0.6.
