# Gan unknown_sentinel clinical-selection harm

Date: 2026-08-06  
Status: development residual audit on unknown gold  
Paper-library role: Gan harm record; start with [failures and limits](../paper/failures_and_limits_2026-08-10.md)

Protocol: recovered from git history; this report is the answer.  
Parent: [cross-task hybrid mechanism synthesis](../shared/cross_task_hybrid_mechanism_synthesis_2026-08-06.md)  
Companion: [Gan hybrid stage ablation](hybrid_stage_ablation_2026-08-06.md)  
Artifact: [`experiments/gan2026_unknown_sentinel_clinical_harm_20260806.json`](../../experiments/gan2026_unknown_sentinel_clinical_harm_20260806.json)

## Plain answer

On 598 unknown-gold row×model cells, Purist accuracy is **0.83** after evidence reconcile, **0.80** after clinical selection, and **0.80** at final.

Clinical selection is the accuracy drop. It asserts active rates or seizure-free labels onto abstention gold.
Largest any-harm family: `repair.breakthrough` (10 any-harm / 0 any-rescue).

## Band endpoints on unknown gold

| Band | Acc | Top wrong modes |
| --- | ---: | --- |
| After evidence reconcile | 0.83 | `false_active_rate` 61, `false_seizure_free` 43 |
| After clinical selection | 0.80 | `false_active_rate` 73, `false_seizure_free` 44 |
| Final | 0.80 | `false_active_rate` 77, `false_seizure_free` 40 |

Mode Δ evidence → clinical (negative = mode shrank): `false_active_rate` +12, `false_seizure_free` +1.

## Clinical / free-interval family ledger (unknown gold only)

| Stage | Band | Fires | First | Rescue | Harm | Any+ | Any- |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `repair.monthly_diary` | clinical_selection | 2 | 2 | 0 | 2 | 0 | 2 |
| `repair.usual_interval` | clinical_selection | 0 | 0 | 0 | 0 | 0 | 0 |
| `repair.typical_over_ytd` | clinical_selection | 0 | 0 | 0 | 0 | 0 | 0 |
| `repair.breakthrough` | clinical_selection | 10 | 10 | 0 | 10 | 0 | 10 |
| `repair.non_epileptic` | clinical_selection | 1 | 1 | 0 | 1 | 0 | 1 |
| `repair.residual_jerk` | clinical_selection | 0 | 0 | 0 | 0 | 0 | 0 |
| `repair.post_change_burst` | clinical_selection | 0 | 0 | 0 | 0 | 0 | 0 |
| `repair.dated_sequence` | clinical_selection | 0 | 0 | 0 | 0 | 0 | 0 |
| `repair.elapsed_anchor` | free_interval | 4 | 4 | 0 | 0 | 0 | 0 |

### Harm shapes by family

- `repair.breakthrough`: `false_active_rate` 10
  - Example: row 10542 / GPT-5.6 Sol: `no seizure frequency reference` → `2 to 4 per 3 month` (gold `unknown, 2 to 4 per cluster`).
- `repair.monthly_diary`: `false_active_rate` 2
  - Example: row 7141 / GPT-5.6 Luna: `no seizure frequency reference` → `3 per 6 month` (gold `unknown`).
- `repair.non_epileptic`: `false_seizure_free` 1
  - Example: row 11259 / DeepSeek V4 Flash: `unknown` → `seizure free for multiple year` (gold `unknown`).

## Residual ownership after clinical/free hops

| Outcome | Count |
| --- | ---: |
| `final_correct_no_clinical_or_free` | 481 |
| `final_wrong_no_clinical_or_free` | 100 |
| `final_wrong_after_clinical_or_free` | 17 |

## Top pathways (clinical/free only)

| Pathway | Count |
| --- | ---: |
| `no_clinical_or_free_change` | 581 |
| `breakthrough` | 10 |
| `elapsed_anchor` | 4 |
| `monthly_diary` | 2 |
| `non_epileptic` | 1 |

## Decision

Unknown-gold hybrid damage after evidence reconcile is concentrated in clinical-selection assertion families, not missing format cleanup. This audit localizes the harm; it does **not** authorize turning those families off without a predeclared leave-one-family-out or guarded repair study.

## Next

1. Done: [breakthrough leave-one-family-out](unknown_breakthrough_loo_2026-08-06.md)
   confirms necessity on unknown (+10/0) with full-ledger cost (−33).
2. Do not change production repairs from this page alone.
3. Operational primary remains the vLLM dev10 task.

## Method

- Split: Gan `dev750`, gold bucket `unknown_sentinel` only.
- Replay: same ordered stack as the Gan hybrid stage ablation.
- Attribution: first clinical/free label-changing hop; any-rescue/harm count later hops too.
- Git: `922ff314` (dirty tree).

## Claim boundary

Development unknown-gold clinical/free harm audit on Gan dev750. Not leave-one-family-out; not a repair rewrite; not holdout.
