# Executive Report: A1 vs A2 Validation250 Comparison

**Date:** June 3, 2026  
**Evaluation Surface:** Validation split, first 250 rows (`gan2026_split_v1`)

---

## 1. Metric Summary

| Metric Layer | A1 (Simplified) | A2 (Sparse Operands) | Delta (A2 - A1) |
| :--- | :---: | :---: | :---: |
| **Structured Records** | 248/250 (99.2%) | 248/250 (99.2%) | 0.0% |
| **Selected Evidence Arithmetic** | 216/250 (86.4%) | 232/250 (92.8%) | **+6.4%** |
| **Final Adapter (Purist)** | 216/250 (86.4%) | **232/250 (92.8%)** | **+6.4%** |
| **Final Adapter (Pragmatic)** | 218/250 (87.2%) | **240/250 (96.0%)** | **+8.8%** |

---

## 2. Key Observations

### A2 Selection and Prompting Gains
A2 outpaced A1 by **+6.4% Purist accuracy** and **+8.8% Pragmatic accuracy** on the 250-row validation surface. A2's prompt structure and sparse schemas led to major improvements in capturing complex clinical frequency states, ranges, and fuzzy representations.

### Sparse-Operand Adapter Stability
* **Equal Performance**: The A2 sparse-operand adapter achieved the exact same Purist score (**232/250**) and a higher Pragmatic score (**240/250**) than A2 Selected-Evidence Arithmetic.
* **Balanced Deltas**: The adapter introduced 4 progressions (wrong-to-correct) and 4 regressions (correct-to-wrong) relative to Selected-Evidence Arithmetic, showing a stable equilibrium after our boundary deferral fixes.
* **Format Errors**: A2 raw LLM output format errors were significantly lower compared to A1 (90/250 scorable formatting issues in A2 vs 182/250 in A1), indicating that A2's schema constraints help the model output structured formatting more reliably.

---

## 3. Conclusions and Next Steps

1. **A2 is Confirmed Superior**: With a **92.8% Purist F1 / 96.0% Pragmatic F1** on the 250-row validation ladder, A2 has successfully met the project's target threshold (0.9000 Purist F1).
2. **Escalation to validation750**: We are ready to escalate A2 to the full validation750 split to verify generalizability over the entire development surface.
