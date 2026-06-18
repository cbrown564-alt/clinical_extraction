# ExECTv2 Diagnosis Enumeration Recall Pass — Result

- Generated: `2026-06-19` (run cycle `2026-06-18`)
- Split/stage: `dev` ladder (`pilot25` -> `dev140`)
- Model: `openai/gpt-4.1-mini`, one call per dev row, temperature `0.0`
- Predeclaration:
  `docs/experiments/exectv2/predeclarations/exectv2_diagnosis_enumeration_recall_pass_predeclaration_2026-06-18.md`
- Component: `exectv2_llm_diagnosis_enumeration_v0.1`, owner `llm_first`
- Gate decision: **PROMOTED as a dev architecture route (clean `llm_first`)**
- Artifacts:
  - `experiments/exectv2_llm_diagnosis_enumeration_v01_pilot25_gpt41mini_20260618.jsonl`
  - `experiments/exectv2_llm_diagnosis_enumeration_v01_dev140_gpt41mini_20260618.jsonl`
  - `experiments/exectv2_diagnosis_enumeration_routed_readout_dev140_20260618.json`
  - `docs/experiments/exectv2/key_entities/exectv2_diagnosis_enumeration_routed_readout_2026-06-18.md`

## Key Result

A single Diagnosis enumeration pass — instructed to list every seizure-type,
semiology, and epilepsy-syndrome mention as a Diagnosis candidate, without
de-duplicating against SeizureFrequency or collapsing repeated mentions — lifts
the routed Diagnosis lane from `0.2898` to `0.6530` and the routed four-family
CUI-free headline from `0.5592` to `0.6835`, at **clean `llm_first` ownership**
for the Diagnosis lane. The aggregate label stays `llm_first_with_hybrid_sf_route`
(the qualifier is the SF route only; the Diagnosis lane adds no hybrid debt).

The predeclared over-enumeration / precision-leak risk did **not** materialise:
Diagnosis precision rose `0.4162 -> 0.6584` alongside recall `0.2222 -> 0.6477`.

## Four-Family Routed Surface (CUI-free, dev140)

| Candidate | F1 | Precision | Recall |
| --- | ---: | ---: | ---: |
| deterministic_all9 | 0.7301 | 0.7281 | 0.7322 |
| llm_only_all_entities | 0.4313 | 0.4860 | 0.3876 |
| hybrid_all_entities | 0.5684 | 0.5931 | 0.5458 |
| family_routed_llm_first | 0.5592 | 0.6195 | 0.5096 |
| **family_routed_with_diagnosis_enumeration_pass** | **0.6835** | 0.6801 | 0.6870 |

## Diagnosis Lane (CUI-free, dev140)

| Lane | F1 | Precision | Recall |
| --- | ---: | ---: | ---: |
| shared-pass Diagnosis (baseline) | 0.2898 | 0.4162 | 0.2222 |
| enumeration Diagnosis | 0.6530 | 0.6584 | 0.6477 |

## candidate_miss FN by slice (dev140, lower is better)

| Slice | Baseline shared FN | Enumeration FN | Reduction |
| --- | ---: | ---: | ---: |
| seizure-type / semiology | 175 | 129 | -46 (-26%) |
| epilepsy-syndrome / named dx | 111 | 89 | -22 (-20%) |

## Gate Evaluation (dev140)

| Gate | Threshold | Observed | Verdict |
| --- | --- | ---: | --- |
| four-family CUI-free F1 > baseline | > 0.5592 | 0.6835 | PASS |
| Diagnosis F1 absolute floor | >= 0.60 | 0.6530 | PASS |
| Diagnosis F1 lift over shared | >= +0.25 | +0.3632 | PASS |
| Diagnosis recall strictly up | > 0.2222 | 0.6477 | PASS |
| Diagnosis precision floor | >= 0.55 | 0.6584 | PASS |
| Diagnosis evidence validity | >= 0.99 | 0.9953 | PASS |
| P/I/SF F1 drift | <= 0.001 | 0.0000 | PASS |

Pilot25 promotion gates also passed: 0 call failures, 0 parse failures,
evidence validity `1.0000`, P/I/SF byte-identical to the current routed assembly,
exactly one model call per row.

## Honest Limits (claim language)

- **Does not beat the deterministic baseline.** On dev140 the enumeration route
  (`0.6835`) closes most of the gap to `deterministic_all9` (`0.7301`) but does
  not surpass it. (On pilot25 it did, `0.8396 > 0.7862`, but pilot25 is 25 rows
  and not the headline surface.) The rules-still-lead fact stands.
- **Diagnosis is not solved.** `0.6530` is roughly on par with the existing
  hybrid reconciler/decomposer candidates (`0.642`-`0.658`) and below the
  no-call focused-replay expectation (`0.7127`) cited in the predeclaration. The
  material change is ownership: this recall is now clean `llm_first`, not hybrid.
- **Dev-only.** No Gan `test450`, ExECTv2 full-200/test, or holdout row-level
  artifact was touched. This is dev architecture evidence and cannot support a
  benchmark or holdout generalization claim.

## What This Confirms

The dev140 Diagnosis weakness was a candidate-generation recall gap, not a
projection or representation problem: instructing the LLM to enumerate
seizure-type and syndrome mentions exhaustively recovered most of the missing
concepts (both slices reduced) and is the clean-`llm_first` counterpart to the
hybrid SF event/state route. It is the first routed lane where the LLM-first
architecture posts a recall gain without an ownership downgrade.
