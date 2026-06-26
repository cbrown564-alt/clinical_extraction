# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v011_live_dev25_gpt41mini_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.11`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 132
- Mentions scored: 113
- Evidence-invalid dropped: 19

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev25`
- Rows: `25`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.8069 | no | Diagnosis, SeizureFrequency |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.7313 | 0.8636 | 0.6341 | 26 | 3 | 15 | 0.1687 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.6667 | 0.6897 | 0.6452 | 20 | 9 | 11 | 0.2333 |
| exectv2_target_indicators_single_call | Prescription | 0.9351 | 0.9231 | 0.9474 | 36 | 3 | 2 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 0.9048 | 0.8636 | 0.9500 | 19 | 3 | 1 | 0.0000 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 15 | 3 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 12 | 10 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 2 | 3 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 1 | 3 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.7313 | 0.1687 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.6667 | 0.2333 |
| Prescription | exectv2_target_indicators_single_call | 0.9351 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 0.9048 | 0.0000 |
