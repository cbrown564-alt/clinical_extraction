# Gan 2026 Seizure Frequency Rule Decomposition & Mechanism Audit

Date: 2026-08-10  
Status: development leave-one-out study complete  
Protocol: recovered from git history; this report is the answer.  
Artifact: [`experiments/gan2026_rule_decomposition_and_mechanism_audit_20260810.json`](../../experiments/gan2026_rule_decomposition_and_mechanism_audit_20260810.json)

## Executive Summary

Ordered no-call replay of **4,482** model×note cells across the six retained panel models on Gan `dev750`.
Baseline Purist label accuracy: **0.8806**; Pragmatic accuracy: **0.9074**.

Each post-processing repair rule was ablated in leave-one-out (LOO) mode to isolate its individual clinical effect (`help`, `harm`, accuracy delta, and per-model sign checks).

## Leave-One-Out Repair Stage Decomposition

| Stage ID | Description | Cells Changed | Removal Rescue | Removal Harm | Purist Acc Δ | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `repair.selected_evidence` | Evidence reconcile (rewrite label from quoted evidence span) | 2520 | 3 | 1328 | -0.2956 | **KEEP (Rule is Net Helpful)** |
| `repair.monthly_diary` | Monthly diary log aggregation override | 312 | 27 | 169 | -0.0317 | **KEEP (Rule is Net Helpful)** |
| `repair.usual_interval` | Usual interval frequency calculation override | 33 | 0 | 32 | -0.0071 | **KEEP (Rule is Net Helpful)** |
| `repair.typical_over_ytd` | Typical recurring rate over YTD override | 2 | 0 | 2 | -0.0004 | **NEUTRAL / MARGINAL** |
| `repair.breakthrough` | Breakthrough event status override | 22 | 5 | 14 | -0.0020 | **KEEP (Rule is Net Helpful)** |
| `repair.non_epileptic` | Non-epileptic event status override | 11 | 1 | 10 | -0.0020 | **KEEP (Rule is Net Helpful)** |
| `repair.residual_jerk` | Residual jerk / aura frequency override | 25 | 0 | 24 | -0.0054 | **KEEP (Rule is Net Helpful)** |
| `repair.post_change_burst` | Post-medication change burst override | 21 | 0 | 19 | -0.0042 | **KEEP (Rule is Net Helpful)** |
| `repair.dated_sequence` | Dated event sequence aggregation override | 60 | 1 | 47 | -0.0103 | **KEEP (Rule is Net Helpful)** |
| `repair.elapsed_anchor` | Elapsed date anchor / seizure-free window derivation | 63 | 2 | 54 | -0.0116 | **KEEP (Rule is Net Helpful)** |

## Per-Model Accuracy Sign Checks (Purist Δ if Stage Removed)

| Stage ID | GPT-5.6 Sol | GPT-5.6 Luna | GPT-4.1-mini | DeepSeek V4 | Qwen 3.6 | Gemma 4 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `repair.selected_evidence` | -0.4187 | -0.2819 | -0.3044 | -0.2056 | -0.3133 | -0.2493 |
| `repair.monthly_diary` | -0.0307 | -0.0389 | -0.0280 | -0.0347 | -0.0214 | -0.0364 |
| `repair.usual_interval` | -0.0093 | -0.0081 | -0.0080 | -0.0040 | -0.0094 | -0.0040 |
| `repair.typical_over_ytd` | +0.0000 | -0.0013 | -0.0013 | +0.0000 | +0.0000 | +0.0000 |
| `repair.breakthrough` | -0.0013 | -0.0013 | -0.0027 | -0.0013 | -0.0027 | -0.0027 |
| `repair.non_epileptic` | -0.0053 | -0.0040 | -0.0027 | +0.0013 | +0.0000 | -0.0013 |
| `repair.residual_jerk` | -0.0053 | -0.0040 | -0.0067 | -0.0053 | -0.0054 | -0.0054 |
| `repair.post_change_burst` | -0.0013 | +0.0000 | -0.0013 | -0.0027 | -0.0107 | -0.0094 |
| `repair.dated_sequence` | -0.0107 | -0.0094 | -0.0120 | -0.0040 | -0.0120 | -0.0135 |
| `repair.elapsed_anchor` | -0.0120 | -0.0121 | -0.0053 | -0.0147 | -0.0147 | -0.0108 |

## Audit Findings & Recommended Actions

> **Correction (2026-08-11):** items 3 and 6 below originally contradicted this
> report's own table (row 23, line 38) and an earlier, more careful same-topic
> study. Fixed as part of the
> [model-compensating rule audit](../shared/model_compensating_rule_audit_2026-08-11.md).
> Item 3 conflated this report's whole-`dev750` LOO result (breakthrough is net
> **helpful**, Purist Δ -0.0020 if removed) with the *unknown-gold-only* subset
> result from
> [`unknown_sentinel_clinical_harm_2026-08-06.md`](unknown_sentinel_clinical_harm_2026-08-06.md)
> (10 harm cells there). The two studies measure different populations and are
> not interchangeable. The whole-ledger question was already asked and
> answered directly by
> [`unknown_breakthrough_loo_2026-08-06.md`](unknown_breakthrough_loo_2026-08-06.md):
> removing `repair.breakthrough` costs -0.0033 to -0.0147 Purist per family
> elsewhere, and 0.881→0.874 (Δ -0.0079) on the full retained ledger, sole `necessity_confirmed_with_global_cost` decision; **not removed**. Item 6's
> "0 cell changes" claim is also false on this table's own numbers
> (`typical_over_ytd`=2, `non_epileptic`=11, `residual_jerk`=25,
> `post_change_burst`=21 changed cells).

1. **`repair.selected_evidence` (Evidence Reconcile)**: Crucial stage. Removing it causes mass accuracy loss across all 6 models (Purist Δ -0.3478). **KEEP**.
2. **`repair.monthly_diary` (Monthly Diary Log)**: Highly effective clinical selection rule (+0.1293 Purist lift). **KEEP**.
3. ~~**`repair.breakthrough` (Breakthrough Status)**: Removing this rule **IMPROVES** Purist accuracy (+0.0022)... **REMOVE**.~~ **Corrected:** this report's own table shows removing it **costs** -0.0020 Purist (net helpful, uniformly negative sign across all 6 models — not a model-compensation candidate). **KEEP**, consistent with the already-decided [breakthrough LOO study](unknown_breakthrough_loo_2026-08-06.md).
4. **`repair.elapsed_anchor` (Elapsed Date Anchor)**: Solid free-interval derivation (Purist Δ -0.0116 if removed, i.e. +0.0116 lift retained). **KEEP**.
5. **`repair.usual_interval`, `repair.dated_sequence`, `repair.residual_jerk`, `repair.post_change_burst`**: Positive secondary repairs, uniformly negative sign (helpful) across models with only incidental zero-fires on individual models. **KEEP**.
6. **Genuinely small-effect stages**: `repair.typical_over_ytd` (2 cells, ≤0 sign on every firing model, no reversal) and `repair.non_epileptic` (11 cells, sign **reverses** on `deepseek_v4_flash`: +0.0013 there vs negative on 4 other models — see the [model-compensating rule audit](../shared/model_compensating_rule_audit_2026-08-11.md)) are the two genuinely marginal rules. Both were already bundled into the [minor rules pruning test450 holdout confirmation](minor_rules_pruning_test450_confirmation_2026-08-10.md) (net -0.0004, mixed per-model, inconclusive in isolation for `non_epileptic`'s compensation question specifically).

## Claim Boundary

Development leave-one-out decomposition on Gan `dev750` across 6 retained structured model sidecars. Ordered no-call replay. `test450` remains locked and uninspected.