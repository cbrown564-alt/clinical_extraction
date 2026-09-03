# Protocol: local Gan `test450` at temperature 1

Date: 2026-08-28
Status: complete holdout and Gemma `dev750`
Authorization: user requested live Gan `test450` on Gemma 4 26B and
Qwen 3.8 27B at temperature 1, then Gemma `dev750` at temperature 1

## Question

What are the aggregate Purist and Pragmatic scores of living
`gan_llm_extract` when local Gemma and Qwen run at temperature 1
instead of the living local default of 0?

## Data and row policy

| Split | Manifest | Rows | Inspection |
| --- | --- | ---: | --- |
| `test` (`test450`) | `gan2026_split_v1` | 450 | aggregate-only |
| `validation` (`dev750`) | `gan2026_split_v1` | 750 | development, inspectable; Gemma only |

The runner may read locked notes only to make the frozen calls. Do not
inspect holdout identifiers, notes, predictions, evidence, errors, or
row tables. A holdout defect starts a new development candidate.

## Frozen condition

| Field | Value |
| --- | --- |
| Method | `gan_llm_extract` (cell 3 extract) |
| Models | `ollama_chat/gemma4:26b`, `ollama_chat/qwen3.8:27b` |
| Temperature | `1` (non-living; living local default remains `0`) |
| Cache | off |
| Thinking | Qwen `think=false` via the local factory |
| `num_ctx` | Gemma 65536; Qwen 32768 |
| Scorer | living Gan Purist primary, Pragmatic sidecar |

Do not overwrite living temperature-0 cells. Holdout work lands under
`scratch/holdout/paper/gan_llm_extract/{slug}/temperature_1/test450/`.
Gemma development work lands under
`experiments/paper/gan_llm_extract/gemma4_26b/temperature_1/dev750/`.

## Stop rule and claim boundary

Aggregate-only local-model transfer at a non-living temperature. Not a
roster swap, not a rewrite of temperature-0 fills, not holdout
generalization language. Compare only published aggregates to the
existing temperature-0 cells for the same method and models.

## Commands

```powershell
.venv\Scripts\python.exe -m clinical_extraction.paper run `
  --method gan_llm_extract --model qwen38_27b --split test450 `
  --live --temperature 1
.venv\Scripts\python.exe -m clinical_extraction.paper run `
  --method gan_llm_extract --model gemma4_26b --split test450 `
  --live --temperature 1
.venv\Scripts\python.exe -m clinical_extraction.paper run `
  --method gan_llm_extract --model gemma4_26b --split dev750 `
  --live --temperature 1
```
