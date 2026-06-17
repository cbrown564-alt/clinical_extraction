# P0.8 — Hard50 Self-Consistency Re-Tabulation (Consistency, partial)

Date: 2026-06-17  ·  n=50 hard rows  ·  k=4 samples @ temp 0.0  ·  Model calls: 0

## Agreement ↔ accuracy curve

| Majority (top/k) | n | Correct | Accuracy |
|---|---:|---:|---:|
| 4/4 | 45 | 31 | 68.9% |
| 3/4 | 3 | 3 | 100.0% |
| 2/4 | 2 | 0 | 0.0% |

> **Temperature caveat.** All samples are temp-0, so this measures reproducibility/determinism, not self-consistency. Genuine self-consistency needs VARYING temperatures (P2.1). The reproducibility-conditioned reading below is what survives that caveat.

- **Temp-0 unanimous (4/4) accuracy: 68.9%** — even fully reproducible hard rows are wrong ~31% of the time, so reproducibility ≠ correctness.
- Temp-0 self-agreement AUROC: 0.5239 (uninformative *at temp-0*; no conclusion drawn about varying-temperature self-consistency).
- Temp-0 non-determinism: **5/50** rows disagree across identical-temperature samples.
- Mean normalized label entropy: 0.044

_All samples temp-0 -> measures reproducibility, not self-consistency. Genuine self-consistency / semantic entropy requires VARYING temperatures and is P2.1 (fresh mini budget). n=50 hard slice._

---

**Reading.** This artifact establishes only that the production path is largely *reproducible* at temp-0, and that reproducibility does not imply correctness (unanimous hard rows wrong ~31%). The genuine self-consistency / semantic-entropy question — does answer instability under VARYING temperature flag the unknown-vs-rate residual? — is deferred to P2.1, which samples at multiple temperatures.
