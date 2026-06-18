# ExECTv2 Family-Routed LLM-First Comparison

- Generated: `2026-06-18`
- Split/stage: `dev` / `dev140`
- Rows: `140`
- Primary routed families: `Prescription, Investigations, Diagnosis, SeizureFrequency`
- Gate decision: **dev-gate-passed-qualified**
- Ownership: `llm_first_with_hybrid_sf_route`
- JSON: `experiments/exectv2_family_routed_llm_first_dev140_gpt41mini_20260618.json`
- JSONL: `experiments/exectv2_family_routed_llm_first_dev140_gpt41mini_20260618.jsonl`
- Pilot25 replay: `dev-gate-passed-qualified` over `25` rows

## Key Insight

The family-routed candidate improves the four-family CUI-free clinical-recovery headline from `0.4313` to `0.5592` by replacing the collapsed single-pass SeizureFrequency surface with the event/state route. The result is a qualified architecture win, not a clean LLM-first benchmark claim, because the SF source uses deterministic candidate/projection and unknown-suppression policy.

## Table 1: Architecture Ownership

| Candidate | Owner | Prediction-bearing component | Deterministic adapters | Claim allowed |
| --- | --- | --- | --- | --- |
| deterministic_all9 | `rules_only` | deterministic rules | projection/scorer | rules baseline |
| llm_only_all_entities | `llm_first` | single broad LLM pass | evidence/CUI/certainty/rendering | negative baseline |
| hybrid_all_entities | `hybrid` | candidate set + verifier | projection/rendering | hybrid comparator |
| family_routed_llm_first | `llm_first_with_hybrid_sf_route` | shared P/I/D pass + SF event/state route | evidence/CUI/certainty/rendering + SF suppression/projection | dev architecture evidence, qualified ownership |

## Table 2: Aggregate Essential Clinical Recovery

| Candidate | Families | CUI-free F1 | Precision | Recall | CUI-projected F1 | Evidence exact |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| deterministic_all9 | routed four | 0.7184 | 0.7250 | 0.7119 | 0.7263 | 1.0000 |
| llm_only_all_entities | routed four | 0.4313 | 0.4860 | 0.3876 | 0.4313 | 1.0000 |
| hybrid_all_entities | routed four | 0.5684 | 0.5931 | 0.5458 | 0.5847 | 1.0000 |
| family_routed_llm_first | routed four | 0.5592 | 0.6195 | 0.5096 | 0.5952 | 1.0000 |

## Table 3: Per-Family Recovery

| Family | Single-pass F1 | Routed F1 | Delta | Evidence exact | Dominant residual |
| --- | ---: | ---: | ---: | ---: | --- |
| Prescription | 0.7472 | 0.7472 | +0.0000 | 1.0000 | candidate_miss (60) |
| Investigations | 0.7475 | 0.7475 | +0.0000 | 1.0000 | wrong_detail_selection (55) |
| Diagnosis | 0.3161 | 0.2898 | -0.0263 | 1.0000 | candidate_miss (287) |
| SeizureFrequency | 0.0118 | 0.6321 | +0.6203 | 1.0000 | wrong_detail_selection (77) |

## Table 4: SF Event/State Diagnostics

| SF diagnostic | Count or rate | Notes |
| --- | ---: | --- |
| emitted event/state records | 199 | dev routed SF mentions |
| exact evidence records | 199 | 1.0000 exact-evidence rate |
| active/seizure-free/unknown distribution | active_rate: 91, seizure_free: 71, change_Frequent: 15, change_Infrequent: 9, change_Increased: 7, change_Same: 3, change_Decreased: 2, unknown: 1 | derived from rendered attributes |
| parse/call failures | 0 | source artifact row-level statuses |
| deterministic projection actions | 37 | named SF projection layer |
| deterministic unknown suppression/defaulting | 10 | named suppression layer |

## Gate Notes

- Four-family F1 delta vs single pass: +0.1279 (0.4313 -> 0.5592).
- Routed SF F1: 0.6321; threshold was 0.6000.
- Prescription delta +0.0000; Investigations delta +0.0000; allowed regression floor was -0.0300.
- Routed exact-evidence rate: 1.0000.
- Ownership is downgraded to `llm_first_with_hybrid_sf_route` because the SF source uses deterministic candidate/projection and unknown-suppression layers.
