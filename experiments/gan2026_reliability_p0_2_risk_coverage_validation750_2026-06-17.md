# P0.2 — Risk-Coverage / Selective-Prediction Curve (HEADLINE)

Date: 2026-06-17  ·  Split: validation750  ·  Model calls: 0

**Predeclared External Risk Score** (frozen before scoring; higher = riskier):

`risk = 3*(3-agreement) + source_flag_count + ambiguity_reason_count`

- agreement from consensus_decision.votes (gpt-4.1-mini+qwen+deepseek)
- source residual flags: source_has_last_event_language, source_has_since_anchor, source_has_trigger_language, source_has_drop_attack_language, source_has_unable_to_quantify
- scored against `v0_reference.comparison.purist_correct` (canonical subject, decision 0018)

Base error rate: **89/750 = 11.9%**. The curve rests on only 89 error events, so every operating point carries a 95% Wilson CI.

## Headline numbers

- **AUC (selective risk vs coverage):** 0.0404 (lower is better; oracle 0.0073, random ≈ 0.1187)
- **AUROC of external score for predicting error:** 0.7806
- **Plateau (safest rows, coverage 0.16):** selective risk 0.8% (CI 0.1%–4.5%)

## Risk at fixed coverage

| Coverage | Selective risk | 95% CI |
|---:|---:|:--|
| 100% | 11.9% | 9.7%–14.4% |
| 95% | 10.8% | 8.7%–13.3% |
| 90% | 9.9% | 7.8%–12.3% |
| 80% | 7.8% | 5.9%–10.1% |
| 70% | 6.6% | 4.8%–9.0% |
| 50% | 3.0% | 1.7%–5.1% |

## Operating points (step function)

| Risk ≤ | Covered | Coverage | Sel. errors | Selective risk | 95% CI |
|---:|---:|---:|---:|---:|:--|
| 0 | 121 | 16.1% | 1 | 0.8% | 0.1%–4.5% |
| 1 | 271 | 36.1% | 6 | 2.2% | 1.0%–4.7% |
| 2 | 405 | 54.0% | 12 | 3.0% | 1.7%–5.1% |
| 3 | 478 | 63.7% | 22 | 4.6% | 3.1%–6.9% |
| 4 | 547 | 72.9% | 36 | 6.6% | 4.8%–9.0% |
| 5 | 631 | 84.1% | 49 | 7.8% | 5.9%–10.1% |
| 6 | 679 | 90.5% | 67 | 9.9% | 7.8%–12.3% |
| 7 | 715 | 95.3% | 77 | 10.8% | 8.7%–13.3% |
| 8 | 740 | 98.7% | 85 | 11.5% | 9.4%–14.0% |
| 9 | 745 | 99.3% | 86 | 11.5% | 9.4%–14.0% |
| 10 | 748 | 99.7% | 88 | 11.8% | 9.6%–14.3% |
| 11 | 749 | 99.9% | 88 | 11.7% | 9.6%–14.3% |
| 12 | 750 | 100.0% | 89 | 11.9% | 9.7%–14.4% |

---

**Reading (falsification test of The Wall).** The external score ranks errors above the diagonal (AUROC 0.781). The recoverable error is the drop in selective risk as coverage falls from 100%; the irreducible residual is the plateau the score cannot shed. If the plateau CI excludes zero, the residual is empirically real: errors leak into the low-risk region precisely because the documented over-reading is *confident*, which is why no forward-observable abstention signal catches it.
