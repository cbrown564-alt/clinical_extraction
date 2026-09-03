# Protocol: Qwen 3.8 27B Gan `test450` with thinking on

Date: 2026-08-29
Status: complete; aggregate-only
Authorization: user requested locked `test450` on Qwen 3.8 27B with
thinking on and temperature 0

## Question

What are the aggregate Purist and Pragmatic scores of living
`gan_llm_extract` on locked `test450` when local Qwen 3.8 27B runs with
Ollama `think=true` against the living `think=false` temperature-0 cell?

## Data and row policy

| Split | Manifest | Rows | Inspection |
| --- | --- | ---: | --- |
| `test` (`test450`) | `gan2026_split_v1` | 450 | aggregate-only |

The runner may read locked notes only to make the frozen calls. Do not
inspect holdout identifiers, notes, predictions, evidence, errors, or
row tables.

## Frozen condition

| Field | Value |
| --- | --- |
| Method | `gan_llm_extract` |
| Model | `ollama_chat/qwen3.8:27b` |
| Temperature | `0` (living local default) |
| Thinking | `think=true` (non-living; living local default is `false`) |
| Cache | off |
| `num_ctx` | 32768 |

Do not overwrite the living think-off cell. Work lands under
`scratch/holdout/paper/gan_llm_extract/qwen38_27b/thinking_enabled/test450/`.

## Stop rule and claim boundary

Aggregate-only local think-on remasure. Not a roster swap and not a
rewrite of living fills. Compare only aggregates to the existing
temperature-0 think-off cell.

## Command

```powershell
.venv\Scripts\python.exe -m clinical_extraction.paper run `
  --method gan_llm_extract --model qwen38_27b --split test450 `
  --live --thinking enabled
```
