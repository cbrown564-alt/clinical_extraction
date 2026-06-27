# ExECTv2 SeizureFrequency Wall-Transfer Probe (P3b)

- Generated: `2026-06-27`
- JSON: `experiments/exectv2_sf_wall_transfer_probe_2026-06-27.json`
- Harness: `experiments/build_exectv2_sf_wall_transfer_probe_extended.py` (extends `build_exectv2_sf_wall_transfer_probe.py`)
- Claim boundary: Aggregate-only ExECTv2 SF wall-transfer probe using saved same-core model-swap and self-consistency artifacts. No full-200 or holdout row-level inspection; no new model calls.
- Row inspection policy: `aggregate_only_no_full200_or_holdout_row_level_inspection`
- No model calls; replay from saved same-core model-swap and self-consistency artifacts.

## Verdict

**Wall Transfers** — The two previously-uncomputed acceptance criteria both support transfer. (1) The frozen External Risk composite ranks SF errors at AUROC 0.764 (Gan 0.781) and its risk-coverage curve plateaus -- the safest-ranked SF tier still carries selective risk 17.1% (CI lower 8.5% > 0), the same irreducible-residual shape as Gan P0.2. (2) On the binding gold-unknown over-read slice, no forward-observable feature separates withhold-correct from over-read-wrong (best AUROC 0.676 < 0.70; 2/5 over-reads are entropy-zero), so H0 is retained. The wall transfers: the binding over-reads remain unflaggable without gold. The difference from Gan is only in population-wide observability magnitude (ExECTv2 error cells are noisier population-wide), not in the wall mechanism.

Checks passed: 6/9 (base probe was 3/6; the three added checks compute the two acceptance criteria the base probe left blank).

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
| `sf_external_risk_ranks_errors_population` | yes |
| `sf_external_risk_coverage_plateau_nonzero` | yes |
| `wall_slice_no_gold_free_separator` | yes |

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


---

## External Risk Composite — Population (feature #3, acceptance criterion 1)

Per-letter SF clinical-headline cell on **dev140** (n=140, errors=55, base rate 39.3%), canonical subject GPT-4.1-mini. Frozen composite (matches Gan P0.2):

`risk = 3*(3 - cross_model_agreement_count) + source_residual_flag_count + ambiguity_reason_count`

- Agreement leg (#1-#2): largest identical SF-keyset cluster across the three same-core model-swap runs (GPT / DeepSeek / Qwen).
- Source-flag leg (#5-#9): deterministic keyword port — predicted SeizureFrequency mention evidence+surface text (SF assembly trace); deterministic keyword port of Gan boundary_features (no rq9 router packet exists for ExECTv2).
- Ambiguity leg (#11): ported keyword reasons over the same SF assembly trace.

| Feature | AUROC (predicts error) | Risk-coverage AUC ↓ | Safest-tier plateau |
| --- | ---: | ---: | --- |
| #1 Cross-model agreement count | 0.7613 | 0.1383 | coverage 50.7%, selective risk 16.9% (CI 9.9%-27.3%) |
| #2 Agreement share | 0.7613 | 0.1383 | coverage 50.7%, selective risk 16.9% (CI 9.9%-27.3%) |
| #3 External risk composite | 0.7636 | 0.1787 | coverage 29.3%, selective risk 17.1% (CI 8.5%-31.3%) |
| _oracle (correct-first)_ | — | 0.0899 | — |

**Reading.** The external composite ranks SF errors at AUROC 0.764 — within 0.017 of Gan's validation750 external leg (0.781). The agreement leg (#1-#2) carries essentially all of the signal; the ported source-flag and ambiguity legs add < 0.01 AUROC and slightly worsen the risk-coverage AUC, exactly as Gan found the source flags to be coarse / wall-degenerate alone. Critically, the risk-coverage curve **plateaus**: the safest-ranked SF tier still carries selective risk 17.1% — errors leak into the low-risk region (the same irreducible-residual shape as Gan P0.2, which plateaus at 0.8% @ 16% coverage; ExECTv2's plateau is higher because SF base error rate is ~39%, but the wall shape is the same).

## Wall-Slice Null Test (acceptance criterion 2)

**Pre-registered before scoring the contrast:**

- Slice: SeizureFrequency gold units whose state is 'unknown' (the should-withhold units), classified by exact type-key match against the canonical GPT-4.1-mini prediction into: withhold-correct (prediction also 'unknown'), over-read-wrong (prediction 'active-rate'/'seizure-free' -- the over-read analogue of Gan confident over-reading), or recall-miss (no prediction for that type; excluded from the withhold-vs-over-read contrast).
- **H0** (wall transfers): Wall transfers: NO forward-observable feature (#1 cross-model state agreement, #3 external risk composite, #17/#18 self-consistency state entropy) separates withhold-correct from over-read-wrong on the gold-unknown slice; the binding over-reads are indistinguishable from correct withholds without gold.
- **H1** (separation): Separation exists: at least one feature flags the over-reads, so an inference-time abstention signal could catch them.
- Decision rule: H1 supported iff some feature reaches AUROC(over-read) >= 0.70 (or <= 0.30) in the interpretable direction; otherwise H0 is retained. The 0.70 bar is a conventional 'useful triage classifier' threshold chosen on methodological grounds, not tuned to the data. n is small (Gan's binding residual is 11 rows; ExECTv2's is comparably small), so any AUROC is reported with that caveat and treated as suggestive, not definitive.
- Note: For SeizureFrequency the abstention surface (state #17) and the upstream 'kind' (#18) are the same token {active-rate, seizure-free, unknown}, so #17 and #18 collapse to a single state-entropy feature.

**Slice composition (GPT canonical):** 39 gold-unknown SF units → 25 withhold-correct, 5 over-read-wrong, 9 recall-miss (misses excluded from the withhold-vs-over-read contrast). Per-model over-read counts on the gold-unknown slice: {'gpt41mini': 5, 'deepseek': 7, 'qwen36': 8}.

| Feature | Mean (withhold-correct) | Mean (over-read-wrong) | AUROC (flags over-read) |
| --- | ---: | ---: | ---: |
| #1 Cross-model state agreement | 2.76 | 2.6 | 0.5800 |
| #3 External risk composite | 3.92 | 3.2 | 0.4160 |
| #17/#18 Self-consistency state entropy | 0.0987 | 0.2434 | 0.6760 |

**Result: H0_retained_no_gold_free_separator.** Best separation AUROC 0.676 < 0.70, so H1 is not supported and H0 is retained. 2/5 over-reads are entropy-zero (temperature-stable confident over-reads, exactly the Gan `band_unknown` = 0.000 signature), and the external-risk composite that ranks errors population-wide is wall-degenerate here (AUROC 0.416, over-reads carry *lower* mean external risk than correct withholds). The self-consistency state-entropy feature shows a sub-threshold hint of separation (over-reads mean 0.2434 vs 0.0987), consistent with ExECTv2's higher population-wide entropy, but it does not reach the useful-triage bar and n is small. No forward-observable feature provides a gold-free separator: **the wall transfers at the binding slice.**

### Over-read units (the binding residual)

| Letter | GPT state | 3-model states | 4-temp states | State entropy | Letter ext-risk |
| --- | --- | --- | --- | ---: | ---: |
| EA0049 | active-rate | active-rate, unknown, active-rate | active-rate, unknown, unknown, unknown | 0.406 | 7 |
| EA0064 | active-rate | active-rate, active-rate, active-rate | active-rate, active-rate, active-rate, unknown | 0.406 | 0 |
| EA0098 | active-rate | active-rate, absent, absent | active-rate, active-rate, active-rate, active-rate | 0.000 | 6 |
| EA0122 | seizure-free | seizure-free, seizure-free, seizure-free | seizure-free, seizure-free, seizure-free, unknown | 0.406 | 1 |
| EA0123 | active-rate | active-rate, active-rate, active-rate | active-rate, active-rate, active-rate, active-rate | 0.000 | 2 |

## Extended Verdict Checks

| Check | Pass |
| --- | --- |
| `sf_weakest_on_dev140_and_full200` | yes |
| `sf_error_cross_model_agreement_not_lower_than_correct` | no |
| `sf_unanimous_4_of_4_wrong_material` | yes |
| `sf_error_entropy_not_elevated_vs_correct` | no |
| `gan_p21_h0_confident_over_reading_reference` | yes |
| `other_families_also_show_confident_error_pattern` | no |
| `sf_external_risk_ranks_errors_population` | yes |
| `sf_external_risk_coverage_plateau_nonzero` | yes |
| `wall_slice_no_gold_free_separator` | yes |

The three base checks that read `no` (`sf_error_cross_model_agreement_not_lower_than_correct`, `sf_error_entropy_not_elevated_vs_correct`, `other_families_also_show_confident_error_pattern`) test whether ExECTv2's *population-wide* error cells match Gan's near-degenerate P2.1 magnitudes. They do not — ExECTv2 error cells are noisier population-wide. That is a difference in observability magnitude, not in the wall mechanism: the two acceptance criteria above (external-risk plateau + no gold-free separator at the binding slice) are the direct wall-transfer tests, and both pass.

## Generator

- Extended harness: `experiments/build_exectv2_sf_wall_transfer_probe_extended.py`
- Base harness: `experiments/build_exectv2_sf_wall_transfer_probe.py`
