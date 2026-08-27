# Sealed holdout category aggregates

Date: 2026-08-06  
Status: holdout family + a_priori bucket lenses unlocked; ExECT rules-only family scores included  
Paper-library role: aggregate-only technical record; start with the [performance view](../artifacts/parallel_two_task_performance_view_2026-08-09.html)

Protocol: [holdout category aggregates protocol](six_model_holdout_category_aggregates_protocol_2026-08-06.md)  
Unlock protocol: [blocked-arm unlock](six_model_holdout_category_aggregates_unlock_protocol_2026-08-06.md)  
Parent: [category-cut performance](six_model_category_cut_performance_2026-08-06.md)  
Artifact: [`experiments/six_model_holdout_category_aggregates_20260806.json`](../../experiments/six_model_holdout_category_aggregates_20260806.json)

## Plain answer

ExECT holdout family lenses remain from public panels, with independent rules-only family scores alongside the two six-model surfaces. Gan a_priori and ExECT letter-bucket holdout scores are unlocked via machine-only sealed scoring with panel/floors fidelity checks. Gan hybrid a_priori lenses: x=none; z=`cluster_burden`. ExECT hybrid letter-bucket lenses with n≥10: x=none; z=none.

ExECT `test60` family lenses under `llm_with_rules`: no strict **x**; **z** = SeizureFrequency; **y** = Diagnosis, Prescription, Investigations. Under `llm`, **z** = SeizureFrequency; Prescription is **y**. Independent rules-only bands: Diagnosis 0.86 (high), SeizureFrequency 0.58 (floor), Prescription 0.84 (mid), Investigations 0.40 (floor).

Gan `test450` overall Purist: llm 0.68–0.74; llm_with_rules (current floors) 0.77–0.85.

Gan hybrid a_priori holdout lenses: **x** = none; **z** = `cluster_burden`; **y** = `ordinary_point_rate`, `range_rate`, `seizure_free`, `unknown_sentinel`, `unresolved_multiple`.

ExECT hybrid letter-bucket holdout lenses (n≥10): **x** = none; **z** = none; **y** = `multi_mention_with_sf`, `present_families_multi_mention_empty_sf`.

Gold mix share shifts are small (Gan max |Δshare| 0.0116; ExECT max |Δshare| 0.0449), so mix alone does not explain the ExECT SF holdout floor.

## ExECT `test60` family lenses

| Family | rules (band) | llm min–max (lens) | llm_with_rules min–max (lens) | Dev hybrid lens |
| --- | --- | --- | --- | --- |
| Diagnosis | **0.86 (high)** | 0.75–0.82 (**y**) | 0.79–0.85 (**y**) | **y** (0.84–0.89) |
| SeizureFrequency | **0.58 (floor)** | 0.40–0.51 (**z**) | 0.49–0.61 (**z**) | **y** (0.62–0.83) |
| Prescription | **0.84 (mid)** | 0.82–0.92 (**y**) | 0.78–0.86 (**y**) | **x** (0.87–0.94) |
| Investigations | **0.40 (floor)** | 0.79–0.92 (**y**) | 0.79–0.92 (**y**) | **y** (0.80–0.95) |

### Overall holdout bands

- llm (`raw_lane`): 0.6918–0.7771
- llm_with_rules (`clinical_headline`): 0.7169–0.8047

### Lens transfer vs development family cut

| Surface | Family | Dev lens | Holdout lens | Changed? |
| --- | --- | --- | --- | --- |
| llm | Diagnosis | **y** | **y** | no |
| llm | SeizureFrequency | **y** | **z** | yes |
| llm | Prescription | **y** | **y** | no |
| llm | Investigations | **y** | **y** | no |
| llm_with_rules | Diagnosis | **y** | **y** | no |
| llm_with_rules | SeizureFrequency | **y** | **z** | yes |
| llm_with_rules | Prescription | **x** | **y** | yes |
| llm_with_rules | Investigations | **y** | **y** | no |

## Gan `test450` a_priori bucket lenses

| Bucket | n | llm min–max (lens) | llm_with_rules min–max (lens) |
| --- | ---: | --- | --- |
| `cluster_burden` | 41 | 0.32–0.51 (**z**) | 0.41–0.68 (**z**) |
| `no_reference_sentinel` | 16 | 0.00–1.00 (below floor) | 0.94–1.00 (below floor) |
| `ordinary_point_rate` | 182 | 0.58–0.66 (**z**) | 0.75–0.90 (**y**) |
| `range_rate` | 58 | 0.76–0.88 (**y**) | 0.84–0.88 (**y**) |
| `seizure_free` | 67 | 0.76–0.88 (**y**) | 0.85–1.00 (**y**) |
| `unknown_sentinel` | 60 | 0.78–0.90 (**y**) | 0.68–0.78 (**y**) |
| `unresolved_multiple` | 26 | 0.77–0.88 (**y**) | 0.81–0.92 (**y**) |

llm lenses: **x**=none; **z**=`cluster_burden`, `ordinary_point_rate`; **y**=`range_rate`, `seizure_free`, `unknown_sentinel`, `unresolved_multiple`; below floor=`no_reference_sentinel`.
hybrid lenses: **x**=none; **z**=`cluster_burden`; **y**=`ordinary_point_rate`, `range_rate`, `seizure_free`, `unknown_sentinel`, `unresolved_multiple`; below floor=`no_reference_sentinel`.

### Overall Purist bands

| Surface | min–max Purist | Source |
| --- | --- | --- |
| llm | 0.6778–0.7444 | `experiments/gan2026_six_model_llm_only_test450_20260801/panel_aggregate.json` |
| llm_with_rules | 0.7733–0.8467 | `experiments/gan2026_six_model_current_floors_replay_20260731/replay_summary.json` |

## ExECT `test60` a_priori letter-bucket lenses

| Bucket | n | llm min–max (lens) | llm_with_rules min–max (lens) |
| --- | ---: | --- | --- |
| `broad_single_mention_with_sf` | 2 | 0.73–1.00 (below floor) | 0.73–1.00 (below floor) |
| `multi_mention_with_sf` | 41 | 0.71–0.80 (**y**) | 0.71–0.80 (**y**) |
| `present_families_multi_mention_empty_sf` | 14 | 0.70–0.82 (**y**) | 0.75–0.84 (**y**) |
| `present_families_single_mention_empty_sf` | 2 | 0.67–0.80 (below floor) | 0.60–0.75 (below floor) |

llm lenses: **x**=none; **z**=none; **y**=`multi_mention_with_sf`, `present_families_multi_mention_empty_sf`; below floor=`broad_single_mention_with_sf`, `present_families_single_mention_empty_sf`.
hybrid lenses: **x**=none; **z**=none; **y**=`multi_mention_with_sf`, `present_families_multi_mention_empty_sf`; below floor=`broad_single_mention_with_sf`, `present_families_single_mention_empty_sf`.

## Gold mix (shares only)

### Gan a_priori buckets

| Bucket | Dev n (share) | Holdout n (share) | Δ share |
| --- | ---: | ---: | ---: |
| `ordinary_point_rate` | 312 (0.416) | 182 (0.404) | -0.012 |
| `range_rate` | 92 (0.123) | 58 (0.129) | +0.006 |
| `cluster_burden` | 64 (0.085) | 41 (0.091) | +0.006 |
| `no_reference_sentinel` | 27 (0.036) | 16 (0.036) | -0.000 |
| `seizure_free` | 112 (0.149) | 67 (0.149) | -0.000 |
| `unresolved_multiple` | 43 (0.057) | 26 (0.058) | +0.000 |
| `unknown_sentinel` | 100 (0.133) | 60 (0.133) | +0.000 |

### ExECT a_priori letter buckets

| Bucket | Dev n (share) | Holdout n (share) | Δ share |
| --- | ---: | ---: | ---: |
| `multi_mention_with_sf` | 91 (0.650) | 41 (0.695) | +0.045 |
| `sparse_multi_family_single_mention_with_sf` | 4 (0.029) | 0 (0.000) | -0.029 |
| `no_four_family_gold` | 3 (0.021) | 0 (0.000) | -0.021 |
| `present_families_single_mention_empty_sf` | 7 (0.050) | 2 (0.034) | -0.016 |
| `present_families_multi_mention_empty_sf` | 31 (0.221) | 14 (0.237) | +0.016 |
| `broad_single_mention_with_sf` | 4 (0.029) | 2 (0.034) | +0.005 |

## Decision

ExECT holdout family lenses remain from public panels, with independent rules-only family scores alongside the two six-model surfaces. Gan a_priori and ExECT letter-bucket holdout scores are unlocked via machine-only sealed scoring with panel/floors fidelity checks. Gan hybrid a_priori lenses: x=none; z=`cluster_burden`. ExECT hybrid letter-bucket lenses with n≥10: x=none; z=none.

Holdout family evidence supports the development reading that SeizureFrequency remains the ExECT floor (holdout hybrid lens **z**). Hybrid lens changes vs development: SeizureFrequency y→z, Prescription x→y.

## Next

1. Treat unlocked holdout bucket lenses as aggregate transfer evidence only; do not open sealed rows for failure catalogs.
2. Operational primary remains the vLLM dev10 task.

## Method

- Family lenses: public ExECT stage panel.
- Rules-only family scores: Decision 0046 test60 aggregate.
- Gan llm buckets: sealed llm-only `test450` ledgers.
- Gan hybrid buckets: no-call matched-v0.5 raw replay through current `hybrid_full_stack`; fidelity to floors `after_purist`.
- ExECT letter buckets: sealed `*_sealed_rows.jsonl` scored with the clinical-headline helper; hybrid fidelity to panel `clinical_headline`.
- Gold taxonomies supply mix shares only; bucket membership recomputed in-process from locked gold loaders.
- Public row identifiers / failure examples: no.
- Git: `4835a093` (dirty tree).

## Claim boundary

Aggregate-only sealed holdout category packaging, including machine-only a_priori bucket scores from restored sealed ledgers. No human sealed-row inspection. Not a Decision 0046 rewrite. Not repair or prompt tuning from holdout.
