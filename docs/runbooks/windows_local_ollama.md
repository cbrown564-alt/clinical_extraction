# Windows Local Ollama Runbook

This runbook covers repository-side preparation for running Gan 2026 LLM
experiments on a Windows laptop with a local Qwen model served by Ollama.
Install and configure Ollama separately first.

## Environment

From the repo root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
```

If PowerShell blocks activation, enable scripts for the current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Smoke Test Without Model Calls

Confirm the CLI, split loading, and artifact writing work before touching the
local model:

```powershell
gan2026-llm-experiment --pipeline llm_only_claim_table_selector --mode prompt-only --limit 25 --jsonl experiments\windows_prompt_only.jsonl --markdown experiments\windows_prompt_only.md
```

## Local Model Smoke Test

After Ollama is running and the Qwen model is available locally, run a small
native Ollama endpoint check before using DSPy:

```powershell
$body = @{
  model = "qwen3.6:35b"
  messages = @(@{ role = "user"; content = "Return exactly JSON: {`"ok`": true}" })
  stream = $false
  options = @{ temperature = 0; num_predict = 32 }
  think = $false
} | ConvertTo-Json -Depth 6
Invoke-RestMethod -Method Post -Uri http://localhost:11434/api/chat -ContentType "application/json" -Body $body
```

For DSPy/LiteLLM, use Ollama's native chat provider route, not the
OpenAI-compatible `/v1/chat/completions` route:

```powershell
$env:OPENAI_API_KEY = "ollama"
gan2026-llm-experiment --pipeline llm_only_claim_table_selector --mode live --limit 1 --model ollama_chat/qwen3.6:35b --api-base http://localhost:11434 --disable-dspy-cache --jsonl experiments\windows_qwen1.jsonl --markdown experiments\windows_qwen1.md
```

Use `qwen3.6:35b` for the planned strong-local comparison. Use
`qwen3.6:27b` only for hardware-constrained endpoint smoke tests and record the
downgrade in the artifact notes. The shared LM builder strips an accidental
`/v1` suffix from `--api-base` for `ollama_chat/...` models and sends
`extra_body={"think": False}` so Qwen reasoning models do not hide final output
inside thinking mode.

Do not run Qwen 3.6 through `--model openai/qwen3.6:35b --api-base
http://localhost:11434/v1`. That route can return hidden reasoning while
leaving the assistant content empty, which causes DSPy parse failures rather
than meaningful extraction failures.

Once validation1 succeeds, run the normal local ladder one step at a time:

```powershell
gan2026-llm-experiment --pipeline llm_only_claim_table_selector --mode live --limit 5 --model ollama_chat/qwen3.6:35b --api-base http://localhost:11434 --disable-dspy-cache --jsonl experiments\windows_qwen5.jsonl --markdown experiments\windows_qwen5.md
gan2026-llm-experiment --pipeline llm_only_claim_table_selector --mode live --limit 25 --model ollama_chat/qwen3.6:35b --api-base http://localhost:11434 --disable-dspy-cache --jsonl experiments\windows_qwen25.jsonl --markdown experiments\windows_qwen25.md
```

Record the exact local model metadata from `http://localhost:11434/api/tags`,
including digest, parameter size, and quantization.

## First Full Validation750 Qwen Rerun

This is the current planned local-model rerun for the Gan 2026 reset thread.
It should be run as a single combined pipeline command, not as a staged
candidate-set assembly chain.

Use the repo virtual environment entrypoints explicitly:

```powershell
.\.venv\Scripts\Activate.ps1
$env:OPENAI_API_KEY = "ollama"

$qwenJsonl = "experiments\gan2026_hybrid_parallel_state_candidate_reasoner_validation750_qwen36_35b_v0_live_2026-06-06.jsonl"
$qwenMd    = "experiments\gan2026_hybrid_parallel_state_candidate_reasoner_validation750_qwen36_35b_v0_live_2026-06-06.md"

.\.venv\Scripts\gan2026-llm-experiment.exe `
  --pipeline hybrid_parallel_state_candidate_reasoner `
  --split validation `
  --mode live `
  --model ollama_chat/qwen3.6:35b `
  --api-base http://localhost:11434 `
  --temperature 0 `
  --max-tokens 5000 `
  --disable-dspy-cache `
  --progress-every 25 `
  --escalation-reason "First full validation750 local-Qwen rerun; 250 rows are insufficient because we now need the combined end-to-end pipeline result on the full validation surface." `
  --jsonl $qwenJsonl `
  --markdown $qwenMd
```

Notes:

- Use `ollama_chat/qwen3.6:35b` with `--api-base http://localhost:11434`, not
  the OpenAI-compatible `/v1` route.
- Omit `--limit` for the full locked validation750 surface.
- If any target artifact already exists and you want to continue the live LLM
  stages, add `--resume-existing` to the relevant
  `gan2026-llm-experiment.exe` command. Use `--overwrite-existing` only when
  you intentionally want to replace an existing output.
- If we want candidate-set, projection, route, or verifier analyses after the
  live run, generate them afterward from the saved combined-run artifact rather
  than using them as the execution protocol.

## Portability Notes

- Prefer `python -m pytest`, `python -m ruff check .`, and
  `python -m mypy src tests` over shell aliases.
- Keep repo paths relative when passing artifact paths.
- Paths containing spaces, such as `data\Gan (2026)\...`, should be quoted in
  ad hoc commands.
- The LLM report records `api_base`; add quantization, hardware notes,
  endpoint smoke latency, cache state, and output-format failure counts to the
  experiment report or registry notes when comparing local and hosted runs.
