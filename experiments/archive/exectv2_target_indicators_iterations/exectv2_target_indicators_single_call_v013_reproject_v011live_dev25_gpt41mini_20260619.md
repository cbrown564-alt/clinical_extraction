# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v013_reproject_v011live_dev25_gpt41mini_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.13`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `no-call-reproject`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 132
- Mentions scored: 112
- Evidence-invalid dropped: 20

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev25`
- Rows: `25`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.8348 | no | Diagnosis, SeizureFrequency |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.7799 | 0.9091 | 0.6829 | 28 | 2 | 13 | 0.1201 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.7170 | 0.7037 | 0.7308 | 19 | 8 | 7 | 0.1830 |
| exectv2_target_indicators_single_call | Prescription | 0.9351 | 0.9231 | 0.9474 | 36 | 3 | 2 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 0.9048 | 0.8636 | 0.9500 | 19 | 3 | 1 | 0.0000 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 13 | 2 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 9 | 9 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 2 | 3 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 1 | 3 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.7799 | 0.1201 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.7170 | 0.1830 |
| Prescription | exectv2_target_indicators_single_call | 0.9351 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 0.9048 | 0.0000 |
