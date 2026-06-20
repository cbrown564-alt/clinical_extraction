# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v02_live_dev10_gpt41mini_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.2`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 10

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 59
- Mentions scored: 58
- Evidence-invalid dropped: 1

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev10`
- Rows: `10`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.6043 | no | Diagnosis, SeizureFrequency, Investigations |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.2857 | 0.4286 | 0.2143 | 6 | 8 | 22 | 0.6143 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.5000 | 0.6429 | 0.4091 | 9 | 5 | 13 | 0.4000 |
| exectv2_target_indicators_single_call | Prescription | 0.9189 | 0.8500 | 1.0000 | 17 | 3 | 0 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 0.8333 | 0.8333 | 0.8333 | 10 | 2 | 2 | 0.0667 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 22 | 8 | 0 | 12 |
| exectv2_target_indicators_single_call | SeizureFrequency | 13 | 5 | 0 | 14 |
| exectv2_target_indicators_single_call | Prescription | 0 | 3 | 0 | 20 |
| exectv2_target_indicators_single_call | Investigations | 2 | 2 | 0 | 12 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.2857 | 0.6143 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.5000 | 0.4000 |
| Prescription | exectv2_target_indicators_single_call | 0.9189 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 0.8333 | 0.0667 |
