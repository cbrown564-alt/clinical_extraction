# 09 — Reliability across tasks

Last updated: 2026-07-18

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
comparison. No selected ExECT report tests broad self-consistency. The
historical DeepSeek result has no recorded thinking state and is audit-only;
the final paper will report only thinking-enabled DeepSeek V4 Flash.

The predeclared six-model ExECT `dev140` over-inference replay found that the
Gan unknown-only denominator has no ExECT counterpart under the fixed
change-aware state transform: zero gold letters have the state set
`{unknown}`. The 41 empty-gold letters remain a separate diagnostic because
the ExECT annotation synthesis documents omission and representation effects.
They cannot be relabelled as unknown after observing the result.

The same replay supplies bounded component evidence. Deterministic SF
projection and suppression improve state-profile F1 for all six models, with
54 wrong-to-correct and one correct-to-wrong transition across the six
model-letter panels. These pooled transition counts are descriptive because
each model is evaluated on the same 140 letters. See the
[protocol](../experiments/exectv2/reliability/exectv2_six_model_sf_overinference_protocol_2026-07-18.md)
and [result](../experiments/exectv2/reliability/exectv2_six_model_sf_overinference_2026-07-18.md).

The frozen ExECT confidence replay evaluated the three historical model outputs
on aggregate-only test60. Failure AUROC was 0.5394 for GPT-4.1-mini, 0.5503 for
historical DeepSeek, and 0.4895 for Qwen. Neither predeclared routing rule met
the catch-rate and burden gates, so the result is retained as negative evidence
and no confidence-based review policy is adopted. It does not establish a
cross-task confidence mechanism, deployment calibration, or a final DeepSeek
V4 Flash result.

Cross-task unknown-versus-rate overconfidence remains unsupported and is not
measurable from the current ExECT gold under the predeclared primary metric.
Answering it would require a separately governed annotation or clinical-review
substrate, not reuse of empty-gold rows. Every final reliability result must
state its dataset, split, model, scorer, repair policy, and row-inspection rule.
