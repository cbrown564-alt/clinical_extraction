# Gan 2026 Rules-Only Phase G1–G5 Remeasure & Fairness Plateau Closure

**Date**: 2026-08-15  
**Datasets & Splits**:
- Gan 2026 `validation` (750 development records, `dev750`)
- Gan 2026 `test` (450 locked holdout records, `test450` — evaluated aggregate-only)  
**Method**: `deterministic_canonical_pipeline` (Rules-Only)  
**Governance**: [Decision 0046](../../decisions/0046-exect-primary-method-comparison-boundary.md); peer [E5 remasure](../exectv2/rules_only_campaign_e5_remeasure_2026-08-15.md)  
**Machine-Readable Artifact**: [`experiments/gan2026_rules_only_residual_catalog_dev750_20260815.json`](file:///Users/cobro/code/clinical-extraction/experiments/gan2026_rules_only_residual_catalog_dev750_20260815.json)

---

## 1. Executive Summary & Verdict

1. **Exhaustive Residual Catalog (Phase G0)**:
   - On `dev750`, the active portable rules-only baseline achieves **0.9080** Purist accuracy ($681/750$) and **0.9187** Pragmatic accuracy ($689/750$).
   - Imperfect rows total 69 ($9.20\%$), partitioned into 4 distinct modes:
     - `g_unknown_over_resolved_to_free_or_rate` (28 rows): specific seizure subtype negations (e.g. "no tonic-clonic convulsions") over-claiming global seizure freedom.
     - `g_missed_rate_dropped_to_unknown` (17 rows): 9 benchmark-specific shorthand notations (`TC *nine/mo`, `sz X2/d` — prohibited from hand-tuning by research safeguards) and 8 complex narrative expressions.
     - `g_granularity_and_period_mismatch` (15 rows): adjacent rate boundary/binning selections (e.g. daily nightly vs yearly intermittent rates).
     - `g_other_misclassifications` (9 rows): non-epileptic / subtle boundary descriptions.
2. **Candidate Rule Trials (Phases G1–G4)**:
   - **Candidate A (`rate.nightly_seizures`)**: Rescued 5 rows on `dev750` ($681 \to 686$), but produced a net $-1$ regression on aggregate `test450` ($329 \to 328$). **KILLED** under stop rules.
   - **Candidate B (`seizure_free.non_epileptic_current`)**: Rescued 1 row on `dev750` ($681 \to 682$), inert ($+0$) on `test450` ($329/450 = 0.7311$).
   - **Qualifier Scoping in `seizure_free`**: Narrowing subtype negations rescues 13 `unknown` rows on `dev750`, but simultaneously harms 8 valid `seizure_free` letters where subtype phrasing represented the patient's primary semiology.
3. **Closure at the Fairness Plateau**:
   - In accordance with Campaign Stop Rules (§14) and the predefined fairness clause (§12: *"If cumulative holdout Purist is < 0.781 after the catalog is all floor, the campaign still succeeds as a fairness attempt: the three-method table then uses the best gold-free rules-only system we can defend, with a named remainder"*), the Gan rules-only baseline is closed at its verified, portable state.
   - Preserves 100% integrity of the locked test firewall and historical benchmark comparisons.

---

## 2. Final Three-Method Parity Boundary Summary

| Benchmark Track | Split | Rules-Only (Active/Promoted) | LLM-Only (GPT-5.6 Sol) | LLM + Rules Hybrid |
| :--- | :---: | :---: | :---: | :---: |
| **ExECTv2 (Four-Family Headline F1)** | `dev140` | **0.9042** (+0.0060) | 0.8872 | **0.9427** |
| | `test60` | **0.7937** (+0.0019) | 0.8037 | **0.8329** |
| **Gan 2026 (Purist Accuracy)** | `dev750` | **0.9080** | 0.8320 | **0.9160** |
| | `test450` | **0.7311** | 0.8356 | **0.8400** |
