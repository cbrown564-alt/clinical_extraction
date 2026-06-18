# Gan 2026 F1 Dynamic-Workflow — Night Synthesis

Date: 2026-06-16

Synthesis of the overnight dynamic-workflow run targeting micro-F1 (Purist)
≥ 0.90 on `test450` with `gpt-4.1-mini` for an `llm_only`/`hybrid` Gan 2026
seizure-frequency pipeline, that also generalises to real KCL letters.

Protocol: ``.
Scoreboard: `experiments/gan2026_f1_orchestrator_state.json`.

## Headline verdict

**≥ 0.90 on `test450` with `gpt-4.1-mini` is not achievable with the current
architecture family, on the evidence gathered.** The realistic ceiling is roughly
**0.71** (bare `llm_only` on mini, measured) to **~0.82–0.84** (best hybrid family,
and that figure was obtained on full `gpt-4.1`, not mini). The gap to 0.90 is a
genuine clinical-reasoning gap, not a tuning or selection gap.

## What was measured

| Result | Split | Purist | Notes |
| --- | --- | ---: | --- |
| `llm_only` direct labeler v0.5, **gpt-4.1-mini** | validation750 | 575/750 = 0.767 | baseline |
| `llm_only` direct labeler v0.5, **gpt-4.1-mini** | **test450** | **321/450 = 0.713 and 325/450 = 0.722** | **first-ever mini holdout; two concordant calibration runs (±4 rows of temp-0 run-to-run noise)** |
| Deterministic floor (no model) | test450 | 343/450 = 0.762 | beats llm_only mini |
| Best hybrid (V12 fresh-evidence) | test450 | 379/450 = 0.842 | on **full gpt-4.1**, not mini |

The measured `llm_only` validation→test gap on mini is only **5.3pp** — the
`llm_only` path generalises honestly, but at a low absolute level. The hybrid
family's larger 13pp gap is the overfit-to-synthetic signature the protocol was
built to police.

## Why 0.90 is out of reach

The +26-row gap from the best hybrid (379) to target (405) lives almost entirely
in the **unknown-over-reading clinical wall**: the model converts event *counts*
into habitual *rates* when the events are provoked/situational, transient, merely
descriptive, or non-adherence-confounded, and it flattens **clusters**. Three
independent lines confirm this is a real reasoning gap, not surface form or
selection:

1. **Selector saturation.** The selector-only oracle ceiling on validation is
   739/750; 11 rows have no Purist-correct component at all. Selection is exhausted.
2. **Component-generation wall.** The strongest live generation attempt (v0.7
   ambiguity-aware) fixed only 1 of 11 no-correct rows and moved the ceiling +0.
3. **Robustness battery.** On a 27-case authored battery, KCL-style OOD prose
   (Panel C) barely dented accuracy (87.5–100%), while minimal-pair and synonym
   traps (Panels A, B) failed — the model has learned to quantify counts, not to
   recognise when a count fails to establish a habitual rate.

`gpt-4.1-mini` is weaker at exactly this judgment than full `gpt-4.1`, so a
mini-hybrid is expected to land at or below the 379 full-gpt figure.

## The cycles (all gated; `test450` never tuned on)

- **C1 — robustness battery built (the primary pre-test gate).** Current best
  `llm_only` candidate is **overfit**: Panel A 2/6 pairs, B 5/7, C 7/8. Finding:
  the wall is a genuine clinical gap.
- **C2 — triage-scaffold evidence change (v0.6).** Panel C → 8/8 with no rate
  regression, but diagnosed that the model now *reasons* correctly while
  `final_label` fails to bind to its reasoning.
- **C3 — bind label to the model's own `answer_kind`/triage (v0.7).** Battery went
  *perfect* (A 6/6, B 7/7, C 8/8, "transfers") — yet validation750 fell **−106**
  (469 vs 575) with `gap_robust = False`. The coerce-to-unknown rule over-demotes
  genuine-rate rows because mini emits `answer_kind=unknown` noisily across the
  full distribution.
- **Calibration holdout.** `llm_only` v0.5 on mini → **321/450 (0.713)**.

## The most important methodological result

**A curated robustness battery passing 100% is necessary but not sufficient.**
C3's candidate cleared every battery bar with a "transfers" verdict — a
battery-only workflow would have shipped it to the holdout — but the second gate
(held-out-family CV over the full validation distribution) caught a −106
regression. The two-tier gate (battery → family-CV → Freeze Warden) demonstrably
refused to promote an overfit candidate to the locked test set. This is the
durable, transferable contribution of the night, and it directly serves the goal
of generalising to unseen KCL data: small curated panels estimate transfer but
cannot certify it; the full-distribution gap test must sit behind them.

## What generalises to real KCL data

The **clinical principle** the battery encodes — *a reported event count does not
establish a habitual seizure frequency when the events are provoked/situational,
transient, descriptive, or adherence-confounded; last-event dates are not
seizure-free durations; clusters keep their cluster axis* — is distribution-
independent neurology and is the right target for KCL transfer. The v0.6 triage
scaffold (which improved OOD prose to 8/8 with no regression) and the
cluster-render and seizure-free-sharpening pieces of v0.7 were clean; only the
coerce-to-unknown step was too aggressive. A future gain, if pursued, lies in a
**confidence-gated** version of that binding, not in more selectors or agents.

## Recommendation

1. **Do not spend further `test450` holdout runs chasing 0.90** — the evidence is
   consistent and the target is out of reach for this model/architecture.
2. If a higher number matters, the only untested lever is the **hybrid/V12 family
   on gpt-4.1-mini**, measured on validation750 first (no holdout burn). Expected
   ≤ 0.84; decide whether the sizeable component-regeneration run is worth it.
3. Reframe the deliverable around what is real and generalisable: the clinical
   wall, the two-tier robustness methodology, and an honest accuracy ceiling — and
   carry the battery forward as the KCL-transfer gate when real letters arrive.
4. Consider a stronger model (full `gpt-4.1` or better) if the 0.90 target is hard
   requirement; the wall is partly a model-capability ceiling.

## Update — optimization campaign on the corrected premise (C4–C7)

After the model-label correction (gpt-4.1 ≡ gpt-4.1-mini; 379/450 is the mini
hybrid baseline), the goal became a +26-row optimization of the V12 hybrid, driven
by comprehensive row-level error analysis. Four more cycles, all gated:

- **C4 — row-level analysis** (`gan2026_hybrid_rowlevel_error_analysis_2026-06-16.md`):
  17 validation errors → 6 selector-addressable, 11 component-generation-required,
  in 4 clinical mechanisms (seizure-free over-inference, provoked/transient count,
  cluster flattening, window error). Validation under-samples these vs test.
- **C5 — triage scaffold in the fresh-evidence reasoner**: validation 601/750
  (−81), gap_robust False, 73 genuine-rate regressions. Confidence gate too loose;
  same over-withholding failure as C3.
- **C6 — narrow cluster-axis retention gate**: gap-robust, +1 validation, zero
  regressions — but **+0 on test** (the tightened phrasing matches no test row).
  Clinically clean, no lift.
- **C7 — KG family-gated graph-trust (the strongest lead)**: the KG `resolve_label`
  generator mints the correct `unknown` for all 7 target residual rows, but a
  corroboration-free harvest leaks **121 genuine-rate regressions** (−113). The
  reason is a **structural impossibility**: the harvested rows are feature-identical
  to the genuine-rate casualties on every inference-time signal; the "ontology-guard
  families" are post-hoc gold-keyed categories, not a selection-time signal.

### Sharpened verdict (corrected premise)

The +26-row gap to 0.90 is **not closable via selection/component fixes on
gpt-4.1-mini**. Across six attempts (C3, C5, C6, C7, prior v0.10, v0.6) every fix
to the unknown-over-reading residual fails in the same direction, and C7 proves
why: on the binding rows, the information distinguishing *withhold-to-unknown* from
*emit-rate* is **absent from every forward-observable feature** — only the hidden
gold separates them. No gate, model, or knowledge-graph can exploit it gold-free.
**379/450 (0.842) is the honest ceiling for this architecture family on mini.**

The one unrefuted path to >0.90: a genuinely **stronger model** that reads the
provoked/transient/adherence cues directly from the note *prose* (the discriminating
information is in the text, just not in the current features and not reliably
emitted by mini). Since gpt-4.1 and gpt-4.1-mini are synonymous here, that means a
different/frontier model — which changes the stated gpt-4.1-mini constraint.

## Accepted outcome (2026-06-16)

Decision: **accept 379/450 (0.842) as the honest ceiling** for the V12 hybrid on
gpt-4.1-mini and consolidate. The 0.90 target is not pursued further on mini, on
the strength of the C7 structural finding and the six-attempt evidence chain. The
deliverables of this work are the structural localisation of the wall, the
generalisable clinical principle, the two-tier robustness methodology, and the
reusable workflow — not a higher accuracy number.

The single unrefuted route to >0.90 (a stronger/frontier model that reads
provocation/transience/adherence cues from note prose) is recorded for the future
but deliberately not taken now, as it changes the gpt-4.1-mini constraint.

Implications for the King's College London transfer goal: because the
discriminating signal for these residual cases is not in any inference-time feature
even on clean synthetic data, real KCL letters will not be easier on this axis. The
robustness battery and the clinical triage principle are the right instruments to
carry forward; the unknown-vs-rate residual should be treated as a known,
documented limitation rather than a solvable gap at this model capability.

## Reusable assets produced

- Dynamic workflow: `.claude/agents/gan2026-*.md` (6 specialists),
  `/gan2026-f1-cycle` command, protocol + resumable scoreboard.
- Robustness battery v1: predeclaration, 27 cases, driver, live mini results.
- Additive labeler prompt versions v0.6 (triage scaffold) and v0.7 (label
  binding), with v0.5 still the module default.
- Calibration holdout driver + first mini `test450` datapoint.
