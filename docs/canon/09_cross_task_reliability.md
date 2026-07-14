# 09 — Reliability across tasks

Last updated: 2026-07-14

| Component removed | ExECT dev140 score change | Gan validation750 score change |
| --- | ---: | ---: |
| Exact-evidence check | 0.0000 | 0.0000 |
| Normalization and shared dictionary | +0.0389 | +0.0293 |

These are development replays of saved outputs. No score change does not make
the evidence check unnecessary; rejection and repair still require direct
tests.

Gan retains aggregate evidence for grounding, calibration, review routing,
consistency, distribution shifts, and runtime behavior. ExECT retains the
internal calibration probe and three-model results. No selected ExECT report
tests the Gan unknown-versus-rate problem or broad self-consistency.

Cross-task overconfidence, out-of-sample confidence, and low-burden review
policies remain open. Every final reliability result must state its dataset,
split, model, scorer, repair policy, and row-inspection rule.
