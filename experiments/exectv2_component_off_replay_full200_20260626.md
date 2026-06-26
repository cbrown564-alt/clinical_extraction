# ExECTv2 One-Component-Off Aggregate Readout (full200)

- Generated: `2026-06-26`
- JSON: `experiments/exectv2_component_off_replay_full200_20260626.json`
- JSONL: `experiments/exectv2_component_off_replay_full200_20260626.jsonl`
- Predeclaration: `docs/experiments/exectv2/reliability/exectv2_component_off_full200_predeclaration_2026-06-26.md`
- Code hash at execution: `ff5c609`
- Worktree state at execution: `dirty: M PROJECT_STATUS.md;  M src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/component_ablation_replay.py;  M tests/test_exectv2_component_ablation_replay.py; ?? experiments/exectv2_component_off_replay_full200_20260626.json; ?? experiments/exectv2_component_off_replay_full200_20260626.jsonl; ?? experiments/exectv2_component_off_replay_full200_20260626.md; ?? scripts/build_exectv2_component_off_full200_replay.py`
- Claim boundary: full-200 aggregate-only component-impact replay under the frozen 2026-06-26 predeclaration; separate from reliability scorecard evidence
- Row inspection boundary: `aggregate_only_no_full200_or_holdout_row_level_inspection`
- No model calls; replay is computed from saved full200 summary artifacts.
- Component Impact evidence only, not Reliability Scorecard evidence.
- Stop-rule outcome: `all_selected_component_deltas_positive_limited_claim`

## Preflight

| Source family | Status | Split | Rows | Surfaces | Telemetry |
| --- | --- | --- | ---: | --- | --- |
| `exectv2_2call_no_sf_adjudicator_gpt41mini_full200` | `pass` | `full200` | 200 | pass | pass |
| `exectv2_2call_no_sf_adjudicator_deepseek_full200` | `pass` | `full200` | 200 | pass | pass |
| `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200` | `pass` | `full200` | 200 | pass | pass |

## Selected Components

| Component | Type | Portability | Prediction-bearing | Baseline | Off |
| --- | --- | --- | --- | --- | --- |
| `standard_dictionary` | `dictionary` | `clinical_epilepsy` | `conditional` | `dictionary_normalized` | `evidence_valid` |
| `residual_semantic_lens` | `semantic_lens` | `benchmark_format` | `yes` | `residual_semantic_added` | `dictionary_normalized` |
| `headline_projection` | `deterministic_projection` | `benchmark_format` | `no` | `headline_projection` | `residual_semantic_added` |

## Aggregate Component-Off Table

| Source family | Component | Baseline F1 | Component-off F1 | Contribution delta | Diagnosis | SF | Rx | Inv |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `exectv2_2call_no_sf_adjudicator_gpt41mini_full200` | standard_dictionary | 0.7922 | 0.7736 | +0.0186 | +0.0508 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_2call_no_sf_adjudicator_gpt41mini_full200` | residual_semantic_lens | 0.8039 | 0.7922 | +0.0117 | +0.0310 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_2call_no_sf_adjudicator_gpt41mini_full200` | headline_projection | 0.8356 | 0.8039 | +0.0317 | +0.0000 | +0.1304 | +0.0000 | +0.0000 |
| `exectv2_2call_no_sf_adjudicator_deepseek_full200` | standard_dictionary | 0.8110 | 0.7879 | +0.0231 | +0.0628 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_2call_no_sf_adjudicator_deepseek_full200` | residual_semantic_lens | 0.8216 | 0.8110 | +0.0106 | +0.0276 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_2call_no_sf_adjudicator_deepseek_full200` | headline_projection | 0.8566 | 0.8216 | +0.0350 | +0.0000 | +0.1417 | +0.0000 | +0.0000 |
| `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200` | standard_dictionary | 0.7797 | 0.7507 | +0.0290 | +0.0802 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200` | residual_semantic_lens | 0.7895 | 0.7797 | +0.0098 | +0.0257 | +0.0000 | +0.0000 | +0.0000 |
| `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200` | headline_projection | 0.8197 | 0.7895 | +0.0302 | +0.0000 | +0.1221 | +0.0000 | +0.0000 |

## Validity And Operations

| Source family | Schema validity | Evidence validity | Calls failed | Parse/schema failures | Invalid evidence dropped |
| --- | ---: | ---: | ---: | ---: | ---: |
| `exectv2_2call_no_sf_adjudicator_gpt41mini_full200` | 1.0000 | 1.0000 | 0 | 0 | 0 |
| `exectv2_2call_no_sf_adjudicator_deepseek_full200` | 0.9988 | 1.0000 | 0 | 1 | 0 |
| `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200` | 1.0000 | 1.0000 | 0 | 0 | 0 |

## Interpretation Boundary

Contribution delta is baseline minus component-off on the declared `clinical_headline` scorer. Positive deltas mean removing the component lowered aggregate F1 on this source family; null or negative deltas remain valid component-impact evidence and stop the audit without tuning.

These rows are full200 aggregate Component Impact evidence only. They are not holdout results, strict benchmark claims, or Reliability Scorecard promotion evidence.
