# Extract-and-select vs extract + rule Select

Date: 2026-08-25
Status: development answer; not a cited five-cell replacement
Owner: this file
Split: `dev140` only. Holdout was not inspected.

## Primary question

On Gemini 3.7 Flash `dev140` only: is it better to ask the model to
extract and select in one call (`exect_llm_extract_and_select`), or to
ask it only to extract (`exect_llm_extract`) and let inventory Select
filter?

## Protocol

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Split | `dev140` (review permitted) |
| Model | Gemini 3.7 Flash, living low |
| Extract prompt | `exect_llm_extract` |
| Extract-and-select prompt | `exect_llm_extract_and_select` |
| Extract raw | saved `paper_experiments/exect/exect_llm_extract/gemini37flash/dev140/structured.jsonl` (no new calls) |
| Extract-and-select raw | `experiments/paper/exect_llm_extract_filtered/gemini37flash/dev140/exect_llm_extract_and_select/structured.jsonl` |
| Artifact | `experiments/paper/exect_llm_extract_filtered/gemini37flash/dev140/comparison.json` |
| Batch | `batch-1787671522-J1grQUPs7M6RJMTPLHRR` |
| Read-only aliases | `exect_llm_only`, `exect_llm_extract_filtered` |
| Select | `StructuredMethodConfig.inventory()` |
| Scorer | `clinical_inventory_unit_keys` (4-family micro F1) |
| Calls | 140 new Gemini letters for the revised extract-and-select prompt |

The extract-and-select payload keeps generic and specific stated
diagnoses, heading named types, and hedge-implied place or type.
Non-epileptic, future-medication, and pending-test filters stay.
Holdout (`test60`) was not loaded.

## Four headline F1s

| Arm | Extract-stop | Select-stop |
| --- | ---: | ---: |
| `exect_llm_extract` | 0.8273 | 0.8877 |
| `exect_llm_extract_and_select` | 0.8384 | 0.8864 |

## Family breakdown

| Arm | Stop | Overall F1 | Diagnosis P/R/F1 | SeizureFrequency P/R/F1 | Prescription P/R/F1 | Investigations P/R/F1 | TP/FP/FN | Mentions |
| --- | --- | ---: | --- | --- | ---: | --- | ---: | ---: |
| `exect_llm_extract` | extract-stop | 0.8273 | 0.6860/0.7568/0.7197 | 0.7286/0.8788/0.7967 | 0.9650/0.9369/0.9507 | 0.9699/0.9485/0.9591 | 716/179/120 | 973 |
| `exect_llm_extract` | select-stop | 0.8877 | 0.8531/0.8298/0.8413 | 0.8034/0.8667/0.8338 | 0.9798/0.9417/0.9604 | 0.9699/0.9485/0.9591 | 739/90/97 | 913 |
| `exect_llm_extract_and_select` | extract-stop | 0.8384 | 0.7321/0.7477/0.7398 | 0.8250/0.8000/0.8123 | 0.9604/0.9417/0.9510 | 0.9618/0.9265/0.9438 | 698/131/138 | 880 |
| `exect_llm_extract_and_select` | select-stop | 0.8864 | 0.8771/0.8024/0.8381 | 0.8784/0.7879/0.8307 | 0.9706/0.9612/0.9659 | 0.9618/0.9265/0.9438 | 718/66/118 | 841 |

## Reading

The living extract plus inventory Select still wins, but only by
0.0013 (0.8877 vs 0.8864). Extract-and-select is the better
extract-stop (0.8384 vs 0.8273) because the model already filters
some false positives before Select. After the same Select stack,
extract still has higher Diagnosis recall (0.8298 vs 0.8024) and
much higher SeizureFrequency recall (0.8667 vs 0.7879). The remaining
extract-and-select SeizureFrequency misses are often seizure-free or
unspecified-rate states that the one-call rules still refuse unless
attributes are filled. Development only; not a cited five-cell
replacement. Holdout was not loaded.

## Decision

On Gemini `dev140`, ask the model to extract (`exect_llm_extract`) and
let inventory Select filter. Extract-and-select is an ablation, not a
replacement for cell 3.

## Next action

Leave cell 3 on `exect_llm_extract`. Do not promote this ablation.
Do not inspect `test60`. If a follow-up is needed, it is the
extract-and-select SeizureFrequency empty-attribute / seizure-free
rules.
