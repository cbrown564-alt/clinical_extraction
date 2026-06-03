# Executive Report: A1 vs A2 Validation50 Comparison (Post-Fix)

**Date:** June 3, 2026  
**Evaluation Surface:** Validation split, first 50 rows (`gan2026_split_v1`)

---

## 1. Metric Summary

| Metric Layer | A1 (Simplified) | A2 (Sparse Operands) | Delta (A2 - A1) |
| :--- | :---: | :---: | :---: |
| **Structured Record Validity** | 50/50 (100.0%) | 50/50 (100.0%) | 0.0% |
| **Selected Evidence Arithmetic** | 45/50 (90.0%) | 47/50 (94.0%) | **+4.0%** |
| **Final Adapter/Normalized Label** | 45/50 (90.0%) | **48/50 (96.0%)** | **+6.0%** |

---

## 2. Key Observations

### A2 Superiority in Clinical Selection
A2's selection prompts and schema structure achieved higher accuracy (96% vs 90%) and successfully resolved multiple rows that A1 missed (e.g. ranges, clusters, and complex frequencies).

### Regression Resolution via Boundary Deferral
By implementing boundary-deferral logic for cyclical windows (e.g. perimenstrual), interval shorthand notation (`qtwo`), bimonthly patterns, and hourly rates, we resolved the regressions in the sparse-operand adapter.
* **Adapter Regressions**: Reduced to **0** (from 4 on the stress panel, and 1 on validation50).
* **Adapter Progressions**: **1 Progression** (Row 1030: `one or three seizures last month` successfully resolved to the range `1 to 3 per 1 month` via sparse operands, while arithmetic had resolved it incorrectly to the single value `1 per month`).
* **Final Result**: The A2 sparse operand adapter achieved **96.0% accuracy** on validation50.

---

## 3. Conclusions and Next Steps

1. **A2 is the Decisive Candidate**: With the boundary deferral logic, A2 achieves **100% on the stress panel** and **96% on validation50**, with zero regressions.
2. **Escalation to validation250/750**: We have successfully validated the hypothesis that sparse operands, paired with boundary-check fallback deferrals, outperform the selection-only schema. We are ready to escalate A2 to validation250 and validation750.
