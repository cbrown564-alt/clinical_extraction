# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_family_routed_llm_first`
- Split/stage: `dev` / `dev140`
- Rows: `140`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| deterministic_all9 | `rules_only` | 0.7301 | no | Diagnosis, SeizureFrequency, Investigations |
| llm_only_all_entities | `llm_first` | 0.4313 | no | Diagnosis, SeizureFrequency, Prescription, Investigations |
| hybrid_all_entities | `hybrid` | 0.5684 | no | Diagnosis, SeizureFrequency, Prescription, Investigations |
| family_routed_llm_first | `llm_first_with_hybrid_sf_route` | 0.5592 | no | Diagnosis, SeizureFrequency, Prescription, Investigations |
| family_routed_with_focused_diagnosis_route | `llm_first_with_hybrid_diagnosis_and_sf_routes` | 0.7081 | no | Diagnosis, SeizureFrequency, Prescription, Investigations |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| deterministic_all9 | Diagnosis | 0.7302 | 0.7955 | 0.6748 | 249 | 64 | 120 | 0.1698 |
| deterministic_all9 | SeizureFrequency | 0.7277 | 0.6942 | 0.7647 | 143 | 63 | 44 | 0.1723 |
| deterministic_all9 | Prescription | 0.9072 | 0.9293 | 0.8860 | 171 | 13 | 22 | 0.0000 |
| deterministic_all9 | Investigations | 0.5263 | 0.4545 | 0.6250 | 85 | 102 | 51 | 0.3737 |
| llm_only_all_entities | Diagnosis | 0.3161 | 0.4162 | 0.2547 | 94 | 115 | 275 | 0.5839 |
| llm_only_all_entities | SeizureFrequency | 0.0118 | 0.0132 | 0.0107 | 2 | 150 | 185 | 0.8882 |
| llm_only_all_entities | Prescription | 0.7472 | 0.8160 | 0.6891 | 133 | 30 | 60 | 0.1528 |
| llm_only_all_entities | Investigations | 0.7475 | 0.6746 | 0.8382 | 114 | 55 | 22 | 0.1525 |
| hybrid_all_entities | Diagnosis | 0.4605 | 0.5617 | 0.3902 | 144 | 71 | 225 | 0.4395 |
| hybrid_all_entities | SeizureFrequency | 0.2963 | 0.3171 | 0.2781 | 52 | 112 | 135 | 0.6037 |
| hybrid_all_entities | Prescription | 0.8241 | 0.7703 | 0.8860 | 171 | 51 | 22 | 0.0759 |
| hybrid_all_entities | Investigations | 0.7412 | 0.6554 | 0.8529 | 116 | 61 | 20 | 0.1588 |
| family_routed_llm_first | Diagnosis | 0.2898 | 0.4162 | 0.2222 | 82 | 115 | 287 | 0.6102 |
| family_routed_llm_first | SeizureFrequency | 0.6321 | 0.6131 | 0.6524 | 122 | 77 | 65 | 0.2679 |
| family_routed_llm_first | Prescription | 0.7472 | 0.8160 | 0.6891 | 133 | 30 | 60 | 0.1528 |
| family_routed_llm_first | Investigations | 0.7475 | 0.6746 | 0.8382 | 114 | 55 | 22 | 0.1525 |
| family_routed_with_focused_diagnosis_route | Diagnosis | 0.7127 | 0.7127 | 0.7127 | 263 | 106 | 106 | 0.1873 |
| family_routed_with_focused_diagnosis_route | SeizureFrequency | 0.6321 | 0.6131 | 0.6524 | 122 | 77 | 65 | 0.2679 |
| family_routed_with_focused_diagnosis_route | Prescription | 0.7472 | 0.8160 | 0.6891 | 133 | 30 | 60 | 0.1528 |
| family_routed_with_focused_diagnosis_route | Investigations | 0.7475 | 0.6746 | 0.8382 | 114 | 55 | 22 | 0.1525 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| deterministic_all9 | Diagnosis | 120 | 64 | 6 | 0 |
| deterministic_all9 | SeizureFrequency | 44 | 63 | 4 | 0 |
| deterministic_all9 | Prescription | 22 | 13 | 0 | 0 |
| deterministic_all9 | Investigations | 51 | 102 | 7 | 0 |
| llm_only_all_entities | Diagnosis | 275 | 115 | 5 | 0 |
| llm_only_all_entities | SeizureFrequency | 185 | 150 | 0 | 0 |
| llm_only_all_entities | Prescription | 60 | 30 | 0 | 0 |
| llm_only_all_entities | Investigations | 22 | 55 | 8 | 0 |
| hybrid_all_entities | Diagnosis | 225 | 71 | 9 | 0 |
| hybrid_all_entities | SeizureFrequency | 135 | 112 | 0 | 0 |
| hybrid_all_entities | Prescription | 22 | 51 | 0 | 0 |
| hybrid_all_entities | Investigations | 20 | 61 | 9 | 0 |
| family_routed_llm_first | Diagnosis | 287 | 115 | 5 | 0 |
| family_routed_llm_first | SeizureFrequency | 65 | 77 | 0 | 0 |
| family_routed_llm_first | Prescription | 60 | 30 | 0 | 0 |
| family_routed_llm_first | Investigations | 22 | 55 | 8 | 0 |
| family_routed_with_focused_diagnosis_route | Diagnosis | 106 | 106 | 76 | 0 |
| family_routed_with_focused_diagnosis_route | SeizureFrequency | 65 | 77 | 0 | 0 |
| family_routed_with_focused_diagnosis_route | Prescription | 60 | 30 | 0 | 0 |
| family_routed_with_focused_diagnosis_route | Investigations | 22 | 55 | 8 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | deterministic_all9 | 0.7302 | 0.1698 |
| SeizureFrequency | deterministic_all9 | 0.7277 | 0.1723 |
| Prescription | deterministic_all9 | 0.9072 | 0.0000 |
| Investigations | llm_only_all_entities | 0.7475 | 0.1525 |
