# Gan unknown-gold breakthrough leave-one-family-out

Date: 2026-08-06  
Status: development leave-one-family-out necessity check  
Paper-library role: Gan counterfactual record; start with [failures and limits](../paper/failures_and_limits_2026-08-10.md)

Protocol: recovered from git history; this report is the answer.  
Parent: [unknown_sentinel clinical harm](unknown_sentinel_clinical_harm_2026-08-06.md)  
Artifact: [`experiments/gan2026_unknown_breakthrough_loo_20260806.json`](../../experiments/gan2026_unknown_breakthrough_loo_20260806.json)

## Plain answer

On 598 unknown-gold cells, omitting `repair.breakthrough` changes final Purist from **0.8043** to **0.8211** (10 rescue / 0 harm vs default).

Full-ledger secondary (4482 cells): 0.8811 → 0.8737 (Δ correct -33; 10 rescue / 43 harm).

**Decision label:** `necessity_confirmed_with_global_cost`.

Omitting breakthrough recovers unknown-gold damage with no new unknown harms, but costs Purist correct cells on the full ledger.

Production rewrite: **not authorized**.

## Unknown-gold arms

| Arm | Final acc | Clinical-selection acc | Wrong modes (final) |
| --- | ---: | ---: | --- |
| default | 0.8043 | 0.8043 | false_active_rate 77, false_seizure_free 40 |
| omit breakthrough | 0.8211 | 0.8211 | false_active_rate 67, false_seizure_free 40 |

Default breakthrough fires on unknown gold: 10.
Disagree cells: 10; later-family spillover cells: 0.

### Final wrong-mode Δ (omit − default)

| Mode | Δ count |
| --- | ---: |
| `false_seizure_free` | +0 |
| `false_active_rate` | -10 |

### Recovered unknown cells (omit corrects default wrong)

- row 6077 / GPT-5.6 Sol: `1 per 8 month` → `no seizure frequency reference` (gold `unknown`; pathway `selected_evidence → breakthrough`)
- row 10542 / GPT-5.6 Sol: `2 to 4 per 3 month` → `no seizure frequency reference` (gold `unknown, 2 to 4 per cluster`; pathway `selected_evidence → breakthrough`)
- row 6077 / GPT-5.6 Luna: `1 per 8 month` → `no seizure frequency reference` (gold `unknown`; pathway `selected_evidence → breakthrough`)

### New unknown harms (omit wrongs default correct)

- none

### Later-family spillover examples

- none material

## Full-ledger secondary (all gold buckets)

| Bucket | N | Default acc | Omit acc | Δ correct | Rescue | Harm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cluster_burden` | 381 | 0.7008 | 0.6693 | -12 | 0 | 12 |
| `no_reference_sentinel` | 160 | 0.9938 | 0.9938 | +0 | 0 | 0 |
| `ordinary_point_rate` | 1867 | 0.8795 | 0.8634 | -30 | 0 | 30 |
| `range_rate` | 550 | 0.9218 | 0.92 | -1 | 0 | 1 |
| `seizure_free` | 669 | 0.9567 | 0.9567 | +0 | 0 | 0 |
| `unknown_sentinel` | 598 | 0.8043 | 0.8211 | +10 | 10 | 0 |
| `unresolved_multiple` | 257 | 0.9844 | 0.9844 | +0 | 0 | 0 |
| **all** | 4482 | 0.8811 | 0.8737 | -33 | 10 | 43 |

## Decision

Omitting breakthrough recovers unknown-gold damage with no new unknown harms, but costs Purist correct cells on the full ledger.

This confirms whether the unknown-harm first-changer is factorial on the omitted family. It does **not** change the default hybrid repair stack.

## Next

1. Only a guarded unknown-stand-down (or similar predeclared repair candidate)
   is in scope if anyone wants to act on the +10 unknown recovery.
2. Do not globally disable `repair.breakthrough`: full-ledger cost is −33
   Purist correct cells, mostly `ordinary_point_rate` (−30) and
   `cluster_burden` (−12).
3. Operational primary remains the vLLM dev10 task.

## Method

- Split: Gan `dev750`; arms = full stack vs study-local omit `repair.breakthrough`.
- Replay: `scripts/build_gan2026_hybrid_stage_ablation.py` `replay_row(..., omit_stages=...)`.
- Git: `45bfe6d2` (dirty tree).

## Claim boundary

Development leave-one-family-out on retained Gan hybrid ledgers. Not holdout. Not a production repair rewrite. Unknown-gold recovery with material full-ledger loss supports only a guarded-bucket hypothesis.
