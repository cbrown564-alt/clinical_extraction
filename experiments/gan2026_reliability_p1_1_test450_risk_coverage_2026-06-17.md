# P1.1 — Frozen test450 Risk-Coverage Replay

## Aggregate-Only Holdout Readout

Date: 2026-06-17  ·  Split: test450 (frozen holdout)  ·  Model calls: 0

_frozen aggregate-only holdout readout; no row-level test inspection._

**Asymmetry.** Two-agent agreement leg ONLY (gpt-4.1-mini + qwen); the validation three-leg / three-agent External Risk Score has no no-call holdout equivalent. Strictly weaker replay than P0.2.

Frozen transform `two_agent_external_risk` sha256 `c949130be583a78f…` (predeclared before touching test450).

- Base error rate: 19.1% (CI 15.7%–23.0%)
- **Agree-only operating point:** coverage 65.8%, selective risk 12.2% (CI 8.9%–16.4%)
- Disagree set: 34.2% of rows, error rate 32.5%
- **Two-agent external-score AUROC for failure: 0.6478**

[comparator: P0.2 validation750, 3-leg/3-agent] AUROC 0.781, AUC 0.040; the holdout port is weaker by construction.

---

**Reading.** Even the weakened two-agent agreement leg separates holdout error: abstaining on the agent-disagreement set lifts selective accuracy on the covered majority. The holdout AUROC is below the validation 0.781 precisely because the two stronger legs (third agent + residual-shape flags) are unavailable no-call on the locked split — the abstention signal is real but degrades gracefully, as decision 0018 predicted.
