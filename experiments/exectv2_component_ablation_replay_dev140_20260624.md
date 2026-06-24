# ExECTv2 Layered Component Impact Replay

- Generated: `2026-06-24`
- JSON: `experiments/exectv2_component_ablation_replay_dev140_20260624.json`
- JSONL: `experiments/exectv2_component_ablation_replay_dev140_20260624.jsonl`
- Claim boundary: dev140 replay-only aggregate component-impact ladder
- Row inspection policy: `aggregate_only`
- No model calls; replay is computed from saved dev140 summary artifacts.

## Architecture Summary

| Architecture | Decision | Final F1 | Raw candidates | Dictionary | Residual semantic | Headline projection |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `exectv2_holistic_finding_assembly_v08_dev140` | control | 0.9155 | 0.8328 | 0.8697 | 0.8872 | 0.9155 |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | simplification | 0.9061 | 0.8231 | 0.8601 | 0.8778 | 0.9061 |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | diagnostic | 0.9174 | 0.7498 | 0.8334 | 0.8728 | 0.9174 |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | diagnostic | 0.9001 | 0.6406 | 0.7526 | 0.8567 | 0.9001 |

## Layer Impacts

| Architecture | Layer | Overall delta | Diagnosis | SF | Rx | Inv |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `exectv2_holistic_finding_assembly_v08_dev140` | Raw lane candidates | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v08_dev140` | Source-scored mentions | -0.0020 | -0.0053 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v08_dev140` | Evidence-valid mentions | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v08_dev140` | Dictionary normalized | +0.0389 | +0.1042 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v08_dev140` | Residual semantic additions | +0.0175 | +0.0476 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v08_dev140` | Headline projection | +0.0283 | +0.0000 | +0.1239 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | Raw lane candidates | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | Source-scored mentions | -0.0020 | -0.0053 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | Evidence-valid mentions | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | Dictionary normalized | +0.0390 | +0.1042 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | Residual semantic additions | +0.0177 | +0.0476 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | Headline projection | +0.0283 | +0.0000 | +0.1239 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | Raw lane candidates | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | Source-scored mentions | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | Evidence-valid mentions | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | Dictionary normalized | +0.0836 | +0.1382 | +0.0824 | +0.0775 | -0.0443 |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | Residual semantic additions | +0.0394 | +0.0333 | +0.0542 | -0.0015 | +0.1039 |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | Headline projection | +0.0446 | +0.0000 | +0.2031 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | Raw lane candidates | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | Source-scored mentions | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | Evidence-valid mentions | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | Dictionary normalized | +0.1120 | +0.1397 | +0.1728 | +0.0257 | +0.0681 |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | Residual semantic additions | +0.1041 | +0.1057 | +0.1505 | +0.0300 | +0.1722 |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | Headline projection | +0.0434 | +0.0000 | +0.1942 | +0.0000 | +0.0000 |

## Interpretation Boundary

These are layered aggregate replays. A positive delta means the score increased from the previous saved surface to the current surface. A zero delta means the layer did not change that score surface for that architecture.

No full-200 or holdout-facing row-level inspection is introduced.
