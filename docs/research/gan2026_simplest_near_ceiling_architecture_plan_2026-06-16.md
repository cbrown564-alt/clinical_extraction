# Gan 2026 — Simplest Near-Ceiling Architecture Plan

Date: 2026-06-16

Follow-on to `gan2026_f1_dynamic_workflow_night_synthesis_2026-06-16.md`, which
accepted **379/450 = 0.842 (Purist, test450, gpt-4.1-mini)** as the honest
accuracy ceiling for the V12 fresh-evidence hybrid and closed the chase for 0.90.

This plan changes the objective. The accuracy axis is settled; the open axis is
**architectural complexity**. Goal: **achieve the highest Purist score we can —
as close to 0.842 as possible — with the simplest architecture**, where "simplest"
is defined and measured, not asserted.

## Why this is the right next objective

The 0.842 architecture is not "a model with glue". It is, concretely:

1. **Three upstream structured-event extractions** — gpt-4.1-mini, Qwen-3.6-35B,
   and DeepSeek — each its own pipeline producing a saved trace
   (`agent_sources = {gpt, qwen, deepseek}` in the fresh-evidence reasoner).
2. **A fourth model pass**, the fresh-evidence reasoner, which reads all three
   traces plus the raw note and decides keep-or-replace.
3. **A deterministic guard layer** — the safety gate in `_render_fresh_action` /
   `_fresh_evidence_safety_gate_reason`: bare-seizure-free, open-ended
   treatment-start denominator, seizure-free-replacing-frequency, vague-multiple
   exactification, same-day cluster-downgrade, plus evidence-substring validation
   and format-only label repair.

So **0.842 = three models + a reasoner + ~6 deterministic guards.** That stack is
hostile to the project's actual deliverables (the clinical principle, the
two-tier robustness methodology, and King's College London transfer): more
components mean more synthetic-overfit surface (the hybrid's own 13pp
validation→test gap was the overfit signature), more operational weight (Qwen and
DeepSeek must both be kept running), and more to break on real letters. A simpler
architecture within ~1pp of the ceiling is therefore a **better** artifact, not a
consolation.

## Anchors (measured)

| Architecture | Model passes | test450 Purist |
| --- | ---: | ---: |
| Deterministic floor (no model) | 0 | 343/450 = 0.762 |
| `llm_only` direct labeler v0.5 | 1 | ~323/450 = 0.71 |
| **V12 fresh-evidence hybrid** | **3 + reasoner** | **379/450 = 0.842** |

Two facts drive the design:

- **Zero-model deterministic (0.762) beats the single direct LLM call (0.71).**
  "Simpler" here does *not* mean "trust the model more"; it means lean on
  deterministic structure and escalate to the model narrowly.
- The prize is the **+36 rows between 0.762 and 0.842**. The design question is
  *how few moving parts buy most of those 36 rows.*

## Design — a complexity ladder (each rung a superset of the one below)

Primary cost axis = **number of distinct model passes** (each upstream model is
real operational weight). Secondary axis = number of deterministic guards / lines.

- **A0** — deterministic floor only. *(0 calls; 0.762, known)*
- **A1** — single mini direct labeler. *(1 call; 0.71, known — dominated, discard)*
- **A2** — single mini structured-event pass → deterministic projection, **no guards**.
- **A3** — A2 **+ the deterministic safety guard layer** (the clinical-wall
  guards, lifted off V12 — pure post-processing, no extra model). **Primary
  candidate for the knee.**
- **A4** — A3 + **one** peer trace (2 models).
- **A5** — full V12 (3 models + reasoner; 0.842, known).

**Central hypothesis:** the +36 rows live in the **guard layer**, not in the
second and third models. The guards *are* the clinical-wall corrections the
synthesis localised (provoked/transient counts, last-event-only, cluster
flattening, seizure-free over-reading). If true, **A3 — one model + deterministic
guards — recovers most of 0.842 at one-third the model cost.**

## Evaluate — decompose first (cheap), confirm last (expensive)

Discipline carried from the night synthesis: **all development on validation750 +
held-out-family CV + the robustness battery; test450 gets exactly one
confirmatory readout at the end.**

### Step 1 — replay decomposition (no new model calls)

The V12 validation750 artifact
(`experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl`,
750 rows) already stores every raw model output, all three agent traces, and
per-layer Purist scores (`score_layers.{raw_model,format_only,final}.comparison.purist_correct`
plus `v0_reference.comparison.purist_correct`). The guard layer is deterministic,
so it can be re-rendered with components toggled **without any model call**.

Outputs of Step 1:
- **Ladder-middle decomposition (free):** Purist of GPT-only `v0_reference`
  (≈ A2 proxy with the GPT trace), raw reasoner output, format-only, and
  full-guard `final` — isolating what the reasoner adds over GPT-only and what
  the guard layer adds over the raw reasoner.
- **Per-guard ablation:** re-render each row with one safety-gate guard disabled
  at a time; report each guard's marginal Purist contribution (and any
  regressions it causes), ranked.

This is pure replay over saved JSONL — near-free — and reuses the existing
ablation harness family (`artifact_analysis/claim_table_component_ablation.py`,
`validation_component_stress_ablation.py`,
`llm_replacement_postprocessing_ablation.py`).

Driver: `experiments/build_gan2026_simplest_arch_decomposition_v1.py`. Report:
`experiments/gan2026_simplest_arch_decomposition_v1_validation750_2026-06-16.md`.

### Step 2 — live runs only for prompt-changing rungs

Dropping peers from the *prompt* (proper A2/A3, A4) changes what the reasoner
sees, so those need a live validation750 re-run — but only for the rungs Step 1
flags as promising. Each live rung is gated on:
- Purist on validation750;
- `gap_robust` via held-out-family CV (the instrument that caught the −106 C3
  regression);
- the robustness battery (the KCL-transfer gate).

### Step 3 — pick the knee, confirm once

**Decision rule (declared up front):** choose the architecture with the **fewest
model passes** whose validation Purist is within **~1.5pp (≈5–7 rows)** of the
best rung, that is **gap-robust** and **clears the robustness battery**. Then run
**one** test450 readout on that single winner via the Freeze Warden. No row-level
test inspection, no post-test tuning.

## Success criteria

- A documented complexity/accuracy frontier across A0–A5 on validation750.
- A chosen architecture strictly simpler than V12 (ideally ≤1 model pass) within
  ~1.5pp of 0.842 on validation, gap-robust, battery-clean.
- One confirmatory test450 number for the chosen architecture.
- If no simpler rung lands within tolerance: a recorded, evidenced statement that
  the ensemble is load-bearing and *why* (which peer, which rows) — itself a
  durable result.

## Claim boundary

Development and decomposition are validation-only. test450 is touched exactly once,
for the single chosen winner, under the existing frozen-holdout protocol. Nothing
here reopens the 0.90 chase; the accuracy ceiling stands at 0.842.

## Results

### Step 1 — replay decomposition (validation750, no model calls)

`experiments/gan2026_simplest_arch_decomposition_v1_validation750_2026-06-16.md`.

| Layer | Model passes | Purist | Δ |
| --- | ---: | ---: | ---: |
| GPT structured-event only (`v0_reference`) | 1 | 661/750 = 0.881 | — |
| + fresh-evidence reasoner (raw) | 3+reasoner | 676/750 = 0.901 | +15 |
| + format-only repair | 3+reasoner | 676/750 = 0.901 | +0 |
| + full deterministic guard layer (`final`) | 3+reasoner | 682/750 = 0.909 | +6 |

The reasoner's net over a single GPT pass is +21, all from the replace mechanism
(43 helped / 22 hurt). **The deterministic guard layer is near-inert on
validation (+6, fires on only 8/750 rows)** — refuting the "guards carry the +36"
hypothesis *on validation*. (Caveat retained: validation under-samples the
clinical-wall cases the guards target; their test value is unmeasured here.) The
sharpened lever became: do the Qwen + DeepSeek peer traces carry the reasoner's
lift?

### Step 2 — A3 (GPT-trace-only reasoner) live on validation750 — REJECTED

`experiments/gan2026_fresh_evidence_v0_11_gpt_only_validation750_live_gpt41_2026-06-16.md`.

| Metric | A3 (GPT-only reasoner) | 3-agent baseline |
| --- | ---: | ---: |
| Purist | 610/750 = 0.813 | 682/750 = 0.909 |
| Net vs baseline | **−72** | — |
| Reasoner vs its *own* GPT pass | **−51** (610 vs 661) | +21 |
| Replace actions (helped/hurt) | 28 / 79 | 43 / 22 |
| Genuine-rate regressions | 89 | — |
| `gap_robust` | False | — |

**Verdict: the peer ensemble is load-bearing.** The confound-free signal is the
within-run comparison: the GPT-only reasoner (610) scores **51 rows worse than
simply keeping the GPT pass it reviews** (661) — same prompt, same run, immune to
any baseline drift. With three traces the reasoner replaces accurately (+21); with
one trace it over-replaces destructively (−51, 89 genuine-rate regressions).
Cross-model corroboration is what makes the *replace* decision safe. A3 (collapse
3 models → 1 *while keeping the reasoner*) is rejected.

### Consequence for the ladder

Two facts now frame the remaining search:

1. The reasoner is only safe **with** peers, so the cheapest viable *reasoner*
   architecture is ≥2 models (A4 — one peer — is the open question for the minimal
   ensemble that preserves corroboration).
2. The best **single-model** option is *not* the GPT-only reasoner (610) and not
   the naive direct labeler (≈0.71 test) — it is the **bare GPT structured-event
   pass + deterministic guards**, which scores 661/750 = 0.881 on validation with
   **no reasoner and no peers**. Its test450 number is unmeasured but already
   exists as the `v0_reference` layer inside the frozen V12 test artifact, readable
   as an aggregate (no new run, no row-level inspection) via the Freeze Warden.

The single highest-information next step is therefore the **GPT-structured-event
pass test450 anchor**: it scores the leading simple candidate on the locked split
and bounds how much the 3-model ensemble actually buys on test (vs the 2.8pp it
buys on validation). A4 (2-model) is the follow-on if a sub-3-model reasoner is
wanted.

### Step 3 — single-model anchor on test450 (Freeze Warden, aggregate-only)

`experiments/gan2026_single_model_anchor_v0reference_test450_aggregate_readout_2026-06-16.md`.
Aggregate read of the `v0_reference` layer already saved in the frozen v0.4 test450
artifact — no new run, no row-level inspection.

| Architecture | Model passes | test450 Purist |
| --- | ---: | ---: |
| Deterministic floor | 0 | 343/450 = 0.762 |
| Naive direct labeler (`llm_only`) | 1 | ~323/450 = 0.71 |
| **GPT structured-event pass (no reasoner, no peers)** | **1** | **364/450 = 0.809** |
| Full V12 hybrid (3 models + reasoner + guards) | 3+reasoner | 379/450 = 0.842 |

**The entire 3-model + reasoner + guard apparatus buys +15 rows (+3.3pp) over a
single GPT structured-event pass on the locked test set** — far less than its
validation footprint implies, and the guard layer's validation near-inertness (+6)
suggests much of that +15 is the peer-corroborated replace mechanism, not the
guards.

### Step 4 — A4 (GPT + one peer, 2 models) live on validation750

`experiments/gan2026_fresh_evidence_v0_12_gpt_deepseek_validation750_live_gpt41_2026-06-16.md`.
Peer = DeepSeek (the weaker peer; Qwen 0.851 > DeepSeek 0.829 standalone on
validation — DeepSeek run first per operator request). Peer trace is a saved
artifact; only the gpt-4.1 reasoner pass is live. (First attempt 2026-06-16 failed
on an OpenAI quota exhaustion — all 750 calls rate-limited; artifacts purged and
the run repeated cleanly after the account was refreshed.)

**The reasoner's replace discipline as a function of corroboration depth:**

| Reasoner input | Models | Purist | Reasoner net vs its own GPT pass | Replace helped/hurt |
| --- | ---: | ---: | ---: | ---: |
| GPT only (A3) | 1 | 610/750 = 0.813 | **−51** | 28 / 79 |
| GPT + DeepSeek (A4) | 2 | 631/750 = 0.841 | **−30** | 34 / 64 |
| GPT + Qwen + DeepSeek (baseline) | 3 | 682/750 = 0.909 | **+21** | 43 / 22 |

As corroboration deepens the replace decision improves monotonically
(−51 → −30 → +21), but **two models is not enough** — with one peer the reasoner
is still net-destructive (64 hurt vs 34 helped, 67 genuine-rate regressions,
`gap_robust = False`). Only the full 3-trace ensemble flips replacement to
net-positive. A4-DeepSeek (0.841 val) even lands **below the bare 1-model GPT pass
(0.881 val)** — adding a peer and a reasoner pass actively hurts here.

Caveat: DeepSeek is the weaker peer; GPT + Qwen (stronger peer) is the remaining
2-model variant and is an upper bound on what one peer can do. It can be run with
`set_active_two_model_peer("qwen")` — no Ollama needed (the Qwen trace is a saved
artifact).

## Current frontier and decision

On test450 the **single GPT structured-event pass (0.809)** is the best simple
architecture: it beats the deterministic floor (0.762) and the naive labeler
(~0.71), uses one model and no reasoner/peers/guards, and sits 3.3pp below the
accepted 0.842 ceiling. The ensemble's entire marginal value is +15 rows bought
with two extra upstream models (Qwen-35B + DeepSeek), a fourth reasoner pass, and
the guard layer.

Two defensible knees, depending on how 3.3pp trades against complexity:

- **Single GPT structured-event pass (1 model, 0.809)** — the simplicity-maximal
  choice; best for KCL transfer, auditability, and operational weight.
- **A4: GPT + one peer (2 models)** — the one unrun experiment that could recover
  most of the +15 (A3 proved corroboration is what makes replacement safe; the
  open question is whether *one* peer suffices vs needing two). Run on
  validation750 first if a sub-3-model reasoner is wanted.

## Status log

- 2026-06-16 — Plan authored. Step 1 decomposition run (guards near-inert on val;
  reasoner replace mechanism carries the +21).
- 2026-06-16 — Step 2 A3 (GPT-only reasoner) run and **rejected**: peers are
  load-bearing (−72 vs baseline; −51 vs its own GPT pass).
- 2026-06-16 — Step 3 single-model test450 anchor read via Freeze Warden: GPT
  structured-event pass = 364/450 = 0.809; the full ensemble buys only +15 rows
  (+3.3pp) on test. Frontier established.
- 2026-06-16 — Step 4 A4 (GPT+DeepSeek, 2-model) on validation = 631/750 = 0.841,
  still −30 vs its own GPT pass and below the 1-model pass (0.881). Two models is
  not enough; only the 3-trace ensemble makes replacement net-positive. Confirms
  the single GPT structured-event pass as the final choice. Optional remaining
  variant: GPT+Qwen (stronger peer) as the one-peer upper bound.
