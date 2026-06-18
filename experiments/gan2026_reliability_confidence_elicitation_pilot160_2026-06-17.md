# Confidence-Elicitation Calibration Probe (pilot160)

Date: 2026-06-17 · Model: openai/gpt-4.1-mini (elicitation temp 0.0) · n=160 · subject: v0_reference single-SE-mini production answers (decision 0018)

Decoupled second-pass elicitation over the production answers; the production path is NOT modified. Predeclared in ``.

**[comparator] degenerate joint self-confidence** (direct labeler): top-bucket share 99.9% (n=750), failure AUROC 0.503. External-signal comparator AUROC (P0.3) = 0.781.

| Variant | n | top-bucket share | mean p | std p | ECE | Brier | failure AUROC | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| C second-reader | 160 | 40.6% | 0.856 | 0.089 | 0.070 | 0.081 | 0.611 | `H0_irrecoverable` |
| D failure-primed | 160 | 78.1% | 0.878 | 0.138 | 0.069 | 0.073 | 0.755 | `H0_irrecoverable` |

## Residual sensitivity (does confidence drop where the model is wrong?)

| Variant | residual n | residual mean p | residual acc | non-resid mean p | non-resid acc |
|---|---:|---:|---:|---:|---:|
| C second-reader | 80 | 0.846 | 90.0% | 0.866 | 95.0% |
| D failure-primed | 80 | 0.859 | 90.0% | 0.896 | 95.0% |

## Reading

**Strict predeclared gate: H0 on both variants** (no single variant clears BOTH top-bucket < 70% AND AUROC ≥ 0.65). But the two axes came apart, and the conjunctive gate conflated *spread* with *usefulness* — the decomposition is the actual finding:

- **Baseline is dead** — joint self-confidence AUROC is at chance (0.503); any lift over that is real signal recovered by re-asking.
- **Spread recovered by C (second-reader framing)**, but it is largely *noise*: confidence is lowered on rows that are often still correct, so AUROC stays weak. Spread ≠ signal.
- **Discrimination recovered by D (failure-mode priming)** — AUROC approaches the external-corroboration signal (0.781) while staying high-valued on average. Its low-confidence bins are genuinely error-enriched. This is a *partial crack in the wall*: a forward-observable SELF-signal that ranks errors, obtained from one extra mini call (cheaper than 3-model agreement). The lever is **naming the failure mode**, not merely decoupling.
- **Caveat:** only {'C': 12, 'D': 12} failures in this stratified subset → AUROC CIs are wide; validation750 is required to confirm the discrimination number.

Net: self-confidence is not *irrecoverable* (the closeout's strong null is softened) — but recovery comes from priming the known failure mode, and even then leaves residual failures hidden at high confidence, so external corroboration (P0.2/P0.3) remains the stronger signal.
