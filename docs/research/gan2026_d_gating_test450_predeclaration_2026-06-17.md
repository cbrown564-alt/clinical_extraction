# Gan 2026 — Variant-D Gating on Frozen test450 (Predeclaration)

Date: 2026-06-17

Predeclared, freeze-warden-gated contract for answering one question on the locked
holdout: **is the variant-D calibrated confidence practically useful as an abstention
gate on the primary single gpt-4.1-mini architecture?** Predeclared before any test450
reviewer call so the result — including a null — is admissible.

Extends the validation750 evidence:
`experiments/gan2026_reliability_d_gating_value_validation750_2026-06-17.md` and the
shadow-run / pilot artifacts. Builds on the freeze-warden pattern of P1.1
(`build_gan2026_reliability_p1_1_test450_risk_coverage.py`).

## Subject (decision 0018)

The canonical single-SE-mini answers read per-row from the `v0_reference` layer of
`gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl`
(`final_label`, `final_kind`, `comparison.purist_correct`). No new SE call is made;
the SE answers already exist on the holdout.

## What is run on test450

The **decoupled variant-D confidence reviewer** (`agentic/confidence_reviewer.py`,
`variant_D_decoupled_v1`) issues one `gpt-4.1-mini` call per test450 row, given only
the note text + the stated `v0_reference` answer (blind to the model's own rationale),
returning `calibrated_confidence`. Risk = `1 − calibrated_confidence`. ~450 live
reviewer calls; resumable; checkpointed.

This is a **live holdout model run**, so it is freeze-warden gated: certification +
`frozen_test_preflight` contamination canaries before the calls, and an aggregate-only
readout after.

## Frozen transforms (hashed before touching test450)

Both are deterministic and already committed; their source SHA-256 is recorded in the
output artifact so they are frozen by hash:

1. **D reviewer** — `confidence_reviewer.py` (`VARIANT_D_INSTRUCTIONS` + parse).
2. **Gating readout** — the gating-table function + the predeclared coverage grid
   `{0.95, 0.90, 0.80, 0.70, 0.50}` + `risk = 1 − calibrated_confidence`.

## Aggregate-only metrics (no per-row leaves the readout)

Forbidden in output: per-row tables, `source_row_index`, `transition_vs_v0`,
`score_layers`. Per-row correctness is read internally only to form aggregates.

- Base accuracy + 95% Wilson CI (the no-gate operating point).
- For each predeclared coverage: **selective accuracy** + Wilson CI, **abstention
  precision** (error rate among abstained rows), the **random-abstention bar**
  (= base error rate), and the lift over it; errors shed.
- D **failure-prediction AUROC** for the whole set.

## Predeclared success criterion

D gating is judged **practically useful on test450** iff, with honest CIs:

- **(i)** failure-prediction AUROC is clearly above chance (CI lower bound > 0.5), AND
- **(ii)** at the 90% operating point the abstention precision materially exceeds the
  base error rate (the gate beats random abstention), AND
- **(iii)** the selective-accuracy lift over base is positive and (approximately)
  monotone across the coverage grid.

**Validation comparator** (`[comparator: validation750]`): base acc 0.884, AUROC 0.684;
at 90% coverage selective acc 0.905, abstention precision 0.307 vs random 0.116 (2.6×).
The holdout question is whether this pattern survives at test450, with the val→test gap
itself a finding.

## Asymmetry vs P1.1 (a feature, not a caveat)

P1.1's external score degraded on test450 (3-agent → 2-agent, residual-shape legs
unavailable no-call), so its holdout port was strictly *weaker* than validation. The
variant-D signal is **single-model and computed live the same way on both splits** —
no degradation by construction. This is therefore an apples-to-apples holdout test of
the identical mechanism, the cleanest read available, and the one that matters for the
primary single-model architecture (which cannot use cross-model corroboration at all).

## Decision rule

- Meets (i)–(iii) → variant D is a usable gate for the single-model deployment; report
  the holdout operating points. Still does not change champion/robustness status (it is
  a triage knob, not a label change).
- Fails → the validation benefit does not generalize; D stays a shadow-only signal and
  the gate is not recommended. Either outcome is reported as the answer.

## Artifacts

- Driver: `experiments/build_gan2026_reliability_d_gating_test450.py` (live, resumable,
  aggregate-only).
- Output: `gan2026_reliability_d_gating_test450_2026-06-17.{json,md}` + resumable
  per-row reviewer sample file (internal; not part of the readout).
