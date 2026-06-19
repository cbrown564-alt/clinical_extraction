# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v04_live_dev10_gpt41mini_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.4`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 10

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 59
- Mentions scored: 59
- Evidence-invalid dropped: 0

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev10`
- Rows: `10`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.6308 | no | Diagnosis, SeizureFrequency, Prescription |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.4118 | 0.5000 | 0.3500 | 7 | 7 | 13 | 0.4882 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.3889 | 0.5000 | 0.3182 | 7 | 7 | 15 | 0.5111 |
| exectv2_target_indicators_single_call | Prescription | 0.8889 | 0.8421 | 0.9412 | 16 | 3 | 1 | 0.0111 |
| exectv2_target_indicators_single_call | Investigations | 0.9167 | 0.9167 | 0.9167 | 11 | 1 | 1 | 0.0000 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 13 | 7 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 15 | 7 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 1 | 3 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 1 | 1 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.4118 | 0.4882 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.3889 | 0.5111 |
| Prescription | exectv2_target_indicators_single_call | 0.8889 | 0.0111 |
| Investigations | exectv2_target_indicators_single_call | 0.9167 | 0.0000 |
