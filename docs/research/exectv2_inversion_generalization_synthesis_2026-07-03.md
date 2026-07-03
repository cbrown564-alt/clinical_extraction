# Synthesis — does the Rx split-dependent inversion generalize?

Date: 2026-07-03. Owner: ExECTv2 workstream.
Companion to: `docs/experiments/exectv2/prescription/exectv2_rx_llm_vs_deterministic_comparator_2026-07-03.md`.

## The question

The 07-03 Rx comparator found a **split-dependent inversion**: the deterministic
Prescription producer wins dev140 (recall), the LLM-tuned extractor wins full-200
(precision), because the two producers fix *different* failure modes with
*different* dev/test prevalence. Is this a **general property** of the v08
architecture's deterministic-vs-LLM lane choice, or a Prescription-specific
quirk?

This synthesis reports the generalization probe across two more families
(Investigations, Seizure Frequency), run 2026-07-03 under the project's gated-
probe discipline. Both tracks are now **REFUTED** as inversions, but the
*reasons* are informative and together they sharpen the paper's
architecture-of-record story.

## Track A — Investigations: the inversion does NOT generalize

**Hypothesis** `inv_llm_precision_vs_hybrid_inversion_2026-07-03` — **REFUTED.**

Built the precision-side analog (the recall side, MRI-crowds-EEG, was already
REFUTED at hypothesis 2026-07-01): an LLM-tuned Inv extractor with a
completed-neuro-investigations-only precision gate, run through the v08 assembly
with same-day baseline+treatment isolation.

| Split | Hybrid Inv (baseline) | LLM-tuned Inv | Δ | LLM precision | LLM recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| dev140 | 0.9132 | 0.8949 | −0.0183 | +0.0124 (FP 8→6) | −0.0441 (FN 15→21) |
| full-200 | 0.9213 | 0.9080 | −0.0133 | +0.0096 (FP 9→7) | −0.0328 (FN 19→25) |

The hybrid wins on **both** splits with the **identical mechanism**: the LLM
precision probe trades recall for precision and loses net. There is no split
where the precision gain outweighs the recall cost — the inversion's second half
(the LLM winning the broader test surface) does not occur.

### Why Inv differs from Rx

The Rx inversion required a specific conjunction Inv does not satisfy:

1. **Rx's deterministic producer had a structural precision weakness** — a bare
   AED lexicon that over-captures non-AED comorbidity drugs on the broader
   full-200 surface. The LLM fixed this *without recall cost* (TP 270→271).
2. **Inv's hybrid lane has no analogous exploitable weakness.** Its arbitration
   handles BOTH recall (MRI-crowds-EEG recovery) AND precision
   (planned-investigation drops via the convention layer's
   `_PLANNED_INVESTIGATION_EVIDENCE` gate). The LLM precision probe can only
   help precision, and on Inv that help always costs more recall than it gains.

**Mechanism asymmetry:** Rx's deterministic lane was pure-deterministic with a
lexicon blind spot; Inv's lane is hybrid, and its arbitration already covers the
precision surface the LLM probed.

## Track B — SF direction: a different, sharper finding

**Hypothesis** `sf_direction_extraction_probe_2026-07-03` — **REFUTED** (main
claim), but with a genuinely informative sub-finding.

### Pre-work correction

A free scorer-replay (zero LLM calls) established that the v08 hybrid SF
producer is **NOT** direction-blind — it scores **0.8897** on
`state_profile_directional` (dev140) by sourcing directions from
`deterministic/rules/change.py`. The direction-blindness finding (0/12 recovery,
`state_profile_directional` 0.6552) is a property of the **raw** two-stage
SF-verify LLM program, which the production pipeline does not use alone.

So Track B tested: can an LLM-only direction-aware program **match** the hybrid's
deterministic direction arbitration?

### The capacity-vs-execution gap (B1 vs B2)

| Phase | What it tested | Result |
| --- | --- | --- |
| **B1** (post-hoc, 28 calls) | Can the model *judge* direction in isolation? | **YES** — recovered +12/30 gold-directional facts, `state_profile_directional` 0.6552 → 0.7254 (+0.07), `state_profile` byte-identical |
| **B2** (full two-stage, ~680 calls) | Can the model *emit* direction as part of extraction? | **NO** — regressed on ALL metrics both splits: dev140 −0.0775 directional / −0.1548 state_profile; trails hybrid by ~0.30 |

The model can judge direction when asked in a focused single-purpose call, but
**cannot cleanly emit it as part of the structured extraction task**. Adding a
direction field to the two-stage event schema increases the extraction's
cognitive load and degrades the other fields — direction emission competes with
rather than complements kind/evidence/applies_to. This is the same task-overload
pattern the Rx probe #3 exhibited before its emit-if-unsure fix.

## The combined finding for the paper

Two negative results that together **strengthen** the v08 architecture-of-record
story, in two distinct ways:

1. **The Rx split-dependent inversion is Prescription-specific**, not a general
   property of the deterministic-vs-LLM lane choice. It traces to a specific
   lexicon blind spot (non-AED over-extraction on the broader test surface) in
   Prescription's *purely-deterministic* producer. The v08 hybrid lanes (Dx, SF,
   Inv) — whose arbitration already covers both recall and precision — are robust
   to LLM-only replacement on both splits.
2. **The deterministic SF direction arbitration is genuinely better than an
   LLM-only direction-aware program** (gap ~0.25-0.30 on
   `state_profile_directional`). `deterministic/rules/change.py` does something
   the LLM demonstrably cannot match even with a schema fix and explicit
   direction discipline. The capacity-vs-execution gap (B1 vs B2) shows this is
   not a model-capacity limit — the model can judge direction in isolation — but
   an *extraction-task-design* limit: structured direction emission degrades the
   whole task.

### Honest framing for the manuscript

The 07-03 Rx comparator's caveat ("the deterministic lane is competitive with
but not strictly better than a tuned LLM on Prescription") is now bounded
precisely: it holds *only* for Prescription, and only because of a specific
lexicon gap. The other three families' hybrid lanes are robust to LLM-only
replacement (Inv, this synthesis) or genuinely superior to it on at least one
load-bearing axis (SF direction, this synthesis). The v08 architecture's hybrid
design — deterministic components for the surfaces where structure beats
contextual judgment, LLM components for the surfaces where it doesn't — is
*vindicated* by the failed generalization, not weakened by it.

## Provenance

- Track A: `docs/experiments/exectv2/investigations/exectv2_inv_llm_vs_hybrid_comparator_2026-07-03.md`
- Track B: `docs/experiments/exectv2/seizure_frequency/exectv2_sf_direction_probe_results_2026-07-03.md`
- Pre-work baseline: `docs/experiments/exectv2/seizure_frequency/_sf_directional_baseline_replay_2026-07-03.json`
- Drivers: `scripts/run_exectv2_v08_inv_llm_vs_hybrid.py`, `scripts/run_exectv2_sf_direction_probe.py`, `scripts/register_inv_sf_inversion_hypotheses.py`
- Total calls: ~1090 (Inv dev140 140 + full-200 60; SF B1 28 + B2 dev140 280 + B2 full-200 400; most dev140 cached).
