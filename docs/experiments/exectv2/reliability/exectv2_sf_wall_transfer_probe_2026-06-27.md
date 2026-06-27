# ExECTv2 SeizureFrequency Wall-Transfer Probe (P3b)

- Generated: `2026-06-27`
- JSON: `experiments/exectv2_sf_wall_transfer_probe_2026-06-27.json`
- Harness: `experiments/build_exectv2_sf_wall_transfer_probe.py`
- Claim boundary: Aggregate-only ExECTv2 SF wall-transfer probe using saved same-core model-swap and self-consistency artifacts. No full-200 or holdout row-level inspection; no new model calls.
- Row inspection policy: `aggregate_only_no_full200_or_holdout_row_level_inspection`
- No model calls; replay from saved same-core model-swap and self-consistency artifacts.

## Verdict

**Partial** — SF weakness and some confident-error signatures transfer, but ExECTv2 entropy/agreement magnitudes differ from Gan's near-zero P2.1 panel — same mechanism, different observability.

Checks passed: 3/6.

## Gan P2.1 Reference (same probe family)

- Hypothesis: `H0_confident_over_reading`
- Mean label entropy: `0.0121`
- Residual mean label entropy: `0.0176`

## Family F1 — Same-Core Model Swap

### Dev140 (GPT / DeepSeek / Qwen)

| Model | Dx | SF | Presc | Inv |
| --- | ---: | ---: | ---: | ---: |
| DeepSeek chat | 0.8845 | 0.7658 | 0.8895 | 0.8966 |
| GPT-4.1-mini | 0.8573 | 0.7645 | 0.8895 | 0.8347 |
| Qwen 3.6 35B | 0.8027 | 0.6919 | 0.8895 | 0.8354 |

### Full-200 (GPT / DeepSeek / Qwen repair v02)

| Model | Dx | SF | Presc | Inv |
| --- | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 0.8397 | 0.7525 | 0.8926 | 0.8563 |
| DeepSeek chat | 0.8708 | 0.7602 | 0.8926 | 0.9091 |
| Qwen 3.6 35B (repair v02) | 0.8307 | 0.7020 | 0.8926 | 0.8503 |

- Weakest family dev140: **SeizureFrequency** (0.7645)
- Weakest family full-200: **SeizureFrequency** (0.7525)

## Cross-Model Agreement (dev140, 3 models)

| Family | Exact 3/3 | Mean Jaccard | Error exact 3/3 | Correct exact 3/3 | Error low-conf | Correct low-conf |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Diagnosis | 0.5143 | 0.7704 | 0.1190 | 0.6837 | 0.1667 | 0.0816 |
| SeizureFrequency | 0.5071 | 0.7429 | 0.2182 | 0.6941 | 0.5273 | 0.4235 |
| Prescription | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.7576 | 0.7850 |
| Investigations | 0.7429 | 0.8492 | 0.2500 | 0.8065 | 0.0000 | 0.0000 |

## Self-Consistency Error Stratification (dev140, k=4 temps)

| Family | Mean entropy | Error entropy | Correct entropy | Unanimous 4/4 wrong | Error unanimous 4/4 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Diagnosis | 0.1796 | 0.3117 | 0.1062 | 0.1571 | 0.4400 |
| SeizureFrequency | 0.1548 | 0.2867 | 0.0694 | 0.1714 | 0.4364 |
| Prescription | 0.0000 | 0.0 | 0.0 | 0.2357 | 1.0000 |
| Investigations | 0.0879 | 0.2522 | 0.0504 | 0.0857 | 0.4615 |

## Verdict Checks

| Check | Pass |
| --- | --- |
| `sf_weakest_on_dev140_and_full200` | yes |
| `sf_error_cross_model_agreement_not_lower_than_correct` | no |
| `sf_unanimous_4_of_4_wrong_material` | yes |
| `sf_error_entropy_not_elevated_vs_correct` | no |
| `gan_p21_h0_confident_over_reading_reference` | yes |
| `other_families_also_show_confident_error_pattern` | no |

## Key Comparison vs Gan P2.1

| Signal | Gan P2.1 | ExECTv2 SF (this probe) |
| --- | --- | --- |
| Residual / error entropy | flat (~0.018) | error > correct (0.287 vs 0.069) |
| Self-consistency unanimous wrong | band_unknown stable at 0.000 | 17.1% of SF cells |
| Cross-model error agreement | external AUROC 0.781 (disagreement signals risk) | error 3/3 exact 21.8% vs correct 69.4% |
| Weakest family | rate/over-reading bands | SF F1 0.7525 full-200 |

## Interpretation Boundary

This probe compares ExECTv2 SF to Gan P2.1 forward-observable features at aggregate level only. High cross-model agreement on error cells is the ExECTv2 analogue of Gan confident over-reading; it is not a holdout claim and does not authorize row-level tuning on full-200.

## Source Artifacts

- `dev140_model_swap`: `experiments/exectv2_same_core_model_swap_dev140_20260625.json`
- `full200_model_swap`: `experiments/exectv2_same_core_model_swap_full200_20260625.json`
- `qwen_full200`: `experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200_20260626.json`
- `self_consistency`: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_20260625.json`
- `gan_p21`: `experiments/gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.json`
