# Gan 2026 F1 Dynamic-Workflow Protocol

Date: 2026-06-15

This is the controlling protocol for the dynamic, orchestrated workflow whose
goal is a reproducible **micro-F1 (Purist) ≥ 0.90 on `test450`** for at least
one `llm_only` or `hybrid` Gan 2026 seizure-frequency pipeline using
`gpt-4.1-mini`, *that also generalises* to a different distribution (real King's
College London letters vs. the GAN-synthetic Gan 2026 data).

It defines the orchestrator, the specialist subagents
(`.claude/agents/gan2026-*.md`), the fitness function, the hard gates, and the
experiment lifecycle. The re-runnable entry point is `/gan2026-f1-cycle`
(`.claude/commands/gan2026-f1-cycle.md`).

## Metric definition (locked)

`evaluate.py` scores a 12-class Purist labelling. In single-label multiclass,
**micro-F1 ≡ accuracy ≡ Purist count / N**. So the target is **≥ 405/450** exact
Purist-correct rows on `test450`. Macro-F1 ≥ 0.90 is *not* the target (singleton
classes such as `seizure_free|row_ok=false` make it infeasible) and weighted-F1
is not the target either. When this doc says "Purist" it means this number.

## The situation that shapes every decision

Read these before proposing anything; they are why this workflow exists and why
it does *not* look like "add more agents."

1. **`validation750` is saturated and can no longer rank candidates.** The
   selector family was driven from v0.1→v0.10; the selector-only oracle ceiling
   over the current deterministic + consensus + fresh-evidence components is
   **739/750**, and **11 rows have no Purist-correct component at all**
   (`gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15`).
2. **The component-generation wall is real.** The strongest generation attempt —
   live v0.7 + safety-v0.9 ambiguity-aware fresh evidence — fixed only **1 of 11**
   no-correct rows, moved the oracle ceiling **+0** (739→739), and regressed a
   previously-correct row (14821)
   (`gan2026_ambiguity_live_component_generation_audit_v0_7_2026-06-15`). Its
   conclusion: *the next bet must change the evidence the model sees, not the
   decision contract layered on top.*
3. **The validation→test gap is the real signal.** Ranked by holdout loss, the
   LLM-owned architectures generalise best; deterministic/consensus borrowing
   overfits. The three-agent consensus *won* validation and generalised *worst*.
4. **More runtime agents have repeatedly failed.** Verifiers, routers,
   adjudicators, and multi-agent panels topped out or regressed; multi-agent did
   not beat matched-budget self-consistency. V12 won by deepening one action.

**Consequence:** the binding evidence is no longer validation Purist. It is
**gap-robustness + out-of-distribution robustness**. The primary instrument is
the adversarial/robustness/hard-case battery (below), not another validation
replay.

## Fitness function (lexicographic — evaluate in this order)

A candidate is ranked, and may only be promoted toward `test450`, by:

1. **Gap-robustness** — passes held-out-family CV
   (`agentic/family_cv_promotion.summarize_family_holdout_cv`): aggregate net
   Purist gain > 0, no boundary band regresses, every changed band clears the
   changed-label precision bar. A positive aggregate riding on one band while a
   held-out band is sacrificed is a **fail**.
2. **OOD / robustness survival** — clears the adversarial/robustness battery:
   synthetic hard-negatives, source-near contrasts, and KCL-style
   out-of-distribution phrasing, with **zero changed-label regressions** on the
   hard-negative slices and a stated minimum on the OOD slices.
3. **Clinical principle** — the change is a generalisable clinical rule a
   neurologist would endorse (e.g. "unknown is safer when count or window is
   unclear"), *not* a validation-mined gate keyed on saved-row behaviour. The
   Rule Designer must state the principle and why it should transfer.
4. **Validation Purist** — tie-breaker only. Never the promotion trigger. A
   change that lifts validation but fails 1–3 is **rejected**.

## Hard gates (the orchestrator and Freeze Warden enforce these)

- **Predeclaration.** Every experiment ships with its hypothesis, expected
  effect, and its synthetic + OOD panels *before* any replay/live run. No
  post-hoc rationalisation of whatever moved the number.
- **No `test450` run without Freeze Warden certification.** The user has
  pre-authorised holdout runs *conditional on the agreed standard*. Authorisation
  means: fitness tiers 1–3 are cleared on predeclared panels, the change is
  clinically principled, and `frozen_test_preflight` passes (source-symmetry hard
  gate across GPT/Qwen/DeepSeek artifacts). The Freeze Warden certifies or
  refuses; it does not lower the bar to manufacture a number.
- **Report the true number.** Whatever `test450` returns is reported verbatim,
  even below 0.90. No tuning on test, no re-running to pick a better seed, no
  inspecting test row failures to revise.
- **Matched-budget comparator.** Any runtime-agent (multi-call) variant must beat
  a single-agent self-consistency baseline *at equal token budget* before it earns
  a slot. Otherwise it is rejected on sight (situation §4).
- **Resumability.** Expensive runs are resumable via `core/run_resume.py`;
  experiments register into `experiments/registry.jsonl` and `RUN_INDEX.md`.

## Specialist subagents

The orchestrator (the main session, or the `/gan2026-f1-cycle` command) holds the
plan and the scoreboard. It delegates to:

| Agent | Role | Tier it owns |
| --- | --- | --- |
| `gan2026-error-analyst` | Decompose the residual; split "correct component exists but unselected" vs "no correct component"; cluster by clinical failure type; rank by leverage | feeds 1 |
| `gan2026-rule-designer` | Turn a cluster into a predeclared, clinically principled change with expected effect + panels | owns 3, predeclaration |
| `gan2026-experiment-runner` | Implement as a `build_gan2026_*.py` driver; run no-call replay and/or live `gpt-4.1-mini`; score Purist + family-CV; register | tier 1, mechanics |
| `gan2026-generalization-adversary` | Build + run the synthetic / source-near / KCL-style OOD battery; red-team for synthetic-artifact overfit | owns 2 |
| `gan2026-freeze-warden` | Certify or refuse `test450`; enforce all hard gates; run the frozen holdout when certified; report verbatim | owns the gate |
| `gan2026-scribe` | Write the dated durable doc in house style; update the scoreboard and `RUN_INDEX.md` | bookkeeping |

## Experiment lifecycle (one cycle of the loop)

1. **Analyse** (error-analyst) → ranked failure clusters + leverage estimate.
2. **Design** (rule-designer) → predeclared change + expected effect + synthetic
   + OOD panels. Prefer "change the evidence the model sees" over new contracts.
3. **Implement & run** (experiment-runner) → driver + no-call/live results +
   family-CV.
4. **Stress** (generalization-adversary) → battery results; overfit verdict.
5. **Certify** (freeze-warden) → fitness tiers 1–3 check; authorise or refuse
   `test450`.
6. **Record** (scribe) → durable doc, registry, scoreboard.
7. **Loop** until a candidate is certified and clears `test450 ≥ 405/450`, or the
   queue is exhausted (then report the honest ceiling and the blocking reason).

## Current scientific frontier (the working hypothesis for the queue)

The component wall is an *evidence* problem, not a *contract* problem. The 11
no-correct rows are dominated by over-reading: last-event/seizure-free snippets
turned into durations, and underspecified recent rates turned into quantified
frequencies, on rows whose gold is `unknown`. The highest-leverage, most
clinically-generalisable bets — and the ones most likely to transfer to KCL —
concern **what evidence the model is shown and how ambiguity is represented in
that evidence**, validated primarily on the OOD battery rather than on the
saturated validation set.

## Scoreboard

Lives in `experiments/gan2026_f1_orchestrator_state.json`. Holds the current
robustness-certified champion, the last authorised `test450` number, the gap, the
predeclared experiment queue, and per-cycle verdicts. The scribe updates it every
cycle; it is the resumable state of the loop.
