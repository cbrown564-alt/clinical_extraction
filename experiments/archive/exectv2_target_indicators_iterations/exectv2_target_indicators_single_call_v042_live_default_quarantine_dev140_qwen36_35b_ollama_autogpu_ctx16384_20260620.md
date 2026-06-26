# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.42`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 1
- Parse/schema failures: 4
- Mentions raw: 839
- Mentions scored: 776
- Evidence-invalid dropped: 21

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev140`
- Rows: `140`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Headline Scoring Policy

| Indicator | Headline score used |
| --- | --- |
| Diagnosis | projected clinical-fact concept_only score after deterministic Diagnosis normalization/projection; scored as projected core facts per letter |
| SeizureFrequency | projected seizure-state clinical_headline score after deterministic frequency-state normalization/projection |
| Prescription | clinical_headline regimen score after deterministic medication normalization/projection |
| Investigations | clinical_headline modality/performed/result score after deterministic investigation normalization/projection |

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.7153 | no | Diagnosis, SeizureFrequency, Prescription, Investigations |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.6693 | 0.7059 | 0.6364 | 189 | 75 | 108 | 0.2307 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.5572 | 0.5491 | 0.5655 | 95 | 78 | 73 | 0.3428 |
| exectv2_target_indicators_single_call | Prescription | 0.8214 | 0.8090 | 0.8342 | 161 | 38 | 32 | 0.0786 |
| exectv2_target_indicators_single_call | Investigations | 0.8615 | 0.9032 | 0.8235 | 112 | 12 | 24 | 0.0385 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 108 | 75 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 97 | 99 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 32 | 38 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 24 | 12 | 0 | 0 |

## Clinical Fidelity Companions

Headline keys deliberately demote projectable attributes, but two keys also forgive a genuine clinical judgement. These companions expose that gap so the headline is not read as the whole story: Diagnosis `concept_only` forgives Negation; SeizureFrequency `clinical_headline` forgives rate magnitude (e.g. 2-4/month and 6-9/week share one key).

| Candidate | Indicator | Companion | Forgives | Headline F1 | Companion F1 | Fidelity gap |
| --- | --- | --- | --- | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | `concept_negation` | Negation (negated vs affirmed) | 0.6693 | 0.6693 | 0.0000 |
| exectv2_target_indicators_single_call | SeizureFrequency | `active_rate_fidelity` | rate magnitude among active states | 0.4335 | 0.2887 | 0.1448 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.6693 | 0.2307 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.5572 | 0.3428 |
| Prescription | exectv2_target_indicators_single_call | 0.8214 | 0.0786 |
| Investigations | exectv2_target_indicators_single_call | 0.8615 | 0.0385 |
