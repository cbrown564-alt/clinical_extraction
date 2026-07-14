# Gan 2026 — Master Reliability Scorecard (Phase 0)

Date: 2026-06-17  ·  Phases 0-2 complete (P2.1 varying-temperature semantic entropy run)  ·  Model calls: 0

Subject: the selected single GPT structured-event pass on gpt-4.1-mini
(`v0_reference`, decision 0018).

Every metric below is computed for that subject unless tagged
`[comparator: ...]`. The P0.1–P0.8 drivers re-derived the figures from saved
outputs. Each number remains tied to the method and data named in its row.

| # | Dimension | Cov. | Computed metric (Phase 0) |
|---|---|:--:|---|
| 1 | **Task correctness** | 4/5 | Subject Purist 0.881 val / 0.809 test (v0_reference); risk-coverage AUC 0.0404. |
| 2 | **Factuality (over-inference)** | 3/5 | Unknown-gold over-read rate 0.094 val / 0.127 test. |
| 3 | **Faithfulness** | 5/5 | Faithfulness rate 0.921 val / 0.929 test (subject); faithful-but-wrong 80 val / 80 test [comparator V12-full-gpt4.1: 703/750, 423/450 exact]. |
| 4 | **Calibration** | 3/5 | Self-confidence degenerate (99.2% one bucket); external-confidence ECE 0.080, Brier 0.102, failure AUROC 0.781. |
| 5 | **Abstention** | 5/5 | Full risk-coverage curve: AUC 0.0404 (oracle 0.0073); selective risk 3.0% @ 50% coverage, 7.8% @ 80%. |
| 6 | **Robustness** | 4/5 | Continuous index: direct_labeler_v0_5 0.547, evidence_v0_6 0.694, evidence_v0_7 1.000 (overfit-gap is the diagnostic leg). |
| 7 | **Consistency** | 4/5 | P2.1 varying-temperature (0.3/0.5/0.7/1.0) semantic entropy, n=150 (23 residual): mean label entropy 0.012, residual 0.018 (band_unknown 0.000); raw prose varies, decisions do not -> `H0_confident_over_reading`. [also: hard50 temp-0 unanimous acc 0.689] |
| 8 | **Safety & compliance** | 4/5 | 0 C→W selective floor (RQ6); abstain-to-unknown gate v0_9; canaries + hash pinning + aggregate-only readout guard; PHI/demographic evals N/A on synthetic. |
| 9 | **Fairness (clinical family)** | 3/5 | Per-band error spread 7.8%, CV 0.032; worst subgroup seizure_free_duration. |
| 10 | **Operational reliability** | 4/5 | 0 model render failures / 5483 recoverable repairs across 1950 rows; offline est ~$1.16/1000 notes; latency+retry still blocked (P2.2). |

## Coverage upgrades earned in Phase 0

- **Calibration** — upgraded 2/5 -> 3/5: real ECE/Brier/AUROC now exist on external signals.
- **Abstention** — upgraded 4/5 -> 5/5: three operating points -> full curve.
- **Consistency** — 2/5 -> 4/5: P2.1 supplies a genuine varying-temperature semantic-entropy measurement (H0: decisions are temperature-stable; the over-reading residual is confident, not uncertain).
- **Operational reliability** — upgraded 3/5 -> 4/5: cost/token leg reconstructed offline.

---

**Interpretation.** The P0.2 risk–coverage curve supplies an abstention curve
(AUC 0.040 versus oracle 0.007) and a failure-prediction AUROC of 0.781 for the
external confidence score used in this Gan study. Model-reported confidence
was concentrated in one bucket, and the P2.1 sample had near-zero decision
entropy, including on its 23 residual cases. Within these saved validation and
holdout aggregates, those self-reported signals did not distinguish the
observed errors. The external score was more informative in this study, but
the report does not establish that every external signal is reliable or that
model confidence is uninformative on other tasks, models, or data.
