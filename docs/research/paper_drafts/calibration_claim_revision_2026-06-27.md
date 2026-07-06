# Calibration Claim Revision

Date: 2026-06-27  
Workstream: Wave 2 · P4 (paper writing)  
Evidence validity: validation-only (aggregate `full-200`); no holdout rows read; no new model calls.  
Decision: revise — tighten language to match evidence; drop Qwen apologetic footnote.

---

## Purpose

This note revises the calibration claim in the ExECTv2 multi-entity phenotyping results
section to match what the evidence actually shows, consuming three inputs:

- **M2 audit findings** — `docs/experiments/reliability/evidence_validity_audit_2026-06-27.md`
  (Qwen REPAIRED_* characterisation)
- **ECE/Brier figures** — `docs/experiments/exectv2/reliability/exectv2_cross_model_reliability_scorecard_2026-06-22.md`
  §Calibration (dimension 4)
- **Critique brief** — `docs/research/closing_stage_research_critique_2026-06-27.md` §2 (calibration
  suspicion) and the Gan 2026 seizure-frequency reliability scorecard
  (`docs/experiments/gan2026/reliability/
  gan2026_reliability_scorecard_and_phased_plan_2026-06-17.md` §Calibration, P0.3) on external
  signal versus degenerate self-confidence

---

## Before Claim (current draft language)

> A grouped cross-validated no-call scoring rule scores 1,706 `dev140` candidate-family cells using
> only predeclared family, provenance, and evidence-ambiguity features grouped by `letter_id` to
> avoid train/test leakage; dev-only ECE is `0.0277` and Brier is `0.1774` versus `0.1874` for the
> grouped constant-base-rate comparator. The aggregate-only full-200 validation audit promotes the
> frozen scoring rule with ECE `0.0432`, Brier `0.2245` versus `0.2387` constant base-rate Brier,
> five populated monotone bins, and per-family ECE reported for Diagnosis (`0.1424`),
> SeizureFrequency (`0.1292`), Prescription (`0.1214`), and Investigations (`0.0925`).
> *(Footnote: Qwen's lower evidence-validity rate of `74.8%` exact on the validation surface is
> noted as a limitation of the Qwen comparator arm.)*

**Problems with the before claim:**

1. ECE `0.0432` sounds well-calibrated in isolation; the paired Brier improvement of `0.0142` (= `0.2387` − `0.2245`) is suppressed.
2. The claim does not state what *kind* of signal drives the scoring rule, leaving the reader to assume self-reported model confidence — which is degenerate on the Gan 2026 seizure-frequency strand and is not what the rule uses.
3. The Qwen footnote apologises for a 74.8% exact evidence rate as if it reflects model quality. The M2 audit establishes that 53.7% of Qwen hybrid and 61.4% of Qwen LLM-only exact-invalid strings are recoverable `REPAIRED_ELLIPSIS` formatting collation artifacts (grounded rates: 94.7% and 90.9% respectively). This framing misleads rather than informs.

---

## After Claim (revised language)

> The scoring rule's calibration is near-base-rate: aggregate full-200 validation Brier is
> `0.2245` versus constant base-rate `0.2387` (Δ = `0.0142`), ECE `0.0432`, five populated
> monotone bins. The improvement above the base rate is real but small; it should not be read as
> evidence of well-calibrated predictive confidence. The signal carried by the rule comes entirely
> from external, predeclared features — family identity, evidence-provenance indicators, and
> evidence-ambiguity flags — not from model-reported confidence scores, which were not used.
> This is consistent with the Gan 2026 seizure-frequency strand's finding that self-reported
> confidence is degenerate
> (749/750 validation rows "high", statistically indistinguishable buckets) and that only
> external corroboration carries calibration-relevant signal.
> Per-family ECE: Diagnosis `0.1424`, SeizureFrequency `0.1292`, Prescription `0.1214`,
> Investigations `0.0925`. The claim is bounded to the aggregate full-200 validation surface;
> holdout or external calibration confirmation has not been run.

---

## Qwen Footnote — Dropping and Replacement

**Drop:** any language presenting Qwen's `74.8%` (hybrid) or `76.5%` (LLM-only) exact evidence
rate as a model-quality limitation.

**Replace with (one sentence, if Qwen comparison must be mentioned):**

> Qwen's exact evidence rate on the raw substring metric is `74.8%` (hybrid) / `76.5%` (LLM-only)
> on the validation surface; the M2 audit shows `53.7%` and `61.4%` of those apparent failures are
> recoverable `REPAIRED_ELLIPSIS` copy-collation artifacts, bringing grounded rates to `94.7%` and
> `90.9%` respectively — the gap is a metric artifact of ellipsis formatting, not evidence absence.

If the Qwen arm does not need to appear in the calibration paragraph at all (it is already covered
in Dimension 10, Operational reliability, where its parse/schema failures are the real concern),
remove the footnote entirely without replacement.

---

## Evidence Validity Statement

All figures cited here carry the following validity label:
**validation-only (aggregate `full-200`); replay-only; no holdout rows inspected; no model calls.**

Specific artifact chain:

| Figure | Source artifact | Validity |
|--------|----------------|----------|
| Brier `0.2245`, ECE `0.0432`, base-rate `0.2387` | ExECTv2 reliability scorecard §Calibration (2026-06-22, refreshed 2026-06-25) | Aggregate full-200 validation |
| "External signal, not self-confidence" | Gan reliability scorecard §Calibration (2026-06-17) P0.3: "self-confidence is degenerate … define calibration score from external features" | Validation-only analysis of Gan artifacts; applied by analogy to ExECTv2 scoring rule architecture |
| Qwen exact 74.8% → grounded 94.7% (hybrid) | M2 audit `evidence_validity_audit_2026-06-27.md` §gan2026 Qwen hybrid row | Replay-only, 750 rows, 2125 strings |
| Qwen exact 76.5% → grounded 90.9% (LLM-only) | Same audit §gan2026 Qwen LLM-only row | Replay-only, 750 rows, 750 strings |
| REPAIRED_ELLIPSIS 53.7% / 61.4% of exact-invalid | Same audit: hybrid 130/242; LLM-only 108/176 | Replay-only |

---

## What Did Not Change

- The numeric ECE and Brier figures are unchanged; only their framing changes.
- The five-bin monotone structure is retained as supporting detail.
- Per-family ECE breakdown (Diagnosis / SF / Rx / Inv) is retained.
- The claim boundary ("aggregate full-200 validation; not deployment-ready probability;
  not holdout calibration") from the scorecard is preserved verbatim.
- No git operations; no model calls; no holdout rows read.

---

## Summary

**Before (2 sentences):** The scoring rule reached ECE `0.0432` and Brier `0.2245` versus
base-rate `0.2387` on aggregate full-200 validation; Qwen's lower evidence-validity rate (`74.8%`
exact) is noted as a limitation of the Qwen comparator arm.

**After (2 sentences):** The scoring rule is near-base-rate calibrated — Brier `0.2245` versus
constant base-rate `0.2387` (Δ = `0.0142`), ECE `0.0432` — with all signal coming from external
predeclared features (family, provenance, evidence-ambiguity indicators), not model-reported
confidence, which is degenerate on the Gan 2026 seizure-frequency strand and unused here.
The Qwen exact evidence gap (`74.8%` raw vs `94.7%` grounded) is a metric artifact of ellipsis-formatting collation
(`REPAIRED_ELLIPSIS` accounts for 53.7% of Qwen hybrid exact-invalid strings) and is not a
calibration limitation.
