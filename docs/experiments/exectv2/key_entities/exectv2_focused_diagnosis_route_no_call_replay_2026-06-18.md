# ExECTv2 Focused Diagnosis Route No-Call Replay

- Generated: `2026-06-18`
- Split/stage: `dev` / `dev140`
- Rows: `140`
- Primary routed families: `Prescription, Investigations, Diagnosis, SeizureFrequency`
- Gate decision: **dev-architecture-route-useful-qualified**
- Ownership: `llm_first_with_hybrid_diagnosis_and_sf_routes`
- JSON: `experiments/exectv2_family_routed_with_focused_diagnosis_route_dev140_gpt41mini_20260618.json`
- JSONL: `experiments/exectv2_family_routed_with_focused_diagnosis_route_dev140_gpt41mini_20260618.jsonl`
- Pilot25 replay: `dev-architecture-route-useful-qualified` over `25` rows

## Key Insight

This no-call replay keeps Prescription and Investigations on the shared broad pass, keeps SeizureFrequency on the existing event/state route, and substitutes the frozen Diagnosis reconciler v0.1 artifact only for Diagnosis.

Current routed Diagnosis remains weak at `0.2898`. The focused Diagnosis lane replays at `0.7127` on dev140, but this is still a qualified development route rather than a solved Diagnosis component or a full-200/test authorization.

## Table 1: Architecture Ownership

| Candidate | Owner | Prediction-bearing component | Deterministic adapters | Claim allowed |
| --- | --- | --- | --- | --- |
| deterministic_all9 | `rules_only` | deterministic rules | projection/scorer | rules baseline |
| llm_only_all_entities | `llm_first` | single broad LLM pass | evidence/CUI/certainty/rendering | negative baseline |
| hybrid_all_entities | `hybrid` | candidate set + verifier | projection/rendering | hybrid comparator |
| family_routed_llm_first | `llm_first_with_hybrid_sf_route` | shared P/I/D pass + SF event/state route | evidence/CUI/certainty/rendering + SF suppression/projection | dev architecture evidence, qualified ownership |
| family_routed_with_focused_diagnosis_route | `llm_first_with_hybrid_diagnosis_and_sf_routes` | shared P/I pass + focused Diagnosis route + SF event/state route | evidence/CUI/certainty/rendering + SF suppression/projection | dev-only no-call route evidence, not Diagnosis solved |

## Table 2: Aggregate Essential Clinical Recovery

| Candidate | Families | CUI-free F1 | Precision | Recall | CUI-projected F1 | Evidence exact |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| deterministic_all9 | routed four | 0.7301 | 0.7281 | 0.7322 | 0.7380 | 1.0000 |
| llm_only_all_entities | routed four | 0.4313 | 0.4860 | 0.3876 | 0.4313 | 1.0000 |
| hybrid_all_entities | routed four | 0.5684 | 0.5931 | 0.5458 | 0.5847 | 1.0000 |
| family_routed_llm_first | routed four | 0.5592 | 0.6195 | 0.5096 | 0.5952 | 1.0000 |
| family_routed_with_focused_diagnosis_route | routed four | 0.7081 | 0.7022 | 0.7141 | 0.7406 | 1.0000 |

## Table 3: Per-Family Recovery

| Family | Baseline F1 | Replay F1 | Delta | Evidence exact | Dominant residual |
| --- | ---: | ---: | ---: | ---: | --- |
| Prescription | 0.7472 | 0.7472 | +0.0000 | 1.0000 | candidate_miss (60) |
| Investigations | 0.7475 | 0.7475 | +0.0000 | 1.0000 | wrong_detail_selection (55) |
| Diagnosis | 0.2898 | 0.7127 | +0.4229 | 1.0000 | candidate_miss (106) |
| SeizureFrequency | 0.6321 | 0.6321 | +0.0000 | 1.0000 | wrong_detail_selection (77) |

## Table 4: SF Event/State Diagnostics

| SF diagnostic | Count or rate | Notes |
| --- | ---: | --- |
| emitted event/state records | 199 | dev routed SF mentions |
| exact evidence records | 199 | 1.0000 exact-evidence rate |
| active/seizure-free/unknown distribution | active_rate: 91, seizure_free: 71, change_Frequent: 15, change_Infrequent: 9, change_Increased: 7, change_Same: 3, change_Decreased: 2, unknown: 1 | derived from rendered attributes |
| parse/call failures | 0 | source artifact row-level statuses |
| deterministic projection actions | 37 | named SF projection layer |
| deterministic unknown suppression/defaulting | 10 | named suppression layer |

## Focused Diagnosis Route Diagnostics

| Diagnosis diagnostic | Count or rate | Notes |
| --- | ---: | --- |
| emitted Diagnosis records | 436 | dev focused Diagnosis mentions |
| exact evidence records | 436 | 1.0000 exact-evidence rate |
| parse/call failures | 0 | source artifact row-level statuses |

## Gate Notes

- Four-family F1 delta vs current routed candidate: +0.1489 (0.5592 -> 0.7081).
- Diagnosis F1 delta vs current routed Diagnosis: +0.4229 (0.2898 -> 0.7127); usefulness thresholds were +0.2500 and >=0.6000.
- Focused Diagnosis exact-evidence rate: 1.0000.
- Prescription/Investigations/SeizureFrequency F1 drift vs current routed: Prescription +0.0000, Investigations +0.0000, SeizureFrequency +0.0000; allowed absolute drift was <=0.001.
- Route source parse/call failures: Diagnosis 0, SeizureFrequency 0.
- This is a no-call dev replay only; it does not solve Diagnosis and does not authorize full-200/test evaluation.
