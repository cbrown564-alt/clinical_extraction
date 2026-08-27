# Protocol: Qwen 3.8 27B reserved-candidate measurement

Date: 2026-08-14
Status: smoke passed; overnight queue started 2026-08-14
Authorization: user requested an Ollama download, a one-letter smoke,
then overnight `test` then `dev` if the smoke passes
Does not change: [decision 0051](../../decisions/0051-gemini-37-flash-succeeds-gpt41mini-six-model-slot.md)
roster, [decision 0050](../../decisions/0050-current-stack-hybrid-primary-fills.md)
fills, Decision 0046 Sol method identity, or Qwen 3.6:35B scores

## Question

On the selected current-stack hybrid methods, can local
`ollama_chat/qwen3.8:27b` complete ExECT and Gan letters, and what are the
aggregate holdout scores plus inspectable development scores?

This is a reserved open-weight successor candidate. It is not a six-model
roster swap and not a rewrite of Qwen 3.6:35B cells.

## Data and row policy

| Task | Split | Rows | Row policy |
| --- | --- | ---: | --- |
| ExECTv2 | `test` / `test60` | 59 | aggregate-only holdout |
| Gan 2026 | `test` / `test450` | 450 | aggregate-only holdout |
| ExECTv2 | `dev` / `dev140` | 140 | development, inspectable |
| Gan 2026 | `validation` / `dev750` | 750 | development, inspectable |

Smoke uses one ExECT `dev140` letter only. The overnight queue runs both
holdout cells first, then both development cells. The runner may read locked
notes only to make frozen holdout calls. No holdout identifier, note,
prediction, evidence, error, changed row, or model-specific failure may be
inspected or copied into a report. A holdout defect starts a new development
candidate; it does not license holdout repair.

## Frozen condition

| Field | Value |
| --- | --- |
| Display name | Qwen 3.8 27B |
| Runtime identifier | `ollama_chat/qwen3.8:27b` |
| Endpoint | `http://localhost:11434` |
| Thinking | `think=false` (same local Qwen factory extra_body) |
| Temperature | `0` |
| Max tokens | 16,000 |
| Cache | off |
| `num_ctx` | 32768 |
| ExECT | Decision 0040/0041 one-call, prompt `exectv2_hybrid_key_family_event_ledger_v0.9.24`, default/default assembly |
| Gan | `llm_with_rules`, prompt `gan2026_hybrid_structured_events_v0.5` |

Ollama 0.32.4 cannot pull this tag (HTTP 412: newer Ollama required). Official
library tag is `qwen3.8:27b` (~18 GB). Record the installed Ollama version,
model digest, quantization, and hardware after the pull succeeds.

## Artifact locations

- Smoke: `scratch/local_queue/qwen38_27b/exect/smoke_dev1.jsonl`
- ExECT `test60`: `scratch/holdout/qwen38_27b_20260814/exect_test60/`
- Gan `test450`: `scratch/holdout/qwen38_27b_20260814/gan_test450/`
- ExECT `dev140`: `experiments/exectv2_six_model_single_call_qwen38_27b_dev140_20260814*`
- Gan `dev750`: `experiments/gan2026_qwen38_27b_candidate_dev750_20260814/`
- Gan `dev750` vs Qwen 3.6:35B: [stage comparison](../gan2026/qwen38_27b_vs_qwen36_35b_dev750_2026-08-16.md)
- Queue logs: `scratch/local_queue/qwen38_27b/`

## Stop rule and claim boundary

The one-letter smoke must finish with zero call failures and zero blocking
parse failures before the overnight queue starts. Overnight holdout cells
are aggregate-only. Development cells are exploratory analysis, not paper
primary fills and not a Decision 0051 roster change. Resume is allowed only
for the same frozen condition.

## Commands

```powershell
ollama pull qwen3.8:27b
.venv\Scripts\python.exe scripts\smoke_exectv2_six_model_condition.py `
  --config configs/exectv2/six_model_comparison/qwen38_27b_dev140.json `
  --rows 1 `
  --output scratch/local_queue/qwen38_27b/exect/smoke_dev1.jsonl
```

The Ollama probe and overnight queue scripts were removed in the 2026-08-16
scripts prune; recover them from git history if this queue is resumed.
