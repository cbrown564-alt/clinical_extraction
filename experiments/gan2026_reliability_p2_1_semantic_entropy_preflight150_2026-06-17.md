# P2.1 — Semantic Entropy over Multi-Sampled Structured Events (preflight150)

Date: 2026-06-17  ·  Model: openai/gpt-4.1-mini  ·  k=4 @ temps [0.3, 0.5, 0.7, 1.0]  ·  n=150

> **DECISION-STABLE UNDER TEMPERATURE** (not a caching artifact): raw model prose genuinely varies across temperatures (different text/length), but the rendered Purist label and selected kind do NOT move (mean entropy < 0.02). Semantic entropy is uninformative because the *decisions* are stable, not because sampling failed.

- Mean label (Purist) entropy: 0.012; mean kind entropy: 0.003
- Rows with non-zero label entropy: 4/150
- **Residual** (band_unknown ∪ seizure_free_duration), n=23: mean label entropy 0.018, kind entropy 0.018
- **Non-residual**, n=127: mean label entropy 0.011, kind entropy 0.000

## Per-band mean entropy

| Band | n | Label entropy | Kind entropy |
|---|---:|---:|---:|
| band_daily | 16 | 0.025 | 0.000 |
| band_monthly | 35 | 0.000 | 0.000 |
| band_submonthly | 16 | 0.000 | 0.000 |
| band_unknown | 15 | 0.000 | 0.000 |
| band_weekly | 55 | 0.018 | 0.000 |
| band_zero | 13 | 0.031 | 0.031 |

**Hypothesis verdict: `H0_confident_over_reading`.**

---

**Reading (H0 — the wall is real, with a mechanism).** Varying-temperature entropy is ~0 everywhere, and the residual (n=23, label entropy 0.0176) is no more uncertain than the rest (non-residual 0.0111); `band_unknown` is perfectly stable. Because the raw prose DOES vary while the decision does not, this is genuine decision-stability: the documented over-reading is CONFIDENT, not uncertain. That is the strongest version of The Wall — the model commits to the same (often wrong) category across temperatures, which is exactly why no forward-observable abstention signal (self-confidence, self-consistency, OR sampling entropy) can catch it. A publishable null that converts the closeout's negative result into a mechanism.
