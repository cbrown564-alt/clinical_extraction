# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_reparse_dev10_gpt41mini_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.1`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `no_call_reparse`
- Letters: 10

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 52
- Mentions scored: 51
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
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.5385 | no | Diagnosis, SeizureFrequency, Prescription, Investigations |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.2105 | 0.4000 | 0.1429 | 4 | 6 | 24 | 0.6895 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.3125 | 0.5000 | 0.2273 | 5 | 5 | 17 | 0.5875 |
| exectv2_target_indicators_single_call | Prescription | 0.8889 | 0.8421 | 0.9412 | 16 | 3 | 1 | 0.0111 |
| exectv2_target_indicators_single_call | Investigations | 0.8333 | 0.8333 | 0.8333 | 10 | 2 | 2 | 0.0667 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 24 | 6 | 0 | 10 |
| exectv2_target_indicators_single_call | SeizureFrequency | 17 | 5 | 0 | 10 |
| exectv2_target_indicators_single_call | Prescription | 1 | 3 | 0 | 19 |
| exectv2_target_indicators_single_call | Investigations | 2 | 2 | 0 | 12 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.2105 | 0.6895 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.3125 | 0.5875 |
| Prescription | exectv2_target_indicators_single_call | 0.8889 | 0.0111 |
| Investigations | exectv2_target_indicators_single_call | 0.8333 | 0.0667 |
