# ExECTv2 One-Component-Off Aggregate Readout (dev140)

- Generated: `2026-06-26`
- JSON: `experiments/exectv2_component_off_replay_dev140_20260626.json`
- JSONL: `experiments/exectv2_component_off_replay_dev140_20260626.jsonl`
- Layer ladder: `experiments/exectv2_component_ablation_replay_dev140_20260624.json`
- Claim boundary: dev140 replay-only one-component-off aggregate component-impact readout; separate from reliability scorecard
- Row inspection policy: `aggregate_only`
- No model calls; replay is computed from saved dev140 summary artifacts.
- Reported separately from the reliability scorecard.

## Aggregate Component-Off Table

| Architecture | Component | Baseline F1 | Component-off F1 | Contribution delta | Diagnosis | SF | Rx | Inv |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `exectv2_holistic_finding_assembly_v08_dev140` | evidence_validation | 0.8308 | 0.8308 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v08_dev140` | standard_dictionary | 0.8697 | 0.8308 | +0.0389 | +0.1042 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v08_dev140` | residual_semantic_lens | 0.8872 | 0.8697 | +0.0175 | +0.0476 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v08_dev140` | headline_projection | 0.9155 | 0.8872 | +0.0283 | +0.0000 | +0.1239 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | evidence_validation | 0.8211 | 0.8211 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | standard_dictionary | 0.8601 | 0.8211 | +0.0390 | +0.1042 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | residual_semantic_lens | 0.8778 | 0.8601 | +0.0177 | +0.0476 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | headline_projection | 0.9061 | 0.8778 | +0.0283 | +0.0000 | +0.1266 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | evidence_validation | 0.7498 | 0.7498 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | standard_dictionary | 0.8334 | 0.7498 | +0.0836 | +0.1382 | +0.0824 | +0.0775 | -0.0443 |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | residual_semantic_lens | 0.8728 | 0.8334 | +0.0394 | +0.0333 | +0.0542 | -0.0015 | +0.1039 |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | headline_projection | 0.9174 | 0.8728 | +0.0446 | +0.0000 | +0.2031 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | evidence_validation | 0.6406 | 0.6406 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | standard_dictionary | 0.7526 | 0.6406 | +0.1120 | +0.1397 | +0.1728 | +0.0257 | +0.0681 |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | residual_semantic_lens | 0.8567 | 0.7526 | +0.1041 | +0.1057 | +0.1505 | +0.0300 | +0.1722 |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | headline_projection | 0.9001 | 0.8567 | +0.0434 | +0.0000 | +0.1942 | +0.0000 | +0.0000 |

## Component Claim Use

### evidence_validation

- Type: `evidence_validation`; prediction-bearing: `no`
- Claim use: On these single-lane holistic dev140 runs the evidence guard is structurally inert: producers only emit verbatim-grounded mentions, so removing validation leaves the clinical_headline score unchanged. Use this as a grounding guard check, not as proof that evidence validation is globally unnecessary.

### standard_dictionary

- Type: `dictionary`; prediction-bearing: `conditional`
- Claim use: Dictionary normalization contributes benchmark-format recovery on dev140, most visibly on `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` (overall +0.1120, mainly SeizureFrequency +0.1728). Report as conditional dictionary impact on the declared scorer, not as proof that dictionaries are globally required.

### residual_semantic_lens

- Type: `semantic_lens`; prediction-bearing: `yes`
- Claim use: Residual semantic recovery is prediction-bearing on dev140: removing the lens lowers clinical_headline by up to +0.1041 on `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` with the largest family effect on Investigations (+0.1722). This is component-impact evidence for semantic add/drop/replace layers, not a reliability-scorecard claim.

### headline_projection

- Type: `deterministic_projection`; prediction-bearing: `no`
- Claim use: Headline projection is a deterministic format layer on dev140: removing it lowers clinical_headline by up to +0.0446 on `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140`, concentrated in SeizureFrequency (+0.2031). Treat this as projection/format contribution separate from semantic fact changes.

## Interpretation Boundary

Contribution delta is baseline minus component-off on the declared `clinical_headline` scorer. A positive delta means removing the component lowered the score on this split. A zero delta means the saved surface did not change when the component was removed.

These rows are component-impact evidence only. They do not prove a component is unnecessary in general, and they must not be blended into reliability-scorecard claims.

No full-200 or holdout-facing row-level inspection is introduced.
