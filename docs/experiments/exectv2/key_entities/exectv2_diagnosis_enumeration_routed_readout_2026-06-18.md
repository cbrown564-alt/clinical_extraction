# ExECTv2 Diagnosis Enumeration Recall Pass — Routed Readout

- Generated: `2026-06-19`
- Split/stage: `dev` / `dev140` (140 letters)
- Enumeration artifact: `experiments/exectv2_llm_diagnosis_enumeration_v01_dev140_gpt41mini_20260618.jsonl`
- Aggregate ownership: `llm_first_with_hybrid_sf_route`
- Mode: **no model calls** (enumeration artifact + frozen lanes replayed).

## Four-Family Routed Surface (CUI-free)

| Candidate | F1 | Precision | Recall |
| --- | ---: | ---: | ---: |
| deterministic_all9 | 0.7301 | 0.7281 | 0.7322 |
| llm_only_all_entities | 0.4313 | 0.4860 | 0.3876 |
| hybrid_all_entities | 0.5684 | 0.5931 | 0.5458 |
| family_routed_llm_first | 0.5592 | 0.6195 | 0.5096 |
| family_routed_with_diagnosis_enumeration_pass | 0.6835 | 0.6801 | 0.6870 |

## Diagnosis Lane (CUI-free)

| Lane | F1 | Precision | Recall |
| --- | ---: | ---: | ---: |
| shared-pass Diagnosis (baseline) | 0.2898 | 0.4162 | 0.2222 |
| enumeration Diagnosis | 0.6530 | 0.6584 | 0.6477 |

## Diagnosis candidate_miss FN by slice (lower is better)

| Slice | Baseline shared FN | Enumeration FN |
| --- | ---: | ---: |
| seizure-type / semiology | 175 | 129 |
| epilepsy-syndrome / named dx | 111 | 89 |

