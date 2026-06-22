# ExECTv2 Clinical-Utility Companion Audit

- Generated: `2026-06-22`
- JSON: `docs/research/exectv2_clinical_utility_companion_dev140_2026-06-22.json`
- Split: `dev`
- Sample rows per run: 20

## Direct Answers

1. Often yes for evidence packaging and supported fact granularity: the best exact-evidence run is v08_dev140_control and the best attribute-signal run is v0922_qwen_diagnostic. These are review signals, not proof that gold labels are wrong.
2. Yes in places. Deterministic provenance shows benchmark-format actions (4073) as well as clinical-useful actions (1455); rows with benchmark-format repair need separate clinical review before treating higher F1 as higher utility.

## Score And Repair Surfaces

| Run | Source raw F1 | Evidence-valid F1 | Full final F1 | Raw mentions | Scored mentions |
| --- | ---: | ---: | ---: | ---: | ---: |
| v08_dev140_control | 0.8308 | 0.8308 | 0.9155 | 1038 | 996 |
| v09_partial_hybrid | 0.8211 | 0.8211 | 0.9061 | 1028 | 986 |
| v0916_deepseek_diagnostic | 0.7498 | 0.7498 | 0.9174 | 899 | 915 |
| v0922_qwen_diagnostic | 0.6406 | 0.6406 | 0.9001 | 749 | 860 |

## Materialized Intermediate Surfaces

| Run | Source | Evidence-valid | Dictionary-only | Residual additions | Direct final | Clinical headline |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v08_dev140_control | 0.8308 | 0.8308 | 0.8697 | 0.8872 | 0.8872 | 0.9155 |
| v09_partial_hybrid | 0.8211 | 0.8211 | 0.8601 | 0.8778 | 0.8778 | 0.9061 |
| v0916_deepseek_diagnostic | 0.7498 | 0.7498 | 0.8334 | 0.8728 | 0.8728 | 0.9174 |
| v0922_qwen_diagnostic | 0.6406 | 0.6406 | 0.7526 | 0.8567 | 0.8567 | 0.9001 |

## Clinical Utility Signals

| Run | Exact evidence | Attribute signal | Sentence-like evidence | Current | Historical | Future | Family history |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v08_dev140_control | 1.000 | 0.946 | 0.295 | 883 | 69 | 11 | 2 |
| v09_partial_hybrid | 1.000 | 0.946 | 0.323 | 867 | 74 | 13 | 2 |
| v0916_deepseek_diagnostic | 1.000 | 0.955 | 0.438 | 795 | 70 | 9 | 7 |
| v0922_qwen_diagnostic | 1.000 | 0.964 | 0.320 | 770 | 57 | 6 | 3 |

## Deterministic Action Buckets

| Run | Clinical-useful | Benchmark-format | Seizure-frequency | Other |
| --- | ---: | ---: | ---: | ---: |
| v08_dev140_control | 330 | 1191 | 540 | 330 |
| v09_partial_hybrid | 320 | 1191 | 540 | 201 |
| v0916_deepseek_diagnostic | 387 | 935 | 243 | 0 |
| v0922_qwen_diagnostic | 418 | 756 | 276 | 0 |

## Gold-Disagreement Review

| Run | Review rows | Gold incomplete | Span drift | Supported benchmark FP | Plausible overcall | Deterministic meaning change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v08_dev140_control | 137 | 61 | 97 | 61 | 29 | 137 |
| v09_partial_hybrid | 137 | 56 | 97 | 56 | 31 | 135 |
| v0916_deepseek_diagnostic | 137 | 37 | 97 | 37 | 28 | 137 |
| v0922_qwen_diagnostic | 138 | 30 | 97 | 30 | 24 | 138 |

## Notes

Raw/source, evidence-valid, dictionary-only, residual-addition, and final surfaces are directly scored when the assembly row contains materialized prediction_surfaces. Older artifacts fall back to their closest available scored surfaces.

The row-level sample in the JSON is intentionally capped; use the JSON for concrete letter IDs and example evidence when adjudicating gold disagreement.
