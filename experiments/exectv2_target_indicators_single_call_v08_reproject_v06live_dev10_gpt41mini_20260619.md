# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v08_reproject_v06live_dev10_gpt41mini_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.8`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `no-call-reproject`
- Letters: 10

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 64
- Mentions scored: 57
- Evidence-invalid dropped: 7

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev10`
- Rows: `10`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.7834 | no | Diagnosis, SeizureFrequency |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.6705 | 0.6923 | 0.6500 | 13 | 4 | 7 | 0.2295 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.6316 | 0.7500 | 0.5455 | 12 | 4 | 10 | 0.2684 |
| exectv2_target_indicators_single_call | Prescription | 0.9091 | 0.9375 | 0.8824 | 15 | 1 | 2 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 1.0000 | 1.0000 | 1.0000 | 12 | 0 | 0 | 0.0000 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 7 | 4 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 10 | 4 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 2 | 1 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 0 | 0 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.6705 | 0.2295 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.6316 | 0.2684 |
| Prescription | exectv2_target_indicators_single_call | 0.9091 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 1.0000 | 0.0000 |
