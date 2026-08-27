# ExECTv2 Focused-Lane Component-Evidence Replay

- Generated: `2026-07-31`
- Split/stage: `dev140` / `dev140140`
- Candidate: `exectv2_deepseek_v4_flash_0731_update_dev140`
- Gate decision: **same-core-model-swap-dev140-readout**
- Claim boundary: ExECTv2 dev140 DeepSeek-V4-Flash-0731 update re-run only.
- JSON: `experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731.json`
- JSONL: `experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731.jsonl`

## Finding Assembly

This replay builds a per-letter clinical finding store, applies entity-specific lenses, and renders scoring views from the same final findings. It is a structural replay over frozen artifacts; it introduces no live model calls.

| Entity | Producer | Lens | Ownership |
| --- | --- | --- | --- |
| Diagnosis | `experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731_structured.jsonl` | `diagnosis_heading_recovery_residual_benchmark_v05` | `named_model_structured_diagnosis_plus_rules` |
| SeizureFrequency | `experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731_sf_unknown_suppression.jsonl` | `sf_state_projection_suppression_v01` | `named_model_sf_plus_projection_suppression` |
| Prescription | `experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731_structured.jsonl` | `prescription_dictionary_v09` | `named_model_prescription_plus_shared_rules` |
| Investigations | `experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731_structured.jsonl` | `investigations_result_v01` | `named_model_investigations` |

## Score Views

| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | `raw_lane_score` | 0.8139 | 0.7700 | 0.6276 | 0.9479 | 0.9506 |
| evidence_valid | `evidence_valid_score` | 0.8648 | 0.8917 | 0.6606 | 0.9353 | 0.9506 |
| benchmark_cui | `cui_projection_companion` | 0.8648 | 0.8917 | 0.6606 | 0.9353 | 0.9506 |
| clinical_headline | `headline_target` | 0.8994 | 0.8917 | 0.8282 | 0.9353 | 0.9506 |

## Materialized Intermediate Surfaces

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `source_scored` | 0.8221 | 0.7700 | 0.6606 | 0.9479 | 0.9506 |
| `evidence_valid` | 0.8221 | 0.7700 | 0.6606 | 0.9479 | 0.9506 |
| `protocol_model_preserving_canonical` | 0.8221 | 0.7700 | 0.6606 | 0.9479 | 0.9506 |
| `dictionary_normalized` | 0.8544 | 0.8634 | 0.6606 | 0.9394 | 0.9506 |
| `residual_benchmark_added` | 0.8648 | 0.8917 | 0.6606 | 0.9353 | 0.9506 |

## Fact-Origin Accounting

| Surface | post_model_rescue | target_model_generated |
| --- | ---: | ---: |
| `source_scored` | 0 | 831 |
| `evidence_valid` | 0 | 831 |
| `protocol_model_preserving_canonical` | 0 | 831 |
| `dictionary_normalized` | 0 | 794 |
| `residual_benchmark_added` | 63 | 794 |

## Benchmark And Fidelity Views

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.4712 |
| Benchmark after CUI/projection | 0.5170 |
| Diagnosis.concept_negation | 0.8851 |
| SeizureFrequency.active_rate_fidelity | 0.6667 |

## Gate Summary

| Gate | Status | Detail |
| --- | --- | --- |
| Prescription control regression | pass | delta vs v0.42 control +0.1139; floor -0.0100 |
| Investigations control regression | pass | delta vs v0.42 control +0.0891; floor -0.0100 |
| Diagnosis headline | pass | 0.8917; must beat 0.6693 and tie/beat 0.7127 |
| Diagnosis concept_negation | pass | 0.8851; baseline 0.6693 |
| SeizureFrequency headline | pass | 0.8282; must beat 0.5572 and tie/beat 0.6321 |
| SeizureFrequency active_rate_fidelity | pass | 0.6667; baseline 0.2887 |
| Prescription changed-row control | fail | 51 changed rows |
| Investigations changed-row control | pass | 0 changed rows |

## Lens Diagnostics

| Entity | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0 | 0 | 0 | 1.0000 |
| SeizureFrequency | 0 | 0 | 0 | 1.0000 |
| Prescription | 0 | 0 | 0 | 1.0000 |
| Investigations | 0 | 0 | 0 | 1.0000 |

## Changed Rows

| Comparison | Indicator | Changed rows | Categories |
| --- | --- | ---: | --- |
| versus_v042_default_quarantine | Diagnosis | 89 | hierarchy_reconciliation=29, assertion_or_negation_change=58, hierarchy_reconciliation_or_duplicate_collapse=58, projection_only=2 |
| versus_v042_default_quarantine | SeizureFrequency | 13 | active_rate=10, projection_action=12, seizure_free=4, unknown_or_change_state=3, reject_or_drop=1 |
| versus_v042_default_quarantine | Prescription | 51 | model_output=51 |
| versus_v042_default_quarantine | Investigations | 0 | none |

Every row-level mention carries source artifact, source lane, ownership, producer provenance, lens provenance, evidence-valid status, and the rendered scoring view can be reconstructed from the JSONL.


## Same-Core Model-Swap Contract

- Architecture core: `exectv2_decision_0041_six_model_single_call_dev140_v1`
- Model: `DeepSeek V4 Flash 0731` (`deepseek/deepseek-v4-flash`)
- Runtime: `official_deepseek_v4_flash_0731_default_thinking`
- Prompt profile: `full`
- Calls per letter: `1.0`
- Live call components: `structured_key_family_event_ledger`
- Replayed/no-call components: `sf_structured_direct_adapter, sf_state_projection, sf_unknown_suppression, prescription_dictionary_lens, finding_assembly`
- Row inspection policy: `dev140_only_no_full200_or_holdout_row_level_inspection`

## Provider-update comparison (ruleset-matched)

Protocol: [0731 re-run protocol](exectv2_deepseek_v4_flash_0731_dev140_protocol_2026-07-31.md)  
Diff artifact:
`experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731_vs_20260715_current_rules.json`  
Ruleset-matched baseline (no new model calls):
[current-rules replay of 2026-07-15 structured](exectv2_deepseek_v4_flash_20260715_model_current_rules_dev140_2026-07-31.md)
(`experiments/exectv2_deepseek_v4_flash_20260715_model_current_rules_dev140_20260731.json`)

Both sides use the same frozen prompt, decision-0040/0041 stack,
Diagnosis/Prescription `default`/`default`, and the **current** SF
projection/suppression + assembly lenses. The baseline freezes the
2026-07-15 DeepSeek structured outputs and re-derives deterministic stages
only. The update side is the live 0731 no-cache run. Structured `max_tokens`
was raised to `64000` for the update run after the retained `16000` budget
truncated under 0731 thinking (see protocol amendment). Final update
structured progress: 140/140 with 0 call failures and 0 parse failures.

The current-rules no-call replay of the 2026-07-15 model reproduces the
original retained panel aggregates exactly (overall 0.8767; same family F1s),
so post-July-15 deterministic changes do not move this DeepSeek cell under
the active default policy.

### Aggregate clinical_headline

| Surface | 2026-07-15 model / current rules | 2026-07-31 0731 | Delta |
| --- | ---: | ---: | ---: |
| Overall | 0.8767 | 0.8994 | +0.0227 |
| Diagnosis | 0.8764 | 0.8917 | +0.0153 |
| SeizureFrequency | 0.7610 | 0.8282 | +0.0672 |
| Prescription | 0.9280 | 0.9353 | +0.0073 |
| Investigations | 0.9389 | 0.9506 | +0.0117 |

Largest gain is Seizure Frequency. This is development evidence for a
provider model revision; it does not automatically replace the retained
six-model panel cell or speak to test60.

### Row-level changed letters

Among 140 shared letters, **59** change prediction keys and/or family F1
under clinical_headline unit keys:

| Letter direction | Count |
| --- | ---: |
| Rescue (net family F1 up) | 38 |
| Regression (net family F1 down) | 11 |
| Prediction-only (keys change, F1 unchanged) | 10 |

Family prediction-key changes: SeizureFrequency 36, Diagnosis 17,
Prescription 8, Investigations 4.

Family correctness direction (letter-local F1 up/down):

| Family | Rescue | Regression |
| --- | ---: | ---: |
| SeizureFrequency | 20 | 4 |
| Diagnosis | 11 | 4 |
| Prescription | 5 | 3 |
| Investigations | 3 | 0 |

Representative rescues (0→1 letter-family F1): EA0028 / EA0068 / EA0102 /
EA0151 (SF); EA0062 / EA0117 (Investigations). Representative regressions:
EA0008 / EA0186 (Prescription 1→0); EA0087 (SF 1→0.4); EA0153 (Diagnosis
1→0.4).

### Decision

Answer: the 0731 API revision **improves** ExECTv2 `dev140` clinical_headline
under this frozen stack, driven mainly by Seizure Frequency, with a smaller
net positive elsewhere and a non-empty regression tail. Claim boundary remains
development-only; panel replacement and holdout transfer are separate
decisions.
