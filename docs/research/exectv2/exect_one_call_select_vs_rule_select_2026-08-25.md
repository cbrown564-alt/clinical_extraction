# Recognise-and-select vs recognise + rule Select

Date: 2026-08-25
Status: development plus holdout aggregate; not a cited five-cell replacement
Owner: this file
Paper reading: [recognise then Select vs recognise-and-select](../paper/exect_extract_vs_extract_and_select_2026-08-25.md)
Split: Gemini `dev140` (review permitted) and Gemini `test60` (aggregate only).
Holdout rows were not inspected.

## Primary question

On Gemini 3.7 Flash: is it better to ask the model to recognise and
select in one call (`exect_llm_extract_and_select`), or to ask it only
to recognise (`exect_llm_extract`) and let inventory Select filter?

## Protocol

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Model | Gemini 3.7 Flash, living low |
| Recognise prompt | `exect_llm_extract` |
| Recognise-and-select prompt | `exect_llm_extract_and_select` |
| Select | `StructuredMethodConfig.inventory()` |
| Scorer | `clinical_inventory_unit_keys` (4-family micro F1) |
| Read-only aliases | `exect_llm_only`, `exect_llm_extract_filtered` |

`dev140` recognise raw is the saved paper cell
`paper_experiments/exect/exect_llm_extract/gemini37flash/dev140/structured.jsonl`.
Revised recognise-and-select: batch `batch-1787671522-J1grQUPs7M6RJMTPLHRR`,
artifact `experiments/paper/exect_llm_extract_filtered/gemini37flash/dev140/comparison.json`.

`test60` recognise raw is the saved paper cell
`paper_experiments/exect/exect_llm_extract/gemini37flash/test60/comparison.json`
(no new recognise calls). Recognise-and-select: live 59 letters, batch
`batch-1787673799-jlJqmJJ42osgebIjZcEF`, artifact
`scratch/holdout/paper/exect_llm_extract_filtered/gemini37flash/test60/comparison.json`.
Parse 0, schema 0, illegal enum 0. Not promoted.

The recognise-and-select payload keeps generic and specific stated
diagnoses, heading named types, and hedge-implied place or type.
Non-epileptic, future-medication, and pending-test filters stay.

## Four headline F1s (`dev140`)

| Arm | Recognise-stop | Select-stop |
| --- | ---: | ---: |
| `exect_llm_extract` | 0.8273 | 0.8877 |
| `exect_llm_extract_and_select` | 0.8384 | 0.8864 |

## Four headline F1s (`test60`, aggregate only)

| Arm | Recognise-stop | Select-stop |
| --- | ---: | ---: |
| `exect_llm_extract` | 0.8491 | 0.8674 |
| `exect_llm_extract_and_select` | 0.8170 | 0.8435 |

## Family F1 (`test60`, aggregate only)

| Arm | Stop | Overall | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `exect_llm_extract` | recognise-stop | 0.8491 | 0.7932 | 0.8235 | 0.9286 | 0.9247 |
| `exect_llm_extract` | select-stop | 0.8674 | 0.8432 | 0.8082 | 0.9286 | 0.9247 |
| `exect_llm_extract_and_select` | recognise-stop | 0.8170 | 0.7944 | 0.6715 | 0.9036 | 0.9462 |
| `exect_llm_extract_and_select` | select-stop | 0.8435 | 0.8500 | 0.6818 | 0.9036 | 0.9462 |

Select-stop SeizureFrequency recall on `test60`: recognise 0.7973 vs
recognise-and-select 0.6081. No holdout letters or row errors were
opened.

## Reading

On `dev140`, living recognise plus inventory Select still wins, but only
by 0.0013 (0.8877 vs 0.8864). Recognise-and-select is the better
recognise-stop there.

On `test60`, recognise plus inventory Select wins at both stops
(0.8491 vs 0.8170 recognise-stop; 0.8674 vs 0.8435 select-stop). The
gap is mostly SeizureFrequency. Holdout is aggregate-only; this is
not a cited five-cell replacement.

## Decision

Ask the model to recognise (`exect_llm_extract`) and let inventory
Select filter. Recognise-and-select remains an ablation, not a
replacement for cell 3.

## Next action

Leave cell 3 on `exect_llm_extract`. Do not promote this ablation.
Do not inspect `test60` rows. Any follow-up stays on `dev140`
SeizureFrequency empty-attribute / seizure-free rules.
