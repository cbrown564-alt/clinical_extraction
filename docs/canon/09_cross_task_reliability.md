# 09 — Reliability across tasks

Last updated: 2026-07-15

| Component removed | ExECT dev140 score change | Gan validation750 score change |
| --- | ---: | ---: |
| Exact-evidence check | 0.0000 | 0.0000 |
| Normalization and shared dictionary | +0.0389 | +0.0293 |

These are development replays of saved outputs. No score change does not make
the evidence check unnecessary; rejection and repair still require direct
tests.

Gan retains aggregate evidence for grounding, calibration, review routing,
consistency, distribution shifts, and runtime behavior. ExECT retains the
internal calibration probe and historical three-model results. Their
Prescription and Seizure Frequency columns do not form a consistent model-led
comparison. No selected ExECT report tests the Gan unknown-versus-rate problem
or broad self-consistency. The
historical DeepSeek result has no recorded thinking state and is audit-only;
the final paper will report only thinking-enabled DeepSeek V4 Flash.

The frozen ExECT confidence replay evaluated the three historical model outputs
on aggregate-only test60. Failure AUROC was 0.5394 for GPT-4.1-mini, 0.5503 for
historical DeepSeek, and 0.4895 for Qwen. Neither predeclared routing rule met
the catch-rate and burden gates, so the result is retained as negative evidence
and no confidence-based review policy is adopted. It does not establish a
cross-task confidence mechanism, deployment calibration, or a final DeepSeek
V4 Flash result.

Cross-task unknown-versus-rate overconfidence remains open. Every final
reliability result must state its dataset, split, model, scorer, repair policy,
and row-inspection rule.
