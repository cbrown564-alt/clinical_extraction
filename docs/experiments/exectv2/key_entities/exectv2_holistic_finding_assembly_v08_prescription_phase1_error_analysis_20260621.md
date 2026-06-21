# ExECTv2 Holistic Assembly v08 Prescription Phase 1 Error Analysis

Date: 2026-06-21  
Split: dev140  
Current assembly: `exectv2_holistic_finding_assembly_v08_dev140`  
Source architecture: holistic finding assembly over frozen family producers  

## Decision

Prescription now clears the >0.9 family target in the official holistic
assembly headline. v08 keeps Diagnosis v05, SF v08, and Investigations v07
fixed, then replaces the Prescription control with the deterministic all-9
regimen parser after targeted regimen-boundary repairs.

| Candidate | Prescription F1 | P | R | TP | FP | FN | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| v07 control | 0.8214 | 0.8090 | 0.8342 | 161 | 38 | 32 | superseded |
| med/inv verifier drop-in | 0.8166 | 0.7731 | 0.8653 | 167 | 49 | 26 | reject |
| per-entity GPT-4.1-mini drop-in | 0.8201 | 0.7634 | 0.8860 | 171 | 53 | 22 | reject |
| prescription adjudicator v02 drop-in | 0.8308 | 0.7990 | 0.8653 | 167 | 42 | 26 | reject |
| deterministic all9 drop-in | 0.9072 | 0.9293 | 0.8860 | 171 | 13 | 22 | clears target |
| deterministic repair v01 | 0.9243 | 0.9316 | 0.9171 | 177 | 13 | 16 | accepted step |
| deterministic repair v03 / v08 lane | 0.9357 | 0.9286 | 0.9430 | 182 | 14 | 11 | accepted |

v08 official holistic headline:

| Family | F1 |
| --- | ---: |
| Diagnosis | 0.9083 |
| SeizureFrequency | 0.9053 |
| Prescription | 0.9357 |
| Investigations | 0.9132 |
| Overall | 0.9152 |

The assembly gate still reports `do-not-promote` because its older P/I
changed-row regression checks expected Prescription and Investigations to remain
unchanged. For this renewed goal, the declared condition was family headline
`>0.900`, which v08 satisfies for all four families.

## Hypotheses Tested

Straight GPT swaps were not enough. The best GPT-4.1-mini-family drop-in reached
only `0.8308`, and key-level union with control raised recall but added enough
false positives to stay below target. Deterministic all9 was the correct anchor:
it already had high precision and mostly missed parser-boundary patterns.

Accepted parser repairs:

- Allow current regimens after prior-trial language when a later active cue
  appears, e.g. "previously tried ... currently taking levetiracetam 1250mg
  twice a day".
- Add `lamtorigine` as a lamotrigine spelling alias.
- Recover left-bound regimens such as `500mg bd of levetiracetam`.
- Trim current dose text before parenthetical or trailing titration plans, so
  `250mg bd (to reduce...)` scores as the current regimen rather than a future
  medication.
- Keep split AM/PM dose slots before a titration tail.
- Suppress future-start and excluded weight-based contexts such as `To start
  carbamazepine`, `suggest introducing zonisamide`, and `60mg/kg/day`.
- Add the `twice aday` typo form.

All accepted rules are prediction-bearing `clinical_epilepsy` parser behavior.

## Remaining Row-Level Errors

v08 Prescription residuals: 11 FN and 14 FP.

Remaining misses are mostly hard boundary or annotation-convention cases:

- Split-dose carbamazepine `100mg am, 200mg pm` in EA0088.
- Current lamotrigine dose followed by planned increase/reduction in EA0197,
  EA0137, and EA0186.
- Annotation oddities: EA0146 gold maps `Brivetiracetam 50mg bd` to
  `DrugName=Perampanel`, while the parser normalizes the text to brivaracetam.
- Residual singletons for perampanel 8mg od, sodium valproate 400mg bd,
  topiramate split dosing, and rescue midazolam.

Remaining over-emissions are mostly current-vs-plan ambiguity:

- Three lamotrigine 75mg bd predictions in reduce/stop contexts.
- Week-by-week lamotrigine plan rows in EA0166.
- Future-start levetiracetam/carbamazepine singletons not fully suppressed.
- One duplicate/historical sodium valproate 400mg bd and one brivaracetam
  annotation-convention mismatch.

These residuals are not ignored, but additional rules here risk becoming
letter-specific. v08 is therefore the stopping point for the dev140 target pass.

## Artifacts

- Manifest: `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml`
- Assembly JSON: `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.json`
- Assembly JSONL: `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.jsonl`
- Assembly report: `docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md`
- Error ledger JSON: `experiments/exectv2_holistic_finding_assembly_v08_error_ledger_dev140_20260621.json`
- Error ledger MD: `experiments/exectv2_holistic_finding_assembly_v08_error_ledger_dev140_20260621.md`
- Prescription source JSONL: `experiments/exectv2_deterministic_prescription_repair_v03_dev140_20260621.jsonl`
- Prescription residual ledger: `experiments/exectv2_deterministic_prescription_repair_v03_error_ledger_dev140_20260621.md`
