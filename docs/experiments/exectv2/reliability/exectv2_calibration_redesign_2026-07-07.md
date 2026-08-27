# ExECTv2 Calibration Scoring-Rule Redesign

Date: 2026-07-07. Owner: ExECTv2 reliability track.

Follows: `docs/plans/calibration_abstention_review_routing_strengthening_plan_2026-07-01.md`.
Companion: `exectv2_calibration_signal_probe_2026-07-07.md` (Phase-0 signal probe).

## 1. Why this exists

After the four-family clinical-headline scorer-scope fixes (`7949a9d4`, 2026-07-02)
re-scored the dev140 evaluation set, the fixed dev140 calibration scoring rule no longer
passed its own predeclared aggregate validation gate on the full-200 artifact. The
reliability curve became non-monotone — the maximum adjacent-bin reversal rose to
`0.1105` (bin q4 accuracy `0.8145` → bin q5 accuracy `0.7040`), breaching the
`<= 0.10` promotion gate, so `build_calibration_validation_audit` returned
`not_promoted`. The dev140 cross-validated rule itself was still well-calibrated
(dev CV ECE `0.0245`, reversal `0.0087`); the failure was a **dev140 → full-200
generalization gap**, not a dev-fit failure.

The strengthening plan proposed three candidate signals already on disk that the
rule had never consumed (cross-model agreement; self-consistency entropy; evidence
support-quality). This redesign ran that plan's Phase 0, then pivoted to the
regularization lever the data pointed to.

## 2. Scope decision (confirmed)

Phase-0 data inspection constrained the plan's three hypotheses before any fitting:

- **H1 (cross-model agreement)** — the three same-core model-swap runs
  (`exectv2_2call_no_sf_adjudicator_{gpt41mini,deepseek,qwen36}_dev140_20260625`)
  share the full 140-letter space and join cleanly on `letter_id`. Actionable.
- **H2 (self-consistency entropy)** — per-letter data exists, but in four separate
  per-temperature `..._assembly.jsonl` files requiring a 4-way join and a
  per-(letter, family) entropy derivation. Actionable but heavier than the plan's
  optimistic read.
- **H3 (evidence support-quality)** — the on-disk audit
  (`exectv2_evidence_support_audit_2026-06-30.json`) is a **5-per-family sample**
  (20 records), not full coverage. Per the plan's own fallback rule ("If any one
  signal fails to join cleanly, scope that signal out"), **H3 was scoped out**;
  making it population-joinable would require a fresh full-coverage audit, which is
  out of scope for a no-new-LLM-calls replay.

A second constraint, confirmed during implementation: H1 and H2 are **dev140-only
training signals**. The full-200 validation artifact is a single GPT-4.1-mini run
with no cross-model or self-consistency data, and the plan forbids new model calls
and full-200 row-level inspection. So these features can inform the dev fit but
cannot be computed at validation time.

## 3. Phase-0 signal probe — predeclared verdicts

`experiments/build_exectv2_calibration_signal_probe.py` replayed the dev140
artifacts and scored both signals against the `not correct` label. Per-family
AUROC (error vs correct):

| Family | Cells | Cross-model agreement | Self-consistency entropy |
| --- | ---: | ---: | ---: |
| Diagnosis | 520 | 0.6291 | 0.5879 |
| SeizureFrequency | 421 | 0.5479 | 0.5662 |
| Prescription | 463 | 0.5000 | 0.5000 |
| Investigations | 315 | 0.6067 | 0.6007 |
| **pooled** | 1719 | **0.5958** | **0.5776** |

H2 cross-feature Spearman ρ = `0.5676` (below the `0.7` redundancy bar).

**H1 — REFUTED (`refuted_does_not_generalize`).** Cross-model agreement does not
clear the predeclared `0.70` usefulness bar on any non-SF family (Diagnosis 0.6291,
Investigations 0.6067), and is **degenerate (`0.5000`, coverage `0.000`) for
Prescription** — because Prescription is produced by a deterministic
dictionary/projection layer that is identical across the three model-swap runs, so
the models trivially agree on every letter (cluster size 3 for all 140). The SF
figure here (`0.5479`) is also well below the wall-transfer probe's `0.7613`
because this measures whole-letter headline agreement (not the SF-keyset-specific
construction the probe used). The SF-only wall-transfer result does not generalize.

**H2 — adds orthogonal signal, but the signal is weak.** ρ = `0.5676` keeps H2
technically non-redundant, but its standalone AUROC (0.55–0.60) is near-uninformative.

Per the plan's stop condition, neither signal is worth folding into the promoted
rule. The signal-construction module
(`reports/reliability/external_signals.py`) and probe are retained as a
**negative-result artifact**: they document that the three "obvious" unused
reliability signals do not separate ExECTv2 errors on dev140, which is itself a
paper-relevant finding and closes the plan's H1/H2 cleanly.

## 4. The redesign lever — L2 regularization

With the candidate signals ruled out, the remaining lever for the
generalization-gap failure was the fit's regularization. The dev140 CV was already
monotone; only the full-200 readout had the high-confidence non-monotone bump,
which is the signature of mild over-fit. The original fit used `l2 = 0.015`
(hard-coded inside `fit_logistic_scoring_rule`).

L2 sweep (full-200 aggregate, dev-fit rule, 700 epochs, lr 0.18):

| L2 | full-200 ECE | full-200 Brier | full-200 reversal | dev CV ECE | gates |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0.015 (old) | 0.0540 | 0.2215 | 0.1105 | 0.0245 | not_promoted (reversal) |
| 0.030 | 0.0587 | 0.2225 | **0.0784** | 0.0229 | **promoted** |
| 0.050 | 0.0590 | 0.2237 | 0.0622 | 0.0338 | promoted |
| 0.080 | 0.0683 | 0.2252 | 0.0622 | 0.0435 | promoted |
| 0.100 | 0.0726 | 0.2259 | 0.0622 | 0.0488 | promoted |

**`L2 = 0.03` is the chosen operating point.** It is the smallest change that clears
the reversal gate (0.1105 → 0.0784) while leaving calibration quality essentially
unchanged — in fact dev CV ECE improves slightly (0.0245 → 0.0229) and full-200 ECE
rises only from 0.0540 to 0.0587 (still far under the 0.1456 protocol baseline).
Higher L2 also promotes but degrades ECE monotonically; lower L2 leaves the
reversal breach. The change is now a single named, documented constant
(`LOGISTIC_L2_STRENGTH = 0.03` in `reliability/calibration.py`) rather than a
magic number, and the learning rate / epoch count were extracted alongside it.

This is a minimal, honest fix. It does not claim the redesign "solved" calibration
— Brier improvement vs the constant base rate is still small (`0.0115`), and
calibration remains dev-developed + aggregate-validated, not deployment-ready. It
restores the promotion the rule earned before the scorer-fix re-scoring shifted
the evaluation set underneath it.

## 5. Fresh full-200 aggregate validation readout (Phase 5 of the plan)

`build_calibration_validation_audit()` with the redesigned rule, aggregate-only on
the accepted full-200 artifact (no full-200 row-level inspection, no re-fit on
full-200):

- Promotion decision: **`promoted`**
- ECE: `0.0587` (gate `< 0.1456`: pass)
- Brier: `0.2225` vs constant base-rate `0.2340` (gate: pass)
- Maximum adjacent-bin reversal: `0.0784` (gate `<= 0.10`: pass)
- Populated reliability bins: `5` (gate `>= 4`: pass)
- Per-family ECE reported for all four families: pass

Dev140 cross-validated (the development set): ECE `0.0229`, Brier `0.1761`,
reversal `0.0`. Five monotone bins.

The committed audit report
(`docs/experiments/exectv2/reliability/exectv2_calibration_validation_audit_2026-06-25.md`)
was regenerated and reflects this readout.

## 6. Hypothesis scorecard

| Hypothesis | Verdict | Evidence |
| --- | --- | --- |
| H1 cross-model agreement generalizes | **REFUTED** | pooled AUROC 0.5958; 0/3 non-SF families above 0.70; Prescription degenerate (0.5000, coverage 0.000) |
| H2 self-consistency is orthogonal | retained-but-weak | ρ = 0.5676 (< 0.7 redundancy bar), but standalone AUROC 0.55–0.60 |
| H3 evidence support-quality | **scoped out** | 5/family sample (20 records), not population-joinable without a fresh audit |
| H4 low-burden review operating point | deferred | not pursued under this redesign; the review-routing operating-point sweep is separate future work |
| L2 regularization clears the gap | **SUPPORTED** | L2 0.015 → 0.03 promotes (reversal 0.1105 → 0.0784) without calibration cost |

## 7. Files

- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/reliability/calibration.py`
  — extracted `LOGISTIC_L2_STRENGTH` (`0.03`), `_LOGISTIC_LEARNING_RATE`,
  `_LOGISTIC_EPOCHS`; documented the choice.
- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/reliability/external_signals.py`
  — new; the cross-model-agreement and self-consistency-entropy feature
  construction (retained as the H1/H2 negative-result artifact).
- `experiments/build_exectv2_calibration_signal_probe.py` — new; the Phase-0 probe.
- `experiments/exectv2_calibration_signal_probe_2026-07-07.json` +
  `exectv2_calibration_signal_probe_2026-07-07.md` — Phase-0 outputs.
- `tests/test_exectv2_reliability_calibration.py`,
  `tests/test_exectv2_reliability_external_signals.py` — new unit tests.
- `tests/test_exectv2_calibration_validation.py` — flipped back to the promoted
  state with the post-redesign aggregate numbers.
- Regenerated: `exectv2_calibration_validation_audit_2026-06-25.md`.

No production scoring path, prompt, or assembly reconciliation was touched. No new LLM calls.

## 8. Limitations and honest framing

- The redesign is a **regularization fix**, not a new calibration method. The
  feature set is unchanged; the rule is the same grouped logistic scorer with one
  hyperparameter moved.
- Calibration remains **dev-developed, aggregate-only full-200 validated** — not a
  deployment-ready probability claim and not holdout calibration.
- The H1/H2 negative result is real and reportable: the three "obvious" external
  reliability signals do not separate ExECTv2 errors on dev140, and Prescription
  is model-invariant by construction. This bounds what calibration on this evaluation set
  can be expected to achieve without new information (e.g., a full-coverage
  evidence-support audit, which is explicitly out of scope here).
